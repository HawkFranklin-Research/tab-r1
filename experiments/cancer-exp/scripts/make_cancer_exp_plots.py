from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import auc, confusion_matrix, roc_curve


DEFAULT_OUTPUT_ROOT = Path("/home/prime/Documents/g3/cancer-exp/outputs/tabpfn3_core")
DEFAULT_PLOTS_DIR = Path("/home/prime/Documents/g3/cancer-exp/plots")
DEFAULT_REPORTS_DIR = Path("/home/prime/Documents/g3/cancer-exp/reports")


def _task_family(dataset_name: str) -> str:
    if "source" in dataset_name:
        return "source"
    if "os_event" in dataset_name:
        return "os_event"
    if "cancer_type" in dataset_name:
        return "cancer_type"
    return "other"


def _load_metrics(output_root: Path) -> pd.DataFrame:
    path = output_root / "aggregate" / "generation_dataset_metrics.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["task_family"] = df["dataset"].map(_task_family)
    return df


def _plot_metric_bars(df: pd.DataFrame, plots_dir: Path) -> Path:
    metrics = [m for m in ["accuracy", "f1", "roc_auc", "log_loss"] if m in df.columns]
    successful = df[df["status"] == "success"].copy()
    fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 3.2 * len(metrics)), sharex=True)
    if len(metrics) == 1:
        axes = [axes]
    for ax, metric in zip(axes, metrics):
        values = successful.set_index("dataset")[metric].sort_values(ascending=metric == "log_loss")
        ax.bar(values.index, values.values, color="#2f6f73")
        ax.set_ylabel(metric)
        ax.grid(axis="y", alpha=0.3)
    axes[-1].tick_params(axis="x", rotation=65)
    fig.suptitle("TabPFN3 cancer experiment metrics")
    fig.tight_layout()
    path = plots_dir / "tabpfn3_metric_bars.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_task_summary(df: pd.DataFrame, plots_dir: Path) -> Path:
    metrics = [m for m in ["accuracy", "f1", "roc_auc", "log_loss"] if m in df.columns]
    successful = df[df["status"] == "success"].copy()
    summary = successful.groupby("task_family")[metrics].mean(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(summary.to_numpy(dtype=float), aspect="auto", cmap="viridis")
    ax.set_xticks(np.arange(len(metrics)), labels=metrics)
    ax.set_yticks(np.arange(len(summary.index)), labels=summary.index)
    for row_idx in range(summary.shape[0]):
        for col_idx in range(summary.shape[1]):
            value = summary.iloc[row_idx, col_idx]
            ax.text(col_idx, row_idx, f"{value:.3f}", ha="center", va="center", color="white")
    fig.colorbar(im, ax=ax)
    ax.set_title("Mean TabPFN3 metrics by task family")
    fig.tight_layout()
    path = plots_dir / "tabpfn3_task_family_heatmap.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _find_prediction_files(output_root: Path) -> list[Path]:
    return sorted(output_root.glob("runs/*/*/predictions/tabpfn_v3_predictions.csv"))


def _plot_binary_roc_grid(prediction_files: list[Path], plots_dir: Path) -> Path | None:
    binary_files = []
    for path in prediction_files:
        df = pd.read_csv(path)
        if {"y_true_encoded", "prob_1"}.issubset(df.columns) and df["y_true_encoded"].nunique() == 2:
            binary_files.append(path)
    if not binary_files:
        return None

    cols = 3
    rows = int(np.ceil(len(binary_files) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 4.2 * rows), squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, path in zip(axes.ravel(), binary_files):
        df = pd.read_csv(path)
        fpr, tpr, _ = roc_curve(df["y_true_encoded"], df["prob_1"])
        score = auc(fpr, tpr)
        dataset = path.parents[2].name
        ax.plot(fpr, tpr, label=f"AUC={score:.3f}", color="#bf5b17")
        ax.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=1)
        ax.set_title(dataset)
        ax.set_xlabel("FPR")
        ax.set_ylabel("TPR")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.axis("on")
    fig.suptitle("TabPFN3 binary ROC grid")
    fig.tight_layout()
    path = plots_dir / "tabpfn3_binary_roc_grid.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_multiclass_confusion(prediction_files: list[Path], plots_dir: Path) -> list[Path]:
    outputs: list[Path] = []
    for path in prediction_files:
        df = pd.read_csv(path)
        if df["y_true"].nunique() <= 2:
            continue
        labels = sorted(set(df["y_true"].astype(str)) | set(df["y_pred"].astype(str)))
        cm = confusion_matrix(df["y_true"].astype(str), df["y_pred"].astype(str), labels=labels, normalize="true")
        fig, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(np.arange(len(labels)), labels=labels, rotation=45, ha="right")
        ax.set_yticks(np.arange(len(labels)), labels=labels)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title(f"Normalized confusion: {path.parents[2].name}")
        for row in range(cm.shape[0]):
            for col in range(cm.shape[1]):
                ax.text(col, row, f"{cm[row, col]:.2f}", ha="center", va="center", color="black")
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        out = plots_dir / f"{path.parents[2].name}_confusion_norm.png"
        fig.savefig(out, dpi=180)
        plt.close(fig)
        outputs.append(out)
    return outputs


def _write_report(df: pd.DataFrame, plots: list[str], output_root: Path, reports_dir: Path) -> Path:
    successful = df[df["status"] == "success"].copy()
    lines = [
        "# TabPFN3 Cancer Experiment Report",
        "",
        f"- Output root: `{output_root}`",
        f"- Successful rows: {len(successful)} / {len(df)}",
        "- Input matrices came from `gpt/processed/train_ready`, exported into dense CSVs with clinical features excluded.",
        "- Feature selection: unsupervised top-variance non-clinical features.",
        "- Caveat: OS-event prediction is preliminary because censoring/time-to-event modeling is not handled here.",
        "",
        "## Dataset Metrics",
        "",
        successful.to_markdown(index=False),
        "",
        "## Mean Metrics By Task Family",
        "",
        successful.groupby("task_family")[["accuracy", "f1", "roc_auc", "log_loss"]].mean(numeric_only=True).to_markdown(),
        "",
        "## Generated Plots",
        "",
    ]
    lines.extend(f"- `{plot}`" for plot in plots)
    path = reports_dir / "tabpfn3_cancer_experiment_report.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create custom summary plots for cancer-exp TabPFN3 outputs.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--plots-dir", default=str(DEFAULT_PLOTS_DIR))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    plots_dir = Path(args.plots_dir).expanduser().resolve()
    reports_dir = Path(args.reports_dir).expanduser().resolve()
    plots_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = _load_metrics(output_root)
    plot_paths = [
        str(_plot_metric_bars(df, plots_dir)),
        str(_plot_task_summary(df, plots_dir)),
    ]
    prediction_files = _find_prediction_files(output_root)
    roc_path = _plot_binary_roc_grid(prediction_files, plots_dir)
    if roc_path:
        plot_paths.append(str(roc_path))
    plot_paths.extend(str(path) for path in _plot_multiclass_confusion(prediction_files, plots_dir))
    report_path = _write_report(df, plot_paths, output_root, reports_dir)
    (reports_dir / "plot_manifest.json").write_text(json.dumps({"plots": plot_paths, "report": str(report_path)}, indent=2))
    print(json.dumps({"plots": plot_paths, "report": str(report_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
