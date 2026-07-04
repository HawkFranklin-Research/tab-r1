from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score


PRED_ROOT = Path("/home/prime/Documents/g3/cancer-exp/outputs/all_splits_predictions_top100")
OUT_DIR = Path("/home/prime/Documents/g3/cancer-exp/plots/publication_suite")
REPORT_DIR = Path("/home/prime/Documents/g3/cancer-exp/reports")


VERSION_ORDER = ["tabpfn_v1", "tabpfn_v2", "tabpfn_v2_5", "tabpfn_v2_6", "tabpfn_v3"]
VERSION_LABELS = {
    "tabpfn_v1": "TabPFN v1",
    "tabpfn_v2": "TabPFN v2",
    "tabpfn_v2_5": "TabPFN v2.5",
    "tabpfn_v2_6": "TabPFN v2.6",
    "tabpfn_v3": "TabPFN v3",
}
SPLIT_ORDER = ["train", "val", "test"]

PALETTE = {
    "tabpfn_v1": "#6F777D",
    "tabpfn_v2": "#167A72",
    "tabpfn_v2_5": "#2E6F9E",
    "tabpfn_v2_6": "#D89C33",
    "tabpfn_v3": "#B75D43",
}
TASK_PALETTE = {
    "cancer_type": "#7A3E48",
    "os_event": "#2E6F9E",
    "source": "#167A72",
}


def task_family(dataset: str) -> str:
    if "source" in dataset:
        return "source"
    if "os_event" in dataset:
        return "os_event"
    if "cancer_type" in dataset:
        return "cancer_type"
    return "other"


def cancer_name(dataset: str) -> str:
    if dataset.startswith("ALL_"):
        return "ALL"
    return dataset.split("_", 1)[0]


def configure_style() -> None:
    sns.set_theme(
        context="paper",
        style="whitegrid",
        rc={
            "figure.dpi": 160,
            "savefig.dpi": 450,
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#23343B",
            "axes.labelcolor": "#23343B",
            "xtick.color": "#23343B",
            "ytick.color": "#23343B",
            "text.color": "#23343B",
            "grid.color": "#E1DED6",
            "axes.facecolor": "#FBFAF6",
            "figure.facecolor": "#FBFAF6",
        },
    )
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42


def prob_cols(df: pd.DataFrame) -> list[str]:
    return [col for col in df.columns if col.startswith("prob_") and not df[col].isna().all()]


def normalize_label(value: object) -> str:
    if pd.isna(value):
        return "nan"
    text = str(value).strip().lower()
    if text.endswith(".0"):
        try:
            return str(int(float(text)))
        except Exception:
            return text
    return text


def true_positive_probability(df: pd.DataFrame) -> pd.Series:
    cols = prob_cols(df)
    if not cols:
        return pd.Series(np.nan, index=df.index)
    lookup = {col.replace("prob_", ""): col for col in cols}
    values = []
    for _, row in df.iterrows():
        key = normalize_label(row["y_true"])
        values.append(row[lookup[key]] if key in lookup else np.nan)
    return pd.Series(values, index=df.index, dtype=float)


def binary_positive_probability(df: pd.DataFrame) -> pd.Series | None:
    cols = prob_cols(df)
    if len(cols) != 2:
        return None
    labels = df[["y_true", "y_true_encoded"]].drop_duplicates().sort_values("y_true_encoded")
    if len(labels) != 2:
        return None
    positive_label = normalize_label(labels.iloc[-1]["y_true"])
    col = f"prob_{positive_label}"
    if col not in df.columns:
        return None
    return df[col].astype(float)


def load_predictions() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(PRED_ROOT.glob("*/*/all_samples_predictions.csv")):
        df = pd.read_csv(path)
        df["task_family"] = df["dataset"].map(task_family)
        df["cancer"] = df["dataset"].map(cancer_name)
        df["model_label"] = df["model_name"].map(VERSION_LABELS)
        cols = prob_cols(df)
        df["confidence"] = df[cols].max(axis=1) if cols else np.nan
        df["true_label_probability"] = true_positive_probability(df)
        df["correct"] = df["y_true"].astype(str) == df["y_pred"].astype(str)
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"No all_samples_predictions.csv files found under {PRED_ROOT}")
    return pd.concat(frames, ignore_index=True)


def compute_metrics(pred: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (dataset, model_name, split), group in pred.groupby(["dataset", "model_name", "split"], sort=False):
        y_true = group["y_true_encoded"].to_numpy()
        y_pred = group["y_pred_encoded"].to_numpy()
        n_classes = len(np.unique(y_true))
        average = "binary" if n_classes == 2 else "weighted"
        try:
            f1 = f1_score(y_true, y_pred, average=average, zero_division=0)
        except Exception:
            f1 = np.nan
        auc_value = np.nan
        pos_prob = binary_positive_probability(group)
        if pos_prob is not None:
            try:
                auc_value = roc_auc_score(y_true, pos_prob)
            except Exception:
                auc_value = np.nan
        elif n_classes > 2:
            cols = prob_cols(group)
            try:
                auc_value = roc_auc_score(y_true, group[cols].to_numpy(), multi_class="ovr", average="weighted")
            except Exception:
                auc_value = np.nan
        rows.append(
            {
                "dataset": dataset,
                "task_family": task_family(dataset),
                "cancer": cancer_name(dataset),
                "model_name": model_name,
                "model_label": VERSION_LABELS.get(model_name, model_name),
                "split": split,
                "accuracy": accuracy_score(y_true, y_pred),
                "f1": f1,
                "roc_auc": auc_value,
                "mean_confidence": group["confidence"].mean(),
                "mean_true_label_probability": group["true_label_probability"].mean(),
                "n": len(group),
            }
        )
    metrics = pd.DataFrame(rows)
    metrics["model_name"] = pd.Categorical(metrics["model_name"], VERSION_ORDER, ordered=True)
    metrics["split"] = pd.Categorical(metrics["split"], SPLIT_ORDER, ordered=True)
    return metrics.sort_values(["dataset", "model_name", "split"])


def save_figure(fig: mpl.figure.Figure, stem: str) -> list[str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ["png", "pdf", "svg"]:
        path = OUT_DIR / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
        paths.append(str(path))
    plt.close(fig)
    return paths


def annotate_panel(ax: plt.Axes, label: str) -> None:
    ax.text(-0.08, 1.06, label, transform=ax.transAxes, fontsize=13, fontweight="bold", va="top", ha="left")


def plot_metric_atlas(metrics: pd.DataFrame) -> list[str]:
    test = metrics[metrics["split"] == "test"].copy()
    task_order = ["cancer_type", "source", "os_event"]
    metric_names = ["accuracy", "f1", "roc_auc", "mean_confidence"]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5))
    for ax, metric, panel in zip(axes.ravel(), metric_names, ["A", "B", "C", "D"]):
        summary = test.groupby(["task_family", "model_name"], observed=True)[metric].mean().reset_index()
        sns.barplot(
            data=summary,
            x="task_family",
            y=metric,
            hue="model_name",
            order=task_order,
            hue_order=VERSION_ORDER,
            palette=PALETTE,
            ax=ax,
            edgecolor="#23343B",
            linewidth=0.35,
        )
        ax.set_xlabel("")
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.set_ylim(0, 1.04 if metric != "mean_confidence" else 1.0)
        ax.legend_.remove()
        annotate_panel(ax, panel)
    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    fig.legend(handles, [VERSION_LABELS.get(label, label) for label in labels], loc="lower center", ncol=5, frameon=False)
    fig.suptitle("TabPFN generation atlas across cancer multiomics tasks", fontsize=16, y=0.99)
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    return save_figure(fig, "figure_01_generation_metric_atlas")


def plot_generalization_gap(metrics: pd.DataFrame) -> list[str]:
    pivot = metrics.pivot_table(index=["dataset", "task_family", "model_name"], columns="split", values="accuracy", observed=True).reset_index()
    pivot["train_test_gap"] = pivot["train"] - pivot["test"]
    gap = pivot.pivot(index="dataset", columns="model_name", values="train_test_gap").loc[:, VERSION_ORDER]
    fig, ax = plt.subplots(figsize=(9.8, 6.8))
    sns.heatmap(
        gap,
        cmap=sns.diverging_palette(220, 25, s=85, l=45, as_cmap=True),
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.6,
        linecolor="#F3EFE2",
        cbar_kws={"label": "Train accuracy - test accuracy"},
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([VERSION_LABELS.get(str(t.get_text()), str(t.get_text())) for t in ax.get_xticklabels()], rotation=30, ha="right")
    ax.set_title("Generalization gap: where memorization appears")
    return save_figure(fig, "figure_02_generalization_gap_heatmap")


def plot_confidence_correctness(pred: pd.DataFrame) -> list[str]:
    test = pred[pred["split"] == "test"].copy()
    test["correctness"] = np.where(test["correct"], "Correct", "Incorrect")
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8), sharey=True)
    for ax, task, panel in zip(axes, ["cancer_type", "source", "os_event"], ["A", "B", "C"]):
        subset = test[test["task_family"] == task]
        sns.violinplot(
            data=subset,
            x="model_name",
            y="confidence",
            hue="correctness",
            order=VERSION_ORDER,
            split=True,
            inner=None,
            palette={"Correct": "#167A72", "Incorrect": "#B75D43"},
            linewidth=0.6,
            cut=0,
            ax=ax,
        )
        sns.stripplot(
            data=subset.sample(min(len(subset), 1200), random_state=42),
            x="model_name",
            y="confidence",
            order=VERSION_ORDER,
            color="#23343B",
            alpha=0.12,
            size=1.2,
            jitter=0.25,
            ax=ax,
        )
        ax.set_title(task.replace("_", " ").title())
        ax.set_xlabel("")
        ax.set_xticklabels([VERSION_LABELS[x].replace("TabPFN ", "") for x in VERSION_ORDER], rotation=35, ha="right")
        ax.set_ylabel("Prediction confidence" if ax is axes[0] else "")
        annotate_panel(ax, panel)
        if ax.legend_:
            ax.legend_.remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles[:2], labels[:2], loc="lower center", ncol=2, frameon=False)
    fig.suptitle("Confidence distributions reveal overconfidence and uncertainty", fontsize=16)
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    return save_figure(fig, "figure_03_confidence_correctness_violin")


def calibration_table(pred: pd.DataFrame) -> pd.DataFrame:
    rows = []
    binary = pred[(pred["split"] == "test") & (pred["task_family"].isin(["source", "os_event"]))].copy()
    for (task, model_name), group in binary.groupby(["task_family", "model_name"], observed=True):
        pos_prob = binary_positive_probability(group)
        if pos_prob is None:
            continue
        temp = group.copy()
        temp["positive_probability"] = pos_prob.to_numpy()
        temp["bin"] = pd.cut(temp["positive_probability"], bins=np.linspace(0, 1, 11), include_lowest=True)
        for interval, b in temp.groupby("bin", observed=True):
            rows.append(
                {
                    "task_family": task,
                    "model_name": model_name,
                    "bin_center": float(b["positive_probability"].mean()),
                    "observed_positive_rate": float(b["y_true_encoded"].mean()),
                    "n": len(b),
                }
            )
    return pd.DataFrame(rows)


def plot_calibration(pred: pd.DataFrame) -> list[str]:
    cal = calibration_table(pred)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharex=True, sharey=True)
    for ax, task, panel in zip(axes, ["source", "os_event"], ["A", "B"]):
        subset = cal[cal["task_family"] == task]
        for model in VERSION_ORDER:
            s = subset[subset["model_name"] == model]
            ax.plot(s["bin_center"], s["observed_positive_rate"], marker="o", linewidth=1.8, markersize=4, color=PALETTE[model], label=VERSION_LABELS[model])
        ax.plot([0, 1], [0, 1], "--", color="#23343B", linewidth=1, alpha=0.65)
        ax.set_title(task.replace("_", " ").title())
        ax.set_xlabel("Predicted positive probability")
        ax.set_ylabel("Observed positive rate" if ax is axes[0] else "")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        annotate_panel(ax, panel)
    axes[1].legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.suptitle("Calibration curves on held-out test samples", fontsize=16)
    fig.tight_layout()
    cal.to_csv(OUT_DIR / "calibration_points.csv", index=False)
    return save_figure(fig, "figure_04_binary_calibration_curves")


def plot_cancer_confusions(pred: pd.DataFrame) -> list[str]:
    test = pred[(pred["split"] == "test") & (pred["task_family"] == "cancer_type")].copy()
    labels = ["BRCA", "ESCA", "HNSCC", "LSCC", "LUAD"]
    fig, axes = plt.subplots(1, 5, figsize=(18, 4.1), sharey=True)
    for ax, model in zip(axes, VERSION_ORDER):
        subset = test[test["model_name"] == model]
        cm = confusion_matrix(subset["y_true"], subset["y_pred"], labels=labels, normalize="true")
        sns.heatmap(
            cm,
            cmap=sns.light_palette(PALETTE[model], as_cmap=True),
            vmin=0,
            vmax=1,
            annot=True,
            fmt=".2f",
            square=True,
            linewidths=0.5,
            linecolor="#F3EFE2",
            cbar=False,
            xticklabels=labels,
            yticklabels=labels,
            ax=ax,
        )
        ax.set_title(VERSION_LABELS[model])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True" if ax is axes[0] else "")
        ax.tick_params(axis="x", rotation=45)
    fig.suptitle("Cancer-type confusion matrices across TabPFN generations", fontsize=16)
    fig.tight_layout()
    return save_figure(fig, "figure_05_cancer_type_confusion_small_multiples")


def plot_source_warning(metrics: pd.DataFrame) -> list[str]:
    test = metrics[(metrics["split"] == "test") & (metrics["task_family"] == "source")].copy()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    sns.stripplot(
        data=test,
        x="cancer",
        y="roc_auc",
        hue="model_name",
        hue_order=VERSION_ORDER,
        palette=PALETTE,
        dodge=True,
        jitter=0.08,
        size=8,
        edgecolor="#23343B",
        linewidth=0.5,
        ax=ax,
    )
    ax.axhline(0.5, color="#23343B", linestyle="--", linewidth=1, alpha=0.6)
    ax.axhspan(0.95, 1.005, color="#B75D43", alpha=0.08, zorder=0)
    ax.set_ylim(0.45, 1.02)
    ax.set_xlabel("")
    ax.set_ylabel("Source prediction ROC AUC")
    ax.set_title("Residual source signal is almost perfectly recoverable")
    ax.legend(title="", frameon=False, ncol=3, bbox_to_anchor=(0.5, -0.16), loc="upper center")
    return save_figure(fig, "figure_06_source_signal_warning")


def plot_os_event_focus(metrics: pd.DataFrame) -> list[str]:
    test = metrics[(metrics["split"] == "test") & (metrics["task_family"] == "os_event")].copy()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharex=True)
    sns.lineplot(
        data=test,
        x="cancer",
        y="roc_auc",
        hue="model_name",
        hue_order=VERSION_ORDER,
        palette=PALETTE,
        marker="o",
        linewidth=2,
        ax=axes[0],
    )
    sns.lineplot(
        data=test,
        x="cancer",
        y="f1",
        hue="model_name",
        hue_order=VERSION_ORDER,
        palette=PALETTE,
        marker="o",
        linewidth=2,
        ax=axes[1],
    )
    for ax, title, panel in zip(axes, ["Discrimination", "Event-class recovery"], ["A", "B"]):
        ax.axhline(0.5 if title == "Discrimination" else 0, color="#23343B", linestyle="--", linewidth=1, alpha=0.5)
        ax.set_title(title)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=25)
        annotate_panel(ax, panel)
    axes[0].set_ylabel("ROC AUC")
    axes[1].set_ylabel("F1")
    axes[0].legend_.remove()
    axes[1].legend(title="", frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.suptitle("OS-event prediction remains weak after multiomics feature selection", fontsize=16)
    fig.tight_layout()
    return save_figure(fig, "figure_07_os_event_failure_modes")


def plot_probability_ternary_surrogate(pred: pd.DataFrame) -> list[str]:
    test = pred[(pred["split"] == "test") & (pred["task_family"] == "cancer_type")].copy()
    # Use the three highest-level axes to make a compact probability simplex surrogate.
    x_col, y_col, size_col = "prob_brca", "prob_hnscc", "prob_luad"
    fig, axes = plt.subplots(1, 5, figsize=(17.5, 4), sharex=True, sharey=True)
    for ax, model in zip(axes, VERSION_ORDER):
        subset = test[test["model_name"] == model]
        sns.scatterplot(
            data=subset,
            x=x_col,
            y=y_col,
            hue="y_true",
            size=size_col,
            sizes=(8, 70),
            palette={"BRCA": "#7A3E48", "ESCA": "#D89C33", "HNSCC": "#167A72", "LSCC": "#2E6F9E", "LUAD": "#8EA86C"},
            alpha=0.72,
            linewidth=0,
            legend=False,
            ax=ax,
        )
        ax.set_title(VERSION_LABELS[model])
        ax.set_xlabel("P(BRCA)")
        ax.set_ylabel("P(HNSCC)" if ax is axes[0] else "")
    fig.suptitle("Cancer-type probability geometry on held-out samples", fontsize=16)
    fig.tight_layout()
    return save_figure(fig, "figure_08_cancer_probability_geometry")


def main() -> int:
    configure_style()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pred = load_predictions()
    metrics = compute_metrics(pred)
    metrics.to_csv(OUT_DIR / "split_level_metrics.csv", index=False)

    plot_paths: list[str] = []
    plot_paths.extend(plot_metric_atlas(metrics))
    plot_paths.extend(plot_generalization_gap(metrics))
    plot_paths.extend(plot_confidence_correctness(pred))
    plot_paths.extend(plot_calibration(pred))
    plot_paths.extend(plot_cancer_confusions(pred))
    plot_paths.extend(plot_source_warning(metrics))
    plot_paths.extend(plot_os_event_focus(metrics))
    plot_paths.extend(plot_probability_ternary_surrogate(pred))

    manifest = {
        "input_root": str(PRED_ROOT),
        "output_dir": str(OUT_DIR),
        "plots": plot_paths,
        "metrics": str(OUT_DIR / "split_level_metrics.csv"),
        "palette": {
            "name": "Cancer-exp editorial palette",
            "versions": PALETTE,
            "tasks": TASK_PALETTE,
            "background": "#FBFAF6",
            "ink": "#23343B",
        },
    }
    (OUT_DIR / "publication_plot_manifest.json").write_text(json.dumps(manifest, indent=2))

    report = [
        "# Cancer-Exp Publication Plot Suite",
        "",
        f"- Input predictions: `{PRED_ROOT}`",
        f"- Output directory: `{OUT_DIR}`",
        "- Style: custom editorial palette using seaborn/matplotlib.",
        "- Formats: PNG, PDF, and SVG for each figure.",
        "",
        "## Figures",
        "",
    ]
    for path in plot_paths:
        if path.endswith(".png"):
            report.append(f"- `{path}`")
    (REPORT_DIR / "publication_plot_suite.md").write_text("\n".join(report) + "\n")
    print(json.dumps({"figures_png": len([p for p in plot_paths if p.endswith('.png')]), "manifest": str(OUT_DIR / "publication_plot_manifest.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
