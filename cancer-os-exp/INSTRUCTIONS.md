# AI Agent Instructions: Cancer OS Experiments

These instructions are for an AI agent running the cancer OS foundation-model experiments.

Do not edit the evaluator package or installed model libraries during this workflow. Use the scripts in this folder and write outputs inside `/home/prime/Documents/g3/cancer-os-exp/`.

## 0. Working Directory

Start here:

```bash
cd /home/prime/Documents/g3/cancer-os-exp
```

## 1. Environment Assumptions

The scripts expect:

- processed cancer matrices at `/home/prime/Documents/g3/c-5/gpt/processed/train_ready`
- evaluator package source at `/home/prime/Documents/g3/tab-r1/package/src`
- TabFM installed in the active Python environment
- TabPFN package/checkpoints available for the selected TabPFN generations
- `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`, and `seaborn`

Recommended thread limits for heavy local runs:

```bash
export OMP_NUM_THREADS=14
export OPENBLAS_NUM_THREADS=14
export MKL_NUM_THREADS=14
export NUMEXPR_NUM_THREADS=14
```

If CUDA/JAX is unstable, prefer TabFM PyTorch backend or CPU execution rather than modifying installed libraries.

## 2. Feature Audit

Run this first. It answers what input modalities exist in the processed matrices.

```bash
python shared/scripts/audit_feature_modalities.py \
  --input-root /home/prime/Documents/g3/c-5/gpt/processed/train_ready \
  --output-dir shared/reports \
  --view core \
  --max-features 100
```

Expected outputs:

```text
shared/reports/feature_modality_audit.csv
shared/reports/feature_modality_prefix_counts.csv
shared/reports/feature_modality_selected_prefix_counts.csv
shared/reports/feature_modality_audit.md
```

Inspect this before running models. Confirm whether the selected non-clinical features are expression, mutation, CNV, methylation, protein, phospho, or other modalities.

## 3. Export Datasets

### Experiment 1: Per-Cancer Fixed-Window OS

```bash
python exp01_per_cancer_fixed_window/scripts/export_per_cancer_fixed_window.py \
  --input-root /home/prime/Documents/g3/c-5/gpt/processed/train_ready \
  --output-dir exp01_per_cancer_fixed_window/datasets \
  --view core \
  --max-features 100 \
  --min-class-count 5
```

Expected manifest:

```text
exp01_per_cancer_fixed_window/datasets/manifest.json
```

### Experiment 2: Combined-Cancer Fixed-Window OS

```bash
python exp02_combined_fixed_window/scripts/export_combined_fixed_window.py \
  --input-root /home/prime/Documents/g3/c-5/gpt/processed/train_ready \
  --output-dir exp02_combined_fixed_window/datasets \
  --view core \
  --max-features 100 \
  --min-class-count 5
```

Expected manifest:

```text
exp02_combined_fixed_window/datasets/manifest.json
```

By default, `cancer_type` is not included as a model feature. It is saved in sidecar metadata for subgroup reporting.

### Experiment 3: Combined Extreme Survival Contrast

```bash
python exp03_combined_extreme_survival/scripts/export_extreme_survival.py \
  --input-root /home/prime/Documents/g3/c-5/gpt/processed/train_ready \
  --output-dir exp03_combined_extreme_survival/datasets \
  --view core \
  --max-features 100 \
  --min-class-count 5
```

Expected manifest:

```text
exp03_combined_extreme_survival/datasets/manifest.json
```

## 4. Verify Dataset Counts Before Model Runs

Before running models, inspect each manifest:

```bash
python - <<'PY'
import json
from pathlib import Path

for path in [
    Path("exp01_per_cancer_fixed_window/datasets/manifest.json"),
    Path("exp02_combined_fixed_window/datasets/manifest.json"),
    Path("exp03_combined_extreme_survival/datasets/manifest.json"),
]:
    payload = json.loads(path.read_text())
    print("\n", path)
    for r in payload["records"]:
        print(r["name"], "n=", r["samples"], "classes=", r["class_counts"])
PY
```

Do not continue if a dataset has only one class or very small sample counts.

## 5. Run Models

Default model set:

- TabFM default
- TabPFN v2
- TabPFN v2.5
- TabPFN v2.6
- TabPFN v3

TabPFN v1 is intentionally excluded unless a compatible legacy runtime is prepared.

### Experiment 1 Models

```bash
python exp01_per_cancer_fixed_window/scripts/run_per_cancer_models.py \
  --manifest exp01_per_cancer_fixed_window/datasets/manifest.json \
  --output-root exp01_per_cancer_fixed_window/outputs \
  --package-src /home/prime/Documents/g3/tab-r1/package/src \
  --models tabfm,tabpfn \
  --tabpfn-versions v2,v2.5,v2.6,v3 \
  --tabfm-backend jax \
  --train-rows-cap 1024 \
  --seed 42
```

### Experiment 2 Models

```bash
python exp02_combined_fixed_window/scripts/run_combined_models.py \
  --manifest exp02_combined_fixed_window/datasets/manifest.json \
  --output-root exp02_combined_fixed_window/outputs \
  --package-src /home/prime/Documents/g3/tab-r1/package/src \
  --models tabfm,tabpfn \
  --tabpfn-versions v2,v2.5,v2.6,v3 \
  --tabfm-backend jax \
  --train-rows-cap 1024 \
  --seed 42
```

### Experiment 3 Models

```bash
python exp03_combined_extreme_survival/scripts/run_extreme_survival_models.py \
  --manifest exp03_combined_extreme_survival/datasets/manifest.json \
  --output-root exp03_combined_extreme_survival/outputs \
  --package-src /home/prime/Documents/g3/tab-r1/package/src \
  --models tabfm,tabpfn \
  --tabpfn-versions v2,v2.5,v2.6,v3 \
  --tabfm-backend jax \
  --train-rows-cap 1024 \
  --seed 42
```

If JAX fails, rerun only TabFM with PyTorch backend:

```bash
python exp02_combined_fixed_window/scripts/run_combined_models.py \
  --manifest exp02_combined_fixed_window/datasets/manifest.json \
  --output-root exp02_combined_fixed_window/outputs_tabfm_pytorch \
  --package-src /home/prime/Documents/g3/tab-r1/package/src \
  --models tabfm \
  --tabfm-backend pytorch \
  --train-rows-cap 1024 \
  --seed 42
```

## 6. Optional TabFM Ensemble

TabFM ensemble is slower and should be run separately from the default TabFM run.

Example for Experiment 2:

```bash
python exp02_combined_fixed_window/scripts/run_combined_models.py \
  --manifest exp02_combined_fixed_window/datasets/manifest.json \
  --output-root exp02_combined_fixed_window/outputs_tabfm_ensemble \
  --package-src /home/prime/Documents/g3/tab-r1/package/src \
  --models tabfm \
  --tabfm-backend jax \
  --tabfm-ensemble \
  --train-rows-cap 1024 \
  --seed 42
```

Keep ensemble outputs separate so default and ensemble comparisons are not confused.

## 7. Generate Reports

### Experiment 1 Report

```bash
python exp01_per_cancer_fixed_window/scripts/make_per_cancer_report.py \
  --output-root exp01_per_cancer_fixed_window/outputs \
  --report-path exp01_per_cancer_fixed_window/reports/report.md \
  --title "Experiment 1: Per-Cancer Fixed-Window OS Event"
```

### Experiment 2 Report

```bash
python exp02_combined_fixed_window/scripts/make_combined_report.py \
  --output-root exp02_combined_fixed_window/outputs \
  --report-path exp02_combined_fixed_window/reports/report.md \
  --title "Experiment 2: Combined-Cancer Fixed-Window OS Event"
```

### Experiment 3 Report

```bash
python exp03_combined_extreme_survival/scripts/make_extreme_survival_report.py \
  --output-root exp03_combined_extreme_survival/outputs \
  --report-path exp03_combined_extreme_survival/reports/report.md \
  --title "Experiment 3: Combined Extreme Survival Contrast"
```

## 8. Important Output Files

Each experiment writes:

```text
outputs/aggregate/all_model_metrics.csv
outputs/aggregate/mean_metrics_by_model.csv
outputs/aggregate/mean_metrics_by_endpoint_model.csv
outputs/aggregate/subgroup_metrics_by_cancer.csv
outputs/aggregate/run_config.json
reports/report.md
reports/plots/*.png
```

Per-run raw artifacts are under:

```text
outputs/tabfm/runs/<dataset>/<timestamp>/
outputs/tabpfn/runs/<dataset>/<timestamp>/
```

Look for:

```text
predictions/*_predictions.csv
raw/*/raw_predictions.json
raw/*/raw_predictions.npz
metrics/metrics_summary.csv
metrics/augmented_metrics.csv
plots/*.png
logs/*.log
```

## 9. Interpretation Rules

Report every result with:

- `n_total`
- `n_train`
- `n_val`
- `n_test`
- class counts in train/val/test
- ROC AUC
- PR AUC
- F1
- sensitivity
- specificity
- log loss

Do not interpret accuracy alone. OS labels are imbalanced, so PR AUC and sensitivity are critical.

## 10. Label Definitions

### Fixed-Window OS Event

For a horizon `H`:

- `1`: patient died on or before `H`
- `0`: patient is known to have survived beyond `H`
- excluded: patient was censored before `H`

For 3 years:

- `H = 1095 days`

For 5 years:

- `H = 1825 days`

### Extreme Survival Contrast

- `1`: died before 3 years, meaning `OS_event = 1` and `OS_days < 1095`
- `0`: alive/censored beyond 5 years, meaning `OS_event = 0` and `OS_days >= 1825`
- excluded: all other patients

This is a binary classification task, not a full censored survival model.

## 11. What Not To Do

- Do not patch installed libraries.
- Do not edit `/tmp/TabPFN_v1`.
- Do not modify `/home/prime/Documents/g3/tab-r1/package` unless explicitly asked.
- Do not mix TabFM default and TabFM ensemble outputs in the same output folder unless the report explicitly labels them.
- Do not hide failed model runs; preserve traceback files and failed rows in metric tables.
