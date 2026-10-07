"""Tabular foundation models (TabPFN v2 / v2.5 / v2.6 / v3, TabFM) and the survival adapters that make ANY regressor or
classifier a survival model.

Why adapters
------------
Only some models have a survival interface. To compare every model on equal footing the same two reductions are applied to all:

``pseudo``  regress jackknife pseudo-observations of RMST / S(h) (``tte.pseudo``); predicted values give a risk score and
            survival probabilities. Works for any regressor (TabPFN versions, TabFM, random forest, CatBoost, ridge).
``ipcw``    train horizon classifiers on training rows resampled with inverse-probability-of-censoring weights. Works for any classifier.
``native``  a re-implementation of ``tabpfn_extensions.survival.SurvivalTabPFN`` (event classifier x event-time distribution), which
            only TabPFN has. The extension cannot be imported with the installed scikit-learn, so the same construct is
            implemented here (Apache-2.0 original, Prior Labs). Its event classifier labels CENSORED patients as non-events, a
            known bias reported alongside every result (``known_bias``).

Model construction reuses the evaluator package of the paper pipeline for TabFM (``ev_tabpfn``) and calls ``tabpfn`` directly
for the four TabPFN versions (so the seed can be set).
"""

from __future__ import annotations

import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .. import pseudo as pseudo_mod
from ..config import REPO_ROOT
from .base import FitContext, SurvivalModel

TABPFN_VERSIONS = {"tabpfn_v2": "V2", "tabpfn_v2_5": "V2_5", "tabpfn_v2_6": "V2_6", "tabpfn_v3": "V3"}
HORIZON_TOKENS = ("h3", "h5")


# ---- estimator factories ------------------------------------------------------------------------------------------------

class _Estimator:
    """Uniform wrapper: ``fit(X, y)``, ``predict(X)`` / ``predict_proba(X)``; imputes unless the model handles NaN itself."""

    def __init__(self, model, supports_nan: bool):
        self.model = model
        self.supports_nan = supports_nan
        self.imputer = None if supports_nan else SimpleImputer(strategy="median", keep_empty_features=True)

    def _x(self, X, fit=False):
        if self.imputer is None:
            return X
        return self.imputer.fit_transform(X) if fit else self.imputer.transform(X)

    def fit(self, X, y):
        self.model.fit(self._x(X, True), y)
        return self

    def predict(self, X):
        return np.asarray(self.model.predict(self._x(X))).ravel()

    def predict_proba(self, X):
        if hasattr(self.model, "_cached_proba_input_id"):     # TabFMAdapter caches by id(X); ids can be reused, so never trust it
            self.model._cached_proba_input_id = None
        return np.asarray(self.model.predict_proba(self._x(X)))


def _ensure_evaluator(cfg_paths=None):
    try:
        import ev_tabpfn  # noqa: F401
    except ImportError:
        sys.path.insert(0, str(REPO_ROOT / "package" / "src"))


def make_tabpfn(kind: str, name: str, seed: int, device: str):
    from tabpfn import TabPFNClassifier, TabPFNRegressor
    from tabpfn.constants import ModelVersion

    cls = TabPFNRegressor if kind == "regressor" else TabPFNClassifier
    version = getattr(ModelVersion, TABPFN_VERSIONS[name])
    return cls.create_default_for_version(version, device=device, random_state=seed)


def make_tabfm(kind: str, seed: int):
    _ensure_evaluator()
    from ev_tabpfn.models.tabfm_backend import TabFMAdapter

    return TabFMAdapter(task_type="regression" if kind == "regressor" else "binary", backend="pytorch", ensemble=False, random_state=seed)


def make_regressor(name: str, ctx: FitContext) -> _Estimator:
    seed, threads, hp = ctx.seed, ctx.threads, ctx.cfg
    if name in TABPFN_VERSIONS:
        return _Estimator(make_tabpfn("regressor", name, seed, ctx.device), supports_nan=True)
    if name == "tabfm":
        return _Estimator(make_tabfm("regressor", seed), supports_nan=False)
    if name == "ridge":
        return _Estimator(make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 3, 12))), supports_nan=False)
    if name == "random_forest":
        p = hp["regressor_random_forest"]
        return _Estimator(RandomForestRegressor(n_estimators=int(p["n_estimators"]), min_samples_leaf=int(p["min_samples_leaf"]),
                                                max_features=p["max_features"], n_jobs=threads, random_state=seed), supports_nan=True)
    if name == "catboost":
        from catboost import CatBoostRegressor

        p = hp["regressor_catboost"]
        return _Estimator(CatBoostRegressor(iterations=int(p["iterations"]), depth=int(p["depth"]), learning_rate=float(p["learning_rate"]),
                                            thread_count=threads, random_seed=seed, verbose=0, allow_writing_files=False), supports_nan=True)
    raise ValueError(f"unknown regressor {name!r}")


def make_classifier(name: str, ctx: FitContext) -> _Estimator:
    seed, threads, hp = ctx.seed, ctx.threads, ctx.cfg
    if name in TABPFN_VERSIONS:
        return _Estimator(make_tabpfn("classifier", name, seed, ctx.device), supports_nan=True)
    if name == "tabfm":
        return _Estimator(make_tabfm("classifier", seed), supports_nan=False)
    if name == "logistic":
        return _Estimator(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)), supports_nan=False)
    if name == "random_forest":
        p = hp["classifier_random_forest"]
        return _Estimator(RandomForestClassifier(n_estimators=int(p["n_estimators"]), min_samples_leaf=int(p["min_samples_leaf"]),
                                                 max_features=p["max_features"], n_jobs=threads, random_state=seed), supports_nan=True)
    if name == "catboost":
        from catboost import CatBoostClassifier

        p = hp["classifier_catboost"]
        return _Estimator(CatBoostClassifier(iterations=int(p["iterations"]), depth=int(p["depth"]), learning_rate=float(p["learning_rate"]),
                                             thread_count=threads, random_seed=seed, verbose=0, allow_writing_files=False), supports_nan=True)
    raise ValueError(f"unknown classifier {name!r}")


# ---- adapters ---------------------------------------------------------------------------------------------------------------

class PseudoObsModel(SurvivalModel):
    """Regress pseudo-observations (targets: 'rmst', 'h3', 'h5'); risk = -prediction of RMST (or of S(h) if RMST is not a target)."""

    family = "pseudo"

    def __init__(self, regressor: str, targets: list[str]):
        self.regressor, self.targets = regressor, list(targets)
        self.spec = f"pseudo:{regressor}:{'+'.join(self.targets)}"

    def fit(self, X, time, event, ctx: FitContext):
        self.models = {}
        for target in self.targets:
            if target not in ctx.pseudo:
                raise KeyError(f"pseudo-value target {target!r} not available (have {sorted(ctx.pseudo)})")
            self.models[target] = make_regressor(self.regressor, ctx).fit(X, ctx.pseudo[target])
        return self

    def _predict(self, X) -> dict[str, np.ndarray]:
        return {t: m.predict(X) for t, m in self.models.items()}

    def predict_risk(self, X, meta=None):
        pred = self._predict(X)
        key = "rmst" if "rmst" in pred else self.targets[-1]
        return -pred[key]

    def predict_survival(self, X, horizons, meta=None):
        pred = self._predict(X)
        return {name: (np.clip(pred[name], 0.0, 1.0) if name in pred else None) for name in horizons}

    def predict_aux(self, X, meta=None):
        return {f"pred_{t}": v for t, v in self._predict(X).items()}


class NativeTabPFNSurvival(SurvivalModel):
    """P(event | x) x F(t | event, x) from a TabPFN classifier and the full predictive distribution of a TabPFN regressor
    trained on the event times of the patients who had an event (re-implementation of SurvivalTabPFN; see module docstring)."""

    family = "native"
    known_bias = "event classifier treats censored patients as non-events"

    def __init__(self, version: str):
        if version not in TABPFN_VERSIONS:
            raise ValueError(f"native survival needs a TabPFN version, got {version!r}")
        self.version = version
        self.spec = f"native:{version}"

    def fit(self, X, time, event, ctx: FitContext):
        hp = ctx.cfg["native_survival"]
        ev = np.asarray(event).astype(bool)
        if ev.sum() < 5 or ev.all():
            raise ValueError(f"need 5+ events and some censored patients (events={int(ev.sum())}, n={len(ev)})")
        self.clf = make_classifier(self.version, ctx).fit(X, ev.astype(int))
        self.reg = make_regressor(self.version, ctx).fit(X[ev], np.asarray(time, float)[ev])
        lo, hi = hp["horizon_quantiles"]
        taus = np.unique(np.quantile(np.asarray(time, float)[ev], np.linspace(lo, hi, int(hp["n_horizons"]))))
        w = float(hp["risk_gamma"]) ** np.arange(len(taus))
        self.taus, self.weights = taus, w / w.sum()
        return self

    def _cif(self, X, taus: np.ndarray) -> np.ndarray:
        import torch

        p_event = self.clf.predict_proba(X)[:, 1]
        full = self.reg.model.predict(self.reg._x(X), output_type="full")
        logits = torch.as_tensor(full["logits"])
        criterion = full["criterion"]
        cols = []
        with torch.no_grad():
            for tau in taus:
                ys = torch.as_tensor([float(tau)], device=logits.device, dtype=logits.dtype)
                cols.append(np.asarray(criterion.cdf(logits, ys).squeeze(-1).cpu().numpy()).reshape(-1))
        return p_event[:, None] * np.column_stack(cols)

    def predict_risk(self, X, meta=None):
        return self._cif(X, self.taus) @ self.weights

    def predict_survival(self, X, horizons, meta=None):
        cif = self._cif(X, np.array(list(horizons.values()), float))
        return {name: np.clip(1.0 - cif[:, i], 0.0, 1.0) for i, name in enumerate(horizons)}


class _ConstantProbability:
    def __init__(self, p: float):
        self.p = p

    def predict_proba(self, X):
        return np.column_stack([np.full(len(X), 1 - self.p), np.full(len(X), self.p)])


class IPCWClassifierModel(SurvivalModel):
    """One classifier per horizon on IPCW-resampled rows (patients censored before the horizon get weight 0)."""

    family = "ipcw"

    def __init__(self, classifier: str):
        self.classifier = classifier
        self.spec = f"ipcw:{classifier}"

    def fit(self, X, time, event, ctx: FitContext):
        floor = float(ctx.cfg["ipcw"]["weight_floor"])
        self.models = {}
        self.degenerate_horizons: list[str] = []
        for j, (name, h) in enumerate(ctx.horizons.items()):
            w = pseudo_mod.ipcw_weights(time, event, h, floor)
            y = pseudo_mod.horizon_label(time, event, h)
            idx = np.flatnonzero(w > 0)
            rng = np.random.default_rng(ctx.seed * 7919 + j)
            draw = rng.choice(idx, size=len(idx), replace=True, p=w[idx] / w[idx].sum())
            if len(np.unique(y[draw])) < 2:
                # every eligible training patient has the same status at this horizon (small cancers at 5 years):
                # predict that status for everyone and record it, instead of failing the whole model
                self.models[name] = _ConstantProbability(float(y[draw].mean()))
                self.degenerate_horizons.append(name)
                continue
            self.models[name] = make_classifier(self.classifier, ctx).fit(X[draw], y[draw])
        return self

    def _p(self, X) -> dict[str, np.ndarray]:
        return {name: m.predict_proba(X)[:, 1] for name, m in self.models.items()}

    def predict_risk(self, X, meta=None):
        return np.mean(list(self._p(X).values()), axis=0)

    def predict_survival(self, X, horizons, meta=None):
        p = self._p(X)
        return {name: (1.0 - p[name] if name in p else None) for name in horizons}
