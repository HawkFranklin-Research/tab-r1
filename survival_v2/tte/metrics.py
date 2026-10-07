"""Evaluation metrics for censored survival predictions.

Primary
-------
``c_harrell``   Harrell's C over all comparable pairs of the test set.
``c_strat``     stratified C: pairs are formed only between patients of the same group (cancer), concordant/discordant counts
                summed over groups. This is the 'rank patients who share a diagnosis' measure; for a pooled test set it removes the
                between-cancer part of the ranking.
``c_uno``       Uno's IPCW C-index truncated at ``tau`` (less sensitive to the censoring distribution of the test set).
Secondary
---------
``auc_h*``      time-dependent ROC AUC (cumulative/dynamic) at the horizons, ``brier_h*`` IPCW Brier score of the predicted survival
                probability at the horizons (when a model provides one), ``auc_elig_h*`` ordinary ROC AUC among the patients whose
                status at the horizon is known - the quantity of the fixed-horizon analysis, for linking to it.

Everything is computed from the saved prediction rows plus the training outcomes (needed for the censoring distribution), so the
metrics can be recomputed at any time without refitting.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sksurv.exceptions import NoComparablePairException
from sksurv.metrics import brier_score, concordance_index_censored, concordance_index_ipcw, cumulative_dynamic_auc
from sksurv.util import Surv


def _surv(time, event):
    return Surv.from_arrays(np.asarray(event).astype(bool), np.asarray(time, float))


def harrell(time, event, risk) -> tuple[float, int, int, int]:
    """Return (C, concordant, discordant, tied risk) or (nan, 0, 0, 0)."""
    event = np.asarray(event).astype(bool)
    if event.sum() == 0 or len(np.unique(risk)) < 1:
        return np.nan, 0, 0, 0
    try:
        c, conc, disc, tied_risk, _ = concordance_index_censored(event, np.asarray(time, float), np.asarray(risk, float))
        return float(c), int(conc), int(disc), int(tied_risk)
    except NoComparablePairException:
        return np.nan, 0, 0, 0


def stratified_c(time, event, risk, groups) -> tuple[float, dict]:
    time, event, risk, groups = (np.asarray(a) for a in (time, event, risk, groups))
    conc = disc = tied = 0
    per_group = {}
    for g in np.unique(groups):
        sel = groups == g
        c, a, b, t = harrell(time[sel], event[sel], risk[sel])
        per_group[str(g)] = c
        conc, disc, tied = conc + a, disc + b, tied + t
    denom = conc + disc + tied
    return ((conc + 0.5 * tied) / denom if denom else np.nan), per_group


def uno_c(train_time, train_event, time, event, risk, tau: float) -> float:
    train_time = np.asarray(train_time, float)
    try:
        tau_eff = min(float(tau), float(np.max(train_time)) * 0.999)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return float(concordance_index_ipcw(_surv(train_time, train_event), _surv(time, event), np.asarray(risk, float), tau=tau_eff)[0])
    except Exception:
        return np.nan


def td_auc(train_time, train_event, time, event, marker, horizon: float) -> float:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            auc, _ = cumulative_dynamic_auc(_surv(train_time, train_event), _surv(time, event), np.asarray(marker, float), [float(horizon)])
        return float(auc[0])
    except Exception:
        return np.nan


def brier_at(train_time, train_event, time, event, surv_prob, horizon: float) -> float:
    try:
        est = np.clip(np.asarray(surv_prob, float), 0.0, 1.0).reshape(-1, 1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, score = brier_score(_surv(train_time, train_event), _surv(time, event), est, [float(horizon)])
        return float(score[0])
    except Exception:
        return np.nan


def eligible_auc(time, event, score, horizon: float) -> float:
    time, event = np.asarray(time, float), np.asarray(event).astype(bool)
    eligible = (event & (time <= horizon)) | (time > horizon)
    label = (event & (time <= horizon))[eligible].astype(int)
    if len(np.unique(label)) < 2:
        return np.nan
    return float(roc_auc_score(label, np.asarray(score, float)[eligible]))


def compute_run_metrics(pred: pd.DataFrame, train_time, train_event, horizons: dict[str, float], tau: float,
                        group_col: str | None = "cancer") -> dict:
    """Metrics for one (unit, model): ``pred`` has columns time, event, risk, and optionally surv_<h>, cancer."""
    time, event, risk = pred["time"].to_numpy(float), pred["event"].to_numpy(int), pred["risk"].to_numpy(float)
    out = {"n_test": int(len(pred)), "n_events_test": int(event.sum())}
    if not np.isfinite(risk).all():
        out["error"] = "non-finite risk"
        return out
    c, _, _, _ = harrell(time, event, risk)
    out["c_harrell"] = c
    out["c_uno"] = uno_c(train_time, train_event, time, event, risk, tau)
    if group_col and group_col in pred and pred[group_col].nunique() > 1:
        out["c_strat"], per_group = stratified_c(time, event, risk, pred[group_col].to_numpy())
        for g, v in per_group.items():
            out[f"c_{g}"] = v
    for name, h in horizons.items():
        surv_col = f"surv_{name}"
        have_surv = surv_col in pred and pred[surv_col].notna().all()
        marker = (1.0 - pred[surv_col].to_numpy(float)) if have_surv else risk
        out[f"auc_{name}"] = td_auc(train_time, train_event, time, event, marker, h)
        out[f"auc_elig_{name}"] = eligible_auc(time, event, marker, h)
        out[f"brier_{name}"] = brier_at(train_time, train_event, time, event, pred[surv_col].to_numpy(float), h) if have_surv else np.nan
    return out
