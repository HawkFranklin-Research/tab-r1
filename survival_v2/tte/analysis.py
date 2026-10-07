"""Analysis stage: question-level tables from metrics/run_metrics.parquet and metrics/external_metrics.parquet.

All contrasts are paired on identical test sets (same cohort, cancer, repeat, fold). Intervals resample the 25 test sets of each
cancer with replacement (2,000 draws) and average cancers for macro summaries. Test sets overlap in training patients, so these
intervals are optimistic; they describe fold-to-fold variation, not a population confidence interval (stated in the README).

Tables written to analysis/:
  q1_summary.csv            context A: mean and SD over test sets per model, per cancer and macro (C, Uno C, td-AUC, Brier)
  q1_vs_reference.csv       context A: each model minus the reference model (default coxnet), paired, with intervals
  q1_ranks.csv              context A: mean rank of each model across cancer x test-set units, Friedman test
  q1_pooled.csv             context P: all-pairs C versus within-cancer (stratified) C per model
  q2_contrasts.csv          B-A, C-A, C-B (and D-A) per model and cancer, macro, with intervals
  q2_family.csv             foundation minus tree mean change for each contrast (difference in differences)
  q3_increments.csv         omics_clinical - clinical and omics - clinical per model and cancer, macro
  q4_summary.csv            external validation per direction, arm and model (mean over seeds, patient-bootstrap interval)
  runtime.csv               median fit/predict seconds per model
  model_coverage.csv        which survival route each model family has (native, pseudo, ipcw)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare

from .config import Cfg, Paths
from .models import CLASSIFIERS, REGRESSORS, TABPFN_VERSIONS

UNIT = ["cohort", "cancer", "repeat", "fold"]
METRICS = ["c_harrell", "c_uno", "auc_h3", "auc_h5", "brier_h3", "brier_h5", "auc_elig_h3", "auc_elig_h5"]


def _boot_means(values_by_cancer: dict[str, np.ndarray], n_boot: int, rng) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    per = {}
    for c, v in values_by_cancer.items():
        v = v[np.isfinite(v)]
        per[c] = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(n_boot)]) if len(v) else np.full(n_boot, np.nan)
    macro = np.nanmean(np.vstack(list(per.values())), axis=0) if per else np.full(n_boot, np.nan)
    return macro, per


def paired_contrast(df: pd.DataFrame, metric: str, cond_col: str, a: str, b: str, by: list[str], n_boot: int, seed: int) -> pd.DataFrame:
    """b - a on identical units, per ``by`` group and cancer, plus a macro row (cancer='macro')."""
    sub = df[df[cond_col].isin([a, b])]
    if sub.duplicated(by + UNIT + [cond_col]).any():
        raise ValueError(f"paired_contrast: more than one row per unit for {by + [cond_col]} (two specs share a model_key in one unit)")
    wide = sub.pivot_table(index=by + UNIT, columns=cond_col, values=metric, aggfunc="first")
    if a not in wide or b not in wide:
        return pd.DataFrame()
    wide = wide.dropna(subset=[a, b])
    wide["diff"] = wide[b] - wide[a]
    rng = np.random.default_rng(seed)
    rows = []
    for key, g in wide.reset_index().groupby(by + ["cohort"]):
        key = key if isinstance(key, tuple) else (key,)
        vals = {c: gg["diff"].to_numpy() for c, gg in g.groupby("cancer")}
        macro_draws, per_draws = _boot_means(vals, n_boot, rng)
        base = dict(zip(by + ["cohort"], key))
        for c, v in vals.items():
            rows.append({**base, "cancer": c, "contrast": f"{b}-{a}", "metric": metric, "n_units": len(v), "mean_a": float(g.loc[g.cancer == c, a].mean()),
                         "mean_b": float(g.loc[g.cancer == c, b].mean()), "diff": float(np.nanmean(v)),
                         "lo": float(np.nanpercentile(per_draws[c], 2.5)), "hi": float(np.nanpercentile(per_draws[c], 97.5))})
        rows.append({**base, "cancer": "macro", "contrast": f"{b}-{a}", "metric": metric, "n_units": int(sum(len(v) for v in vals.values())),
                     "mean_a": float(g.groupby("cancer")[a].mean().mean()), "mean_b": float(g.groupby("cancer")[b].mean().mean()),
                     "diff": float(np.nanmean([np.nanmean(v) for v in vals.values()])),
                     "lo": float(np.nanpercentile(macro_draws, 2.5)), "hi": float(np.nanpercentile(macro_draws, 97.5))})
    return pd.DataFrame(rows)


def summarise(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    metrics = [m for m in METRICS if m in df]
    per = df.groupby(by + ["cancer"])[metrics].agg(["mean", "std"])
    per.columns = [f"{m}_{s}" for m, s in per.columns]
    per = per.reset_index()
    macro = per.groupby(by)[[c for c in per.columns if c.endswith("_mean")]].mean().reset_index()
    macro["cancer"] = "macro"
    return pd.concat([per, macro], ignore_index=True)


def ranks(df: pd.DataFrame, metric: str = "c_harrell") -> tuple[pd.DataFrame, dict]:
    full = df.pivot_table(index=UNIT, columns="model_key", values=metric)
    wide = full.dropna(axis=1, how="any").dropna()
    dropped = sorted(set(full.columns) - set(wide.columns))
    if wide.shape[1] < 3 or wide.shape[0] < 3:
        return pd.DataFrame(), {"dropped_models": dropped}
    r = wide.rank(axis=1, ascending=False)
    stat, p = friedmanchisquare(*[wide[c].to_numpy() for c in wide.columns])
    out = r.mean().sort_values().rename("mean_rank").reset_index()
    return out, {"friedman_chi2": float(stat), "p_value": float(p), "n_units": int(wide.shape[0]), "n_models": int(wide.shape[1]),
                 "dropped_models_with_missing_units": ";".join(dropped)}


def coverage_table() -> pd.DataFrame:
    models = sorted(set(REGRESSORS) | set(CLASSIFIERS))
    rows = []
    for m in models:
        rows.append({"model": m, "native_survival": m in TABPFN_VERSIONS, "pseudo_observations": m in REGRESSORS,
                     "ipcw_classifier": m in CLASSIFIERS})
    rows += [{"model": c, "native_survival": True, "pseudo_observations": False, "ipcw_classifier": False}
             for c in ("coxnet", "coxph", "rsf", "gbsa")]
    return pd.DataFrame(rows)


def run_analysis(cfg: Cfg, paths: Paths, n_boot: int = 2000, reference: str = "coxnet", log=print) -> dict:
    out_dir = paths.analysis
    out_dir.mkdir(parents=True, exist_ok=True)
    seed = int(cfg["compute"]["seed"])
    n_boot = 200 if cfg.get("smoke_mode") else n_boot
    written = {}
    mpath = paths.metrics / "run_metrics.parquet"
    if mpath.exists():
        m = pd.read_parquet(mpath)
        A = m[(m.context == "A") & (m.arm == "omics")]
        if len(A):
            summarise(A, ["cohort", "model_key", "model_group"]).to_csv(out_dir / "q1_summary.csv", index=False)
            A2 = A.assign(cond=np.where(A.model_key == reference, "ref", A.model_key))
            parts = []
            for mk in sorted(set(A.model_key) - {reference}):
                for metric in ("c_harrell", "c_uno"):
                    d = paired_contrast(A2[A2.cond.isin(["ref", mk])], metric, "cond", "ref", mk, [], n_boot, seed)
                    if len(d):
                        parts.append(d.assign(model_key=mk, reference=reference))
            if parts:
                pd.concat(parts, ignore_index=True).to_csv(out_dir / "q1_vs_reference.csv", index=False)
            rk, fr = ranks(A)
            if len(rk):
                rk.to_csv(out_dir / "q1_ranks.csv", index=False)
                pd.DataFrame([fr]).to_csv(out_dir / "q1_friedman.csv", index=False)
            written["q1"] = len(A)
        P = m[m.context == "P"]
        if len(P):
            cols = [c for c in P.columns if c.startswith("c_") and c not in ("c_harrell_lo", "c_harrell_hi")]
            P.groupby(["cohort", "model_key", "model_group"])[cols].mean().reset_index().to_csv(out_dir / "q1_pooled.csv", index=False)
            written["q1_pooled"] = len(P)
        Q2 = m[(m.arm == "omics") & m.context.isin(["A", "B", "C", "D"])]
        if Q2.context.nunique() > 1:
            parts = []
            for a, b in [("A", "B"), ("A", "C"), ("B", "C"), ("A", "D")]:
                if {a, b} <= set(Q2.context):
                    for metric in ("c_harrell", "c_uno"):
                        parts.append(paired_contrast(Q2, metric, "context", a, b, ["model_key", "model_group"], n_boot, seed))
            q2 = pd.concat([p for p in parts if len(p)], ignore_index=True)
            q2.to_csv(out_dir / "q2_contrasts.csv", index=False)
            fam = (q2[q2.cancer == "macro"].groupby(["cohort", "contrast", "metric", "model_group"])["diff"].mean().unstack("model_group"))
            if {"foundation", "tree"} <= set(fam.columns):
                fam["foundation_minus_tree"] = fam["foundation"] - fam["tree"]
            fam.reset_index().to_csv(out_dir / "q2_family.csv", index=False)
            written["q2"] = len(q2)
        Q3 = m[m.context == "A"]
        if {"clinical", "omics_clinical"} <= set(Q3.arm):
            parts = []
            for a, b in [("clinical", "omics_clinical"), ("clinical", "omics")]:
                for metric in ("c_harrell", "c_uno"):
                    parts.append(paired_contrast(Q3, metric, "arm", a, b, ["model_key", "model_group"], n_boot, seed))
            q3 = pd.concat([p for p in parts if len(p)], ignore_index=True)
            q3.to_csv(out_dir / "q3_increments.csv", index=False)
            written["q3"] = len(q3)
        rt = m.groupby("model_key")[["fit_seconds", "predict_seconds"]].median().reset_index()
        rt.to_csv(out_dir / "runtime.csv", index=False)
    epath = paths.metrics / "external_metrics.parquet"
    if epath.exists():
        e = pd.read_parquet(epath)
        cols = [c for c in ["c_harrell", "c_harrell_lo", "c_harrell_hi", "c_uno", "auc_h3", "auc_h5", "brier_h3", "brier_h5"] if c in e]
        e.groupby(["direction", "arm", "model_key", "model_group"])[cols].mean().reset_index().to_csv(out_dir / "q4_summary.csv", index=False)
        written["q4"] = len(e)
    coverage_table().to_csv(out_dir / "model_coverage.csv", index=False)
    log(f"analysis tables written to {out_dir}: {written}")
    return written
