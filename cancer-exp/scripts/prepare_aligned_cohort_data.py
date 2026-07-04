#!/usr/bin/env python3
"""Aligns and prepares TCGA and CPTAC cancer datasets for cross-cohort evaluation.

Cohort normalization is performed by standardizing features within each cohort
separately (batch normalization), resolving the feature alignment issue.
TCGA is split into Train/Val/Test (primary), and CPTAC is kept as Test Set 2 (domain transfer).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Monkey-patch combat.pycombat to fix reference batch indexing bug
import combat.pycombat
def adjust_data(s_data, gamma_star, delta_star, batch_design, n_batches, var_pooled, stand_mean, n_array, ref, batches, dat):
    bayes_data = np.transpose(s_data)
    j = 0
    for i in batches:
        bayes_data[i] = (bayes_data[i] - np.dot(np.transpose(batch_design)[i], gamma_star)) / \
            np.transpose(np.outer(np.sqrt(delta_star[j]), np.asarray([1]*n_batches[j])))
        j += 1

    bayes_data = np.multiply(np.transpose(bayes_data), np.outer(np.sqrt(var_pooled), np.asarray([1]*n_array))) + stand_mean

    if ref is not None:
        bayes_data[:, batches[ref]] = dat[:, batches[ref]]

    return bayes_data

combat.pycombat.adjust_data = adjust_data
from combat.pycombat import pycombat

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

HARMONIZED_ROOT = Path("/home/prime/Documents/g3/c-5/gpt/processed/harmonized")
OUTPUT_ROOT = Path("/home/prime/Documents/g3/cancer-exp/datasets_aligned")
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

CANCERS = ["BRCA", "LUAD", "LSCC", "HNSCC"]

def load_biological_pathway_genes() -> list[str]:
    """Loads p53 pathway genes from Reactome participants file."""
    pathway_path = Path("/home/prime/Documents/g3/cancer-exp/outputs/tp53_participants.json")
    if not pathway_path.exists():
        logging.warning("Reactome p53 participants file not found! Falling back to empty list.")
        return []
    
    import re
    with open(pathway_path) as f:
        entities = json.load(f)
    
    candidate_symbols = set()
    for e in entities:
        names = [e.get('displayName', '')] + e.get('name', [])
        for name in names:
            words = re.findall(r'[a-zA-Z0-9]+', name)
            for w in words:
                if w.isupper() and w[0].isalpha() and len(w) >= 2:
                    candidate_symbols.add(f"GENE:{w}")
    return sorted(list(candidate_symbols))

def load_and_align_cohort_pair(cancer: str, target_gene: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads harmonized RNA-Seq and Mutation data for CPTAC and TCGA,

    aligns samples and features, and returns (tcga_aligned, cptac_aligned).
    """
    cohorts = ["tcga", "cptac"]
    expr_dict = {}
    mut_dict = {}

    for cohort in cohorts:
        expr_path = HARMONIZED_ROOT / cohort / cancer / "rnaseq_gene.parquet"
        mut_path = HARMONIZED_ROOT / cohort / cancer / "mutation_binary.parquet"
        
        expr = pd.read_parquet(expr_path).set_index("sample_id")
        mut = pd.read_parquet(mut_path).set_index("sample_id")
        
        common_samples = expr.index.intersection(mut.index)
        expr_dict[cohort] = expr.loc[common_samples]
        mut_dict[cohort] = mut.loc[common_samples]

    # Align genes (intersection of features)
    genes_tcga = expr_dict["tcga"].columns
    genes_cptac = expr_dict["cptac"].columns
    common_genes = sorted(list(set(genes_tcga).intersection(set(genes_cptac))))
    
    # Filter out zero-variance genes to prevent ComBat division by zero and NaN propagation
    var_tcga = expr_dict["tcga"][common_genes].var(axis=0)
    var_cptac = expr_dict["cptac"][common_genes].var(axis=0)
    keep_genes = var_tcga[var_tcga > 0.0].index.intersection(var_cptac[var_cptac > 0.0].index)
    common_genes = sorted(list(keep_genes))
    
    logging.info(f"{cancer} {target_gene} | Common genes after zero-variance filtering: {len(common_genes)}")

    # Combine data for ComBat
    tcga_df = expr_dict["tcga"][common_genes]
    cptac_df = expr_dict["cptac"][common_genes]
    
    combined_df = pd.concat([tcga_df, cptac_df], axis=0)
    batch = ["TCGA"] * len(tcga_df) + ["CPTAC"] * len(cptac_df)
    
    # Run ComBat batch correction (TCGA as reference batch)
    corrected_df_t = pycombat(combined_df.T, batch, ref_batch="TCGA")
    corrected_df = corrected_df_t.T
    
    tcga_expr_norm = corrected_df.iloc[:len(tcga_df)].copy()
    cptac_expr_norm = corrected_df.iloc[len(tcga_df):].copy()

    # Add target column
    tcga_expr_norm["target"] = mut_dict["tcga"][f"GENE:{target_gene}"].astype(int)
    cptac_expr_norm["target"] = mut_dict["cptac"][f"GENE:{target_gene}"].astype(int)

    return tcga_expr_norm, cptac_expr_norm

def export_mutation_task(cancer: str, target_gene: str, max_features: int = 500, feature_selection: str = "unsupervised") -> None:
    logging.info(f"Processing mutation task: {cancer} {target_gene} (mode: {feature_selection})")
    tcga, cptac = load_and_align_cohort_pair(cancer, target_gene)

    X_tcga = tcga.drop(columns=["target"])
    y_tcga = tcga["target"]

    if feature_selection == "unsupervised":
        variances = X_tcga.var(axis=0)
        top_genes = variances.nlargest(max_features).index.tolist()
        task_suffix = f"top{max_features}"
    else:
        bio_genes = load_biological_pathway_genes()
        top_genes = [g for g in bio_genes if g in X_tcga.columns]
        task_suffix = "biological"

    # Subset features
    X_tcga_sub = X_tcga[top_genes]
    
    cptac_X = cptac.drop(columns=["target"])[top_genes]
    cptac_y = cptac["target"]

    # Re-assemble dataframes
    clean_genes = [g.replace("::", "__").replace(":", "_").replace(" ", "_") for g in top_genes]
    
    tcga_df = pd.DataFrame(X_tcga_sub.values, index=X_tcga_sub.index, columns=clean_genes)
    tcga_df["target"] = y_tcga.values

    cptac_df = pd.DataFrame(cptac_X.values, index=cptac_X.index, columns=clean_genes)
    cptac_df["target"] = cptac_y.values

    # Save outputs (keeping the sample_id index)
    task_dir = OUTPUT_ROOT / f"{cancer.lower()}_{target_gene.lower()}_{task_suffix}"
    task_dir.mkdir(parents=True, exist_ok=True)
    
    tcga_df.to_csv(task_dir / "tcga_all.csv", index_label="sample_id")
    cptac_df.to_csv(task_dir / "cptac_test2.csv", index_label="sample_id")

    logging.info(f"Exported to {task_dir}: TCGA={len(tcga_df)} CPTAC={len(cptac_df)} features={len(top_genes)}")

def export_multiclass_cancer_type(max_features: int = 500, feature_selection: str = "unsupervised") -> None:
    logging.info(f"Processing multiclass cancer type classification task (mode: {feature_selection})")
    
    # Load all cancers, intersect genes
    cptac_exprs = {}
    tcga_exprs = {}
    
    all_genes_list = []
    
    for cancer in CANCERS:
        tcga_path = HARMONIZED_ROOT / "tcga" / cancer / "rnaseq_gene.parquet"
        cptac_path = HARMONIZED_ROOT / "cptac" / cancer / "rnaseq_gene.parquet"
        
        tcga_df = pd.read_parquet(tcga_path).set_index("sample_id")
        cptac_df = pd.read_parquet(cptac_path).set_index("sample_id")
        
        tcga_exprs[cancer] = tcga_df
        cptac_exprs[cancer] = cptac_df
        all_genes_list.append(tcga_df.columns)
        all_genes_list.append(cptac_df.columns)

    common_genes = sorted(list(set(all_genes_list[0]).intersection(*[set(g) for g in all_genes_list[1:]])))
    logging.info(f"Cancer Type Task | Common genes across 4 cancers/cohorts: {len(common_genes)}")

    # Combine the unnormalized dataframes for ComBat
    tcga_frames = []
    cptac_frames = []
    tcga_cancers = []
    cptac_cancers = []

    for cancer in CANCERS:
        t_expr = tcga_exprs[cancer][common_genes]
        c_expr = cptac_exprs[cancer][common_genes]
        
        tcga_frames.append(t_expr)
        cptac_frames.append(c_expr)
        
        tcga_cancers.extend([cancer] * len(t_expr))
        cptac_cancers.extend([cancer] * len(c_expr))

    tcga_combined_unnorm = pd.concat(tcga_frames)
    cptac_combined_unnorm = pd.concat(cptac_frames)

    # Filter out zero-variance genes in the combined cohorts to prevent ComBat division by zero and NaN propagation
    var_tcga = tcga_combined_unnorm.var(axis=0)
    var_cptac = cptac_combined_unnorm.var(axis=0)
    keep_genes = var_tcga[var_tcga > 0.0].index.intersection(var_cptac[var_cptac > 0.0].index)
    common_genes = sorted(list(keep_genes))
    
    tcga_combined_unnorm = tcga_combined_unnorm[common_genes]
    cptac_combined_unnorm = cptac_combined_unnorm[common_genes]

    combined_all = pd.concat([tcga_combined_unnorm, cptac_combined_unnorm], axis=0)
    batch = ["TCGA"] * len(tcga_combined_unnorm) + ["CPTAC"] * len(cptac_combined_unnorm)
    covariates = tcga_cancers + cptac_cancers

    # Run ComBat batch correction with reference batch TCGA and cancer type as covariate
    corrected_all_t = pycombat(combined_all.T, batch, mod=covariates, ref_batch="TCGA")
    corrected_all = corrected_all_t.T

    # Split back into TCGA and CPTAC and add target column
    tcga_combined = corrected_all.iloc[:len(tcga_combined_unnorm)].copy()
    tcga_combined["target"] = tcga_cancers

    cptac_combined = corrected_all.iloc[len(tcga_combined_unnorm):].copy()
    cptac_combined["target"] = cptac_cancers

    X_tcga = tcga_combined.drop(columns=["target"])
    y_tcga = tcga_combined["target"]

    if feature_selection == "unsupervised":
        variances = X_tcga.var(axis=0)
        top_genes = variances.nlargest(max_features).index.tolist()
        task_suffix = f"top{max_features}"
    else:
        bio_genes = load_biological_pathway_genes()
        top_genes = [g for g in bio_genes if g in X_tcga.columns]
        task_suffix = "biological"

    clean_genes = [g.replace("::", "__").replace(":", "_").replace(" ", "_") for g in top_genes]

    tcga_df = pd.DataFrame(X_tcga[top_genes].values, index=X_tcga.index, columns=clean_genes)
    tcga_df["target"] = y_tcga.values

    cptac_df = pd.DataFrame(cptac_combined[top_genes].values, index=cptac_combined.index, columns=clean_genes)
    cptac_df["target"] = cptac_combined["target"].values

    task_dir = OUTPUT_ROOT / f"multiclass_cancer_type_{task_suffix}"
    task_dir.mkdir(parents=True, exist_ok=True)
    
    tcga_df.to_csv(task_dir / "tcga_all.csv", index_label="sample_id")
    cptac_df.to_csv(task_dir / "cptac_test2.csv", index_label="sample_id")

    logging.info(f"Exported multiclass task: TCGA={len(tcga_df)} CPTAC={len(cptac_df)} features={len(top_genes)}")

def load_and_align_cohort_pair_cross_modal(cancer: str, target_gene: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads harmonized TCGA RNA-Seq and CPTAC Proteomics data,
    aligns samples and features, and returns (tcga_rna_aligned, cptac_protein_aligned).
    """
    # Load TCGA RNA-Seq and Mutation
    tcga_expr_path = HARMONIZED_ROOT / "tcga" / cancer / "rnaseq_gene.parquet"
    tcga_mut_path = HARMONIZED_ROOT / "tcga" / cancer / "mutation_binary.parquet"
    
    tcga_expr = pd.read_parquet(tcga_expr_path).set_index("sample_id")
    tcga_mut = pd.read_parquet(tcga_mut_path).set_index("sample_id")
    
    tcga_samples = tcga_expr.index.intersection(tcga_mut.index)
    tcga_expr = tcga_expr.loc[tcga_samples]
    tcga_mut = tcga_mut.loc[tcga_samples]

    # Load CPTAC Proteomics and Mutation
    cptac_expr_path = HARMONIZED_ROOT / "cptac" / cancer / "protein_gene.parquet"
    cptac_mut_path = HARMONIZED_ROOT / "cptac" / cancer / "mutation_binary.parquet"
    
    cptac_expr = pd.read_parquet(cptac_expr_path).set_index("sample_id")
    # Impute missing proteomics values using protein medians, then drop columns that remain NaN
    cptac_expr = cptac_expr.fillna(cptac_expr.median())
    cptac_expr = cptac_expr.dropna(axis=1, how="any")
    
    cptac_mut = pd.read_parquet(cptac_mut_path).set_index("sample_id")
    
    cptac_samples = cptac_expr.index.intersection(cptac_mut.index)
    cptac_expr = cptac_expr.loc[cptac_samples]
    cptac_mut = cptac_mut.loc[cptac_samples]

    # Align genes (intersection of RNA genes and Protein genes)
    common_genes = sorted(list(set(tcga_expr.columns).intersection(set(cptac_expr.columns))))
    
    # Filter out zero-variance genes in either cohort
    var_tcga = tcga_expr[common_genes].var(axis=0)
    var_cptac = cptac_expr[common_genes].var(axis=0)
    keep_genes = var_tcga[var_tcga > 0.0].index.intersection(var_cptac[var_cptac > 0.0].index)
    common_genes = sorted(list(keep_genes))
    
    logging.info(f"{cancer} {target_gene} (Cross-Modal) | Common genes after zero-variance filtering: {len(common_genes)}")

    # Combine data for ComBat
    tcga_df = tcga_expr[common_genes]
    cptac_df = cptac_expr[common_genes]
    
    combined_df = pd.concat([tcga_df, cptac_df], axis=0)
    batch = ["TCGA_RNA"] * len(tcga_df) + ["CPTAC_Protein"] * len(cptac_df)
    
    # Run ComBat batch correction (TCGA RNA as reference batch)
    corrected_df_t = pycombat(combined_df.T, batch, ref_batch="TCGA_RNA")
    corrected_df = corrected_df_t.T
    
    tcga_expr_norm = corrected_df.iloc[:len(tcga_df)].copy()
    cptac_expr_norm = corrected_df.iloc[len(tcga_df):].copy()

    # Add target column
    tcga_expr_norm["target"] = tcga_mut[f"GENE:{target_gene}"].astype(int)
    cptac_expr_norm["target"] = cptac_mut[f"GENE:{target_gene}"].astype(int)

    return tcga_expr_norm, cptac_expr_norm

def export_mutation_task_cross_modal(cancer: str, target_gene: str, max_features: int = 500, feature_selection: str = "unsupervised") -> None:
    logging.info(f"Processing cross-modal mutation task: {cancer} {target_gene} (mode: {feature_selection})")
    tcga, cptac = load_and_align_cohort_pair_cross_modal(cancer, target_gene)

    X_tcga = tcga.drop(columns=["target"])
    y_tcga = tcga["target"]

    if feature_selection == "unsupervised":
        variances = X_tcga.var(axis=0)
        top_genes = variances.nlargest(max_features).index.tolist()
        task_suffix = f"protein_top{max_features}"
    else:
        bio_genes = load_biological_pathway_genes()
        top_genes = [g for g in bio_genes if g in X_tcga.columns]
        task_suffix = "protein_biological"

    # Subset features
    X_tcga_sub = X_tcga[top_genes]
    
    cptac_X = cptac.drop(columns=["target"])[top_genes]
    cptac_y = cptac["target"]

    # Re-assemble dataframes
    clean_genes = [g.replace("::", "__").replace(":", "_").replace(" ", "_") for g in top_genes]
    
    tcga_df = pd.DataFrame(X_tcga_sub.values, index=X_tcga_sub.index, columns=clean_genes)
    tcga_df["target"] = y_tcga.values

    cptac_df = pd.DataFrame(cptac_X.values, index=cptac_X.index, columns=clean_genes)
    cptac_df["target"] = cptac_y.values

    # Save outputs (keeping the sample_id index)
    task_dir = OUTPUT_ROOT / f"{cancer.lower()}_{target_gene.lower()}_{task_suffix}"
    task_dir.mkdir(parents=True, exist_ok=True)
    
    tcga_df.to_csv(task_dir / "tcga_all.csv", index_label="sample_id")
    cptac_df.to_csv(task_dir / "cptac_test2.csv", index_label="sample_id")

    logging.info(f"Exported cross-modal to {task_dir}: TCGA={len(tcga_df)} CPTAC={len(cptac_df)} features={len(top_genes)}")

def export_multiclass_cancer_type_cross_modal(max_features: int = 500, feature_selection: str = "unsupervised") -> None:
    logging.info(f"Processing cross-modal multiclass cancer type classification task (mode: {feature_selection})")
    
    # Load all cancers, intersect genes
    tcga_exprs = {}
    cptac_exprs = {}
    all_genes_list = []
    
    for cancer in CANCERS:
        tcga_path = HARMONIZED_ROOT / "tcga" / cancer / "rnaseq_gene.parquet"
        cptac_path = HARMONIZED_ROOT / "cptac" / cancer / "protein_gene.parquet"
        
        tcga_df = pd.read_parquet(tcga_path).set_index("sample_id")
        cptac_df = pd.read_parquet(cptac_path).set_index("sample_id")
        
        # Impute missing proteomics values using protein medians, then drop columns that remain NaN
        cptac_df = cptac_df.fillna(cptac_df.median())
        cptac_df = cptac_df.dropna(axis=1, how="any")
        
        tcga_exprs[cancer] = tcga_df
        cptac_exprs[cancer] = cptac_df
        all_genes_list.append(tcga_df.columns)
        all_genes_list.append(cptac_df.columns)

    common_genes = sorted(list(set(all_genes_list[0]).intersection(*[set(g) for g in all_genes_list[1:]])))
    
    # Combine the unnormalized dataframes for ComBat
    tcga_frames = []
    cptac_frames = []
    tcga_cancers = []
    cptac_cancers = []

    for cancer in CANCERS:
        t_expr = tcga_exprs[cancer][common_genes]
        c_expr = cptac_exprs[cancer][common_genes]
        
        tcga_frames.append(t_expr)
        cptac_frames.append(c_expr)
        
        tcga_cancers.extend([cancer] * len(t_expr))
        cptac_cancers.extend([cancer] * len(c_expr))

    tcga_combined_unnorm = pd.concat(tcga_frames)
    cptac_combined_unnorm = pd.concat(cptac_frames)

    # Filter out zero-variance genes in the combined cohorts to prevent ComBat division by zero and NaN propagation
    var_tcga = tcga_combined_unnorm.var(axis=0)
    var_cptac = cptac_combined_unnorm.var(axis=0)
    keep_genes = var_tcga[var_tcga > 0.0].index.intersection(var_cptac[var_cptac > 0.0].index)
    common_genes = sorted(list(keep_genes))
    
    tcga_combined_unnorm = tcga_combined_unnorm[common_genes]
    cptac_combined_unnorm = cptac_combined_unnorm[common_genes]

    combined_all = pd.concat([tcga_combined_unnorm, cptac_combined_unnorm], axis=0)
    batch = ["TCGA_RNA"] * len(tcga_combined_unnorm) + ["CPTAC_Protein"] * len(cptac_combined_unnorm)
    covariates = tcga_cancers + cptac_cancers

    # Run ComBat batch correction with reference batch TCGA_RNA and cancer type as covariate
    corrected_all_t = pycombat(combined_all.T, batch, mod=covariates, ref_batch="TCGA_RNA")
    corrected_all = corrected_all_t.T

    # Split back into TCGA and CPTAC and add target column
    tcga_combined = corrected_all.iloc[:len(tcga_combined_unnorm)].copy()
    tcga_combined["target"] = tcga_cancers

    cptac_combined = corrected_all.iloc[len(tcga_combined_unnorm):].copy()
    cptac_combined["target"] = cptac_cancers

    X_tcga = tcga_combined.drop(columns=["target"])
    y_tcga = tcga_combined["target"]

    if feature_selection == "unsupervised":
        variances = X_tcga.var(axis=0)
        top_genes = variances.nlargest(max_features).index.tolist()
        task_suffix = f"protein_top{max_features}"
    else:
        bio_genes = load_biological_pathway_genes()
        top_genes = [g for g in bio_genes if g in X_tcga.columns]
        task_suffix = "protein_biological"

    clean_genes = [g.replace("::", "__").replace(":", "_").replace(" ", "_") for g in top_genes]

    tcga_df = pd.DataFrame(X_tcga[top_genes].values, index=X_tcga.index, columns=clean_genes)
    tcga_df["target"] = y_tcga.values

    cptac_df = pd.DataFrame(cptac_combined[top_genes].values, index=cptac_combined.index, columns=clean_genes)
    cptac_df["target"] = cptac_combined["target"].values

    task_dir = OUTPUT_ROOT / f"multiclass_cancer_type_{task_suffix}"
    task_dir.mkdir(parents=True, exist_ok=True)
    
    tcga_df.to_csv(task_dir / "tcga_all.csv", index_label="sample_id")
    cptac_df.to_csv(task_dir / "cptac_test2.csv", index_label="sample_id")

    logging.info(f"Exported cross-modal multiclass task: TCGA={len(tcga_df)} CPTAC={len(cptac_df)} features={len(top_genes)}")

def main():
    # --- Part 1: Unsupervised Top-500 High-Variance Cohorts ---
    # Somatic mutation tasks (RNA-to-RNA)
    export_mutation_task("BRCA", "TP53")
    export_mutation_task("BRCA", "PIK3CA")
    export_mutation_task("LUAD", "TP53")
    export_mutation_task("HNSCC", "TP53")
    export_mutation_task("LSCC", "TP53")
    
    # Multiclass cancer type task (RNA-to-RNA)
    export_multiclass_cancer_type()
    
    # Somatic mutation tasks (Cross-Modal RNA-to-Protein)
    export_mutation_task_cross_modal("BRCA", "TP53")
    export_mutation_task_cross_modal("BRCA", "PIK3CA")
    export_mutation_task_cross_modal("LUAD", "TP53")
    export_mutation_task_cross_modal("HNSCC", "TP53")
    export_mutation_task_cross_modal("LSCC", "TP53")
    
    # Multiclass cancer type task (Cross-Modal RNA-to-Protein)
    export_multiclass_cancer_type_cross_modal()

    # --- Part 2: Biological Pathway Targeted Cohorts ---
    # Somatic mutation tasks (RNA-to-RNA)
    export_mutation_task("BRCA", "TP53", feature_selection="biological")
    export_mutation_task("BRCA", "PIK3CA", feature_selection="biological")
    export_mutation_task("LUAD", "TP53", feature_selection="biological")
    export_mutation_task("HNSCC", "TP53", feature_selection="biological")
    export_mutation_task("LSCC", "TP53", feature_selection="biological")
    
    # Multiclass cancer type task (RNA-to-RNA)
    export_multiclass_cancer_type(feature_selection="biological")
    
    # Somatic mutation tasks (Cross-Modal RNA-to-Protein)
    export_mutation_task_cross_modal("BRCA", "TP53", feature_selection="biological")
    export_mutation_task_cross_modal("BRCA", "PIK3CA", feature_selection="biological")
    export_mutation_task_cross_modal("LUAD", "TP53", feature_selection="biological")
    export_mutation_task_cross_modal("HNSCC", "TP53", feature_selection="biological")
    export_mutation_task_cross_modal("LSCC", "TP53", feature_selection="biological")
    
    # Multiclass cancer type task (Cross-Modal RNA-to-Protein)
    export_multiclass_cancer_type_cross_modal(feature_selection="biological")
    
    logging.info("All aligned cohort datasets successfully prepared!")

if __name__ == "__main__":
    main()
