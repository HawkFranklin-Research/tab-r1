"""In-fold feature selection (training rows only).

Selectors
---------
``pseudo_corr``  |Pearson correlation| between each candidate feature and the pseudo-value target. This is a fast univariate
                 screen that handles censoring through the pseudo-values. ``mode='pooled'`` correlates over all training rows;
                 ``mode='within'`` correlates inside each group (cancer), then combines the groups by Fisher's z with
                 weights n_g - 3 (a fixed-effects Stouffer score), so features that merely separate cancers score zero.
``variance``     variance of the training rows (the unsupervised rule of the fixed-horizon paper; use with care, see README).

Modality quotas (``quota='equal'``) keep the selection from collapsing onto one assay: k / n_modalities per modality,
unfilled slots go to the best remaining features. All statistics are accumulated in float64 over row chunks, so the
n x ~95k matrix is never materialised.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .store import UniverseView

MIN_GROUP_N = 20


@dataclass
class Selection:
    columns: np.ndarray           # store column indices, best first
    scores: np.ndarray
    by_modality: dict


def _accumulate(view: UniverseView, patient_ids: np.ndarray, target: np.ndarray):
    n = len(patient_ids)
    width = len(view.columns)
    sx = np.zeros(width)
    sxx = np.zeros(width)
    sxy = np.zeros(width)
    nnz = np.zeros(width)
    pos = 0
    for chunk in view.iter_chunks(patient_ids):
        y = target[pos:pos + len(chunk)].astype(np.float32)
        sx += chunk.sum(axis=0, dtype=np.float64)
        sxx += np.einsum("ij,ij->j", chunk, chunk, dtype=np.float64)
        sxy += (chunk.T @ y).astype(np.float64)
        nnz += (chunk != 0).sum(axis=0)
        pos += len(chunk)
    return {"n": n, "sx": sx, "sxx": sxx, "sxy": sxy, "nnz": nnz, "sy": float(target.sum()), "syy": float((target ** 2).sum())}


def _pearson(s) -> np.ndarray:
    n = s["n"]
    cov = s["sxy"] - s["sx"] * s["sy"] / n
    vx = s["sxx"] - s["sx"] ** 2 / n
    vy = s["syy"] - s["sy"] ** 2 / n
    with np.errstate(divide="ignore", invalid="ignore"):
        r = cov / np.sqrt(np.maximum(vx, 0) * max(vy, 0))
    r[~np.isfinite(r)] = 0.0
    return np.clip(r, -0.999999, 0.999999)


def select_features(view: UniverseView, patient_ids, groups, target, *, selector: str, mode: str,
                    k: int, quota: str, min_nonzero: int, modalities: list[str]) -> Selection:
    patient_ids = np.asarray(patient_ids)
    groups = np.asarray(groups)
    target = np.asarray(target, float)
    levels = [g for g in np.unique(groups) if (groups == g).sum() >= (MIN_GROUP_N if mode == "within" else 1)]
    stats = {g: _accumulate(view, patient_ids[groups == g], target[groups == g]) for g in levels}
    total = {key: sum(s[key] for s in stats.values()) for key in ("n", "sx", "sxx", "sxy", "nnz", "sy", "syy")}
    if selector == "variance":
        score = total["sxx"] / total["n"] - (total["sx"] / total["n"]) ** 2
    elif selector == "pseudo_corr":
        if mode == "pooled":
            score = np.abs(_pearson(total))
        elif mode == "within":
            num = np.zeros(len(view.columns))
            den = 0.0
            for g, s in stats.items():
                w = s["n"] - 3.0
                num += w * np.arctanh(_pearson(s))
                den += w
            score = np.abs(num / np.sqrt(max(den, 1e-9)))
        else:
            raise ValueError(f"unknown selection mode {mode!r}")
    else:
        raise ValueError(f"unknown selector {selector!r}")
    score = np.nan_to_num(score, nan=0.0, posinf=0.0, neginf=0.0)
    eligible = total["nnz"] >= min_nonzero
    if selector == "variance":
        eligible &= score > 0
    score = np.where(eligible, score, -np.inf)

    mods = view.modality
    universe = view.columns
    present = [m for m in modalities if (mods == m).any() and eligible[mods == m].any()]
    chosen: list[int] = []
    if quota == "equal" and present:
        base, extra = divmod(k, len(present))
        for i, m in enumerate(present):
            take = base + (1 if i < extra else 0)
            idx = np.flatnonzero((mods == m) & eligible)
            chosen.extend(idx[np.argsort(-score[idx], kind="stable")[:take]].tolist())
    if len(chosen) < k:
        taken = np.zeros(len(universe), bool)
        taken[chosen] = True
        rest = np.flatnonzero(eligible & ~taken)
        chosen.extend(rest[np.argsort(-score[rest], kind="stable")[:k - len(chosen)]].tolist())
    chosen_arr = np.asarray(chosen, dtype=np.int64)
    chosen_arr = chosen_arr[np.argsort(-score[chosen_arr], kind="stable")]
    by_mod = {m: int((mods[chosen_arr] == m).sum()) for m in sorted(set(mods[chosen_arr].tolist()))}
    return Selection(columns=universe[chosen_arr], scores=score[chosen_arr], by_modality=by_mod)
