from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse


DEFAULT_INPUT_ROOT = Path("/home/prime/Documents/g3/c-5/gpt/processed/train_ready")
DEFAULT_OUTPUT_DIR = Path("/home/prime/Documents/g3/cancer-survival-exp/datasets_fixed_window_top100")
WINDOWS_DAYS = {"os_3yr": 3 * 365, "os_5yr": 5 * 365}


@dataclass
class ExportRecord:
    name: str
    path: str
    task: str
    target: str
    source_cancers: list[str]
    view: str
    endpoint: str
    horizon_days: int
    samples: int
    features: int
    class_counts: dict[str, int]
    excluded_ambiguous: int
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
    return np.flatnonzero((~feature_ids.str.startswith("clinical::")).to_numpy())


def _top_variance_positions(X: sparse.csr_matrix, candidates: np.ndarray, max_features: int) -> np.ndarray:
    if len(candidates) == 0:
        raise ValueError("No candidate features available after filtering clinical features.")
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


def _fixed_window_label(sample_index: pd.DataFrame, horizon_days: int) -> tuple[pd.Series, pd.Series, int]:
    os_days = pd.to_numeric(sample_index["OS_days"], errors="coerce")
    os_event = pd.to_numeric(sample_index["OS_event"], errors="coerce")
    has_survival = os_days.notna() & os_event.notna()

    event_by_horizon = has_survival & (os_event == 1) & (os_days <= horizon_days)
    known_no_event_by_horizon = has_survival & (
        ((os_event == 0) & (os_days >= horizon_days)) | ((os_event == 1) & (os_days > horizon_days))
    )
    usable = event_by_horizon | known_no_event_by_horizon
    ambiguous = int((has_survival & ~usable).sum())

    y = pd.Series(np.where(event_by_horizon[usable], "1", "0"), index=sample_index.index[usable])
    return usable, y.reset_index(drop=True), ambiguous


def _write_csv(df: pd.DataFrame, output_dir: Path, name: str) -> Path:
    path = output_dir / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def export_fixed_window_tasks(
    input_root: Path,
    output_dir: Path,
    view: str,
    max_features: int,
    windows: dict[str, int],
) -> list[ExportRecord]:
    records: list[ExportRecord] = []
    for cancer_dir in sorted(p for p in input_root.iterdir() if p.is_dir()):
        cancer = cancer_dir.name
        X, sample_index, feature_index = _read_train_ready(input_root, cancer, view)
        if not {"OS_days", "OS_event"}.issubset(sample_index.columns):
            continue
        for endpoint, horizon_days in windows.items():
            usable, y, ambiguous = _fixed_window_label(sample_index, horizon_days)
            if usable.sum() < 50 or y.nunique() < 2:
                continue
            X_use = X[usable.to_numpy()]
            positions = _top_variance_positions(X_use, _nonclinical_feature_positions(feature_index), max_features)
            frame = _dense_frame(X_use, feature_index, positions)
            frame["target"] = y
            name = f"{cancer}_{view}_{endpoint}_event_top{len(positions)}"
            path = _write_csv(frame, output_dir, name)
            counts = {str(k): int(v) for k, v in y.value_counts().to_dict().items()}
            records.append(
                ExportRecord(
                    name=name,
                    path=str(path),
                    task="binary",
                    target="target",
                    source_cancers=[cancer],
                    view=view,
                    endpoint=endpoint,
                    horizon_days=horizon_days,
                    samples=len(frame),
                    features=len(positions),
                    class_counts=counts,
                    excluded_ambiguous=ambiguous,
                    note=(
                        f"Predicts observed death by {horizon_days} days. "
                        "Patients censored before the horizon are excluded."
                    ),
                )
            )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Export fixed-window OS event CSVs for cancer foundation-model runs.")
    parser.add_argument("--input-root", default=str(DEFAULT_INPUT_ROOT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--view", default="core", choices=["core", "proteogenomic"])
    parser.add_argument("--max-features", type=int, default=100)
    args = parser.parse_args()

    input_root = Path(args.input_root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = export_fixed_window_tasks(input_root, output_dir, args.view, args.max_features, WINDOWS_DAYS)
    manifest = {
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "view": args.view,
        "max_features": args.max_features,
        "label_contract": {
            "positive_class": "1 = death observed on or before the fixed OS horizon",
            "negative_class": "0 = alive/censored beyond the fixed OS horizon, or death after the horizon",
            "excluded": "patients censored before the fixed OS horizon",
            "horizons_days": WINDOWS_DAYS,
        },
        "leakage_control": "All features with prefix clinical:: are excluded from exported model matrices.",
        "records": [asdict(record) for record in records],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    pd.DataFrame([asdict(record) for record in records]).to_csv(output_dir / "manifest.csv", index=False)
    print(json.dumps({"datasets_exported": len(records), "manifest": str(output_dir / "manifest.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
