from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LANDSCAPE = ROOT / "paper" / "tables" / "source_data" / "landscape"
DEFAULT_OUTPUT = ROOT / "paper" / "figures" / "evidence"
DATASET_ROOT = (
    ROOT
    / "Accurate_Prediction_on_Small_Dataset_with_TabPFN_Research"
    / "Practical Research"
    / "Datasets"
    / "Datasets from TabPFN Classification"
    / "Classification DataSets"
)
BENCHMARK_FILES = (
    "ada_dataset.csv",
    "australian_dataset.csv",
    "blood_transfusion-service-center.csv",
    "car.csv",
    "chum.csv",
    "cmc.csv",
    "credit-g.csv",
)
PALETTE = ["#16324F", "#1B998B", "#E2A03F", "#C44536", "#6D597A", "#4F6D7A"]


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(-0.12, 1.08, label, transform=axis.transAxes, fontsize=14, fontweight="bold", va="top")


def require(directory: Path, filename: str) -> pd.DataFrame:
    path = directory / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing landscape source data: {path}")
    return pd.read_csv(path)


def benchmark_landscape() -> pd.DataFrame:
    rows = []
    for filename in BENCHMARK_FILES:
        frame = pd.read_csv(DATASET_ROOT / filename, sep=None, engine="python")
        target = frame.iloc[:, -1]
        classes = target.nunique(dropna=True)
        task = "binary" if classes == 2 else "multiclass"
        rows.append(
            {
                "dataset": Path(filename).stem.replace("-", "_"),
                "samples": len(frame),
                "features": frame.shape[1] - 1,
                "classes": classes,
                "task": task,
            }
        )
    return pd.DataFrame(rows)


def draw_box_flow(axis: plt.Axes, labels: list[str], colors: list[str], title: str) -> None:
    axis.set_xlim(0, 1)
    axis.set_ylim(0, len(labels))
    axis.axis("off")
    for position, (label, color) in enumerate(zip(labels, colors)):
        y = len(labels) - position - 0.5
        axis.text(
            0.5,
            y,
            label,
            ha="center",
            va="center",
            fontsize=9,
            color="white",
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.55", "facecolor": color, "edgecolor": "none"},
        )
        if position < len(labels) - 1:
            axis.annotate(
                "",
                xy=(0.5, y - 0.7),
                xytext=(0.5, y - 0.3),
                arrowprops={"arrowstyle": "->", "color": "#64748B"},
            )
    axis.set_title(title)


def figure_study_design(landscape_dir: Path, output_dir: Path) -> plt.Figure:
    counts = require(landscape_dir, "cohort_counts.csv")
    benchmark = benchmark_landscape()
    source_output = output_dir / "source_data" / "figure_01"
    source_output.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(source_output / "panel_c_benchmark_landscape.csv", index=False)
    counts.to_csv(source_output / "panel_d_cancer_cohort_flow.csv", index=False)

    fig = plt.figure(figsize=(15, 10), constrained_layout=True)
    grid = fig.add_gridspec(2, 6)
    axes = [
        fig.add_subplot(grid[0, :2]),
        fig.add_subplot(grid[0, 2:4]),
        fig.add_subplot(grid[0, 4:]),
        fig.add_subplot(grid[1, :3]),
        fig.add_subplot(grid[1, 3:]),
    ]

    model_families = pd.DataFrame(
        {
            "family": ["Prior-fitted", "Tabular ICL", "AutoML", "Tree/linear"],
            "models": ["TabPFN v2-v3", "TabFM", "AutoGluon", "CatBoost, XGBoost, LightGBM, RF, LR"],
        }
    )
    axes[0].axis("off")
    for position, row in enumerate(model_families.itertuples()):
        y = 0.86 - position * 0.22
        axes[0].text(0.05, y, row.family, fontweight="bold", color=PALETTE[position], transform=axes[0].transAxes)
        axes[0].text(0.38, y, row.models, fontsize=9, transform=axes[0].transAxes)
    axes[0].set_title("Model families")
    model_families.to_csv(source_output / "panel_a_model_families.csv", index=False)

    workflow = ["Raw tables", "Grouped folds", "Train-only selection", "Predictions", "Evidence"]
    draw_box_flow(axes[1], workflow, [PALETTE[0], PALETTE[1], PALETTE[2], PALETTE[3], PALETTE[4]], "Evaluation workflow")
    pd.DataFrame({"order": range(1, len(workflow) + 1), "stage": workflow}).to_csv(source_output / "panel_b_workflow.csv", index=False)

    sns.scatterplot(
        data=benchmark,
        x="samples",
        y="features",
        size="classes",
        hue="task",
        sizes=(50, 180),
        palette={"binary": PALETTE[0], "multiclass": PALETTE[2]},
        ax=axes[2],
    )
    for row in benchmark.itertuples():
        axes[2].annotate(row.dataset, (row.samples, row.features), fontsize=6, xytext=(3, 3), textcoords="offset points")
    axes[2].set(xscale="log", xlabel="Samples", ylabel="Features", title="Engineering benchmark")
    axes[2].legend(frameon=False, fontsize=7)

    long_counts = counts.melt(
        id_vars="cancer",
        value_vars=[column for column in ("n_os_3yr", "n_os_5yr") if column in counts],
        var_name="endpoint",
        value_name="eligible",
    ).dropna()
    sns.barplot(data=long_counts, x="cancer", y="eligible", hue="endpoint", ax=axes[3], palette=[PALETTE[1], PALETTE[4]])
    axes[3].set(xlabel="Cancer cohort", ylabel="Eligible patients", title="Fixed-window cohort flow")
    axes[3].legend(title="", frameon=False)

    axes[4].set_xlim(0, 7)
    axes[4].set_ylim(0, 1)
    axes[4].axis("off")
    axes[4].hlines(0.52, 0, 7, color="#64748B", linewidth=2)
    for year, label in ((0, "Diagnosis"), (3, "3-year"), (5, "5-year")):
        axes[4].vlines(year, 0.42, 0.62, color="#16324F", linewidth=2)
        axes[4].text(year, 0.67, label, ha="center", fontsize=9, fontweight="bold")
    axes[4].text(1.5, 0.30, "Class 1: death by horizon", ha="center", color=PALETTE[3])
    axes[4].text(4.0, 0.18, "Class 0: known survival beyond horizon", ha="center", color=PALETTE[1])
    axes[4].text(4.0, 0.88, "Extreme contrast: death <3 y vs survival >=5 y", ha="center", color=PALETTE[4])
    axes[4].set_title("Outcome definitions")
    pd.DataFrame(
        {
            "endpoint": ["os_3yr", "os_5yr", "extreme_os"],
            "positive": ["death <=1095 d", "death <=1825 d", "death <1095 d"],
            "negative": ["known survival >1095 d", "known survival >1825 d", "alive/censored >=1825 d"],
        }
    ).to_csv(source_output / "panel_e_outcome_definitions.csv", index=False)

    for label, axis in zip("ABCDE", axes):
        panel_label(axis, label)
    fig.suptitle("Study design: benchmark validation and cancer multiomics stress testing", fontsize=16, fontweight="bold")
    return fig


def figure_cancer_landscape(landscape_dir: Path, output_dir: Path) -> plt.Figure:
    counts = require(landscape_dir, "cohort_counts.csv")
    balance = require(landscape_dir, "class_balance.csv")
    km = require(landscape_dir, "kaplan_meier.csv")
    overlap = require(landscape_dir, "selected_feature_overlap.csv")
    modalities = require(landscape_dir, "selected_feature_modalities.csv")
    separability = require(landscape_dir, "cohort_separability.csv")
    source_output = output_dir / "source_data" / "figure_03"
    source_output.mkdir(parents=True, exist_ok=True)
    for filename, frame in {
        "panel_a_cohort_counts.csv": counts,
        "panel_b_modalities.csv": modalities,
        "panel_c_class_balance.csv": balance,
        "panel_d_kaplan_meier.csv": km,
        "panel_e_feature_overlap.csv": overlap,
        "panel_f_cohort_separability.csv": separability,
    }.items():
        frame.to_csv(source_output / filename, index=False)

    fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
    sns.barplot(data=counts, x="cancer", y="n_raw", color="#CBD5E1", ax=axes[0, 0], label="Raw")
    sns.barplot(data=counts, x="cancer", y="n_os_3yr", color=PALETTE[1], ax=axes[0, 0], label="3-year eligible")
    axes[0, 0].set(xlabel="", ylabel="Patients", title="Outcome availability")
    axes[0, 0].legend(frameon=False)

    modality_table = modalities.pivot_table(index="cancer", columns="modality", values="count", fill_value=0)
    sns.heatmap(modality_table, cmap="YlGnBu", annot=True, fmt=".0f", cbar=False, ax=axes[0, 1])
    axes[0, 1].set(xlabel="", ylabel="", title="Selected modality composition")

    balance_plot = balance.copy()
    balance_plot["cohort_endpoint"] = (
        balance_plot["cancer"]
        + "\n"
        + balance_plot["endpoint"].str.replace("os_", "").str.replace("yr", " year")
    )
    sns.barplot(
        data=balance_plot,
        x="cohort_endpoint",
        y="count",
        hue="class",
        errorbar=None,
        ax=axes[0, 2],
        palette=[PALETTE[1], PALETTE[3]],
    )
    axes[0, 2].set(xlabel="", ylabel="Patients", title="Class balance by endpoint")
    axes[0, 2].legend(title="Event class", frameon=False)

    for cancer, group in km.groupby("cancer"):
        axes[1, 0].step(group["time_days"] / 365.0, group["survival"], where="post", label=cancer)
        axes[1, 0].fill_between(group["time_days"] / 365.0, group["ci_low"], group["ci_high"], step="post", alpha=0.08)
    axes[1, 0].set(xlabel="Years", ylabel="Overall survival", ylim=(0, 1.02), title="Observed survival distributions")
    axes[1, 0].legend(frameon=False, fontsize=7)

    overlap_table = overlap.pivot(index="cancer_a", columns="cancer_b", values="jaccard")
    sns.heatmap(overlap_table, vmin=0, vmax=1, cmap="mako", annot=True, fmt=".2f", cbar=False, ax=axes[1, 1])
    axes[1, 1].set(xlabel="", ylabel="", title="Selected-feature Jaccard overlap")

    sep_long = separability.melt(
        id_vars=["control", "n", "folds"],
        value_vars=["accuracy", "balanced_accuracy"],
        var_name="metric",
        value_name="value",
    )
    sns.barplot(data=sep_long, y="control", x="value", hue="metric", ax=axes[1, 2], palette=[PALETTE[2], PALETTE[4]])
    axes[1, 2].set(xlim=(0, 1), xlabel="Cross-validated score", ylabel="", title="Cancer-cohort separability")
    axes[1, 2].legend(title="", frameon=False, fontsize=7)

    for label, axis in zip("ABCDEF", axes.flat):
        panel_label(axis, label)
    fig.suptitle("Cancer cohort landscape and structural heterogeneity", fontsize=16, fontweight="bold")
    return fig


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, formats: Iterable[str], dpi: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for extension in formats:
        fig.savefig(output_dir / f"{stem}.{extension}", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate study-design and cancer-landscape figures.")
    parser.add_argument("--landscape-dir", default=str(DEFAULT_LANDSCAPE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--figures", default="1,3")
    parser.add_argument("--formats", default="png,pdf,svg")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    sns.set_theme(style="whitegrid", context="paper")
    landscape_dir = Path(args.landscape_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    selected = set(item.strip() for item in args.figures.split(",") if item.strip())
    formats = [item.strip() for item in args.formats.split(",") if item.strip()]
    if args.smoke:
        formats = ["png"]
        args.dpi = min(args.dpi, 120)
    if "1" in selected:
        save_figure(figure_study_design(landscape_dir, output_dir), output_dir, "figure_01_study_design", formats, args.dpi)
    if "3" in selected:
        save_figure(figure_cancer_landscape(landscape_dir, output_dir), output_dir, "figure_03_cancer_landscape", formats, args.dpi)
    print(f"Generated figures {sorted(selected)} in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
