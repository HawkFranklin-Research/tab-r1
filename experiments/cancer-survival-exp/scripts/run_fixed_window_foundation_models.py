from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import average_precision_score, recall_score


DEFAULT_PACKAGE_SRC = Path("/home/prime/Documents/g3/tab-r1/package/src")
DEFAULT_DATASETS_DIR = Path("/home/prime/Documents/g3/cancer-survival-exp/datasets_fixed_window_top100")
DEFAULT_OUTPUT_ROOT = Path("/home/prime/Documents/g3/cancer-survival-exp/outputs/fixed_window_foundation_top100")
DEFAULT_LOG_DIR = Path("/home/prime/Documents/g3/cancer-survival-exp/logs")
DEFAULT_LEGACY_V1_ROOT = Path("/tmp/TabPFN_v1")


def _dataset_items(datasets_dir: Path) -> list[dict[str, Any]]:
    paths = sorted(path for path in datasets_dir.glob("*.csv") if not path.name.startswith("manifest"))
    return [{"path": str(path), "name": path.stem, "target_column": "target", "task": "binary"} for path in paths]


def _load_foundation_imports(package_src: Path) -> None:
    package_src_text = str(package_src)
    if package_src_text not in sys.path:
        sys.path.insert(0, package_src_text)


def _run_tabpfn_generations(
    *,
    dataset_items: list[dict[str, Any]],
    output_root: Path,
    seed: int,
    train_rows_cap: int,
    legacy_v1_root: Path,
) -> None:
    from ev_tabpfn.evaluation.generations import compare_tabpfn_generations

    compare_tabpfn_generations(
        datasets=dataset_items,
        versions=["v1", "v2", "v2_5", "v2_6", "v3"],
        output_root=output_root,
        target_column="target",
        task="binary",
        seed=seed,
        train_rows_cap=train_rows_cap,
        legacy_v1_root=str(legacy_v1_root),
        model_configs={},
    )


def _run_tabfm_one(
    *,
    dataset_item: dict[str, Any],
    output_root: Path,
    seed: int,
    train_rows_cap: int,
    backend: str,
) -> dict[str, Any]:
    from ev_tabpfn.artifacts.paths import create_run_dirs
    from ev_tabpfn.artifacts.writers import setup_logger, write_json, write_metrics_csv, write_predictions, write_raw_predictions
    from ev_tabpfn.data.loader import DataLoader
    from ev_tabpfn.evaluation.labels import ClassificationLabelContract
    from ev_tabpfn.evaluation.metrics import classification_metrics
    from ev_tabpfn.models.tabfm_backend import TabFMAdapter
    from ev_tabpfn.reporting.plots import plotting_available, save_classification_plots

    dirs = create_run_dirs(output_root, dataset_item["name"])
    logger = setup_logger(dirs["logs"] / "run.log", logger_name=f"fixed_window.tabfm.{dataset_item['name']}")
    loader = DataLoader(seed=seed)
    dataset = loader.load_local_csv(
        dataset_item["path"],
        target_column=dataset_item["target_column"],
        task_override=dataset_item["task"],
    )
    label_contract = ClassificationLabelContract.from_labels(dataset.task_type, dataset.y_train)
    model_name = "tabfm_default"

    write_json(
        dirs["metadata"] / "dataset_metadata.json",
        {
            "dataset_name": dataset_item["name"],
            "dataset_path": dataset_item["path"],
            "task_type": dataset.task_type,
            "target_name": dataset.target_name,
            "feature_names": dataset.feature_names,
            "metadata": dataset.metadata,
            "model_name": model_name,
            "tabfm_backend": backend,
            "train_rows_cap": train_rows_cap,
            "classification_label_contract": label_contract.metadata(),
            "plotting_available": plotting_available(),
        },
    )

    rows: list[dict[str, Any]] = []
    status: dict[str, Any] = {}
    try:
        estimator = TabFMAdapter(
            task_type=dataset.task_type,
            backend=backend,
            ensemble=False,
            max_train_rows=train_rows_cap,
            random_state=seed,
        )
        estimator.fit(dataset.X_train, dataset.y_train)
        y_pred = estimator.predict(dataset.X_test)
        y_prob = estimator.predict_proba(dataset.X_test)
        y_prob_classes = getattr(estimator, "classes_", None)
        metrics = classification_metrics(
            dataset.task_type,
            dataset.y_test,
            y_pred,
            y_prob,
            label_contract=label_contract,
            y_prob_classes=y_prob_classes,
        )
        write_predictions(
            dirs["predictions"] / f"{model_name}_predictions.csv",
            y_true=dataset.y_test,
            y_pred=y_pred,
            y_prob=y_prob,
            label_contract=label_contract,
            y_prob_classes=y_prob_classes,
        )
        raw_paths = write_raw_predictions(
            dirs["base"],
            model_name=model_name,
            dataset_name=dataset_item["name"],
            task_type=dataset.task_type,
            y_true=dataset.y_test,
            y_pred=y_pred,
            y_prob=y_prob,
            y_prob_classes=y_prob_classes,
        )
        plot_files = save_classification_plots(
            output_dir=dirs["plots"],
            task_type=dataset.task_type,
            model_name=model_name,
            y_true=dataset.y_test,
            y_pred=y_pred,
            y_prob=y_prob,
            label_contract=label_contract,
            y_prob_classes=y_prob_classes,
        )
        row = {"model_name": model_name, "version": "tabfm_1_0_0", "task_type": dataset.task_type, "status": "success", **metrics}
        rows.append(row)
        status[model_name] = {"status": "success", "raw_files": raw_paths, "plot_files": plot_files}
        logger.info("Completed %s", model_name)
    except Exception as exc:
        row = {
            "model_name": model_name,
            "version": "tabfm_1_0_0",
            "task_type": dataset.task_type,
            "status": "failed",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
        rows.append(row)
        status[model_name] = {"status": "failed", "error_type": type(exc).__name__, "error_message": str(exc)}
        (dirs["logs"] / f"{model_name}_traceback.txt").write_text(traceback.format_exc())

    write_metrics_csv(dirs["metrics"] / "metrics_summary.csv", rows)
    write_json(dirs["metrics"] / "metrics_summary.json", {"dataset_name": dataset_item["name"], "rows": rows})
    write_json(dirs["metadata"] / "model_status.json", status)
    return {"dataset": dataset_item["name"], "status": rows[0]["status"], "run_dir": str(dirs["base"]), "rows": rows}


def _task_family(dataset_name: str) -> str:
    if "os_3yr" in dataset_name:
        return "os_3yr"
    if "os_5yr" in dataset_name:
        return "os_5yr"
    return "other"


def _write_combined_aggregate(output_root: Path, tabfm_runs: list[dict[str, Any]]) -> dict[str, str]:
    aggregate_dir = output_root / "aggregate"
    aggregate_dir.mkdir(parents=True, exist_ok=True)

    tabpfn_path = aggregate_dir / "generation_dataset_metrics.csv"
    frames: list[pd.DataFrame] = []
    if tabpfn_path.exists():
        frames.append(pd.read_csv(tabpfn_path))
    tabfm_rows: list[dict[str, Any]] = []
    for run in tabfm_runs:
        for row in run["rows"]:
            tabfm_rows.append({"dataset": run["dataset"], **row})
    if tabfm_rows:
        frames.append(pd.DataFrame(tabfm_rows))

    if frames:
        dataset_metrics = pd.concat(frames, ignore_index=True)
    else:
        dataset_metrics = pd.DataFrame(columns=["dataset", "model_name", "version", "task_type", "status"])
    dataset_metrics["task_family"] = dataset_metrics["dataset"].map(_task_family)
    dataset_metrics = _add_prediction_metrics(output_root, dataset_metrics)
    dataset_path = aggregate_dir / "foundation_dataset_metrics.csv"
    dataset_metrics.to_csv(dataset_path, index=False)

    successful = dataset_metrics[dataset_metrics["status"] == "success"].copy()
    metric_cols = ["accuracy", "f1", "roc_auc", "pr_auc", "sensitivity_event", "log_loss"]
    mean_path = aggregate_dir / "foundation_mean_metrics.csv"
    task_mean_path = aggregate_dir / "foundation_task_family_metrics.csv"
    if successful.empty:
        pd.DataFrame(columns=["model_name", *metric_cols]).to_csv(mean_path, index=False)
        pd.DataFrame(columns=["task_family", "model_name", *metric_cols]).to_csv(task_mean_path, index=False)
    else:
        successful.groupby("model_name", as_index=False)[metric_cols].mean(numeric_only=True).to_csv(mean_path, index=False)
        successful.groupby(["task_family", "model_name"], as_index=False)[metric_cols].mean(numeric_only=True).to_csv(
            task_mean_path, index=False
        )
    return {
        "dataset_metrics": str(dataset_path),
        "mean_metrics": str(mean_path),
        "task_family_metrics": str(task_mean_path),
    }


def _prediction_file(output_root: Path, dataset: str, model_name: str) -> Path | None:
    candidates = sorted(
        (output_root / "runs" / dataset).glob(f"*/predictions/{model_name}_predictions.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _add_prediction_metrics(output_root: Path, metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["pr_auc"] = pd.NA
    out["sensitivity_event"] = pd.NA
    if out.empty:
        return out
    for idx, row in out.iterrows():
        if row.get("status") != "success":
            continue
        pred_path = _prediction_file(output_root, str(row["dataset"]), str(row["model_name"]))
        if pred_path is None:
            continue
        pred = pd.read_csv(pred_path)
        if not {"y_true_encoded", "y_pred_encoded", "prob_1"}.issubset(pred.columns):
            continue
        y_true = pred["y_true_encoded"].astype(int)
        y_pred = pred["y_pred_encoded"].astype(int)
        if y_true.nunique() < 2:
            continue
        out.at[idx, "pr_auc"] = float(average_precision_score(y_true, pred["prob_1"].astype(float)))
        out.at[idx, "sensitivity_event"] = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fixed-window OS labels with TabPFN generations and TabFM default.")
    parser.add_argument("--datasets-dir", default=str(DEFAULT_DATASETS_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--package-src", default=str(DEFAULT_PACKAGE_SRC))
    parser.add_argument("--legacy-v1-root", default=str(DEFAULT_LEGACY_V1_ROOT))
    parser.add_argument("--train-rows-cap", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tabfm-backend", choices=["jax", "pytorch"], default="jax")
    parser.add_argument("--skip-tabpfn", action="store_true")
    parser.add_argument("--skip-tabfm", action="store_true")
    args = parser.parse_args()

    datasets_dir = Path(args.datasets_dir).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    package_src = Path(args.package_src).expanduser().resolve()
    legacy_v1_root = Path(args.legacy_v1_root).expanduser().resolve()
    log_dir = DEFAULT_LOG_DIR
    output_root.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    _load_foundation_imports(package_src)

    dataset_items = _dataset_items(datasets_dir)
    if not dataset_items:
        raise FileNotFoundError(f"No CSV datasets found in {datasets_dir}")
    if not args.skip_tabpfn and not legacy_v1_root.exists():
        raise FileNotFoundError(f"Legacy TabPFN v1 root does not exist: {legacy_v1_root}")

    command_record = {
        "datasets_dir": str(datasets_dir),
        "dataset_count": len(dataset_items),
        "output_root": str(output_root),
        "package_src": str(package_src),
        "legacy_v1_root": str(legacy_v1_root),
        "train_rows_cap": args.train_rows_cap,
        "seed": args.seed,
        "tabfm_backend": args.tabfm_backend,
        "skip_tabpfn": args.skip_tabpfn,
        "skip_tabfm": args.skip_tabfm,
    }
    (log_dir / "fixed_window_foundation_command.json").write_text(json.dumps(command_record, indent=2))

    if not args.skip_tabpfn:
        _run_tabpfn_generations(
            dataset_items=dataset_items,
            output_root=output_root,
            seed=args.seed,
            train_rows_cap=args.train_rows_cap,
            legacy_v1_root=legacy_v1_root,
        )

    tabfm_runs: list[dict[str, Any]] = []
    if not args.skip_tabfm:
        for item in dataset_items:
            tabfm_runs.append(
                _run_tabfm_one(
                    dataset_item=item,
                    output_root=output_root,
                    seed=args.seed,
                    train_rows_cap=args.train_rows_cap,
                    backend=args.tabfm_backend,
                )
            )

    aggregate_paths = _write_combined_aggregate(output_root, tabfm_runs)
    summary = {
        "datasets_total": len(dataset_items),
        "tabfm_success": sum(1 for run in tabfm_runs if run["status"] == "success"),
        "tabfm_failed": sum(1 for run in tabfm_runs if run["status"] != "success"),
        "aggregate_paths": aggregate_paths,
    }
    (output_root / "fixed_window_foundation_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if summary["tabfm_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
