"""Harmonised clinical covariates.

The c-5 pipeline stores clinical variables from the two sources under different column names
(CPTAC: Age/Sex/Stage/Path_Stage_pT/Path_Stage_pN; TCGA: AGE/SEX/AJCC_PATHOLOGIC_TUMOR_STAGE/PATH_T_STAGE/PATH_N_STAGE).
This module reads ``clinical/patient_master.parquet`` as produced by that pipeline (trusted as delivered) and maps both
families onto one numeric scheme:

    age        years
    sex_male   1 male, 0 female
    stage      1-4   (AJCC stage group, sub-stages collapsed: IA/IB -> 1, IIA -> 2, ...)
    t_stage    1-4   (pathological T, sub-categories collapsed: T1c -> 1)
    n_stage    0-3   (pathological N, sub-categories collapsed: N1a -> 1; N0(i+) -> 0)

Unknown/unevaluable categories (STAGE X, TX, NX, ...) become NaN; models impute them from the training rows only.
Grade is not harmonised: it exists for CPTAC patients only and would encode the source.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

COLUMNS = ["age", "sex_male", "stage", "t_stage", "n_stage"]
_SOURCES = {
    "age": ["Age", "AGE", "years_to_birth"],
    "sex": ["Sex", "SEX", "gender"],
    "stage": ["Stage", "AJCC_PATHOLOGIC_TUMOR_STAGE", "pathologic_stage"],
    "t": ["Path_Stage_pT", "PATH_T_STAGE", "pathology_T_stage"],
    "n": ["Path_Stage_pN", "PATH_N_STAGE", "pathology_N_stage"],
}
_ROMAN = {"iv": 4, "iii": 3, "ii": 2, "i": 1}


def _coalesce(frame: pd.DataFrame, names: list[str]) -> pd.Series:
    out = pd.Series(pd.NA, index=frame.index, dtype="object")
    for name in names:
        if name in frame.columns:
            col = frame[name].astype("object")
            out = out.where(out.notna(), col)
    return out


def _is_missing(value) -> bool:
    return value is None or value is pd.NA or (isinstance(value, float) and np.isnan(value))


def _compact(value) -> str:
    return re.sub(r"[\s_]+", "", str(value).strip().lower())


def parse_stage(value) -> float:
    """'Stage II', 'STAGE IIB', 'stageiii' -> 2, 2, 3; 'STAGE X', NaN -> NaN."""
    if _is_missing(value):
        return np.nan
    match = re.fullmatch(r"stage(iv|iii|ii|i)([abc]\d?)?", _compact(value))
    return float(_ROMAN[match.group(1)]) if match else np.nan


def parse_t(value) -> float:
    """'pT2', 'T1C', 't3' -> 2, 1, 3; 'TX', 'Tis', 'T0' -> NaN."""
    if _is_missing(value):
        return np.nan
    match = re.match(r"p?t([1-4])", _compact(value))
    return float(match.group(1)) if match else np.nan


def parse_n(value) -> float:
    """'pN1', 'N1A', 'N0 (I+)', 'n2' -> 1, 1, 0, 2; 'NX' -> NaN."""
    if _is_missing(value):
        return np.nan
    match = re.match(r"p?n([0-3])", _compact(value))
    return float(match.group(1)) if match else np.nan


def parse_sex(value) -> float:
    if _is_missing(value):
        return np.nan
    text = str(value).strip().lower()
    if text.startswith("m"):
        return 1.0
    if text.startswith("f"):
        return 0.0
    return np.nan


def harmonise(master: pd.DataFrame) -> pd.DataFrame:
    """Return a table indexed by ``patient_id`` with the columns in :data:`COLUMNS`."""
    frame = master.copy()
    if "patient_id" not in frame.columns:
        raise KeyError("patient_master must contain 'patient_id'")
    out = pd.DataFrame(index=frame["patient_id"].to_numpy())
    out["age"] = pd.to_numeric(_coalesce(frame, _SOURCES["age"]), errors="coerce").to_numpy(float)
    out["sex_male"] = _coalesce(frame, _SOURCES["sex"]).map(parse_sex).to_numpy(float)
    out["stage"] = _coalesce(frame, _SOURCES["stage"]).map(parse_stage).to_numpy(float)
    out["t_stage"] = _coalesce(frame, _SOURCES["t"]).map(parse_t).to_numpy(float)
    out["n_stage"] = _coalesce(frame, _SOURCES["n"]).map(parse_n).to_numpy(float)
    out.index.name = "patient_id"
    # a handful of malformed ages would otherwise leak absurd values into scaling
    out.loc[(out["age"] < 15) | (out["age"] > 110), "age"] = np.nan
    return out


def coverage(clinical: pd.DataFrame, samples: pd.DataFrame) -> pd.DataFrame:
    """Share of non-missing values per cancer and source (reported in the store report)."""
    merged = samples.set_index("patient_id")[["cancer", "source"]].join(clinical, how="left")
    return merged.groupby(["cancer", "source"])[COLUMNS].agg(lambda s: float(s.notna().mean())).round(3)
