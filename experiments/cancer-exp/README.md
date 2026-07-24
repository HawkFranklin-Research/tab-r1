# Cancer Multiomics TabPFN3 Experiment

This folder is an isolated experiment workspace. It does not modify:

- `/home/prime/Documents/g3/tab-r1/package`
- `/home/prime/Documents/g3/c-5/gpt`
- `/home/prime/Documents/g3/c-5/cptac-5`
- `/home/prime/Documents/g3/c-5/tcga-5`

## Goal

Evaluate TabPFN3 on preliminary cancer multiomics tasks derived from the processed GPT train-ready matrices.

The source matrices are sparse `X.npz` files from:

`/home/prime/Documents/g3/c-5/gpt/processed/train_ready`

The evaluator package is used as-is from:

`/home/prime/Documents/g3/tab-r1/package`

## Experiment Design

The current run uses the `core` view only.

Exported task families:

- `source`: binary TCGA-vs-CPTAC source prediction per cancer, used as a batch-effect / normalization diagnostic.
- `os_event`: binary observed overall-survival event prediction per cancer, preliminary only because censoring is not modeled.
- `cancer_type`: multiclass prediction across BRCA, LUAD, LSCC, HNSCC, and ESCA.

Leakage control:

- All `clinical::` features are excluded from exported model matrices.
- This avoids known train-ready leakage warnings from the GPT preprocessing report.

Feature selection:

- Unsupervised top-variance feature selection.
- Default feature cap: 500 features per exported dataset.

## Commands Used

Export CSV datasets:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/export_cancer_tabpfn_csvs.py --view core --max-features 500
```

Run TabPFN3:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/run_tabpfn3_compare.py
```

Generate custom plots and report:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/make_cancer_exp_plots.py
```

## Main Outputs

Datasets:

- `datasets/*.csv`
- `datasets/manifest.json`
- `datasets/manifest.csv`

TabPFN3 evaluation:

- `outputs/tabpfn3_core/generation_summary.json`
- `outputs/tabpfn3_core/aggregate/generation_dataset_metrics.csv`
- `outputs/tabpfn3_core/aggregate/generation_mean_metrics.csv`
- `outputs/tabpfn3_core/runs/*/*/predictions/tabpfn_v3_predictions.csv`
- `outputs/tabpfn3_core/runs/*/*/raw/tabpfn_v3/raw_predictions.npz`
- `outputs/tabpfn3_core/runs/*/*/raw/tabpfn_v3/raw_predictions.json`
- `outputs/tabpfn3_core/runs/*/*/plots/*.png`

Custom plots:

- `plots/tabpfn3_metric_bars.png`
- `plots/tabpfn3_task_family_heatmap.png`
- `plots/tabpfn3_binary_roc_grid.png`
- `plots/all_core_cancer_type_top488_confusion_norm.png`

Report:

- `reports/tabpfn3_cancer_experiment_report.md`
- `reports/tabpfn_all_generations_cancer_report.md`

## Current Result Summary

All 10 exported datasets completed successfully with TabPFN3.

Mean metrics by task family:

| Task family | Accuracy | F1 | ROC AUC | Log loss |
|---|---:|---:|---:|---:|
| cancer_type | 0.9568 | 0.9601 | 0.9979 | 0.1386 |
| os_event | 0.6745 | 0.0671 | 0.5607 | 0.6007 |
| source | 0.9986 | 0.9992 | 0.9992 | 0.0069 |

Interpretation:

- Cancer-type prediction is very strong, suggesting the selected multiomics features clearly separate cancer types.
- Source prediction is nearly perfect, which is a warning sign: TCGA/CPTAC source effects remain highly detectable after preprocessing.
- OS-event prediction is weak despite moderate accuracy; low F1 suggests class imbalance and/or that event prediction is not well captured by this preliminary setup.

## Caveats

- These are preliminary runs.
- The package performs its own train/test split; it does not yet consume the original `splits.json` from the GPT preprocessing output.
- OS-event classification ignores censoring and should not be treated as a proper survival model.
- Feature selection is unsupervised and uses the full exported matrix. That is acceptable for a first diagnostic pass, but a stricter publication workflow should fit feature selection on train folds only.

## All-Generation Comparison

Legacy TabPFN v1 has a hard 100-feature input limit. To compare v1, v2, v2.5, v2.6, and v3 fairly, a separate top100 export was generated:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/export_cancer_tabpfn_csvs.py --view core --max-features 100 --output-dir /home/prime/Documents/g3/cancer-exp/datasets_top100
```

The legacy v1 worktree was restored at:

`/tmp/TabPFN_v1`

The five-generation comparison was run with:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/run_tabpfn_all_generations.py
```

The report and plots were generated with:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/make_all_generations_report.py
```

All-generation outputs:

- `outputs/tabpfn_all_generations_top100/aggregate/generation_dataset_metrics.csv`
- `outputs/tabpfn_all_generations_top100/aggregate/generation_mean_metrics.csv`
- `outputs/tabpfn_all_generations_top100/runs/*/*/predictions/*.csv`
- `outputs/tabpfn_all_generations_top100/runs/*/*/raw/*/raw_predictions.npz`
- `reports/tabpfn_all_generations_cancer_report.md`
- `reports/tabpfn_all_generations_mean_metrics.csv`
- `reports/tabpfn_all_generations_task_family_metrics.csv`
- `plots/all_generations_top100/*.png`
- `outputs/all_splits_predictions_top100/*/*/train_predictions.csv`
- `outputs/all_splits_predictions_top100/*/*/val_predictions.csv`
- `outputs/all_splits_predictions_top100/*/*/test_predictions.csv`
- `outputs/all_splits_predictions_top100/*/*/all_samples_predictions.csv`
- `outputs/all_splits_predictions_top100/*/*/all_samples_predictions.npz`

Mean metrics across the 10 top100 datasets:

| Model | Accuracy | F1 | ROC AUC | Log loss |
|---|---:|---:|---:|---:|
| TabPFN v1 | 0.8177 | 0.5124 | 0.7774 | 0.3525 |
| TabPFN v2 | 0.8218 | 0.6133 | 0.7889 | 0.3389 |
| TabPFN v2.5 | 0.8207 | 0.6144 | 0.7882 | 0.3272 |
| TabPFN v2.6 | 0.8223 | 0.5861 | 0.7854 | 0.3262 |
| TabPFN v3 | 0.8294 | 0.5676 | 0.7854 | 0.3215 |

## Full Train/Validation/Test Prediction Export

The package's standard generation-comparison output saves held-out test predictions because those are the predictions used for reported metrics. A separate experiment-side script was added to save predictions for every sample in every split.

Command:

```bash
python /home/prime/Documents/g3/cancer-exp/scripts/save_all_split_predictions.py
```

Output root:

`/home/prime/Documents/g3/cancer-exp/outputs/all_splits_predictions_top100`

For every dataset and every TabPFN generation, the script saves:

- `train_predictions.csv`
- `val_predictions.csv`
- `test_predictions.csv`
- `all_samples_predictions.csv`
- `all_samples_predictions.npz`

Each prediction row includes:

- dataset name
- model name
- TabPFN version
- split name
- original CSV row index
- true label
- predicted label
- encoded true/predicted labels
- probability columns for each class

Current export status:

- 10 datasets
- 5 TabPFN generations
- 50 successful model prediction bundles
- 0 failures
