# Paper Analysis Code

This directory contains the code-only reconstruction layer for the TABR1 manuscript. It does not replace or modify the evaluator package, installed model libraries, or historical experiment outputs.

## Safety Contract

- Maximum supported CPU threads: 12.
- Maximum supported address-space limit: 12 GB.
- Smoke mode never runs TabPFN or TabFM.
- Existing foundation-model predictions are immutable inputs.
- Full-scale commands must not be launched until explicitly approved.
- Manuscript and bibliography rewriting are a separate later step.

## Utilities

### `run_matched_baselines.py`

Runs only classical comparators on selected validation datasets. Dataset and model lists are explicit. `--smoke` runs logistic regression and random forest on a 128-row training subset of Australian.

### `analyze_saved_cancer_results.py`

Reads existing TabPFN and TabFM test predictions, computes bootstrap confidence intervals, and fits lightweight prevalence, cohort-identity, source-identity, structural-zero-pattern, and linear-molecular controls on the historical split.

### `run_cohort_stress_tests.py`

Runs leave-one-cancer-out, leave-one-source-out, global-label permutation, and within-cancer permutation controls. It does not invoke a foundation model.

### `prepare_leakage_safe_folds.py`

Reads the original sparse cancer matrices and exports patient-grouped folds. For pooled folds, cancers are harmonized by exact common feature identifiers. Variance feature selection is fitted using training rows only and separately for every repeat/fold.

### `run_leakage_safe_fold_models.py`

Consumes the exported train, validation, and test files directly, avoiding evaluator re-splitting. It derives each binary decision threshold from validation data only and saves sample-level test probabilities. Non-smoke runs, including every TabPFN or TabFM run, require the explicit `--confirm-full-run` flag.

### `make_evidence_figures.py`

Generates six-panel survival and confounding figures entirely from analysis CSVs and saved test probabilities. Every plotted curve is exported as machine-readable panel source data.

### `analyze_cancer_landscape.py`

Builds cohort-flow, class-balance, Kaplan-Meier, selected-modality, feature-overlap, and cancer-separability source tables. Cohort separability explicitly tests whether molecular values or structural zero patterns reveal cancer identity.

### `make_study_design_figures.py`

Generates the data-linked study-design and cancer-landscape multi-panel figures. Conceptual workflow nodes are exported alongside all numerical panel source tables.

### `build_provenance_manifest.py`

Creates CSV and JSON inventories with paths, schemas, sizes, and SHA-256 checksums for source tables and figure data.

## Bounded Smoke Validation

These commands are safe for the current development stage:

```bash
export OMP_NUM_THREADS=12
export OPENBLAS_NUM_THREADS=12
export MKL_NUM_THREADS=12
export NUMEXPR_NUM_THREADS=12

python paper/analysis/run_matched_baselines.py \
  --smoke --threads 12 --memory-gb 12 \
  --output-dir paper/tables/source_data/smoke_baselines

python paper/analysis/analyze_saved_cancer_results.py \
  --smoke --bootstrap-iterations 30 --threads 12 --memory-gb 12 \
  --output-dir paper/tables/source_data/smoke_cancer

python paper/analysis/run_cohort_stress_tests.py \
  --smoke --permutations 2 --threads 12 --memory-gb 12 \
  --output-dir paper/tables/source_data/smoke_stress

python paper/analysis/prepare_leakage_safe_folds.py \
  --smoke --threads 12 --memory-gb 12 \
  --output-root /tmp/tabr1-smoke-folds

python paper/analysis/run_leakage_safe_fold_models.py \
  --fold-manifest /tmp/tabr1-smoke-folds/fold_manifest.csv \
  --output-root /tmp/tabr1-smoke-fold-models \
  --smoke --threads 12 --memory-gb 12

python paper/analysis/make_evidence_figures.py \
  --source-dir paper/tables/source_data/smoke_cancer \
  --stress-source-dir paper/tables/source_data/smoke_stress \
  --output-dir /tmp/tabr1-smoke-figures \
  --figures 4,5 --smoke

python paper/analysis/analyze_cancer_landscape.py \
  --smoke --threads 12 --memory-gb 12 \
  --output-dir /tmp/tabr1-smoke-landscape

python paper/analysis/make_study_design_figures.py \
  --landscape-dir /tmp/tabr1-smoke-landscape \
  --output-dir /tmp/tabr1-smoke-study-figures \
  --figures 1,3 --smoke
```

## Deferred Full Execution

Do not run the following workflow until explicit approval:

1. Run `prepare_leakage_safe_folds.py` without `--smoke` for five repeats and five outer folds.
2. Run `run_leakage_safe_fold_models.py --confirm-full-run` on the exported identical folds.
3. Run `analyze_saved_cancer_results.py` with 2,000 bootstrap iterations.
4. Run `run_cohort_stress_tests.py` with at least 500 permutations.
5. Generate final PNG, PDF, and SVG figures from the completed source tables.
6. Build checksum manifests for all tables and figure panel data.

The current code intentionally does not start that workflow automatically.

## Intentionally Deferred Figure 2

The controlled-benchmark Figure 2 is not generated from the historical seven-dataset summaries because those model families were produced by different runs and are not fold-matched. Its final rank, paired-delta, uncertainty, and runtime panels must be generated only after the identical-fold benchmark run is approved and completed. The historical seven-dataset result remains engineering validation rather than confirmatory model-comparison evidence.
