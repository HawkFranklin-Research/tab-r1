# Cancer OS Foundation Model Experiments

This folder contains a fresh experiment codebase for fixed-window overall-survival event classification using the processed TCGA/CPTAC-derived cancer matrices.

The goal is to evaluate whether molecular features can predict survival-event labels under cleaner label definitions than the earlier raw `OS_event` proxy.

## Source Data

Default input root:

```text
/home/prime/Documents/g3/c-5/gpt/processed/train_ready
```

Expected structure:

```text
<CANCER>/<VIEW>/
  X.npz
  sample_index.csv
  feature_index.csv
```

Each `sample_index.csv` must contain:

- `OS_days`
- `OS_event`

Each `feature_index.csv` must contain:

- `feature_id`

Clinical features beginning with `clinical::` are excluded by default. The exporters select top-variance non-clinical features.

Exporters also enforce a default minimum of five samples per class before a dataset is kept. This avoids downstream stratified split failures where a label exists but is too rare to split safely.

## Shared Scripts

```text
shared/scripts/audit_feature_modalities.py
shared/scripts/os_exp_common.py
shared/scripts/run_foundation_models.py
shared/scripts/make_foundation_report.py
```

### `audit_feature_modalities.py`

Reads all `feature_index.csv` files and reports what kinds of inputs exist:

- total features
- clinical features
- non-clinical features
- feature prefix/modality counts
- selected top-variance feature prefix counts

Outputs:

```text
shared/reports/feature_modality_audit.csv
shared/reports/feature_modality_prefix_counts.csv
shared/reports/feature_modality_selected_prefix_counts.csv
shared/reports/feature_modality_audit.md
```

### `run_foundation_models.py`

Runs exported CSV datasets through:

- TabFM default or optional TabFM ensemble
- TabPFN v2, v2.5, v2.6, v3
- optional TabPFN v1 only if a compatible legacy runtime is supplied

Saved outputs include:

- prediction CSVs
- raw prediction JSON/NPZ files
- metrics CSV/JSON
- ROC/confusion plots from the evaluator package
- aggregate metrics
- cancer subgroup metrics where metadata is available

Important metrics:

- accuracy
- F1
- ROC AUC
- PR AUC
- sensitivity
- specificity
- balanced accuracy
- log loss

### `make_foundation_report.py`

Reads saved model outputs and creates Markdown reports plus summary plots. It does not rerun models.

## Experiment 1: Per-Cancer Fixed-Window OS Event

Folder:

```text
exp01_per_cancer_fixed_window/
```

Question:

> Within each cancer type, can molecular features predict fixed-window OS event?

Labels:

- 3-year: `1 = death observed on or before 1095 days`, `0 = known survival beyond 1095 days`
- 5-year: `1 = death observed on or before 1825 days`, `0 = known survival beyond 1825 days`
- censored-before-horizon patients are excluded

This trains/evaluates separate datasets per cancer and horizon.

## Experiment 2: Combined-Cancer Fixed-Window OS Event

Folder:

```text
exp02_combined_fixed_window/
```

Question:

> If cancers are pooled, can a single foundation model predict fixed-window OS event, and does it behave evenly across cancer types?

Labels:

- same 3-year and 5-year definitions as Experiment 1
- all cancers are pooled into one dataset per horizon
- cancer type is retained in metadata for subgroup reporting
- cancer type is not included as a model feature by default

## Experiment 3: Combined Extreme Survival Contrast

Folder:

```text
exp03_combined_extreme_survival/
```

Question:

> Can molecular features separate early-death patients from long-surviving patients under a cleaner extreme contrast?

Labels:

- `1 = OS_event = 1 and OS_days < 1095`
- `0 = OS_event = 0 and OS_days >= 1825`
- everyone else is excluded

This is not a Cox survival model. It is a binary classification experiment with cleaner event labels.

## Model Policy

Default model set:

```text
TabFM default
TabPFN v2
TabPFN v2.5
TabPFN v2.6
TabPFN v3
```

TabPFN v1 is not included by default because it requires a separate compatible legacy runtime.

## Important Caveats

- These are classification experiments, not censored survival models.
- The label cleanup happens only on the target side.
- The input matrices remain the processed molecular feature matrices from `train_ready`.
- Accuracy alone is not enough because OS-event labels can be imbalanced.
- Use ROC AUC, PR AUC, F1, sensitivity, specificity, log loss, and class counts together.
