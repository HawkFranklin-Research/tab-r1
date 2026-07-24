from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_OUTPUT_ROOT = Path("/home/prime/Documents/g3/cancer-survival-exp/outputs/fixed_window_foundation_top100")
DEFAULT_PLOTS_DIR = Path("/home/prime/Documents/g3/cancer-survival-exp/plots/fixed_window_foundation_top100")
DEFAULT_REPORTS_DIR = Path("/home/prime/Documents/g3/cancer-survival-exp/reports")
DEFAULT_DATASETS_DIR = Path("/home/prime/Documents/g3/cancer-survival-exp/datasets_fixed_window_top100")


def _load_metrics(output_root: Path) -> pd.DataFrame:
    path = output_root / "aggregate" / "foundation_dataset_metrics.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _load_manifest(datasets_dir: Path) -> pd.DataFrame:
    path = datasets_dir / "manifest.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _success(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["status"] == "success"].copy()


def _plot_horizon_metric_bars(df: pd.DataFrame, plots_dir: Path) -> Path:
    metrics = ["roc_auc", "pr_auc", "f1", "sensitivity_event", "log_loss"]
    successful = _success(df)
    grouped = successful.groupby(["task_family", "model_name"])[metrics].mean(numeric_only=True).reset_index()
    fig, axes = plt.subplots(3, 2, figsize=(14, 12), squeeze=False)
    for ax, metric in zip(axes.ravel(), metrics):
        pivot = grouped.pivot(index="task_family", columns="model_name", values=metric).sort_index()
        pivot.plot(kind="bar", ax=ax)
        ax.set_title(metric)
        ax.set_xlabel("")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    axes.ravel()[-1].axis("off")
    fig.suptitle("Fixed-window OS event classification by horizon")
    fig.tight_layout()
    path = plots_dir / "fixed_window_horizon_metric_bars.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_dataset_roc_auc(df: pd.DataFrame, plots_dir: Path) -> Path:
    successful = _success(df)
    pivot = successful.pivot(index="dataset", columns="model_name", values="roc_auc")
    fig, ax = plt.subplots(figsize=(14, 7))
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel("ROC AUC")
    ax.set_title("Dataset-level fixed-window OS event ROC AUC")
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(axis="x", rotation=65)
    fig.tight_layout()
    path = plots_dir / "fixed_window_dataset_roc_auc.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _plot_model_rank_heatmap(df: pd.DataFrame, plots_dir: Path) -> Path:
    metrics = ["roc_auc", "pr_auc", "f1", "sensitivity_event", "log_loss"]
    mean_df = _success(df).groupby("model_name")[metrics].mean(numeric_only=True).sort_index()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    values = mean_df.to_numpy(dtype=float)
    im = ax.imshow(values, cmap="mako" if "mako" in plt.colormaps() else "viridis", aspect="auto")
    ax.set_xticks(np.arange(len(metrics)), labels=metrics)
    ax.set_yticks(np.arange(len(mean_df.index)), labels=mean_df.index)
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            ax.text(col, row, f"{values[row, col]:.3f}", ha="center", va="center", color="white")
    fig.colorbar(im, ax=ax)
    ax.set_title("Mean fixed-window OS metrics by model")
    fig.tight_layout()
    path = plots_dir / "fixed_window_model_metric_heatmap.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _write_report(
    df: pd.DataFrame,
    manifest: pd.DataFrame,
    plots: list[str],
    output_root: Path,
    datasets_dir: Path,
    reports_dir: Path,
) -> Path:
    metrics = ["accuracy", "f1", "roc_auc", "pr_auc", "sensitivity_event", "log_loss"]
    successful = _success(df)
    mean_by_model = successful.groupby("model_name")[metrics].mean(numeric_only=True).reset_index()
    mean_by_horizon_model = successful.groupby(["task_family", "model_name"])[metrics].mean(numeric_only=True).reset_index()
    failure_rows = df[df["status"] != "success"].copy()

    lines = [
        "# Fixed-Window OS Event Foundation-Model Experiment",
        "",
        f"- Output root: `{output_root}`",
        f"- Dataset source: `{datasets_dir}`",
        "- Endpoints: 3-year and 5-year observed OS event classification.",
        "- Positive class: death observed on or before the fixed horizon.",
        "- Negative class: no observed death before the fixed horizon.",
        "- Excluded: patients censored before the horizon, because their fixed-window label is unknown.",
        "- Features: top 100 non-clinical high-variance molecular features per cancer dataset.",
        "- Compared models: TabPFN v1, v2, v2.5, v2.6, v3, and TabFM 1.0.0 default.",
        "- TabFM ensemble is intentionally excluded.",
        "",
    ]
    if not manifest.empty:
        cols = ["name", "endpoint", "horizon_days", "samples", "class_counts", "excluded_ambiguous"]
        lines.extend(["## Exported Label Sets", "", manifest[cols].to_markdown(index=False), ""])

    lines.extend(
        [
            "## Mean Metrics By Model",
            "",
            mean_by_model.to_markdown(index=False),
            "",
            "## Mean Metrics By Horizon And Model",
            "",
            mean_by_horizon_model.to_markdown(index=False),
            "",
            "## Dataset-Level Metrics",
            "",
            successful.to_markdown(index=False),
            "",
        ]
    )
    if not failure_rows.empty:
        lines.extend(["## Failures", "", failure_rows.to_markdown(index=False), ""])
    lines.extend(["## Generated Plots", ""])
    lines.extend(f"- `{plot}`" for plot in plots)

    path = reports_dir / "fixed_window_foundation_os_report.md"
    path.write_text("\n".join(lines) + "\n")
    mean_by_model.to_csv(reports_dir / "fixed_window_foundation_mean_metrics.csv", index=False)
    mean_by_horizon_model.to_csv(reports_dir / "fixed_window_foundation_task_family_metrics.csv", index=False)
    successful.to_csv(reports_dir / "fixed_window_foundation_dataset_metrics.csv", index=False)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create report for fixed-window OS foundation-model experiment.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--plots-dir", default=str(DEFAULT_PLOTS_DIR))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    parser.add_argument("--datasets-dir", default=str(DEFAULT_DATASETS_DIR))
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    plots_dir = Path(args.plots_dir).expanduser().resolve()
    reports_dir = Path(args.reports_dir).expanduser().resolve()
    datasets_dir = Path(args.datasets_dir).expanduser().resolve()
    plots_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = _load_metrics(output_root)
    manifest = _load_manifest(datasets_dir)
    plot_paths = [
        str(_plot_horizon_metric_bars(df, plots_dir)),
        str(_plot_dataset_roc_auc(df, plots_dir)),
        str(_plot_model_rank_heatmap(df, plots_dir)),
    ]
    report_path = _write_report(df, manifest, plot_paths, output_root, datasets_dir, reports_dir)
    payload = {"plots": plot_paths, "report": str(report_path)}
    (reports_dir / "fixed_window_foundation_plot_manifest.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
