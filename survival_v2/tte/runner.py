"""Fit stage: enumerate work units, fit every model on every frozen training set, save per-patient predictions.

A *unit* is one training/test set: (context, cohort, arm, cancer, repeat, fold). For each unit the expensive shared steps
(pseudo-values, feature selection, design matrices) are done once and every requested model is fitted on the result.

Outputs per unit (paths mirror the unit key ``<context>/<cohort>/<arm>/<cancer>/r<repeat>_f<fold>``):
  predictions/<key>.parquet   one row per (model, test patient): risk, survival probability at each horizon, raw regressor
                              predictions, plus time/event/cancer/source, so every metric can be recomputed from raw results
  runs/<key>.json             training/test sizes, selected feature ids, per-model status, timings and errors

Resume: a unit/model pair already present in the prediction file is skipped, so an interrupted run (or a Spot VM pre-emption)
continues where it stopped. ``shard=(i, n)`` takes every n-th unit starting at i, for parallel processes or machines.
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from . import pseudo as pseudo_mod
from .config import Cfg, Paths, horizons as cfg_horizons
from .design import DesignSpec, build_design
from .folds import Folds
from .limits import clear_accelerator_cache
from .models import FitContext, build_model, model_key, normalise
from .selection import select_features
from .store import ArrayStore

PRED_COLUMNS = ["model", "patient_id", "cancer", "source", "time", "event", "risk"]


@dataclass(frozen=True)
class Unit:
    context: str
    cohort: str
    arm: str
    cancer: str
    repeat: int
    fold: int

    @property
    def key(self) -> str:
        return f"{self.context}/{self.cohort}/{self.arm}/{self.cancer}/r{self.repeat}_f{self.fold}"


def n_folds_to_run(cfg: Cfg) -> int:
    return int(cfg["smoke"]["n_splits_run"]) if cfg.get("smoke_mode") else int(cfg["folds"]["n_splits"])


def model_list(cfg: Cfg, question: str, override: list[str] | None) -> list[str]:
    if override:
        return [normalise(s) for s in override]
    if cfg.get("smoke_mode"):
        return [normalise(s) for s in cfg["smoke"]["models"]]
    return [normalise(s) for s in cfg["model_sets"][question]]


def _add_spec(bucket: list[str], spec: str) -> None:
    """Add ``spec`` unless a spec with the same model key is present; of two such pseudo specs keep the one with more targets."""
    for i, have in enumerate(bucket):
        if model_key(have) == model_key(spec):
            if len(spec.split(":")[-1].split("+")) > len(have.split(":")[-1].split("+")) and spec.startswith("pseudo:"):
                bucket[i] = spec
            return
    bucket.append(spec)


def enumerate_units(cfg: Cfg, questions: list[str], models_override: list[str] | None = None) -> list[tuple[Unit, list[str]]]:
    """All units of the requested questions with the union of their model specs (deterministic order)."""
    plan: dict[Unit, list[str]] = {}
    n_folds = n_folds_to_run(cfg)
    for q in questions:
        if q == "q4":
            continue
        qcfg = cfg["questions"][q]
        specs = model_list(cfg, q, models_override)
        for cohort in cfg["cohorts"]:
            for context in qcfg["contexts"]:
                scope = cfg["contexts"][context]["scope"]
                cancers = list(cfg["cancers"]) if scope == "per_cancer" else ["ALL"]
                for arm in qcfg["arms"]:
                    for cancer in cancers:
                        for repeat in range(int(cfg["folds"]["n_repeats"])):
                            for fold in range(n_folds):
                                unit = Unit(context, cohort, arm, cancer, repeat, fold)
                                bucket = plan.setdefault(unit, [])
                                for spec in specs:
                                    _add_spec(bucket, spec)
    return sorted(plan.items(), key=lambda kv: (kv[0].context, kv[0].cohort, kv[0].arm, kv[0].cancer, kv[0].repeat, kv[0].fold))


class RunEnv:
    """Loaded data shared by all units of a process."""

    def __init__(self, cfg: Cfg, paths: Paths, device: str, threads: int, log=print):
        self.cfg, self.paths, self.device, self.threads, self.log = cfg, paths, device, threads, log
        self.store = ArrayStore(paths, cfg, cancers=list(cfg["cancers"]))
        self.folds = Folds(paths.folds)
        missing = set(cfg["cancers"]) - set(self.folds.manifest["cancers"])
        if missing:
            raise RuntimeError(f"folds were built without {sorted(missing)}; rebuild the folds stage")
        self.horizons = cfg_horizons(cfg)
        self.tau = float(cfg["tau_days"])
        self.clinical_cols = list(cfg["clinical_features"])
        self._views: dict[str, object] = {}

    def view(self, cohort: str):
        if cohort not in self._views:
            universe = self.store.universe(cohort)
            if len(universe) == 0:
                raise RuntimeError(f"empty feature universe for cohort {cohort!r}; check features.min_observed")
            self.log(f"feature universe [{cohort}]: {len(universe):,} candidate features")
            self._views[cohort] = self.store.view(universe)
        return self._views[cohort]


def _subsample(ids: np.ndarray, outcomes: pd.DataFrame, n: int, seed: int) -> np.ndarray:
    """Stratified (cancer x event) random subset of ``ids`` of size about ``n`` (smoke mode only)."""
    if len(ids) <= n:
        return ids
    frame = outcomes.loc[ids, ["cancer", "event"]].copy()
    frac = n / len(ids)
    picked = frame.groupby(["cancer", "event"], group_keys=False).sample(frac=frac, random_state=seed)
    return picked.index.to_numpy()


def unit_patients(env: RunEnv, unit: Unit) -> tuple[np.ndarray, np.ndarray]:
    ctx = env.cfg["contexts"][unit.context]
    scope = ctx["scope"]
    train, test = env.folds.split(scope, unit.cohort, unit.cancer, unit.repeat, unit.fold)
    if scope == "per_cancer" and ctx["pool"]:
        # the target cancer's training rows plus every patient of the other cancers; the test set is unchanged,
        # so contexts A-D are paired on identical test patients
        others = env.folds.patients(unit.cohort, exclude_cancer=unit.cancer)
        keep = env.folds.outcomes_idx.loc[others, "cancer"].isin(env.cfg["cancers"]).to_numpy()
        train = np.concatenate([train, others[keep]])
    if env.cfg.get("smoke_mode"):
        seed = int(env.cfg["compute"]["seed"]) + unit.repeat * 31 + unit.fold
        train = _subsample(train, env.folds.outcomes_idx, int(env.cfg["smoke"]["max_train"]), seed)
        test = _subsample(test, env.folds.outcomes_idx, int(env.cfg["smoke"]["max_test"]), seed + 1)
    return np.asarray(train), np.asarray(test)


def atomic_parquet(frame: pd.DataFrame, path) -> None:
    tmp = path.with_name(path.name + ".tmp")        # not matched by the '*.parquet' globs of later stages
    frame.to_parquet(tmp, index=False)
    tmp.replace(path)


def atomic_text(text: str, path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    tmp.replace(path)


def read_json(path) -> dict:
    try:
        return json.loads(path.read_text()) if path.exists() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def censoring_reference(env, unit: Unit) -> np.ndarray:
    """Training rows whose censoring distribution is used by Uno's C, td-AUC and Brier for this unit.

    For per-cancer test sets this is the target cancer's own training rows - identical for contexts A-D, so a contrast between
    contexts compares predictions only, never censoring curves. For pooled (P) units it is the pooled training set.
    """
    ctx = env.cfg["contexts"][unit.context]
    train, _ = env.folds.split(ctx["scope"], unit.cohort, unit.cancer, unit.repeat, unit.fold)
    if env.cfg.get("smoke_mode"):
        seed = int(env.cfg["compute"]["seed"]) + unit.repeat * 31 + unit.fold
        train = _subsample(train, env.folds.outcomes_idx, int(env.cfg["smoke"]["max_train"]), seed)
    return np.asarray(train)


def _read_existing(path) -> pd.DataFrame | None:
    if path.exists():
        try:
            return pd.read_parquet(path)
        except Exception:
            return None
    return None


def run_unit(env: RunEnv, unit: Unit, specs: list[str], force: bool = False) -> dict:
    cfg = env.cfg
    pred_path = env.paths.predictions / f"{unit.key}.parquet"
    run_path = env.paths.runs / f"{unit.key}.json"
    existing = None if force else _read_existing(pred_path)
    done = set(existing["model"].unique()) if existing is not None else set()
    todo = [s for s in specs if s not in done]
    if not todo:
        return {"unit": unit.key, "status": "skipped", "models": 0}

    ctxcfg = cfg["contexts"][unit.context]
    train_ids, test_ids = unit_patients(env, unit)
    out_idx = env.folds.outcomes_idx
    tr = out_idx.loc[train_ids]
    te = out_idx.loc[test_ids]
    t_time, t_event = tr["time"].to_numpy(float), tr["event"].to_numpy(int)
    groups = tr["cancer"].to_numpy(object)

    t0 = time.time()
    pseudo = pseudo_mod.pseudo_values(t_time, t_event, env.horizons, env.tau,
                                      strata=groups if ctxcfg.get("stratified_pseudo") else None)
    design = DesignSpec.for_arm(unit.arm, onehot=bool(ctxcfg["onehot"]), nan_policy=str(ctxcfg["nan"]))
    columns = np.array([], dtype=np.int64)
    selection_info: dict = {}
    if design.use_omics:
        fcfg = cfg["features"]
        sel = select_features(env.view(unit.cohort), train_ids, groups, pseudo["rmst"], selector=ctxcfg["selector"],
                              mode=ctxcfg["mode"], k=int(fcfg["k"]), quota=str(fcfg["modality_quota"]),
                              min_nonzero=int(fcfg["min_nonzero"]), modalities=list(fcfg["modalities"]))
        columns = sel.columns
        selection_info = {"features": [str(f) for f in env.store.feature_ids[columns]], "scores": [round(float(s), 5) for s in sel.scores],
                          "by_modality": sel.by_modality}
    X_tr, names = build_design(env.store, train_ids, columns, design, env.clinical_cols)
    X_te, _ = build_design(env.store, test_ids, columns, design, env.clinical_cols)
    prep_seconds = time.time() - t0

    meta_tr = tr[["patient_id", "cancer", "source"]].reset_index(drop=True)
    meta_te = te[["patient_id", "cancer", "source"]].reset_index(drop=True)
    seed = int(cfg["compute"]["seed"]) + 1000 * unit.repeat + unit.fold
    fctx = FitContext(pseudo=pseudo, meta=meta_tr, horizons=env.horizons, tau=env.tau, seed=seed, threads=env.threads,
                      device=env.device, cfg=dict(cfg["models"]))

    rows, statuses = [], {}
    for spec in todo:
        t1 = time.time()
        try:
            model = build_model(spec)
            model.fit(X_tr, t_time, t_event, fctx)
            fit_s = time.time() - t1
            t2 = time.time()
            risk = np.asarray(model.predict_risk(X_te, meta_te), float)
            surv = model.predict_survival(X_te, env.horizons, meta_te)
            aux = model.predict_aux(X_te, meta_te)
            pred_s = time.time() - t2
            frame = meta_te.copy()
            frame.insert(0, "model", spec)
            frame["time"] = te["time"].to_numpy(float)
            frame["event"] = te["event"].to_numpy(int)
            frame["risk"] = risk
            for name in env.horizons:
                frame[f"surv_{name}"] = surv.get(name) if surv.get(name) is not None else np.nan
            for name, values in aux.items():
                frame[name] = np.asarray(values, float)
            rows.append(frame)
            statuses[spec] = {"status": "ok", "fit_seconds": round(fit_s, 3), "predict_seconds": round(pred_s, 3),
                              "known_bias": getattr(model, "known_bias", None), "model_key": model_key(spec),
                              "degenerate_horizons": getattr(model, "degenerate_horizons", None) or None}
        except Exception as exc:
            statuses[spec] = {"status": "error", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()[-2500:],
                              "seconds": round(time.time() - t1, 3), "model_key": model_key(spec)}
        finally:
            clear_accelerator_cache()

    pred_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        new = pd.concat(rows, ignore_index=True)
        merged = new if existing is None else pd.concat([existing[~existing["model"].isin(new["model"].unique())], new], ignore_index=True)
        atomic_parquet(merged, pred_path)            # a pre-empted process never leaves a half-written file
    info = read_json(run_path) if not force else {}
    info.update({"unit": asdict(unit), "key": unit.key, "n_train": int(len(train_ids)), "n_test": int(len(test_ids)),
                 "events_train": int(t_event.sum()), "events_test": int(te["event"].sum()),
                 "train_cancers": tr["cancer"].value_counts().to_dict(), "n_columns": len(names), "columns_kind": names[:3] + ["..."],
                 "prep_seconds": round(prep_seconds, 2), "selection": selection_info or info.get("selection", {}),
                 "device": env.device, "smoke": bool(cfg.get("smoke_mode"))})
    info.setdefault("models", {}).update(statuses)
    atomic_text(json.dumps(info, indent=1, default=str), run_path)
    n_err = sum(1 for s in statuses.values() if s["status"] != "ok")
    return {"unit": unit.key, "status": "done", "models": len(todo), "errors": n_err}


def run_units(env: RunEnv, plan: list[tuple[Unit, list[str]]], shard: tuple[int, int] = (0, 1), force: bool = False) -> list[dict]:
    i, n = shard
    mine = [item for k, item in enumerate(plan) if k % n == i]
    env.log(f"shard {i}/{n}: {len(mine)} of {len(plan)} units")
    results, t0 = [], time.time()
    for k, (unit, specs) in enumerate(mine, start=1):
        res = run_unit(env, unit, specs, force=force)
        results.append(res)
        elapsed = time.time() - t0
        eta = elapsed / k * (len(mine) - k)
        env.log(f"[{k}/{len(mine)}] {unit.key}: {res['status']} ({res.get('models', 0)} models, {res.get('errors', 0)} errors) "
                f"elapsed {elapsed / 60:.1f} min, eta {eta / 60:.1f} min")
    return results
