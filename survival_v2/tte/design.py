"""Model input matrices for one training/test set: omics block, clinical block, cancer indicator."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .store import ArrayStore


@dataclass(frozen=True)
class DesignSpec:
    use_omics: bool = True
    use_clinical: bool = False
    onehot: bool = False
    nan_policy: str = "imputed"        # imputed: missing omics cells are 0; nan: they are NaN (models that cannot take NaN impute)

    @staticmethod
    def for_arm(arm: str, onehot: bool, nan_policy: str) -> "DesignSpec":
        if arm == "omics":
            return DesignSpec(True, False, onehot, nan_policy)
        if arm == "clinical":
            return DesignSpec(False, True, onehot, nan_policy)
        if arm == "omics_clinical":
            return DesignSpec(True, True, onehot, nan_policy)
        raise ValueError(f"unknown arm {arm!r}")


def build_design(store: ArrayStore, patient_ids, columns: np.ndarray, spec: DesignSpec, clinical_cols: list[str]):
    """Return (X float32 [n, p], column names). Clinical NaN is always kept; omics NaN only for ``nan_policy='nan'``."""
    blocks, names = [], []
    ids = list(patient_ids)
    if spec.use_omics:
        blocks.append(store.omics(ids, columns, nan_missing=(spec.nan_policy == "nan")))
        names += [str(f) for f in store.feature_ids[columns]]
    if spec.use_clinical:
        blocks.append(store.clinical.reindex(ids)[clinical_cols].to_numpy(np.float32))
        names += [f"clinical::{c}" for c in clinical_cols]
    if spec.onehot:
        cancer = store.samples.loc[ids, "cancer"].to_numpy(object)
        blocks.append(np.stack([(cancer == c).astype(np.float32) for c in store.cancers], axis=1))
        names += [f"cancer::{c}" for c in store.cancers]
    if not blocks:
        raise ValueError("design has no columns")
    return np.hstack(blocks).astype(np.float32, copy=False), names
