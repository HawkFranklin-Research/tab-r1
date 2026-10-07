"""Kaplan-Meier utilities, jackknife pseudo-observations and IPCW weights.

Pseudo-observations (Andersen & Klein): for a statistic theta of the survival distribution (here S(h) at a horizon, or the
restricted mean survival time up to tau), the pseudo-value of subject i is  n * theta_hat - (n - 1) * theta_hat_(-i), where
theta_hat_(-i) is the Kaplan-Meier estimate without subject i. Pseudo-values are ordinary numbers with
E[pseudo_i | X_i] = theta(X_i) under independent censoring, so any regressor can be trained on them and every training patient
(censored or not) contributes. Pseudo-values must be computed from the TRAINING rows only.

The leave-one-out Kaplan-Meier curves are obtained for all subjects at once from log-increments (an n x m array, m = number of
distinct event times up to the largest horizon), validated against brute force in tests/test_pseudo.py.
"""

from __future__ import annotations

import numpy as np


def _components(time: np.ndarray, event: np.ndarray, t_max: float):
    """Distinct event times <= t_max, deaths d_j and at-risk counts n_j at each (n_j counts time >= t_j)."""
    ev_times = np.unique(time[event & (time <= t_max)])
    n_risk = len(time) - np.searchsorted(np.sort(time), ev_times, side="left")
    ev_sorted = np.sort(time[event])
    deaths = np.searchsorted(ev_sorted, ev_times, side="right") - np.searchsorted(ev_sorted, ev_times, side="left")
    return ev_times, deaths.astype(float), n_risk.astype(float)


def km_survival(time, event, query) -> np.ndarray:
    """Kaplan-Meier S(q) (right-continuous) at the query times."""
    time = np.asarray(time, float)
    event = np.asarray(event).astype(bool)
    query = np.atleast_1d(np.asarray(query, float))
    ut, d, n = _components(time, event, np.inf)
    if len(ut) == 0:
        return np.ones(len(query))
    with np.errstate(divide="ignore"):
        cum = np.cumsum(np.log1p(-d / n))         # -inf once everyone at risk has died: S = 0, as intended
    k = np.searchsorted(ut, query, side="right")
    return np.where(k == 0, 1.0, np.exp(cum[np.maximum(k - 1, 0)]))


def km_rmst(time, event, tau: float) -> float:
    """Area under the Kaplan-Meier curve on [0, tau]."""
    time = np.asarray(time, float)
    event = np.asarray(event).astype(bool)
    ut, d, n = _components(time, event, tau)
    if len(ut) == 0:
        return float(tau)
    with np.errstate(divide="ignore"):
        surv = np.r_[1.0, np.exp(np.cumsum(np.log1p(-d / n)))]
    widths = np.diff(np.r_[0.0, ut, tau])
    return float(surv @ widths)


def _pseudo_single(time: np.ndarray, event: np.ndarray, horizons: dict[str, float], tau: float) -> dict[str, np.ndarray]:
    n = len(time)
    t_max = max(list(horizons.values()) + [tau])
    ut, d, nr = _components(time, event, t_max)
    m = len(ut)
    out: dict[str, np.ndarray] = {}
    if n < 3 or m == 0:
        for name in horizons:
            out[name] = np.full(n, float(km_survival(time, event, horizons[name])[0]))
        out["rmst"] = np.full(n, km_rmst(time, event, tau))
        return out
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.log1p(-d / nr)                               # full-data factor, t_j
        den = nr - 1.0
        safe = np.where(den > 0, den, 1.0)
        b = np.where(den > 0, np.log1p(-d / safe), 0.0)     # subject i at risk and not dying at t_j: n_j - 1
        c = np.where(den > 0, np.log1p(-(d - 1.0) / safe), 0.0)   # subject i dies at t_j: d_j - 1 and n_j - 1
    ti = time[:, None]
    less = ti > ut[None, :]                                  # t_j < time_i
    equal = ti == ut[None, :]
    mid = np.where(event[:, None], c[None, :], b[None, :])
    log_inc = np.where(less, b[None, :], np.where(equal, mid, a[None, :]))
    s_loo = np.exp(np.cumsum(log_inc, axis=1))               # n x m
    s_full = np.exp(np.cumsum(a))
    for name, h in horizons.items():
        k = int(np.searchsorted(ut, h, side="right"))
        full = 1.0 if k == 0 else float(s_full[k - 1])
        loo = np.ones(n) if k == 0 else s_loo[:, k - 1]
        out[name] = n * full - (n - 1) * loo
    k = int(np.searchsorted(ut, tau, side="right"))
    widths = np.diff(np.r_[0.0, ut[:k], tau])
    s_full_ext = np.r_[1.0, s_full[:k]]
    s_loo_ext = np.hstack([np.ones((n, 1)), s_loo[:, :k]])
    out["rmst"] = n * float(s_full_ext @ widths) - (n - 1) * (s_loo_ext @ widths)
    return out


def pseudo_values(time, event, horizons: dict[str, float], tau: float, strata=None) -> dict[str, np.ndarray]:
    """Pseudo-values for ``S(h)`` (keys = horizon names) and ``rmst`` (key 'rmst'), optionally computed within strata."""
    time = np.asarray(time, float)
    event = np.asarray(event).astype(bool)
    if strata is None:
        return _pseudo_single(time, event, horizons, tau)
    strata = np.asarray(strata)
    out = {name: np.empty(len(time)) for name in list(horizons) + ["rmst"]}
    for level in np.unique(strata):
        sel = strata == level
        part = _pseudo_single(time[sel], event[sel], horizons, tau)
        for name, values in part.items():
            out[name][sel] = values
    return out


def ipcw_weights(time, event, horizon: float, floor: float = 0.05) -> np.ndarray:
    """Inverse-probability-of-censoring weights for the binary status 'died by horizon'.

    Eligible: death at or before the horizon, or follow-up beyond it. Patients censored before the horizon get weight 0.
    G is the Kaplan-Meier estimate of the censoring distribution, evaluated at min(time, horizon).
    """
    time = np.asarray(time, float)
    event = np.asarray(event).astype(bool)
    # G(t-) at the death time (a censoring on the same day does not count against the death), G(h) for patients alive at h
    query = np.where(event & (time <= horizon), np.nextafter(time, -np.inf), np.minimum(time, horizon))
    g = km_survival(time, ~event, query)
    eligible = (event & (time <= horizon)) | (time > horizon)
    return np.where(eligible, 1.0 / np.maximum(g, floor), 0.0)


def horizon_label(time, event, horizon: float) -> np.ndarray:
    """1 if death at or before the horizon, else 0 (meaningful only for eligible patients)."""
    return (np.asarray(event).astype(bool) & (np.asarray(time, float) <= horizon)).astype(int)
