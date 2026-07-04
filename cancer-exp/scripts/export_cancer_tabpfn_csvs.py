from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse


DEFAULT_INPUT_ROOT = Path("/home/prime/Documents/g3/c-5/gpt/processed/train_ready")
DEFAULT_OUTPUT_DIR = Path("/home/prime/Documents/g3/cancer-exp/datasets")


@dataclass
class ExportRecord:
    name: str
    path: str
    task: str
    target: str
    source_cancers: list[str]
    view: str
    samples: int
    features: int
    class_counts: dict[str, int]
    note: str


def _read_train_ready(input_root: Path, cancer: str, view: str) -> tuple[sparse.csr_matrix, pd.DataFrame, pd.DataFrame]:
    base = input_root / cancer / view
    X = sparse.load_npz(base / "X.npz").tocsr().astype(np.float32)
    sample_index = pd.read_csv(base / "sample_index.csv")
    feature_index = pd.read_csv(base / "feature_index.csv")
    if X.shape[0] != len(sample_index):
        raise ValueError(f"{cancer}/{view}: sample count mismatch: X={X.shape[0]} sample_index={len(sample_index)}")
    if X.shape[1] != len(feature_index):
        raise ValueError(f"{cancer}/{view}: feature count mismatch: X={X.shape[1]} feature_index={len(feature_index)}")
    return X, sample_index, feature_index


def _nonclinical_feature_positions(feature_index: pd.DataFrame) -> np.ndarray:
    feature_ids = feature_index["feature_id"].astype(str)
    keep = ~feature_ids.str.startswith("clinical::")
    return np.flatnonzero(keep.to_numpy())


def _top_variance_positions(X: sparse.csr_matrix, candidates: np.ndarray, max_features: int) -> np.ndarray:
    if len(candidates) == 0:
        raise ValueError("No candidate features available after filtering.")
    if len(candidates) <= max_features:
        return candidates
    Xc = X[:, candidates]
    mean = np.asarray(Xc.mean(axis=0)).ravel()
    mean_sq = np.asarray(Xc.power(2).mean(axis=0)).ravel()
    variance = np.maximum(mean_sq - mean**2, 0.0)
    selected_local = np.argsort(variance)[-max_features:][::-1]
    return candidates[selected_local]


def _dense_frame(X: sparse.csr_matrix, feature_index: pd.DataFrame, positions: np.ndarray) -> pd.DataFrame:
    matrix = X[:, positions].toarray().astype(np.float32, copy=False)
    names = feature_index.iloc[positions]["feature_id"].astype(str).tolist()
    safe_names = [name.replace("::", "__").replace(":", "_").replace(" ", "_").replace("/", "_") for name in names]
    return pd.DataFrame(matrix, columns=safe_names)


def _write_csv(df: pd.DataFrame, output_dir: Path, name: str) -> Path:
    path = output_dir / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def export_source_tasks(input_root: Path, output_dir: Path, view: str, max_features: int) -> list[ExportRecord]:
    records: list[ExportRecord] = []
    for cancer_dir in sorted(p for p in input_root.iterdir() if p.is_dir()):
        cancer = cancer_dir.name
        X, sample_index, feature_index = _read_train_ready(input_root, cancer, view)
        if "cohort_x" not in sample_index.columns:
            continue
        labels = sample_index["cohort_x"].astype("string")
        usable = labels.notna()
        counts = labels[usable].value_counts()
        if len(counts) < 2:
            continue
        X_use = X[usable.to_numpy()]
        labels_use = labels[usable].astype(str).reset_index(drop=True)
        positions = _top_variance_positions(X_use, _nonclinical_feature_positions(feature_index), max_features)
        frame = _dense_frame(X_use, feature_index, positions)
        frame["target"] = labels_use
        name = f"{cancer}_{view}_source_top{len(positions)}"
        path = _write_csv(frame, output_dir, name)
        records.append(
            ExportRecord(
                name=name,
                path=str(path),
                task="binary",
                target="target",
                source_cancers=[cancer],
                view=view,
                samples=len(frame),
                features=len(positions),
                class_counts={str(k): int(v) for k, v in labels_use.value_counts().to_dict().items()},
                note="Predicts TCGA/CPTAC source; useful as batch-effect and normalization diagnostic.",
            )
        )
    return records


def export_os_event_tasks(input_root: Path, output_dir: Path, view: str, max_features: int) -> list[ExportRecord]:
    records: list[ExportRecord] = []
    for cancer_dir in sorted(p for p in input_root.iterdir() if p.is_dir()):
        cancer = cancer_dir.name
        X, sample_index, feature_index = _read_train_ready(input_root, cancer, view)
        if "OS_event" not in sample_index.columns:
            continue
        labels = sample_index["OS_event"]
        usable = labels.notna()
        if usable.sum() < 50:
            continue
        y = labels[usable].astype(int).astype(str).reset_index(drop=True)
        if y.nunique() < 2:
            continue
        X_use = X[usable.to_numpy()]
        positions = _top_variance_positions(X_use, _nonclinical_feature_positions(feature_index), max_features)
        frame = _dense_frame(X_use, feature_index, positions)
        frame["target"] = y
        name = f"{cancer}_{view}_os_event_top{len(positions)}"
        path = _write_csv(frame, output_dir, name)
        records.append(
            ExportRecord(
                name=name,
                path=str(path),
                task="binary",
                target="target",
                source_cancers=[cancer],
                view=view,
                samples=len(frame),
                features=len(positions),
                class_counts={str(k): int(v) for k, v in y.value_counts().to_dict().items()},
                note="Predicts observed OS event; preliminary only because time-to-event censoring is not modeled.",
            )
        )
    return records


def export_cancer_type_task(input_root: Path, output_dir: Path, view: str, max_features: int) -> list[ExportRecord]:
    cancers = sorted(p.name for p in input_root.iterdir() if p.is_dir())
    per_cancer_top = max(1, max_features // max(1, len(cancers)))
    selected_by_cancer: dict[str, pd.Series] = {}
    loaded: dict[str, tuple[sparse.csr_matrix, pd.DataFrame, pd.DataFrame]] = {}

    for cancer in cancers:
        X, sample_index, feature_index = _read_train_ready(input_root, cancer, view)
        loaded[cancer] = (X, sample_index, feature_index)
        positions = _top_variance_positions(X, _nonclinical_feature_positions(feature_index), per_cancer_top)
        selected_by_cancer[cancer] = feature_index.iloc[positions]["feature_id"].astype(str)

    union_features = sorted(set(pd.concat(list(selected_by_cancer.values())).tolist()))
    if len(union_features) > max_features:
        union_features = union_features[:max_features]

    frames: list[pd.DataFrame] = []
    for cancer in cancers:
        X, sample_index, feature_index = loaded[cancer]
        feature_to_pos = dict(zip(feature_index["feature_id"].astype(str), feature_index["feature_index"].astype(int)))
        out = np.zeros((X.shape[0], len(union_features)), dtype=np.float32)
        present_cols: list[int] = []
        present_positions: list[int] = []
        for col_idx, feature_id in enumerate(union_features):
            pos = feature_to_pos.get(feature_id)
            if pos is not None:
                present_cols.append(col_idx)
                present_positions.append(pos)
        if present_positions:
            out[:, present_cols] = X[:, present_positions].toarray().astype(np.float32, copy=False)
        safe_names = [name.replace("::", "__").replace(":", "_").replace(" ", "_").replace("/", "_") for name in union_features]
        frame = pd.DataFrame(out, columns=safe_names)
        frame["target"] = cancer
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)
    name = f"ALL_{view}_cancer_type_top{len(union_features)}"
    path = _write_csv(combined, output_dir, name)
    return [
        ExportRecord(
            name=name,
            path=str(path),
            task="multiclass",
            target="target",
            source_cancers=cancers,
            view=view,
            samples=len(combined),
            features=len(union_features),
            class_counts={str(k): int(v) for k, v in combined["target"].value_counts().to_dict().items()},
            note="Predicts cancer type across all five cohorts; feature union is built from per-cancer high-variance features.",
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Export c-5 sparse train-ready matrices into ev-tabpfn CSV inputs.")
    parser.add_argument("--input-root", default=str(DEFAULT_INPUT_ROOT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--view", default="core", choices=["core", "proteogenomic"])
    parser.add_argument("--max-features", type=int, default=500)
    parser.add_argument("--tasks", nargs="+", default=["source", "os_event", "cancer_type"], choices=["source", "os_event", "cancer_type"])
    args = parser.parse_args()

    input_root = Path(args.input_root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records: list[ExportRecord] = []
    if "source" in args.tasks:
        records.extend(export_source_tasks(input_root, output_dir, args.view, args.max_features))
    if "os_event" in args.tasks:
        records.extend(export_os_event_tasks(input_root, output_dir, args.view, args.max_features))
    if "cancer_type" in args.tasks:
        records.extend(export_cancer_type_task(input_root, output_dir, args.view, args.max_features))

    manifest = {
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "view": args.view,
        "max_features": args.max_features,
        "leakage_control": "All features with prefix clinical:: are excluded from exported model matrices.",
        "records": [asdict(record) for record in records],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    pd.DataFrame([asdict(record) for record in records]).to_csv(output_dir / "manifest.csv", index=False)
    print(json.dumps({"datasets_exported": len(records), "manifest": str(output_dir / "manifest.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
