from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "paper" / "tables" / "source_data"
DEFAULT_OUTPUT = ROOT / "paper" / "figures" / "evidence"
CANCER_ROOT = ROOT / "cancer-os-exp"
COLORS = {
    "tabpfn_v2": "#386FA4",
    "tabpfn_v2_5": "#1B998B",
    "tabpfn_v2_6": "#D9903D",
    "tabpfn_v3": "#C44536",
    "tabfm_default": "#6D597A",
    "prevalence_only": "#9CA3AF",
    "cancer_identity_only": "#D1495B",
    "source_identity_only": "#EDA55D",
    "cancer_and_source_only": "#A23E48",
    "structural_zero_pattern": "#00798C",
    "linear_molecular": "#30638E",
}


def require(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Required source table is missing: {path}. Run the corresponding analysis utility first."
        )
    return pd.read_csv(path)


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(-0.12, 1.08, label, transform=axis.transAxes, fontsize=14, fontweight="bold", va="top")


def display_name(value: str) -> str:
    names = {
        "tabpfn_v2": "TabPFN v2",
        "tabpfn_v2_5": "TabPFN v2.5",
        "tabpfn_v2_6": "TabPFN v2.6",
        "tabpfn_v3": "TabPFN v3",
        "tabfm_default": "TabFM",
        "prevalence_only": "Prevalence",
        "cancer_identity_only": "Cancer identity",
        "source_identity_only": "Source identity",
        "cancer_and_source_only": "Cancer + source",
        "structural_zero_pattern": "Zero pattern",
        "linear_molecular": "Linear molecular",
    }
    return names.get(value, value.replace("_", " ").title())


def endpoint_name(value: str) -> str:
    return {"os_3yr": "3-year OS", "os_5yr": "5-year OS", "extreme_os": "Extreme OS"}.get(
        value, value
    )


def save_panel_data(frame: pd.DataFrame, directory: Path, filename: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_csv(directory / filename, index=False)


def forest_panel(axis: plt.Axes, frame: pd.DataFrame, metric: str, title: str) -> None:
    plot = frame.copy().reset_index(drop=True)
    labels = [f"{endpoint_name(row.endpoint)} | {display_name(row.model_name)}" for row in plot.itertuples()]
    positions = np.arange(len(plot))
    values = plot[metric].to_numpy(dtype=float)
    lower = plot[f"{metric}_ci_low"].to_numpy(dtype=float)
    upper = plot[f"{metric}_ci_high"].to_numpy(dtype=float)
    colors = [COLORS.get(name, "#4B5563") for name in plot["model_name"]]
    axis.errorbar(values, positions, xerr=[values - lower, upper - values], fmt="none", ecolor="#6B7280", capsize=2)
    axis.scatter(values, positions, c=colors, s=42, zorder=3, edgecolor="white", linewidth=0.6)
    axis.axvline(0.5, color="#6B7280", linestyle="--", linewidth=1)
    axis.set_yticks(positions, labels, fontsize=7)
    axis.set_xlim(0, 1)
    axis.set_xlabel(title)
    axis.invert_yaxis()


def figure_survival(source_dir: Path, output_dir: Path) -> plt.Figure:
    intervals = require(source_dir / "cancer_saved_prediction_bootstrap_intervals.csv")
    predictions = require(source_dir / "cancer_saved_prediction_index.csv")
    metrics = require(source_dir / "cancer_existing_model_metrics.csv")
    source_output = output_dir / "source_data" / "figure_04"

    fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
    forest_panel(axes[0, 0], intervals, "roc_auc", "ROC AUC (95% bootstrap CI)")
    forest_panel(axes[0, 1], intervals, "pr_auc", "PR AUC (95% bootstrap CI)")
    save_panel_data(intervals, source_output, "panels_a_b_bootstrap_intervals.csv")

    roc_rows: list[dict[str, float | str]] = []
    pr_rows: list[dict[str, float | str]] = []
    calibration_rows: list[dict[str, float | str]] = []
    for (endpoint, model), group in predictions.groupby(["endpoint", "model_name"]):
        y_true = group["y_true"].to_numpy(dtype=int)
        probability = group["probability"].to_numpy(dtype=float)
        fpr, tpr, _ = roc_curve(y_true, probability)
        precision, recall, _ = precision_recall_curve(y_true, probability)
        observed, predicted = calibration_curve(y_true, probability, n_bins=8, strategy="quantile")
        label = f"{endpoint_name(endpoint)} | {display_name(model)}"
        color = COLORS.get(model, "#4B5563")
        axes[0, 2].plot(fpr, tpr, color=color, linewidth=1.7, alpha=0.9, label=label)
        axes[1, 0].plot(recall, precision, color=color, linewidth=1.7, alpha=0.9, label=label)
        axes[1, 1].plot(predicted, observed, marker="o", color=color, linewidth=1.5, label=label)
        roc_rows.extend({"endpoint": endpoint, "model_name": model, "fpr": x, "tpr": y} for x, y in zip(fpr, tpr))
        pr_rows.extend(
            {"endpoint": endpoint, "model_name": model, "recall": x, "precision": y}
            for x, y in zip(recall, precision)
        )
        calibration_rows.extend(
            {"endpoint": endpoint, "model_name": model, "mean_predicted": x, "observed": y}
            for x, y in zip(predicted, observed)
        )
    axes[0, 2].plot([0, 1], [0, 1], linestyle="--", color="#6B7280", linewidth=1)
    axes[0, 2].set(xlabel="False-positive rate", ylabel="True-positive rate", title="Saved test predictions")
    axes[0, 2].legend(fontsize=6, frameon=False)
    axes[1, 0].set(xlabel="Recall", ylabel="Precision", title="Precision-recall curves")
    axes[1, 0].legend(fontsize=6, frameon=False)
    axes[1, 1].plot([0, 1], [0, 1], linestyle="--", color="#6B7280", linewidth=1)
    axes[1, 1].set(xlabel="Mean predicted risk", ylabel="Observed event rate", title="Calibration")
    save_panel_data(pd.DataFrame(roc_rows), source_output, "panel_c_roc_curves.csv")
    save_panel_data(pd.DataFrame(pr_rows), source_output, "panel_d_pr_curves.csv")
    save_panel_data(pd.DataFrame(calibration_rows), source_output, "panel_e_calibration.csv")

    operating = metrics[["endpoint", "model_name", "sensitivity", "specificity"]].dropna().copy()
    operating = operating.groupby(["endpoint", "model_name"], as_index=False)[["sensitivity", "specificity"]].mean()
    long = operating.melt(
        id_vars=["endpoint", "model_name"],
        value_vars=["sensitivity", "specificity"],
        var_name="measure",
        value_name="value",
    )
    long["label"] = long["endpoint"].map(endpoint_name) + " | " + long["model_name"].map(display_name)
    sns.barplot(data=long, y="label", x="value", hue="measure", ax=axes[1, 2], palette=["#D1495B", "#00798C"])
    axes[1, 2].set(xlim=(0, 1), xlabel="Rate at stored threshold", ylabel="", title="Operating characteristics")
    axes[1, 2].legend(title="", frameon=False, fontsize=7)
    save_panel_data(long, source_output, "panel_f_operating_characteristics.csv")

    for label, axis in zip("ABCDEF", axes.flat):
        panel_label(axis, label)
    fig.suptitle("Cancer survival classification from immutable test predictions", fontsize=16, fontweight="bold")
    return fig


def pivot_heatmap(axis: plt.Axes, frame: pd.DataFrame, value: str, title: str) -> pd.DataFrame:
    table = frame.pivot_table(index="partition_value", columns="control", values=value, aggfunc="mean")
    sns.heatmap(table, vmin=0, vmax=1, cmap="crest", annot=True, fmt=".2f", cbar=False, ax=axis)
    axis.set(xlabel="", ylabel="Held-out cohort", title=title)
    axis.set_xticklabels([display_name(item.get_text()) for item in axis.get_xticklabels()], rotation=25, ha="right")
    return table.reset_index()


def figure_confounding(source_dir: Path, stress_source_dir: Path, output_dir: Path) -> plt.Figure:
    controls = require(source_dir / "cancer_shortcut_control_metrics.csv")
    held_out = require(stress_source_dir / "cancer_cohort_held_out_metrics.csv")
    permutations = require(stress_source_dir / "cancer_label_permutation_metrics.csv")
    intervals = require(source_dir / "cancer_saved_prediction_bootstrap_intervals.csv")
    source_output = output_dir / "source_data" / "figure_05"
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)

    controls = controls.copy()
    controls["control_label"] = controls["control"].map(display_name)
    label_palette = {display_name(name): color for name, color in COLORS.items()}
    order = controls.groupby("control_label")["roc_auc"].mean().sort_values().index
    sns.barplot(
        data=controls,
        y="control_label",
        x="roc_auc",
        order=order,
        hue="control_label",
        legend=False,
        ax=axes[0, 0],
        palette=label_palette,
    )
    axes[0, 0].axvline(0.5, color="#6B7280", linestyle="--", linewidth=1)
    axes[0, 0].set(xlim=(0, 1), xlabel="ROC AUC", ylabel="", title="Shortcut controls")
    sns.barplot(
        data=controls,
        y="control_label",
        x="pr_auc",
        order=order,
        hue="control_label",
        legend=False,
        ax=axes[0, 1],
        palette=label_palette,
    )
    axes[0, 1].set(xlim=(0, 1), xlabel="PR AUC", ylabel="", title="Imbalance-aware performance")
    save_panel_data(controls, source_output, "panels_a_b_shortcut_controls.csv")

    cancer_held = held_out.loc[held_out["partition_type"].eq("leave_one_cancer_out")]
    source_held = held_out.loc[held_out["partition_type"].eq("leave_one_source_out")]
    table_c = pivot_heatmap(axes[0, 2], cancer_held, "roc_auc", "Leave-one-cancer-out ROC AUC")
    table_d = pivot_heatmap(axes[1, 0], source_held, "roc_auc", "Leave-one-source-out ROC AUC")
    save_panel_data(table_c, source_output, "panel_c_leave_one_cancer_out.csv")
    save_panel_data(table_d, source_output, "panel_d_leave_one_source_out.csv")

    sns.violinplot(data=permutations, x="permutation", y="roc_auc", hue="permutation", legend=False, inner="box", ax=axes[1, 1], palette="Set2")
    axes[1, 1].axhline(0.5, color="#6B7280", linestyle="--", linewidth=1)
    axes[1, 1].set(xlabel="Label permutation", ylabel="ROC AUC", title="Permutation null distributions")
    save_panel_data(permutations, source_output, "panel_e_permutation_null.csv")

    model_comparison = intervals[["endpoint", "model_name", "roc_auc"]].rename(columns={"model_name": "method"})
    control_comparison = controls[["endpoint", "control", "roc_auc"]].rename(columns={"control": "method"})
    comparison = pd.concat([model_comparison, control_comparison], ignore_index=True)
    comparison["method_label"] = comparison["method"].map(display_name)
    sns.barplot(data=comparison, x="roc_auc", y="method_label", hue="endpoint", ax=axes[1, 2], palette="mako")
    axes[1, 2].axvline(0.5, color="#6B7280", linestyle="--", linewidth=1)
    axes[1, 2].set(xlim=(0, 1), xlabel="ROC AUC", ylabel="", title="Models versus shortcuts")
    axes[1, 2].legend(title="Endpoint", frameon=False, fontsize=7)
    save_panel_data(comparison, source_output, "panel_f_models_versus_shortcuts.csv")

    for label, axis in zip("ABCDEF", axes.flat):
        panel_label(axis, label)
    fig.suptitle("Cohort identity and structural confounding stress tests", fontsize=16, fontweight="bold")
    return fig


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, formats: Iterable[str], dpi: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for extension in formats:
        fig.savefig(output_dir / f"{stem}.{extension}", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate evidence-linked manuscript figures without simulated data.")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE))
    parser.add_argument("--stress-source-dir", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--figures", default="4,5")
    parser.add_argument("--formats", default="png,pdf,svg")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.0)
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
    source_dir = Path(args.source_dir).expanduser().resolve()
    stress_source = Path(args.stress_source_dir).expanduser().resolve() if args.stress_source_dir else source_dir
    output_dir = Path(args.output_dir).expanduser().resolve()
    formats = [item.strip() for item in args.formats.split(",") if item.strip()]
    if args.smoke:
        formats = ["png"]
        args.dpi = min(args.dpi, 120)
    selected = {item.strip() for item in args.figures.split(",") if item.strip()}
    if "4" in selected:
        save_figure(figure_survival(source_dir, output_dir), output_dir, "figure_04_survival_prediction", formats, args.dpi)
    if "5" in selected:
        save_figure(
            figure_confounding(source_dir, stress_source, output_dir),
            output_dir,
            "figure_05_confounding_stress_tests",
            formats,
            args.dpi,
        )
    print(f"Generated figures {sorted(selected)} in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
