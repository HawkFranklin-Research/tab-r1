"""Build and read the compact analysis store from the c-5 ``train_ready`` matrices.

Why a store
-----------
The c-5 matrices (``X.npz`` + ``missing_mask.npz``, one pair per cancer) are large sparse files with ~280k columns. Two facts
about them shape this module (both verified on the delivered files; see paper/analysis/reusability/exploratory/NOTES_source_blocks.md):

* ``missing_mask`` is 1 where a value is MISSING (the stored X value in such cells is one imputed constant).
* Most non-clinical feature ids occur TWICE per cancer, as source-specific blocks: one copy holds values for TCGA rows only and
  one for CPTAC rows only, each missing for the other source (and each z-scored within its own source). We coalesce the two
  copies per patient, so a CPTAC patient carries real values instead of the structural zeros that arise when only one copy
  is kept. If both copies are observed in a cell the values are averaged (this never happened in the delivered data and is
  counted in the report).

Output (``<output_root>/store``)
--------------------------------
``X_<cancer>.npy`` float32 [n_patients, n_features] and ``M_<cancer>.npy`` uint8 (1 = missing after coalescing), columns in the
same order for every cancer (the sorted common feature ids); ``features.parquet`` (id, modality, gene, observed fraction per
cancer for rows of the ``all`` and ``tcga`` cohorts); ``samples.parquet``; ``clinical.parquet``; ``store_report.json``.
Continuous features keep the c-5 scaling (cohort-centred and z-scored within each source block); binary/GISTIC features keep their native
scale; missing cells are stored as 0.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

from . import clinical as clin
from .config import Cfg, Paths

SURVIVAL_COLUMNS = ["OS_days", "OS_event", "DSS_days", "DSS_event", "PFS_days", "PFS_event"]
BLOCK = 8000


def modality_of(feature_id: str) -> str:
    return feature_id.split("::", 1)[0]


def gene_of(feature_id: str) -> str | None:
    tail = feature_id.split("::", 1)[-1]
    return tail.split(":", 1)[1] if tail.startswith("GENE:") else None


def _unique_columns(feature_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Unique ids in first-appearance order with the positions of their first and (optional) second copy."""
    codes, uniq = pd.factorize(feature_ids)
    order = np.argsort(codes, kind="stable")
    sorted_codes = codes[order]
    starts = np.flatnonzero(np.r_[True, sorted_codes[1:] != sorted_codes[:-1]])
    counts = np.diff(np.r_[starts, len(sorted_codes)])
    if counts.max() > 2:
        raise ValueError(f"feature id present {counts.max()} times; the coalescing rule supports at most two copies")
    first = np.empty(len(uniq), dtype=np.int64)
    second = np.full(len(uniq), -1, dtype=np.int64)
    first[sorted_codes[starts]] = order[starts]
    pair = starts[counts == 2]
    second[sorted_codes[pair]] = order[pair + 1]
    return np.asarray(uniq, dtype=object), first, second


def coalesce_block(A, MA, B, MB):
    """Coalesce two aligned copies; ``MA/MB`` are 1 where missing. Returns (values, missing, n_both_observed)."""
    obs_a = MA == 0
    obs_b = MB == 0
    count = obs_a.astype(np.int8) + obs_b.astype(np.int8)
    total = np.where(obs_a, A, 0.0) + np.where(obs_b, B, 0.0)
    values = (total / np.maximum(count, 1)).astype(np.float32)
    return values, (count == 0).astype(np.uint8), int((count == 2).sum())


def build_store(cfg: Cfg, paths: Paths, force: bool = False, log=print) -> dict:
    paths.ensure()
    report_path = paths.store / "store_report.json"
    if report_path.exists() and not force:
        log(f"store already built ({report_path}); use --force to rebuild")
        return json.loads(report_path.read_text())
    t0 = time.time()
    all_cancers = ["BRCA", "ESCA", "HNSCC", "LSCC", "LUAD"]
    cancers = [c for c in all_cancers if c in cfg["cancers"]] if cfg.get("smoke_mode") else all_cancers

    # 1. column bookkeeping ---------------------------------------------------------------------------------
    book = {}
    for cancer in cancers:
        findex = pd.read_csv(paths.train_ready / cancer / "core" / "feature_index.csv")
        keep = ~findex["feature_id"].str.startswith("clinical::")
        positions = findex.loc[keep, "feature_index"].to_numpy(np.int64)
        uniq, first, second = _unique_columns(findex.loc[keep, "feature_id"].to_numpy(object))
        book[cancer] = dict(uniq=uniq, col1=positions[first], col2=np.where(second >= 0, positions[np.maximum(second, 0)], -1))
        log(f"{cancer}: {len(uniq):,} unique non-clinical ids ({int((second >= 0).sum()):,} with two copies)")
    common = sorted(set.intersection(*[set(book[c]["uniq"].tolist()) for c in cancers]))
    n_u = len(common)
    log(f"common feature ids across {len(cancers)} cancers: {n_u:,}")
    common_arr = np.asarray(common, dtype=object)

    # 2. samples ---------------------------------------------------------------------------------------------
    frames = []
    for cancer in cancers:
        s = pd.read_csv(paths.train_ready / cancer / "core" / "sample_index.csv")
        out = pd.DataFrame({"patient_id": s["patient_id"], "sample_id": s["sample_id"], "cancer": cancer,
                            "source": s["cohort_x"], "row": np.arange(len(s))})
        for col in SURVIVAL_COLUMNS:
            out[col.lower()] = pd.to_numeric(s[col], errors="coerce") if col in s.columns else np.nan
        frames.append(out)
    samples = pd.concat(frames, ignore_index=True)
    if samples["patient_id"].duplicated().any():
        raise ValueError("duplicate patient ids across cancers")

    # 3. coalesce + write matrices ----------------------------------------------------------------------------
    obs = {}
    stats = {"pairs": 0, "both_observed_cells": 0}
    for cancer in cancers:
        t1 = time.time()
        rows_meta = samples[samples["cancer"] == cancer]
        is_tcga = (rows_meta["source"].to_numpy() == "TCGA")
        n = len(rows_meta)
        X = sp.load_npz(paths.train_ready / cancer / "core" / "X.npz").tocsc()
        M = sp.load_npz(paths.train_ready / cancer / "core" / "missing_mask.npz").tocsc()
        pos = pd.Index(book[cancer]["uniq"]).get_indexer(common_arr)
        c1 = book[cancer]["col1"][pos]
        c2 = book[cancer]["col2"][pos]
        Xo = np.lib.format.open_memmap(paths.store / f"X_{cancer}.npy", mode="w+", dtype=np.float32, shape=(n, n_u))
        Mo = np.lib.format.open_memmap(paths.store / f"M_{cancer}.npy", mode="w+", dtype=np.uint8, shape=(n, n_u))
        obs_all = np.empty(n_u)
        obs_tcga = np.empty(n_u)
        for start in range(0, n_u, BLOCK):
            sl = slice(start, min(start + BLOCK, n_u))
            a = X[:, c1[sl]].toarray()
            ma = M[:, c1[sl]].toarray().astype(np.uint8)
            has2 = c2[sl] >= 0
            b = np.zeros_like(a)
            mb = np.ones_like(ma)
            if has2.any():
                idx2 = c2[sl][has2]
                b[:, has2] = X[:, idx2].toarray()
                mb[:, has2] = M[:, idx2].toarray().astype(np.uint8)
            values, missing, both = coalesce_block(a, ma, b, mb)
            stats["pairs"] += int(has2.sum())
            stats["both_observed_cells"] += both
            Xo[:, sl] = values
            Mo[:, sl] = missing
            obs_all[sl] = 1.0 - missing.mean(axis=0)
            obs_tcga[sl] = 1.0 - missing[is_tcga].mean(axis=0) if is_tcga.any() else np.nan
        Xo.flush()
        Mo.flush()
        obs[(cancer, "all")] = obs_all
        obs[(cancer, "tcga")] = obs_tcga
        del X, M, Xo, Mo
        log(f"{cancer}: wrote X/M [{n} x {n_u:,}] in {time.time() - t1:.0f}s")

    features = pd.DataFrame({"feature_id": common_arr})
    features["modality"] = features["feature_id"].map(modality_of)
    features["gene"] = features["feature_id"].map(gene_of)
    for (cancer, variant), values in obs.items():
        features[f"obs_{cancer}_{variant}"] = values.astype(np.float32)
    features.to_parquet(paths.store / "features.parquet", index=False)
    samples.to_parquet(paths.store / "samples.parquet", index=False)

    # 4. clinical -----------------------------------------------------------------------------------------------
    master = pd.read_parquet(paths.clinical_master)
    clinical = clin.harmonise(master)
    dup = clinical.index.duplicated()
    if dup.any():
        log(f"clinical master: {int(dup.sum())} duplicated patient ids; keeping the first row of each")
    clinical = clinical[~dup]
    clinical = clinical.loc[clinical.index.intersection(samples["patient_id"])]
    clinical.to_parquet(paths.store / "clinical.parquet")
    cov = clin.coverage(clinical, samples)

    # 5. report -------------------------------------------------------------------------------------------------
    universes = {}
    for variant in ("tcga", "all"):
        mask = universe_mask(features, cfg, variant, cancers)
        universes[variant] = {"n_features": int(mask.sum()),
                              "by_modality": features.loc[mask, "modality"].value_counts().to_dict()}
    report = {
        "built_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "seconds": round(time.time() - t0, 1),
        "cancers": cancers, "n_samples": int(len(samples)), "n_common_features": int(n_u), "coalescing": stats,
        "universes": universes, "clinical_coverage": cov.reset_index().to_dict(orient="records"),
        "n_patients_by_cancer_source": samples.groupby(["cancer", "source"]).size().rename("n").reset_index().to_dict(orient="records"),
        "inputs": {c: {f: (paths.train_ready / c / "core" / f).stat().st_size for f in ("X.npz", "missing_mask.npz")} for c in cancers},
    }
    report_path.write_text(json.dumps(report, indent=2, default=str))
    log(f"store built in {time.time() - t0:.0f}s: universes {json.dumps({k: v['n_features'] for k, v in universes.items()})}; "
        f"both-observed cells during coalescing: {stats['both_observed_cells']}")
    return report


def universe_mask(features: pd.DataFrame, cfg: Cfg, variant: str, cancers: list[str]) -> np.ndarray:
    """Features observed in at least ``min_observed`` of the rows of ``variant`` in every analysed cancer, in allowed modalities."""
    thr = float(cfg["features"]["min_observed"][variant])
    keep = features["modality"].isin(cfg["features"]["modalities"]).to_numpy()
    for cancer in cancers:
        keep &= (features[f"obs_{cancer}_{variant}"].to_numpy() >= thr)
    return keep


class ArrayStore:
    """Read access to the store (matrices in RAM or memory-mapped)."""

    def __init__(self, paths: Paths, cfg: Cfg, cancers: list[str] | None = None, preload: bool | None = None):
        self.cfg = cfg
        self.paths = paths
        self.features = pd.read_parquet(paths.store / "features.parquet")
        samples = pd.read_parquet(paths.store / "samples.parquet")
        self.cancers = cancers or [c for c in ["BRCA", "ESCA", "HNSCC", "LSCC", "LUAD"] if c in set(samples["cancer"])]
        self.samples = samples[samples["cancer"].isin(self.cancers)].set_index("patient_id", drop=False)
        self.clinical = pd.read_parquet(paths.store / "clinical.parquet")
        preload = cfg["features"].get("preload", True) if preload is None else preload
        mode = None if preload else "r"
        self.X = {c: np.load(paths.store / f"X_{c}.npy", mmap_mode=mode) for c in self.cancers}
        self.M = {c: np.load(paths.store / f"M_{c}.npy", mmap_mode=mode) for c in self.cancers}
        self.feature_ids = self.features["feature_id"].to_numpy(object)
        self.modality = self.features["modality"].to_numpy(object)

    # ---- universe ------------------------------------------------------------------------------------------
    def universe(self, variant: str) -> np.ndarray:
        """Column indices (into the store) of the candidate features for a cohort variant."""
        return np.flatnonzero(universe_mask(self.features, self.cfg, variant, self.cancers))

    # ---- row access -------------------------------------------------------------------------------------------
    def _locate(self, patient_ids) -> tuple[np.ndarray, np.ndarray]:
        frame = self.samples.loc[list(patient_ids), ["cancer", "row"]]
        return frame["cancer"].to_numpy(object), frame["row"].to_numpy(np.int64)

    def omics(self, patient_ids, columns: np.ndarray, nan_missing: bool = False) -> np.ndarray:
        """Dense float32 [len(patient_ids), len(columns)]; missing cells are 0, or NaN when ``nan_missing``."""
        cancer, row = self._locate(patient_ids)
        out = np.empty((len(row), len(columns)), dtype=np.float32)
        for c in np.unique(cancer):
            sel = np.flatnonzero(cancer == c)
            ix = np.ix_(row[sel], columns)
            block = self.X[c][ix]
            if nan_missing:
                block = block.astype(np.float32, copy=True)
                block[self.M[c][ix] == 1] = np.nan
            out[sel] = block
        return out

    def view(self, columns: np.ndarray) -> "UniverseView":
        """Contiguous per-cancer copy of the given columns for fast row-wise streaming (used by feature selection)."""
        return UniverseView(self, np.asarray(columns))


class UniverseView:
    """Row-streaming access to a fixed set of candidate columns; rows are gathered contiguously."""

    def __init__(self, store: ArrayStore, columns: np.ndarray):
        self.store = store
        self.columns = columns
        self.modality = store.modality[columns]
        self.X = {c: np.ascontiguousarray(store.X[c][:, columns]) for c in store.cancers}

    def iter_chunks(self, patient_ids, chunk: int = 256):
        """Yield dense float32 chunks [<=chunk, n_columns] (missing cells are 0) in the order of ``patient_ids``."""
        ids = list(patient_ids)
        for start in range(0, len(ids), chunk):
            cancer, row = self.store._locate(ids[start:start + chunk])
            out = np.empty((len(row), len(self.columns)), dtype=np.float32)
            for c in np.unique(cancer):
                sel = np.flatnonzero(cancer == c)
                out[sel] = self.X[c][row[sel]]
            yield out
