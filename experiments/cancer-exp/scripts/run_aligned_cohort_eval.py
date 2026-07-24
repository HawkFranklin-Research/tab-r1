#!/usr/bin/env python3
"""Runs cross-cohort evaluation for all models on aligned and batch-normalized cancer datasets.

Saves raw predictions for TCGA Test and CPTAC Test Set 2 to CSV files,
aggregates metrics, generates a custom color palette, and plots a Nature-style
multi-panel figure (Panels A, B, C, D).
"""

from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, log_loss, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Paths
DATASETS_ROOT = Path("/home/prime/Documents/g3/cancer-exp/datasets_aligned")
OUTPUT_DIR = Path("/home/prime/Documents/g3/cancer-exp/outputs/aligned_cross_cohort")
RUNS_DIR = OUTPUT_DIR / "runs"
RESULTS_DIR = OUTPUT_DIR / "results"
PLOTS_DIR = Path("/home/prime/Documents/g3/cancer-exp/plots")

RUNS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = ["logistic_regression", "random_forest", "xgboost", "lightgbm", "catboost", "autogluon", "tabpfn_v3"]

def generate_custom_palette(seed: int = 42) -> dict[str, str]:
    """Generates a professional publication HSL color palette and maps it to models."""
    random.seed(seed)
    palette = {}
    hues = [20, 60, 120, 180, 240, 280, 325] # Spread out hues
    random.shuffle(hues)
    
    # Let's map specific colors to make them look awesome
    for idx, model in enumerate(MODELS):
        h = hues[idx]
        s = random.randint(65, 80)
        l = random.randint(45, 55)
        # Convert HSL to RGB Hex
        from colorsys import hls_to_rgb
        r, g, b = hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        palette[model] = hex_color

    # Overwrite tabpfn_v3 to a premium deep blue and autogluon to a rich purple
    palette["tabpfn_v3"] = "#1e3a8a"
    palette["autogluon"] = "#7c3aed"
    palette["catboost"] = "#e11d48"
    palette["xgboost"] = "#ea580c"
    palette["lightgbm"] = "#16a34a"
    palette["random_forest"] = "#0d9488"
    palette["logistic_regression"] = "#4b5563"
    
    palette_path = RESULTS_DIR / "color_palette.json"
    palette_path.write_text(json.dumps(palette, indent=2))
    logging.info(f"Custom color palette generated and saved to {palette_path}")
    return palette

def train_and_eval_model_cv(
    model_name: str,
    task_name: str,
    tcga_df: pd.DataFrame,
    cptac_df: pd.DataFrame,
    task_type: str,
    device: str
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Fits the requested model using 5-fold Stratified CV on TCGA and evaluates on CPTAC."""
    X_tcga = tcga_df.drop(columns=["target"])
    y_tcga = tcga_df["target"]
    
    X_cptac = cptac_df.drop(columns=["target"])
    y_cptac = cptac_df["target"]

    estimator = None
    classes = sorted(y_tcga.unique().tolist())
    n_samples_tcga = len(tcga_df)
    n_samples_cptac = len(cptac_df)

    # Arrays to store out-of-fold predictions
    oof_preds = np.zeros(n_samples_tcga, dtype=object) if task_type == "multiclass" else np.zeros(n_samples_tcga)
    oof_probs = np.zeros((n_samples_tcga, len(classes)))

    # Arrays to accumulate CPTAC predictions from each fold
    cptac_probs_accum = np.zeros((n_samples_cptac, len(classes)))

    from sklearn.model_selection import StratifiedKFold, train_test_split
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    fit_times = []
    predict_times = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(X_tcga, y_tcga)):
        logging.info(f"  Fold {fold+1}/5")
        X_tr_all, X_te = X_tcga.iloc[train_idx], X_tcga.iloc[test_idx]
        y_tr_all, y_te = y_tcga.iloc[train_idx], y_tcga.iloc[test_idx]
        
        # Split train into train (60% of original) and val (20% of original)
        X_tr, X_va, y_tr, y_va = train_test_split(
            X_tr_all, y_tr_all, test_size=0.25, random_state=42 + fold, stratify=y_tr_all
        )
        
        # Construct train and val DataFrames (required for AutoGluon)
        train_fold_df = X_tr.copy()
        train_fold_df["target"] = y_tr
        val_fold_df = X_va.copy()
        val_fold_df["target"] = y_va
        
        fit_start = time.perf_counter()
        
        if model_name == "logistic_regression":
            estimator = LogisticRegression(max_iter=1000, random_state=42)
            estimator.fit(X_tr, y_tr)
        elif model_name == "random_forest":
            estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            estimator.fit(X_tr, y_tr)
        elif model_name == "xgboost":
            from xgboost import XGBClassifier
            estimator = XGBClassifier(n_estimators=100, random_state=42)
            if task_type == "multiclass":
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                y_tr_enc = le.fit_transform(y_tr)
                y_va_enc = le.transform(y_va)
                estimator.fit(X_tr, y_tr_enc, eval_set=[(X_va, y_va_enc)], verbose=False)
            else:
                estimator.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
        elif model_name == "lightgbm":
            from lightgbm import LGBMClassifier
            estimator = LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
            estimator.fit(X_tr, y_tr, eval_set=[(X_va, y_va)])
        elif model_name == "catboost":
            from catboost import CatBoostClassifier
            estimator = CatBoostClassifier(n_estimators=100, random_seed=42, verbose=False)
            estimator.fit(X_tr, y_tr, eval_set=[(X_va, y_va)])
        elif model_name == "autogluon":
            from autogluon.tabular import TabularPredictor
            # Unique predictor path per fold
            predictor_path = RUNS_DIR / task_name / f"autogluon_models_fold_{fold}_{model_name}"
            estimator = TabularPredictor(label="target", path=predictor_path, verbosity=0)
            estimator.fit(train_data=train_fold_df, tuning_data=val_fold_df, presets="medium_quality", time_limit=10)
        elif model_name == "tabpfn_v3":
            from tabpfn import TabPFNClassifier
            ckpt_path = "/home/prime/Documents/g3/tab-r1/tabpfn_3/tabpfn-v3-classifier-v3_default.ckpt"
            estimator = TabPFNClassifier(model_path=ckpt_path, device=device)
            estimator.fit(X_tr, y_tr)
            
        fit_times.append(time.perf_counter() - fit_start)
        
        # Predictions
        pred_start = time.perf_counter()
        
        def get_predictions(clf, X_data):
            if model_name == "autogluon":
                preds = clf.predict(X_data)
                probs = clf.predict_proba(X_data)
                return np.asarray(preds), np.asarray(probs)
            elif model_name == "xgboost" and task_type == "multiclass":
                preds_enc = clf.predict(X_data)
                preds = le.inverse_transform(preds_enc)
                probs = clf.predict_proba(X_data)
                return preds, probs
            else:
                preds = clf.predict(X_data)
                probs = clf.predict_proba(X_data) if hasattr(clf, "predict_proba") else None
                return np.asarray(preds), probs

        y_pred_te, y_prob_te = get_predictions(estimator, X_te)
        y_pred_te = np.asarray(y_pred_te).ravel()
        
        y_pred_cptac, y_prob_cptac = get_predictions(estimator, X_cptac)
        
        predict_times.append(time.perf_counter() - pred_start)
        
        # Store out-of-fold predictions
        oof_preds[test_idx] = y_pred_te
        if y_prob_te is not None:
            oof_probs[test_idx] = y_prob_te
            
        # Accumulate CPTAC predicted probabilities
        if y_prob_cptac is not None:
            cptac_probs_accum += y_prob_cptac / 5.0

    # Ensemble prediction on CPTAC
    cptac_preds = np.array([classes[idx] for idx in np.argmax(cptac_probs_accum, axis=1)])

    # Build out-of-fold predictions DataFrame
    oof_df = pd.DataFrame(index=X_tcga.index)
    oof_df["y_true"] = y_tcga.values
    oof_df["y_pred"] = oof_preds
    for idx, cls in enumerate(classes):
        oof_df[f"prob_{cls}"] = oof_probs[:, idx]

    # Build CPTAC predictions DataFrame
    cptac_preds_df = pd.DataFrame(index=X_cptac.index)
    cptac_preds_df["y_true"] = y_cptac.values
    cptac_preds_df["y_pred"] = cptac_preds
    for idx, cls in enumerate(classes):
        cptac_preds_df[f"prob_{cls}"] = cptac_probs_accum[:, idx]

    # Compute metrics
    def calculate_metrics(y_true, y_pred, y_prob):
        metrics = {}
        if task_type == "binary":
            y_t = y_true.astype(int)
            y_p = y_pred.astype(int)
            metrics["accuracy"] = accuracy_score(y_t, y_p)
            metrics["f1"] = f1_score(y_t, y_p, zero_division=0)
            if y_prob is not None:
                metrics["roc_auc"] = roc_auc_score(y_t, y_prob[:, 1])
                metrics["log_loss"] = log_loss(y_t, y_prob)
            else:
                metrics["roc_auc"] = np.nan
                metrics["log_loss"] = np.nan
        else:
            metrics["accuracy"] = accuracy_score(y_true, y_pred)
            metrics["f1"] = f1_score(y_true, y_pred, average="weighted", zero_division=0)
            if y_prob is not None:
                metrics["roc_auc"] = roc_auc_score(y_true, y_prob, multi_class="ovr")
                metrics["log_loss"] = log_loss(y_true, y_prob)
            else:
                metrics["roc_auc"] = np.nan
                metrics["log_loss"] = np.nan
        return metrics

    tcga_metrics = calculate_metrics(y_tcga, oof_preds, oof_probs)
    cptac_metrics = calculate_metrics(y_cptac, cptac_preds, cptac_probs_accum)

    summary_row = {
        "fit_time_s": sum(fit_times),
        "predict_time_s": sum(predict_times),
        "tcga_accuracy": tcga_metrics["accuracy"],
        "tcga_f1": tcga_metrics["f1"],
        "tcga_roc_auc": tcga_metrics["roc_auc"],
        "tcga_log_loss": tcga_metrics["log_loss"],
        "cptac_accuracy": cptac_metrics["accuracy"],
        "cptac_f1": cptac_metrics["f1"],
        "cptac_roc_auc": cptac_metrics["roc_auc"],
        "cptac_log_loss": cptac_metrics["log_loss"]
    }

    return summary_row, oof_df, cptac_preds_df

def run_evaluation() -> None:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Running evaluation using device: {device}")
    
    palette = generate_custom_palette()

    task_dirs = sorted(p for p in DATASETS_ROOT.iterdir() if p.is_dir())
    
    rows = []
    
    for task_path in task_dirs:
        task_name = task_path.name
        logging.info(f"========== Evaluating Task: {task_name} ==========")
        
        # Load datasets
        tcga_df = pd.read_csv(task_path / "tcga_all.csv").set_index("sample_id")
        cptac_df = pd.read_csv(task_path / "cptac_test2.csv").set_index("sample_id")
        
        # Infer task type
        task_type = "binary" if "cancer_type" not in task_name else "multiclass"
        
        for model in MODELS:
            logging.info(f"Running model {model} on {task_name}")
            try:
                metrics, tcga_preds, cptac_preds = train_and_eval_model_cv(
                    model, task_name, tcga_df, cptac_df, task_type, device
                )
                
                # Save predictions
                pred_dir = RUNS_DIR / task_name / "predictions"
                pred_dir.mkdir(parents=True, exist_ok=True)
                
                tcga_preds.to_csv(pred_dir / f"{model}_predictions_tcga_oof.csv", index_label="sample_id")
                cptac_preds.to_csv(pred_dir / f"{model}_predictions_cptac.csv", index_label="sample_id")
                
                row = {
                    "task": task_name,
                    "model": model,
                    "task_type": task_type,
                    "status": "success",
                    **metrics
                }
                rows.append(row)
            except Exception as exc:
                logging.exception(f"Model {model} failed on task {task_name}")
                rows.append({
                    "task": task_name,
                    "model": model,
                    "task_type": task_type,
                    "status": "failed",
                    "error": str(exc)
                })

    # Save summary metrics
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(RESULTS_DIR / "metrics_summary.csv", index=False)
    logging.info(f"Evaluation finished! Metrics summary written to {RESULTS_DIR / 'metrics_summary.csv'}")

def plot_publication_figure() -> None:
    logging.info("Generating Nature-style publication figure")
    metrics_path = RESULTS_DIR / "metrics_summary.csv"
    if not metrics_path.exists():
        logging.error("Metrics summary not found. Run evaluation first.")
        return
        
    df = pd.read_csv(metrics_path)
    df = df[df["status"] == "success"]
    
    # Load color palette
    with open(RESULTS_DIR / "color_palette.json") as f:
        palette = json.load(f)

    # Separate by task type, modality and feature selection
    all_tasks = df["task"].unique()
    
    # Use biological targeted datasets for Panels A, B, and C
    rna_binary_tasks_bio = sorted([t for t in all_tasks if "cancer_type" not in t and "protein" not in t and "biological" in t])
    protein_binary_tasks_bio = sorted([t for t in all_tasks if "cancer_type" not in t and "protein" in t and "biological" in t])
    
    rna_multiclass_tasks_bio = [t for t in all_tasks if "cancer_type" in t and "protein" not in t and "biological" in t]
    protein_multiclass_tasks_bio = [t for t in all_tasks if "cancer_type" in t and "protein" in t and "biological" in t]

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({"font.size": 12, "axes.titlesize": 14, "axes.labelsize": 12})
    
    # Clean model names for legend/display
    df["Model_Display"] = df["model"].str.replace("_", " ").str.title()
    df["Model_Display"] = df["Model_Display"].replace("Tabpfn V3", "TabPFN v3").replace("Autogluon", "AutoGluon")
    clean_palette = {m.replace("_", " ").title().replace("Tabpfn V3", "TabPFN v3").replace("Autogluon", "AutoGluon"): c for m, c in palette.items()}

    # Helper function to clean task names for labels
    def clean_task_label(t):
        val = t.replace("_top500", "").replace("_protein", "").replace("_biological", "").replace("_", " ").upper()
        return val

    # Panel A: RNA-to-RNA mutation prediction (Scenario B) ROC AUC on CPTAC Test Set 2 (Biological Pathway)
    df_rna_bin = df[df["task"].isin(rna_binary_tasks_bio)].sort_values("model")
    ax_a = axes[0, 0]
    sns.barplot(
        data=df_rna_bin,
        x="task",
        y="cptac_roc_auc",
        hue="Model_Display",
        palette=clean_palette,
        ax=ax_a
    )
    ax_a.set_title("A", loc="left", fontweight="bold", fontsize=16)
    ax_a.set_xlabel("Somatic Mutation Task (RNA-to-RNA, Biological Pathway)")
    ax_a.set_ylabel("CPTAC Test Set 2 ROC AUC")
    ax_a.set_xticklabels([clean_task_label(t) for t in rna_binary_tasks_bio])
    ax_a.get_legend().remove()
    ax_a.set_ylim(0.3, 1.05)

    # Panel B: RNA-to-Protein cross-modal mutation prediction (Scenario C) ROC AUC on CPTAC Test Set 2 (Biological Pathway)
    df_prot_bin = df[df["task"].isin(protein_binary_tasks_bio)].sort_values("model")
    ax_b = axes[0, 1]
    sns.barplot(
        data=df_prot_bin,
        x="task",
        y="cptac_roc_auc",
        hue="Model_Display",
        palette=clean_palette,
        ax=ax_b
    )
    ax_b.set_title("B", loc="left", fontweight="bold", fontsize=16)
    ax_b.set_xlabel("Somatic Mutation Task (RNA-to-Protein, Biological Pathway)")
    ax_b.set_ylabel("CPTAC Test Set 2 ROC AUC")
    ax_b.set_xticklabels([clean_task_label(t) for t in protein_binary_tasks_bio])
    ax_b.legend(title="Model", bbox_to_anchor=(1.05, 1.0), loc="upper left")
    ax_b.set_ylim(0.3, 1.05)

    # Panel C: Multiclass cancer type prediction accuracy on CPTAC Test Set 2 (Biological Pathway, comparing modalities)
    ax_c = axes[1, 0]
    df_multi = df[df["task"].isin(rna_multiclass_tasks_bio + protein_multiclass_tasks_bio)].copy()
    df_multi["Modality"] = df_multi["task"].apply(lambda t: "RNA-to-Protein" if "protein" in t else "RNA-to-RNA")
    
    sns.barplot(
        data=df_multi.sort_values("model"),
        x="Modality",
        y="cptac_accuracy",
        hue="Model_Display",
        palette=clean_palette,
        ax=ax_c
    )
    ax_c.set_title("C", loc="left", fontweight="bold", fontsize=16)
    ax_c.set_xlabel("Classification Modality (Biological Pathway)")
    ax_c.set_ylabel("CPTAC Test Set 2 Accuracy")
    ax_c.get_legend().remove()
    ax_c.set_ylim(0.5, 1.05)

    # Panel D: Generalization Performance Boxplot (Distribution of ROC AUC comparing Unsupervised vs. Biological)
    ax_d = axes[1, 1]
    binary_tasks = [t for t in all_tasks if "cancer_type" not in t]
    df_bin_all = df[df["task"].isin(binary_tasks)].copy()
    df_bin_all["Feature_Selection"] = df_bin_all["task"].apply(lambda t: "Biological" if "biological" in t else "Unsupervised (Top 500)")
    
    sns.boxplot(
        data=df_bin_all.sort_values("model"),
        x="Model_Display",
        y="cptac_roc_auc",
        hue="Feature_Selection",
        palette={"Unsupervised (Top 500)": "#9ca3af", "Biological": "#2563eb"},
        ax=ax_d
    )
    ax_d.set_title("D", loc="left", fontweight="bold", fontsize=16)
    ax_d.set_xlabel("Model")
    ax_d.set_ylabel("CPTAC Test Set 2 ROC AUC")
    ax_d.set_xticklabels(ax_d.get_xticklabels(), rotation=30, ha="right")
    ax_d.legend(title="Feature Selection", loc="lower left")

    # Clean up layout
    plt.tight_layout()
    
    # Save plots
    fig.savefig(PLOTS_DIR / "publication_figure_cancer.png", dpi=300, bbox_inches="tight")
    fig.savefig(PLOTS_DIR / "publication_figure_cancer.pdf", bbox_inches="tight")
    plt.close(fig)
    logging.info(f"Nature-style publication figure generated at {PLOTS_DIR / 'publication_figure_cancer.png'}")

def main():
    run_evaluation()
    plot_publication_figure()

if __name__ == "__main__":
    main()
