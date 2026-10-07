"""Common interface for every survival model in the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class FitContext:
    """Everything a model may need besides (X, time, event); built once per training set and shared by all models."""

    pseudo: dict[str, np.ndarray]                 # 'rmst' and one entry per horizon name ('h3', 'h5'), aligned with the training rows
    meta: pd.DataFrame                            # training rows: patient_id, cancer, source
    horizons: dict[str, float]
    tau: float
    seed: int = 0
    threads: int = 1
    device: str = "cpu"
    cfg: dict = field(default_factory=dict)       # the 'models' block of the configuration


class SurvivalModel:
    """fit(X, time, event, ctx); predict_risk(X, meta) higher = earlier event; optional survival probabilities at the horizons."""

    spec: str = ""
    family: str = ""
    supports_nan: bool = False
    known_bias: str | None = None

    def fit(self, X: np.ndarray, time: np.ndarray, event: np.ndarray, ctx: FitContext) -> "SurvivalModel":
        raise NotImplementedError

    def predict_risk(self, X: np.ndarray, meta: pd.DataFrame | None = None) -> np.ndarray:
        raise NotImplementedError

    def predict_survival(self, X: np.ndarray, horizons: dict[str, float], meta: pd.DataFrame | None = None) -> dict[str, np.ndarray | None]:
        return {name: None for name in horizons}

    def predict_aux(self, X: np.ndarray, meta: pd.DataFrame | None = None) -> dict[str, np.ndarray]:
        """Extra raw predictions worth saving (e.g. the regressors' pseudo-value predictions)."""
        return {}


def surv_at(times: np.ndarray, surv: np.ndarray, horizon: float) -> np.ndarray:
    """Evaluate survival curves given as an array [n, len(times)] on an increasing grid at ``horizon`` (step function, S=1 before the first time)."""
    k = int(np.searchsorted(times, horizon, side="right"))
    return np.ones(surv.shape[0]) if k == 0 else surv[:, k - 1]


def step_fn_at(fns, horizon: float) -> np.ndarray:
    out = np.empty(len(fns))
    for i, fn in enumerate(fns):
        lo, hi = fn.domain
        out[i] = 1.0 if horizon < lo else float(fn(min(horizon, hi)))
    return out
