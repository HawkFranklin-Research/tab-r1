"""Metrics stage: recompute every metric from the saved per-patient predictions.

Training outcomes (needed for Uno's C, time-dependent AUC and the IPCW Brier score) are reconstructed deterministically from
the frozen folds for internal units, and read from ``external/train_outcomes_<direction>.parquet`` for Question 4.
Nothing is refitted; deleting ``metrics/`` and re-running this stage reproduces it exactly.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pandas as pd

from .config import Cfg, Paths, horizons as cfg_horizons
from .folds import Folds
from .metrics import compute_run_metrics
from .models import model_group, model_key
from .runner import Unit, censoring_reference, read_json, unit_patients


def _parse_key(rel: str) -> Unit:
    context, cohort, arm, cancer, rf = rel.split("/")
    repeat, fold = rf.replace("r", "").split("_f")
    return Unit(context, cohort, arm, cancer, int(repeat), int(fold))


def _run_info(paths: Paths, key: str) -> dict:
    return read_json(paths.runs / f"{key}.json")


def internal_metrics(cfg: Cfg, paths: Paths, log=print) -> pd.DataFrame:
    folds = Folds(paths.folds)
    env = SimpleNamespace(cfg=cfg, folds=folds)
    horizons, tau = cfg_horizons(cfg), float(cfg["tau_days"])
    rows = []
    files = sorted(paths.predictions.rglob("*.parquet"))
    for n, path in enumerate(files, start=1):
        rel = str(path.relative_to(paths.predictions)).removesuffix(".parquet")
        unit = _parse_key(rel)
        train_ids, _ = unit_patients(env, unit)
        info = _run_info(paths, rel)
        if info.get("n_train") is not None and int(info["n_train"]) != len(train_ids):
            raise RuntimeError(f"{rel}: training set rebuilt from the current config has {len(train_ids)} patients but the fit used "
                               f"{info['n_train']}; the config changed between fit and metrics")
        tr = folds.outcomes_idx.loc[censoring_reference(env, unit)]
        pred = pd.read_parquet(path)
        group_col = "cancer" if cfg["contexts"][unit.context]["scope"] == "pooled" else None
        for spec, part in pred.groupby("model", sort=False):
            m = compute_run_metrics(part, tr["time"].to_numpy(float), tr["event"].to_numpy(int), horizons, tau, group_col=group_col)
            m["n_censoring_reference"] = int(len(tr))
            status = info.get("models", {}).get(spec, {})
            rows.append({"context": unit.context, "cohort": unit.cohort, "arm": unit.arm, "cancer": unit.cancer,
                         "repeat": unit.repeat, "fold": unit.fold, "model": spec, "model_key": model_key(spec),
                         "model_group": model_group(spec), "n_train": len(train_ids), "events_train": int(tr["event"].sum()),
                         "fit_seconds": status.get("fit_seconds"), "predict_seconds": status.get("predict_seconds"), **m})
        if n % 200 == 0:
            log(f"metrics: {n}/{len(files)} prediction files")
    out = pd.DataFrame(rows)
    paths.metrics.mkdir(parents=True, exist_ok=True)
    out.to_parquet(paths.metrics / "run_metrics.parquet", index=False)
    errors = collect_errors(paths)
    errors.to_csv(paths.metrics / "model_errors.csv", index=False)
    log(f"metrics: {len(out)} (unit, model) rows from {len(files)} files; {len(errors)} recorded model errors")
    return out


def collect_errors(paths: Paths) -> pd.DataFrame:
    rows = []
    for path in sorted(paths.runs.rglob("*.json")):
        info = read_json(path)
        for spec, s in info.get("models", {}).items():
            if s.get("status") != "ok":
                rows.append({"unit": info.get("key", str(path)), "model": spec, "error": s.get("error", "")})
    return pd.DataFrame(rows, columns=["unit", "model", "error"])


def _bootstrap_c(time, event, risk, n_boot: int, seed: int) -> tuple[float, float]:
    from .metrics import harrell

    rng = np.random.default_rng(seed)
    n = len(time)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        c = harrell(time[i], event[i], risk[i])[0]
        if np.isfinite(c):
            vals.append(c)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))) if vals else (np.nan, np.nan)


def external_metrics(cfg: Cfg, paths: Paths, log=print) -> pd.DataFrame:
    root = paths.external / "predictions"
    if not root.exists():
        return pd.DataFrame()
    horizons, tau = cfg_horizons(cfg), float(cfg["tau_days"])
    n_boot = int(cfg["external"]["bootstrap"]) if not cfg.get("smoke_mode") else 50
    rows = []
    for path in sorted(root.rglob("*.parquet")):
        direction, arm, seed = str(path.relative_to(root)).removesuffix(".parquet").split("/")
        pred = pd.read_parquet(path)
        for spec, part in pred.groupby("model", sort=False):
            # external validation: censoring is estimated in the test cohort itself (its follow-up pattern differs from training)
            m = compute_run_metrics(part, part["time"].to_numpy(float), part["event"].to_numpy(int), horizons, tau, group_col=None)
            lo, hi = _bootstrap_c(part["time"].to_numpy(float), part["event"].to_numpy(int), part["risk"].to_numpy(float), n_boot,
                                  int(cfg["compute"]["seed"]))
            rows.append({"direction": direction, "arm": arm, "seed": int(seed.removeprefix("seed")), "model": spec,
                         "model_key": model_key(spec), "model_group": model_group(spec), "c_harrell_lo": lo, "c_harrell_hi": hi, **m})
    out = pd.DataFrame(rows)
    out.to_parquet(paths.metrics / "external_metrics.parquet", index=False)
    log(f"external metrics: {len(out)} rows")
    return out
