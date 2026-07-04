from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_OUTPUT_ROOT = Path("/home/prime/Documents/g3/cancer-exp/outputs/tabpfn_all_generations_top100")
DEFAULT_PLOTS_DIR = Path("/home/prime/Documents/g3/cancer-exp/plots/all_generations_top100")
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


def _success(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["status"] == "success"].copy()


def _plot_mean_metric_heatmap(df: pd.DataFrame, plots_dir: Path) -> Path:
    metrics = ["accuracy", "f1", "roc_auc", "log_loss"]
    mean_df = _success(df).groupby("model_name")[metrics].mean(numeric_only=True).sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    values = mean_df.to_numpy(dtype=float)
    im = ax.imshow(values, cmap="viridis", aspect="auto")
    ax.set_xticks(np.arange(len(metrics)), labels=metrics)
    ax.set_yticks(np.arange(len(mean_df.index)), labels=mean_df.index)
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            ax.text(col, row, f"{values[row, col]:.3f}", ha="center", va="center", color="white")
    fig.colorbar(im, ax=ax)
    ax.set_title("Mean metrics by TabPFN generation")
    fig.tight_layout()
    path = plots_dir / "all_generations_mean_metric_heatmap.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_metric_by_task(df: pd.DataFrame, plots_dir: Path) -> Path:
    metrics = ["accuracy", "f1", "roc_auc", "log_loss"]
    successful = _success(df)
    grouped = successful.groupby(["task_family", "model_name"])[metrics].mean(numeric_only=True).reset_index()
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), squeeze=False)
    for ax, metric in zip(axes.ravel(), metrics):
        pivot = grouped.pivot(index="task_family", columns="model_name", values=metric)
        pivot.plot(kind="bar", ax=ax)
        ax.set_title(metric)
        ax.set_xlabel("")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("TabPFN generation metrics by task family")
    fig.tight_layout()
    path = plots_dir / "all_generations_task_family_bars.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_dataset_accuracy(df: pd.DataFrame, plots_dir: Path) -> Path:
    successful = _success(df)
    pivot = successful.pivot(index="dataset", columns="model_name", values="accuracy")
    fig, ax = plt.subplots(figsize=(13, 7))
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel("accuracy")
    ax.set_title("Dataset-level accuracy by TabPFN generation")
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis="x", rotation=65)
    fig.tight_layout()
    path = plots_dir / "all_generations_dataset_accuracy.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _write_report(df: pd.DataFrame, plots: list[str], output_root: Path, reports_dir: Path) -> Path:
    metrics = ["accuracy", "f1", "roc_auc", "log_loss"]
    successful = _success(df)
    mean_by_model = successful.groupby("model_name")[metrics].mean(numeric_only=True).reset_index()
    mean_by_task_model = successful.groupby(["task_family", "model_name"])[metrics].mean(numeric_only=True).reset_index()
    failure_rows = df[df["status"] != "success"].copy()
    lines = [
        "# TabPFN Generation Comparison on Cancer Multiomics",
        "",
        f"- Output root: `{output_root}`",
        "- Dataset source: `/home/prime/Documents/g3/cancer-exp/datasets_top100`",
        "- Feature cap: 100 non-clinical top-variance features per exported dataset, required so legacy TabPFN v1 can run.",
        "- Compared generations: v1, v2, v2.5, v2.6, v3.",
        "- All prediction CSVs and raw `.npz` prediction files are saved under each run directory.",
        "",
        "## Mean Metrics By Generation",
        "",
        mean_by_model.to_markdown(index=False),
        "",
        "## Mean Metrics By Task Family And Generation",
        "",
        mean_by_task_model.to_markdown(index=False),
        "",
        "## Dataset-Level Metrics",
        "",
        successful.to_markdown(index=False),
        "",
    ]
    if not failure_rows.empty:
        lines.extend(["## Failures", "", failure_rows.to_markdown(index=False), ""])
    lines.extend(["## Generated Plots", ""])
    lines.extend(f"- `{plot}`" for plot in plots)
    path = reports_dir / "tabpfn_all_generations_cancer_report.md"
    path.write_text("\n".join(lines) + "\n")
    mean_by_model.to_csv(reports_dir / "tabpfn_all_generations_mean_metrics.csv", index=False)
    mean_by_task_model.to_csv(reports_dir / "tabpfn_all_generations_task_family_metrics.csv", index=False)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create comprehensive report for all TabPFN generation comparison.")
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
        str(_plot_mean_metric_heatmap(df, plots_dir)),
        str(_plot_metric_by_task(df, plots_dir)),
        str(_plot_dataset_accuracy(df, plots_dir)),
    ]
    report_path = _write_report(df, plot_paths, output_root, reports_dir)
    manifest = {"plots": plot_paths, "report": str(report_path)}
    (reports_dir / "tabpfn_all_generations_plot_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
