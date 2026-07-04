from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PACKAGE_SRC = Path("/home/prime/Documents/g3/tab-r1/package/src")
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from ev_tabpfn.data.loader import DataLoader  # noqa: E402
from ev_tabpfn.evaluation.generation_preprocessing import TabPFNGenerationPreprocessor, cap_training_rows  # noqa: E402
from ev_tabpfn.evaluation.labels import ClassificationLabelContract, flatten_predictions  # noqa: E402
from ev_tabpfn.models.tabpfn_versions import build_tabpfn_classifier, clear_accelerator_cache, purge_tabpfn_modules  # noqa: E402


DEFAULT_DATASETS_DIR = Path("/home/prime/Documents/g3/cancer-exp/datasets_top100")
DEFAULT_OUTPUT_DIR = Path("/home/prime/Documents/g3/cancer-exp/outputs/all_splits_predictions_top100")
DEFAULT_LEGACY_V1_ROOT = Path("/tmp/TabPFN_v1")
VERSIONS = ["v1", "v2", "v2_5", "v2_6", "v3"]


def _predict(model: Any, X: np.ndarray) -> tuple[np.ndarray, np.ndarray | None, Any | None]:
    y_pred = model.predict(X)
    y_prob = None
    if hasattr(model, "predict_proba"):
        try:
            y_prob = model.predict_proba(X)
        except Exception:
            y_prob = None
    return np.asarray(y_pred), None if y_prob is None else np.asarray(y_prob), getattr(model, "classes_", None)


def _probability_columns(
    y_prob: np.ndarray | None,
    label_contract: ClassificationLabelContract,
    y_prob_classes: Any | None,
) -> pd.DataFrame:
    if y_prob is None:
        return pd.DataFrame()
    return label_contract.probability_frame(y_prob, y_prob_classes)


def _split_frame(
    *,
    dataset_name: str,
    model_name: str,
    version: str,
    split_name: str,
    original_index: pd.Index,
    y_true: pd.Series,
    y_pred: Any,
    y_prob: np.ndarray | None,
    y_prob_classes: Any | None,
    label_contract: ClassificationLabelContract,
) -> pd.DataFrame:
    y_pred_flat = flatten_predictions(y_pred)
    frame = pd.DataFrame(
        {
            "dataset": dataset_name,
            "model_name": model_name,
            "version": version,
            "split": split_name,
            "original_row_index": list(original_index),
            "y_true": y_true.reset_index(drop=True),
            "y_pred": pd.Series(y_pred_flat),
        }
    )
    frame["y_true_encoded"] = label_contract.encode(y_true)
    frame["y_pred_encoded"] = label_contract.encode(y_pred_flat)
    prob_df = _probability_columns(y_prob, label_contract, y_prob_classes)
    if not prob_df.empty:
        frame = pd.concat([frame, prob_df], axis=1)
    return frame


def _save_prediction_bundle(base_dir: Path, frames: dict[str, pd.DataFrame], y_prob_by_split: dict[str, np.ndarray | None]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.concat([frames["train"], frames["val"], frames["test"]], ignore_index=True)
    for split_name, frame in frames.items():
        frame.to_csv(base_dir / f"{split_name}_predictions.csv", index=False)
    combined.to_csv(base_dir / "all_samples_predictions.csv", index=False)
    np.savez_compressed(
        base_dir / "all_samples_predictions.npz",
        split=combined["split"].to_numpy(dtype=str),
        original_row_index=combined["original_row_index"].to_numpy(),
        y_true=combined["y_true"].to_numpy(),
        y_pred=combined["y_pred"].to_numpy(),
        y_true_encoded=combined["y_true_encoded"].to_numpy(),
        y_pred_encoded=combined["y_pred_encoded"].to_numpy(),
        train_y_prob=y_prob_by_split["train"] if y_prob_by_split["train"] is not None else np.array([]),
        val_y_prob=y_prob_by_split["val"] if y_prob_by_split["val"] is not None else np.array([]),
        test_y_prob=y_prob_by_split["test"] if y_prob_by_split["test"] is not None else np.array([]),
    )


def _build_model(version: str, legacy_v1_root: Path) -> Any:
    config: dict[str, Any] = {}
    if version == "v1":
        config = {
            "legacy_v1_root": str(legacy_v1_root),
            "allow_runtime_swap": True,
            "n_ensemble_configurations": 32,
        }
    else:
        legacy_path = str(legacy_v1_root.resolve())
        if legacy_path in sys.path:
            sys.path.remove(legacy_path)
        purge_tabpfn_modules()
    return build_tabpfn_classifier(version, config)


def _run_dataset(dataset_path: Path, output_dir: Path, seed: int, train_rows_cap: int, legacy_v1_root: Path) -> list[dict[str, Any]]:
    dataset_name = dataset_path.stem
    dataset_output = output_dir / dataset_name
    dataset_output.mkdir(parents=True, exist_ok=True)

    loader = DataLoader(seed=seed)
    dataset = loader.load_local_csv(str(dataset_path), target_column="target")
    capped = cap_training_rows(dataset.X_train, dataset.y_train, task_type=dataset.task_type, seed=seed, max_rows=train_rows_cap)
    preprocessor = TabPFNGenerationPreprocessor().fit(capped.X_train)
    X_train_all = preprocessor.transform(dataset.X_train)
    X_val = preprocessor.transform(dataset.X_val)
    X_test = preprocessor.transform(dataset.X_test)
    X_train_fit = preprocessor.transform(capped.X_train)
    label_contract = ClassificationLabelContract.from_labels(dataset.task_type, capped.y_train)

    metadata = {
        "dataset_name": dataset_name,
        "dataset_path": str(dataset_path),
        "task_type": dataset.task_type,
        "target_name": dataset.target_name,
        "total_samples": dataset.metadata["total_samples"],
        "train_samples": dataset.metadata["train_samples"],
        "val_samples": dataset.metadata["val_samples"],
        "test_samples": dataset.metadata["test_samples"],
        "train_rows_cap": train_rows_cap,
        "train_rows_used_for_fit": capped.rows_used,
        "versions": VERSIONS,
        "note": "Predictions are saved for train, val, test, and combined all_samples. Models are fit on the same capped training subset used by generation comparison.",
    }
    (dataset_output / "dataset_metadata.json").write_text(json.dumps(metadata, indent=2))

    rows: list[dict[str, Any]] = []
    for version in VERSIONS:
        model_name = f"tabpfn_{version}"
        model_dir = dataset_output / model_name
        try:
            model = _build_model(version, legacy_v1_root)
            if version == "v1":
                model.fit(X_train_fit, capped.y_train, overwrite_warning=True)
            else:
                model.fit(X_train_fit, capped.y_train)

            split_inputs = {
                "train": (X_train_all, dataset.X_train.index, dataset.y_train),
                "val": (X_val, dataset.X_val.index, dataset.y_val),
                "test": (X_test, dataset.X_test.index, dataset.y_test),
            }
            frames: dict[str, pd.DataFrame] = {}
            probs: dict[str, np.ndarray | None] = {}
            for split_name, (X_split, original_index, y_true) in split_inputs.items():
                y_pred, y_prob, y_prob_classes = _predict(model, X_split)
                probs[split_name] = y_prob
                frames[split_name] = _split_frame(
                    dataset_name=dataset_name,
                    model_name=model_name,
                    version=version,
                    split_name=split_name,
                    original_index=original_index,
                    y_true=y_true,
                    y_pred=y_pred,
                    y_prob=y_prob,
                    y_prob_classes=y_prob_classes,
                    label_contract=label_contract,
                )
            _save_prediction_bundle(model_dir, frames, probs)
            rows.append(
                {
                    "dataset": dataset_name,
                    "model_name": model_name,
                    "version": version,
                    "status": "success",
                    "output_dir": str(model_dir),
                    "train_predictions": len(frames["train"]),
                    "val_predictions": len(frames["val"]),
                    "test_predictions": len(frames["test"]),
                    "all_predictions": sum(len(frame) for frame in frames.values()),
                }
            )
        except Exception as exc:
            model_dir.mkdir(parents=True, exist_ok=True)
            (model_dir / "traceback.txt").write_text(traceback.format_exc())
            rows.append(
                {
                    "dataset": dataset_name,
                    "model_name": model_name,
                    "version": version,
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "output_dir": str(model_dir),
                }
            )
        finally:
            clear_accelerator_cache()
    pd.DataFrame(rows).to_csv(dataset_output / "all_split_prediction_status.csv", index=False)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Save train/val/test/all-sample predictions for every TabPFN generation.")
    parser.add_argument("--datasets-dir", default=str(DEFAULT_DATASETS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--legacy-v1-root", default=str(DEFAULT_LEGACY_V1_ROOT))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-rows-cap", type=int, default=512)
    args = parser.parse_args()

    datasets_dir = Path(args.datasets_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    legacy_v1_root = Path(args.legacy_v1_root).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_paths = sorted(path for path in datasets_dir.glob("*.csv") if not path.name.startswith("manifest"))
    all_rows: list[dict[str, Any]] = []
    for dataset_path in dataset_paths:
        all_rows.extend(_run_dataset(dataset_path, output_dir, args.seed, args.train_rows_cap, legacy_v1_root))
    status = pd.DataFrame(all_rows)
    status.to_csv(output_dir / "all_split_prediction_status.csv", index=False)
    summary = {
        "datasets": len(dataset_paths),
        "model_runs": len(status),
        "success": int((status["status"] == "success").sum()),
        "failed": int((status["status"] == "failed").sum()),
        "output_dir": str(output_dir),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
