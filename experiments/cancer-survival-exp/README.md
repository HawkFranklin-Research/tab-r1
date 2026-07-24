# Fixed-Window OS Event Foundation-Model Experiment

This is a fresh workspace for stricter label-level survival-event classification.

It does not modify:

- `/home/prime/Documents/g3/cancer-exp`
- `/home/prime/Documents/g3/c-5/gpt`
- `/home/prime/Documents/g3/tab-r1/package`

## Goal

Compare TabPFN generations and Google's TabFM on fixed-window OS event labels derived from the same processed cancer multiomics matrices.

The task is binary classification:

- `1`: death observed on or before the fixed horizon
- `0`: no observed death before the fixed horizon
- excluded: patients censored before the fixed horizon

The two fixed horizons are:

- 3-year OS event: `1095` days
- 5-year OS event: `1825` days

This is still not a proper censored survival model. It is a cleaner fixed-window event-classification framing than raw `OS_event`.

## Inputs

Sparse train-ready matrices:

`/home/prime/Documents/g3/c-5/gpt/processed/train_ready`

The exporter excludes all `clinical::` features and keeps top-variance non-clinical molecular features.

## Commands

Export fixed-window CSVs:

```bash
python /home/prime/Documents/g3/cancer-survival-exp/scripts/export_fixed_window_os_csvs.py
```

Run TabPFN v1, v2, v2.5, v2.6, v3, and TabFM default:

```bash
python /home/prime/Documents/g3/cancer-survival-exp/scripts/run_fixed_window_foundation_models.py
```

Generate report and plots:

```bash
python /home/prime/Documents/g3/cancer-survival-exp/scripts/make_fixed_window_report.py
```

## Outputs

- `datasets_fixed_window_top100/*.csv`
- `datasets_fixed_window_top100/manifest.csv`
- `outputs/fixed_window_foundation_top100/runs/*`
- `outputs/fixed_window_foundation_top100/aggregate/foundation_dataset_metrics.csv`
- `outputs/fixed_window_foundation_top100/aggregate/foundation_mean_metrics.csv`
- `outputs/fixed_window_foundation_top100/aggregate/foundation_task_family_metrics.csv`
- `reports/fixed_window_foundation_os_report.md`
- `plots/fixed_window_foundation_top100/*.png`

## Metrics

The combined report includes:

- accuracy
- F1
- ROC AUC
- PR AUC
- event-class sensitivity
- log loss

Accuracy is not the primary interpretation metric because event labels are imbalanced.
