"""Classical censored-survival models (scikit-survival) and reference models.

All of them impute missing values (median, fitted on the training rows) and, where it matters, standardise. They use the
censoring information properly (partial likelihood / survival trees), unlike the horizon classifiers of the fixed-horizon paper.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import GradientBoostingSurvivalAnalysis, RandomSurvivalForest
from sksurv.linear_model import CoxnetSurvivalAnalysis, CoxPHSurvivalAnalysis
from sksurv.metrics import concordance_index_censored
from sksurv.util import Surv

from .. import pseudo as pseudo_mod
from .base import FitContext, SurvivalModel, step_fn_at, surv_at


def _imputer(scale: bool):
    steps = [SimpleImputer(strategy="median", keep_empty_features=True)]
    if scale:
        steps.append(StandardScaler())
    return make_pipeline(*steps)


def _y(time, event):
    return Surv.from_arrays(np.asarray(event).astype(bool), np.asarray(time, float))


class CoxNet(SurvivalModel):
    family = "classical"
    spec = "coxnet"

    def fit(self, X, time, event, ctx: FitContext):
        hp = ctx.cfg["coxnet"]
        self.prep = _imputer(True)
        Xp = self.prep.fit_transform(X)
        y = _y(time, event)
        kwargs = dict(l1_ratio=float(hp["l1_ratio"]), max_iter=int(hp["max_iter"]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            alphas = CoxnetSurvivalAnalysis(n_alphas=int(hp["n_alphas"]), alpha_min_ratio=float(hp["alpha_min_ratio"]), **kwargs).fit(Xp, y).alphas_
            best = self._choose_alpha(Xp, y, event, alphas, int(hp["inner_folds"]), ctx.seed, kwargs)
            self.est = CoxnetSurvivalAnalysis(alphas=[best], fit_baseline_model=True, **kwargs).fit(Xp, y)
        self.alpha_ = float(best)
        return self

    @staticmethod
    def _choose_alpha(Xp, y, event, alphas, folds, seed, kwargs) -> float:
        event = np.asarray(event).astype(int)
        if event.sum() < 2 * folds or (1 - event).sum() < folds:
            return float(alphas[len(alphas) // 2])
        scores = np.full(len(alphas), np.nan)
        accum = [[] for _ in alphas]
        for train, valid in StratifiedKFold(folds, shuffle=True, random_state=seed).split(Xp, event):
            try:
                est = CoxnetSurvivalAnalysis(alphas=list(alphas), **kwargs).fit(Xp[train], y[train])
            except Exception:
                continue
            for i, a in enumerate(alphas):
                try:
                    risk = est.predict(Xp[valid], alpha=a)
                    accum[i].append(concordance_index_censored(y[valid]["event"], y[valid]["time"], risk)[0])
                except Exception:
                    continue
        for i, vals in enumerate(accum):
            if vals:
                scores[i] = float(np.mean(vals))
        if np.isnan(scores).all():
            return float(alphas[len(alphas) // 2])
        best_i = int(np.nanargmax(scores))        # first maximum = strongest penalty among ties (alphas are decreasing)
        return float(alphas[best_i])

    def predict_risk(self, X, meta=None):
        return np.asarray(self.est.predict(self.prep.transform(X)), float)

    def predict_survival(self, X, horizons, meta=None):
        fns = self.est.predict_survival_function(self.prep.transform(X))
        return {name: step_fn_at(fns, h) for name, h in horizons.items()}


class CoxPH(SurvivalModel):
    family = "classical"
    spec = "coxph"

    def fit(self, X, time, event, ctx: FitContext):
        self.prep = _imputer(True)
        Xp = self.prep.fit_transform(X)
        y = _y(time, event)
        alpha = float(ctx.cfg["coxph"]["alpha"])
        last: Exception | None = None
        for mult in (1.0, 10.0, 100.0, 1000.0):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.est = CoxPHSurvivalAnalysis(alpha=alpha * mult, ties="efron").fit(Xp, y)
                self.alpha_ = alpha * mult
                return self
            except Exception as exc:        # ill-conditioned fits get a stronger ridge
                last = exc
        raise RuntimeError(f"CoxPH failed at every penalty: {last}")

    def predict_risk(self, X, meta=None):
        return np.asarray(self.est.predict(self.prep.transform(X)), float)

    def predict_survival(self, X, horizons, meta=None):
        fns = self.est.predict_survival_function(self.prep.transform(X))
        return {name: step_fn_at(fns, h) for name, h in horizons.items()}


class _TreeSurvival(SurvivalModel):
    family = "classical"

    def _estimator(self, ctx: FitContext):
        raise NotImplementedError

    def fit(self, X, time, event, ctx: FitContext):
        self.prep = _imputer(False)
        Xp = self.prep.fit_transform(X)
        self.est = self._estimator(ctx)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.est.fit(Xp, _y(time, event))
        return self

    def predict_risk(self, X, meta=None):
        return np.asarray(self.est.predict(self.prep.transform(X)), float)

    def predict_survival(self, X, horizons, meta=None):
        Xp = self.prep.transform(X)
        surv = np.asarray(self.est.predict_survival_function(Xp, return_array=True))
        times = np.asarray(self.est.unique_times_)
        return {name: surv_at(times, surv, h) for name, h in horizons.items()}


class RSF(_TreeSurvival):
    spec = "rsf"

    def _estimator(self, ctx):
        hp = ctx.cfg["rsf"]
        return RandomSurvivalForest(n_estimators=int(hp["n_estimators"]), min_samples_leaf=int(hp["min_samples_leaf"]),
                                    max_features=hp["max_features"], n_jobs=ctx.threads, random_state=ctx.seed)


class GBSA(_TreeSurvival):
    spec = "gbsa"

    def _estimator(self, ctx):
        hp = ctx.cfg["gbsa"]
        return GradientBoostingSurvivalAnalysis(n_estimators=int(hp["n_estimators"]), learning_rate=float(hp["learning_rate"]),
                                                max_depth=int(hp["max_depth"]), subsample=float(hp["subsample"]), random_state=ctx.seed)


class KaplanMeier(SurvivalModel):
    """No-information reference: constant risk (C = 0.5) and the training Kaplan-Meier curve for Brier-score reference."""

    family = "reference"
    spec = "km"

    def fit(self, X, time, event, ctx: FitContext):
        self.time = np.asarray(time, float)
        self.event = np.asarray(event).astype(bool)
        return self

    def predict_risk(self, X, meta=None):
        return np.zeros(len(X))

    def predict_survival(self, X, horizons, meta=None):
        return {name: np.full(len(X), float(pseudo_mod.km_survival(self.time, self.event, h)[0])) for name, h in horizons.items()}


class NullGroup(SurvivalModel):
    """Risk from group membership alone (group-level mean pseudo-RMST): quantifies what the cancer or the source explains."""

    family = "reference"

    def __init__(self, column: str):
        self.column = column
        self.spec = f"null_{column}"

    def fit(self, X, time, event, ctx: FitContext):
        groups = ctx.meta[self.column].to_numpy(object)
        self.global_rmst = float(np.mean(ctx.pseudo["rmst"]))
        self.rmst = {g: float(np.mean(ctx.pseudo["rmst"][groups == g])) for g in np.unique(groups)}
        self.surv = {name: {g: float(np.mean(ctx.pseudo[name][groups == g])) for g in np.unique(groups)}
                     for name in ctx.horizons}
        self.global_surv = {name: float(np.mean(ctx.pseudo[name])) for name in ctx.horizons}
        return self

    def _groups(self, X, meta):
        if meta is None:
            raise ValueError("null_group models need the 'meta' frame at prediction time")
        return meta[self.column].to_numpy(object)

    def predict_risk(self, X, meta=None):
        return -np.array([self.rmst.get(g, self.global_rmst) for g in self._groups(X, meta)])

    def predict_survival(self, X, horizons, meta=None):
        groups = self._groups(X, meta)
        return {name: np.array([self.surv[name].get(g, self.global_surv[name]) for g in groups]) for name in horizons}
