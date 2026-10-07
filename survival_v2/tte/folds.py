"""Outcome table and frozen patient-grouped folds.

Every patient is one row (the c-5 sample index has one sample per patient), so a fold assignment is a table
``(scope, cohort, cancer, repeat, patient_id, fold)`` rather than copies of the data. The table, its parameters and a SHA-256 of its
canonical text are written once (``folds/``); the runner refuses to use folds whose hash does not match the manifest.

Scopes
------
``per_cancer``  each cancer split on its own, stratified by event (used by contexts A-D)
``pooled``      all cancers split together, stratified by cancer x event (context P)
"""

from __future__ import annotations

import hashlib
import json
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from .config import Cfg


def outcome_table(samples: pd.DataFrame, cfg: Cfg) -> pd.DataFrame:
    """Patients with a usable survival time/event for the configured endpoint (optionally administratively censored)."""
    endpoint = str(cfg["endpoint"]).lower()
    t_col, e_col = f"{endpoint}_days", f"{endpoint}_event"
    out = samples[["patient_id", "cancer", "source"]].copy()
    out["time"] = pd.to_numeric(samples[t_col], errors="coerce")
    out["event"] = pd.to_numeric(samples[e_col], errors="coerce")
    out = out[out["time"].notna() & out["event"].isin([0, 1]) & (out["time"] > 0)].copy()
    out["event"] = out["event"].astype(int)
    max_fu = cfg.get("max_followup_days")
    if max_fu:
        late = out["time"] > float(max_fu)
        out.loc[late, "time"] = float(max_fu)
        out.loc[late, "event"] = 0
    out["in_tcga"] = out["source"] == "TCGA"
    out["in_all"] = True
    return out.reset_index(drop=True)


def cohort_members(outcomes: pd.DataFrame, variant: str) -> pd.DataFrame:
    return outcomes[outcomes[f"in_{variant}"]]


def _seed(base: int, *key) -> int:
    return (base * 1_000_003 + zlib.crc32("|".join(map(str, key)).encode())) % (2**31 - 1)


def _kfold(labels: np.ndarray, n_splits: int, seed: int, what: str) -> np.ndarray:
    counts = pd.Series(labels).value_counts()
    if (counts < n_splits).any():
        raise ValueError(f"{what}: class(es) {counts[counts < n_splits].index.tolist()} have fewer than {n_splits} patients")
    fold = np.empty(len(labels), dtype=np.int16)
    for k, (_, test) in enumerate(StratifiedKFold(n_splits, shuffle=True, random_state=seed).split(np.zeros(len(labels)), labels)):
        fold[test] = k
    return fold


def build_assignments(outcomes: pd.DataFrame, cfg: Cfg, cohorts: list[str] | None = None) -> pd.DataFrame:
    cohorts = cohorts or list(cfg["cohorts"])
    f = cfg["folds"]
    rows = []
    for variant in cohorts:
        members = cohort_members(outcomes, variant)
        for repeat in range(int(f["n_repeats"])):
            for cancer in cfg["cancers"]:
                sub = members[members["cancer"] == cancer].sort_values("patient_id")
                if sub.empty:
                    continue
                fold = _kfold(sub["event"].to_numpy(), int(f["n_splits"]), _seed(int(f["seed"]), "per_cancer", variant, cancer, repeat),
                              f"per_cancer/{variant}/{cancer}")
                rows.append(pd.DataFrame({"scope": "per_cancer", "cohort": variant, "cancer": cancer, "repeat": repeat,
                                          "patient_id": sub["patient_id"].to_numpy(), "fold": fold}))
            pooled = members[members["cancer"].isin(cfg["cancers"])].sort_values("patient_id")
            labels = (pooled["cancer"] + "|" + pooled["event"].astype(str)).to_numpy()
            fold = _kfold(labels, int(f["n_splits"]), _seed(int(f["seed"]), "pooled", variant, "ALL", repeat), f"pooled/{variant}")
            rows.append(pd.DataFrame({"scope": "pooled", "cohort": variant, "cancer": "ALL", "repeat": repeat,
                                      "patient_id": pooled["patient_id"].to_numpy(), "fold": fold}))
    out = pd.concat(rows, ignore_index=True)
    return out.sort_values(["scope", "cohort", "cancer", "repeat", "patient_id"]).reset_index(drop=True)


def canonical_hash(assignments: pd.DataFrame) -> str:
    text = assignments.sort_values(["scope", "cohort", "cancer", "repeat", "patient_id"]).to_csv(index=False)
    return hashlib.sha256(text.encode()).hexdigest()


def verify(assignments: pd.DataFrame, outcomes: pd.DataFrame, cfg: Cfg) -> None:
    """Every patient appears exactly once per (scope, cohort, cancer, repeat); folds are balanced; events are stratified."""
    n_splits = int(cfg["folds"]["n_splits"])
    merged = assignments.merge(outcomes[["patient_id", "event", "cancer"]].rename(columns={"cancer": "own_cancer"}), on="patient_id")
    for key, group in merged.groupby(["scope", "cohort", "cancer", "repeat"]):
        if group["patient_id"].duplicated().any():
            raise AssertionError(f"patient appears twice in {key}")
        sizes = group["fold"].value_counts()
        n_strata = 2 * group["own_cancer"].nunique()          # pooled folds are stratified on cancer x event
        tol = 1 if key[0] == "per_cancer" else n_strata
        if len(sizes) != n_splits or sizes.max() - sizes.min() > tol:
            raise AssertionError(f"unbalanced folds in {key}: {sizes.to_dict()}")
        # events must be balanced within every cancer (each stratum is off by at most one patient per fold)
        for cancer, part in group.groupby("own_cancer"):
            events = part.groupby("fold")["event"].sum().reindex(range(n_splits), fill_value=0)
            if events.max() - events.min() > 1:
                raise AssertionError(f"events not stratified in {key} for {cancer}: {events.to_dict()}")
        if key[0] == "per_cancer" and (group["own_cancer"] != key[2]).any():
            raise AssertionError(f"patient of another cancer in {key}")


def write_folds(assignments: pd.DataFrame, outcomes: pd.DataFrame, cfg: Cfg, folds_dir: Path) -> dict:
    folds_dir.mkdir(parents=True, exist_ok=True)
    verify(assignments, outcomes, cfg)
    assignments.to_parquet(folds_dir / "assignments.parquet", index=False)
    outcomes.to_parquet(folds_dir / "outcomes.parquet", index=False)
    manifest = {
        "sha256": canonical_hash(assignments), "n_rows": int(len(assignments)), "folds": dict(cfg["folds"]),
        "endpoint": cfg["endpoint"], "max_followup_days": cfg.get("max_followup_days"), "cohorts": sorted(assignments["cohort"].unique()),
        "cancers": list(cfg["cancers"]),
        "patients": outcomes.groupby("cancer").agg(n=("patient_id", "size"), events=("event", "sum")).reset_index().to_dict(orient="records"),
    }
    (folds_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=int))
    return manifest


class Folds:
    """Read access to frozen folds with integrity checking."""

    def __init__(self, folds_dir: Path):
        self.assignments = pd.read_parquet(folds_dir / "assignments.parquet")
        self.outcomes = pd.read_parquet(folds_dir / "outcomes.parquet")
        manifest = json.loads((folds_dir / "manifest.json").read_text())
        if canonical_hash(self.assignments) != manifest["sha256"]:
            raise RuntimeError("fold assignments do not match their manifest hash; refusing to run on altered folds")
        self.manifest = manifest
        self._groups = {k: g for k, g in self.assignments.groupby(["scope", "cohort", "cancer", "repeat"])}
        self.outcomes_idx = self.outcomes.set_index("patient_id", drop=False)

    def split(self, scope: str, cohort: str, cancer: str, repeat: int, fold: int) -> tuple[np.ndarray, np.ndarray]:
        group = self._groups[(scope, cohort, cancer, repeat)]
        test = group.loc[group["fold"] == fold, "patient_id"].to_numpy()
        train = group.loc[group["fold"] != fold, "patient_id"].to_numpy()
        return train, test

    def patients(self, cohort: str, cancer: str | None = None, exclude_cancer: str | None = None) -> np.ndarray:
        members = cohort_members(self.outcomes, cohort)
        if cancer is not None:
            members = members[members["cancer"] == cancer]
        if exclude_cancer is not None:
            members = members[members["cancer"] != exclude_cancer]
        return members["patient_id"].to_numpy()
