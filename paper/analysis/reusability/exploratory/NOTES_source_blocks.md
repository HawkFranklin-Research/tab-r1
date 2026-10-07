# Source-specific feature blocks in the c-5 matrices (found 2026-10-03)

**Status: exploratory, read-only. No manuscript text has been changed.** Script: `source_block_check.py`
(output: `output/source_block_check.csv`). Run from the repository root.

## What the data look like
`c-5/gpt/processed/train_ready/{cancer}/core/feature_index.csv` lists most non-clinical features **twice** under the same id
(BRCA 70,532 duplicated ids, HNSCC 78,097, LSCC 79,153, LUAD 79,326; ESCA only mutation_binary, 4,482). Example, BRCA
`rnaseq_gene::GENE:TSPAN6`: column 0 has values only for CPTAC rows (TCGA rows 100% missing); column 195,132 has values only
for TCGA rows (CPTAC rows 100% missing). Each block is z-scored inside its own source, as the c-5 README describes
("conservatively centered by cohort"). `missing_mask.npz`: 1 = missing (imputed cells share one constant value in X; verified).

## What happened downstream in the paper pipeline
- `prepare_leakage_safe_folds.py::harmonize_cohorts` maps feature id -> column with a dict, so for a duplicated id the **later
  column wins** (the TCGA block in BRCA). Per-cancer variance selection also favoured TCGA-block columns.
- Result in the frozen folds (`generated_folds/per_cancer/*/BRCA..LUAD/repeat_00_fold_00`): **every CPTAC row has all 100 selected
  features exactly zero (e.g. HNSCC 3-year 37/37, LSCC 38/38, LUAD 31/31), and no TCGA row does.** The all-zero vector therefore
  identifies the source inside each cancer.
- Fixed-horizon labelling excludes patients censored before the horizon, and CPTAC follow-up is short, so the CPTAC patients who
  remain are mostly events: event rate among eligible CPTAC vs TCGA patients is 0.88-1.00 vs 0.66-0.85 at 5 years and for the
  extreme endpoint (HNSCC, LSCC, LUAD). So "all-zero vector" correlates with the positive class.

## Effect on the reported within-cancer AUC (saved predictions, fold-level)
Excluding CPTAC test patients changes the mean within-cancer ROC AUC (all models, per-cancer tasks) from
0.535 -> 0.528 (3-year), 0.552 -> 0.529 (5-year), 0.585 -> 0.569 (extreme); by cancer up to -0.065 (HNSCC 5-year 0.560 -> 0.495),
-0.046 (LSCC 3-year), -0.043 (HNSCC extreme); BRCA, ESCA and LUAD about 0. Foundation models lose more (-0.019) than the others
(-0.011) on average. Test CPTAC counts are small (about 4-12 patients per fold), so these are noisy; they are an indication, not
an estimate with an interval.

## What it implies (not yet acted on)
1. Part of the within-cancer discrimination in the paper (about 0.01-0.02 AUC on average, more in HNSCC and LSCC) comes from
   identifying CPTAC patients, not from molecular survival signal.
2. The paper's pooled "zero-pattern" findings describe cohort identification at the cancer level; this is an additional,
   source-level zero pattern inside each cancer.
3. `survival_v2` coalesces the two source blocks per sample (`tte/store.py`) so that CPTAC patients carry real feature values, and
   adds source-only controls, so the new analysis does not inherit this.
