"""Question 4: external validation between TCGA-BRCA and METABRIC, in both directions.

TCGA uses RNA-seq and METABRIC an Illumina HT-12 microarray, so values are never compared on their raw scale: each cohort is
z-scored on its own (TCGA values are already z-scored within the TCGA block by the c-5 pipeline; METABRIC log2 intensities are
z-scored per gene here, duplicated symbols averaged). Only gene symbols present in both cohorts are used. Feature selection,
pseudo-values and model fitting use the training cohort only; the other cohort is touched only at prediction time.
Follow-up is administratively censored at ``external.max_followup_days`` in both cohorts (METABRIC follows patients for ~16 years,
TCGA for far less). Overall survival counts deaths from any cause in both cohorts.

Outputs: external/predictions/<direction>/<arm>/seed<k>.parquet (same schema as the internal predictions),
external/runs/<direction>/<arm>/seed<k>.json, external/train_outcomes_<direction>.parquet.
"""

from __future__ import annotations

import json
import time
import traceback

import numpy as np
import pandas as pd

from . import pseudo as pseudo_mod
from .config import Cfg, Paths, horizons as cfg_horizons
from .limits import clear_accelerator_cache
from .models import FitContext, build_model, model_key, normalise
from .runner import atomic_parquet, atomic_text, read_json
from .store import ArrayStore

MONTH_DAYS = 30.4375
DIRECTIONS = {"tcga_to_metabric": ("TCGA", "METABRIC"), "metabric_to_tcga": ("METABRIC", "TCGA")}


def _read_cbio(path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", comment="#", low_memory=False)


def load_metabric(root) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (patients: time, event, age, stage indexed by patient id; expression: patients x gene symbols, z-scored)."""
    pat = _read_cbio(root / "data_clinical_patient.txt").set_index("PATIENT_ID")
    pat = pat[~pat.index.duplicated()]
    smp = _read_cbio(root / "data_clinical_sample.txt")
    smp = smp.drop_duplicates("PATIENT_ID").set_index("PATIENT_ID")       # one primary sample per patient in brca_metabric
    clinical = pd.DataFrame(index=pat.index)
    clinical["time"] = pd.to_numeric(pat["OS_MONTHS"], errors="coerce") * MONTH_DAYS
    clinical["event"] = pat["OS_STATUS"].astype(str).str.startswith("1").astype(int)
    clinical.loc[pat["OS_STATUS"].isna(), "event"] = np.nan
    clinical["age"] = pd.to_numeric(pat["AGE_AT_DIAGNOSIS"], errors="coerce")
    stage = pd.to_numeric(smp["TUMOR_STAGE"], errors="coerce").reindex(clinical.index)
    clinical["stage"] = stage.where(stage.between(1, 4))       # stage 0 (in situ) has no TCGA counterpart
    expr = pd.read_csv(root / "data_mrna_illumina_microarray.txt", sep="\t", low_memory=False)
    expr = expr.dropna(subset=["Hugo_Symbol"]).drop(columns=["Entrez_Gene_Id"]).groupby("Hugo_Symbol").mean()
    values = expr.to_numpy(np.float32).T                            # patients x genes
    mean = np.nanmean(values, axis=0)
    sd = np.nanstd(values, axis=0)
    z = (values - mean) / np.where(sd > 0, sd, 1.0)
    z = np.where(np.isnan(z), 0.0, z).astype(np.float32)
    expression = pd.DataFrame(z, index=expr.columns, columns=expr.index)
    keep = clinical.index.intersection(expression.index)
    clinical = clinical.loc[keep]
    clinical = clinical[clinical["time"].notna() & clinical["event"].notna() & (clinical["time"] > 0)]
    return clinical, expression.loc[clinical.index]


def _censor(frame: pd.DataFrame, max_days) -> pd.DataFrame:
    frame = frame.copy()
    if max_days:
        late = frame["time"] > float(max_days)
        frame.loc[late, "time"] = float(max_days)
        frame.loc[late, "event"] = 0
    frame["event"] = frame["event"].astype(int)
    return frame


def build_cohorts(cfg: Cfg, paths: Paths, store: ArrayStore):
    """Aligned TCGA-BRCA and METABRIC cohorts: dict name -> (outcomes, expression [n x G], clinical [n x q]); gene list."""
    mb_clin, mb_expr = load_metabric(paths.metabric)
    feats = store.features
    thr = float(cfg["features"]["min_observed"]["tcga"])
    rna = feats[(feats["modality"] == "rnaseq_gene") & feats["gene"].notna() & (feats["obs_BRCA_tcga"] >= thr)]
    rna = rna[~rna["gene"].duplicated()]
    shared = sorted(set(rna["gene"]) & set(mb_expr.columns))
    cols = rna.set_index("gene").loc[shared].index
    col_idx = rna.reset_index().set_index("gene").loc[shared, "index"].to_numpy(np.int64)
    s = store.samples
    tc = s[(s["cancer"] == "BRCA") & (s["source"] == "TCGA") & s["os_days"].notna() & s["os_event"].isin([0, 1]) & (s["os_days"] > 0)]
    tc_out = pd.DataFrame({"patient_id": tc["patient_id"].to_numpy(), "time": tc["os_days"].to_numpy(float),
                           "event": tc["os_event"].to_numpy(int), "cancer": "BRCA", "source": "TCGA"})
    mb_out = pd.DataFrame({"patient_id": mb_clin.index.to_numpy(), "time": mb_clin["time"].to_numpy(float),
                           "event": mb_clin["event"].to_numpy(int), "cancer": "BRCA", "source": "METABRIC"})
    max_days = cfg["external"]["max_followup_days"]
    tc_out, mb_out = _censor(tc_out, max_days), _censor(mb_out, max_days)
    clin_cols = list(cfg["external"]["clinical"])
    tc_clin = store.clinical.reindex(tc_out["patient_id"])[clin_cols].to_numpy(np.float32)
    mb_clin_arr = mb_clin.loc[mb_out["patient_id"], clin_cols].to_numpy(np.float32)
    cohorts = {
        "TCGA": (tc_out, store.omics(tc_out["patient_id"], col_idx), tc_clin),
        "METABRIC": (mb_out, mb_expr.loc[mb_out["patient_id"], list(cols)].to_numpy(np.float32), mb_clin_arr),
    }
    return cohorts, list(cols)


def _select_dense(X: np.ndarray, target: np.ndarray, k: int) -> np.ndarray:
    """Top-k |Pearson r| with the pseudo-value target (training cohort only)."""
    xc = X - X.mean(axis=0)
    yc = target - target.mean()
    denom = np.sqrt((xc ** 2).sum(axis=0) * (yc ** 2).sum())
    r = np.where(denom > 0, (xc.T @ yc) / np.where(denom > 0, denom, 1.0), 0.0)
    return np.argsort(-np.abs(r), kind="stable")[:k]


def run_external(cfg: Cfg, paths: Paths, store: ArrayStore, device: str, threads: int, models_override=None,
                 force: bool = False, log=print) -> list[dict]:
    specs = [normalise(s) for s in (models_override or (cfg["smoke"]["external_models"] if cfg.get("smoke_mode") else cfg["model_sets"]["q4"]))]
    horizons, tau = cfg_horizons(cfg), float(cfg["tau_days"])
    cohorts, genes = build_cohorts(cfg, paths, store)
    log(f"external: {len(genes):,} shared genes; TCGA-BRCA n={len(cohorts['TCGA'][0])} (events {int(cohorts['TCGA'][0]['event'].sum())}), "
        f"METABRIC n={len(cohorts['METABRIC'][0])} (events {int(cohorts['METABRIC'][0]['event'].sum())}) after censoring at "
        f"{cfg['external']['max_followup_days']} days")
    out_root = paths.external
    results = []
    k = int(cfg["features"]["k"])
    for direction, (train_name, test_name) in DIRECTIONS.items():
        tr_out, tr_x, tr_c = cohorts[train_name]
        te_out, te_x, te_c = cohorts[test_name]
        (out_root).mkdir(parents=True, exist_ok=True)
        tr_out.to_parquet(out_root / f"train_outcomes_{direction}.parquet", index=False)
        pseudo = pseudo_mod.pseudo_values(tr_out["time"].to_numpy(float), tr_out["event"].to_numpy(int), horizons, tau)
        top = _select_dense(tr_x, pseudo["rmst"], k)
        for arm in ("omics", "clinical", "omics_clinical"):
            blocks_tr = ([tr_x[:, top]] if "omics" in arm else []) + ([tr_c] if "clinical" in arm else [])
            blocks_te = ([te_x[:, top]] if "omics" in arm else []) + ([te_c] if "clinical" in arm else [])
            X_tr, X_te = np.hstack(blocks_tr), np.hstack(blocks_te)
            for seed_k in range(int(cfg["external"]["n_seeds"])):
                pred_path = out_root / "predictions" / direction / arm / f"seed{seed_k}.parquet"
                run_path = out_root / "runs" / direction / arm / f"seed{seed_k}.json"
                existing = None
                if pred_path.exists() and not force:
                    try:
                        existing = pd.read_parquet(pred_path)
                    except Exception:
                        existing = None              # a torn file from an interrupted run is simply recomputed
                done = set(existing["model"]) if existing is not None else set()
                todo = [s for s in specs if s not in done]
                if not todo:
                    continue
                fctx = FitContext(pseudo=pseudo, meta=tr_out[["patient_id", "cancer", "source"]], horizons=horizons, tau=tau,
                                  seed=int(cfg["compute"]["seed"]) + seed_k, threads=threads, device=device, cfg=dict(cfg["models"]))
                meta_te = te_out[["patient_id", "cancer", "source"]].reset_index(drop=True)
                rows, statuses = [], {}
                for spec in todo:
                    t1 = time.time()
                    try:
                        model = build_model(spec).fit(X_tr, tr_out["time"].to_numpy(float), tr_out["event"].to_numpy(int), fctx)
                        fit_s = time.time() - t1
                        frame = meta_te.copy()
                        frame.insert(0, "model", spec)
                        frame["time"], frame["event"] = te_out["time"].to_numpy(float), te_out["event"].to_numpy(int)
                        frame["risk"] = np.asarray(model.predict_risk(X_te, meta_te), float)
                        surv = model.predict_survival(X_te, horizons, meta_te)
                        for name in horizons:
                            frame[f"surv_{name}"] = surv.get(name) if surv.get(name) is not None else np.nan
                        for name, values in model.predict_aux(X_te, meta_te).items():
                            frame[name] = np.asarray(values, float)
                        rows.append(frame)
                        statuses[spec] = {"status": "ok", "fit_seconds": round(fit_s, 3), "model_key": model_key(spec)}
                    except Exception as exc:
                        statuses[spec] = {"status": "error", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()[-2500:]}
                    finally:
                        clear_accelerator_cache()
                pred_path.parent.mkdir(parents=True, exist_ok=True)
                run_path.parent.mkdir(parents=True, exist_ok=True)
                if rows:
                    new = pd.concat(rows, ignore_index=True)
                    merged = new if existing is None else pd.concat([existing[~existing["model"].isin(new["model"])], new], ignore_index=True)
                    atomic_parquet(merged, pred_path)
                info = read_json(run_path) if not force else {}
                info.update({"direction": direction, "arm": arm, "seed": seed_k, "n_train": len(tr_out), "n_test": len(te_out),
                             "genes_selected": [genes[i] for i in top] if "omics" in arm else []})
                info.setdefault("models", {}).update(statuses)
                atomic_text(json.dumps(info, indent=1, default=str), run_path)
                n_err = sum(s["status"] != "ok" for s in statuses.values())
                log(f"external {direction}/{arm}/seed{seed_k}: {len(todo)} models, {n_err} errors")
                results.append({"direction": direction, "arm": arm, "seed": seed_k, "models": len(todo), "errors": n_err})
    return results
