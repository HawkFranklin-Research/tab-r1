# TabPFN3 Cancer Experiment Report

- Output root: `/home/prime/Documents/g3/cancer-exp/outputs/tabpfn3_core`
- Successful rows: 10 / 10
- Input matrices came from `gpt/processed/train_ready`, exported into dense CSVs with clinical features excluded.
- Feature selection: unsupervised top-variance non-clinical features.
- Caveat: OS-event prediction is preliminary because censoring/time-to-event modeling is not handled here.

## Dataset Metrics

| dataset                     | model_name   | version   | task_type   | status   |   accuracy |       f1 |   roc_auc |    log_loss | task_family   |
|:----------------------------|:-------------|:----------|:------------|:---------|-----------:|---------:|----------:|------------:|:--------------|
| ALL_core_cancer_type_top488 | tabpfn_v3    | v3        | multiclass  | success  |   0.95679  | 0.960086 |  0.997906 | 0.138611    | cancer_type   |
| BRCA_core_os_event_top500   | tabpfn_v3    | v3        | binary      | success  |   0.870787 | 0        |  0.425806 | 0.391062    | os_event      |
| BRCA_core_source_top500     | tabpfn_v3    | v3        | binary      | success  |   0.994475 | 0.996923 |  0.996933 | 0.0238765   | source        |
| ESCA_core_os_event_top500   | tabpfn_v3    | v3        | binary      | success  |   0.607143 | 0.153846 |  0.59375  | 0.675479    | os_event      |
| HNSCC_core_os_event_top500  | tabpfn_v3    | v3        | binary      | success  |   0.621053 | 0.181818 |  0.622807 | 0.655829    | os_event      |
| HNSCC_core_source_top500    | tabpfn_v3    | v3        | binary      | success  |   1        | 1        |  1        | 1.3679e-05  | source        |
| LSCC_core_os_event_top500   | tabpfn_v3    | v3        | binary      | success  |   0.606742 | 0        |  0.508466 | 0.659826    | os_event      |
| LSCC_core_source_top500     | tabpfn_v3    | v3        | binary      | success  |   1        | 1        |  1        | 1.42012e-05 | source        |
| LUAD_core_os_event_top500   | tabpfn_v3    | v3        | binary      | success  |   0.666667 | 0        |  0.652445 | 0.62115     | os_event      |
| LUAD_core_source_top500     | tabpfn_v3    | v3        | binary      | success  |   1        | 1        |  1        | 0.00388947  | source        |

## Mean Metrics By Task Family

| task_family   |   accuracy |        f1 |   roc_auc |   log_loss |
|:--------------|-----------:|----------:|----------:|-----------:|
| cancer_type   |   0.95679  | 0.960086  |  0.997906 | 0.138611   |
| os_event      |   0.674478 | 0.0671329 |  0.560655 | 0.600669   |
| source        |   0.998619 | 0.999231  |  0.999233 | 0.00694847 |

## Generated Plots

- `/home/prime/Documents/g3/cancer-exp/plots/tabpfn3_metric_bars.png`
- `/home/prime/Documents/g3/cancer-exp/plots/tabpfn3_task_family_heatmap.png`
- `/home/prime/Documents/g3/cancer-exp/plots/tabpfn3_binary_roc_grid.png`
- `/home/prime/Documents/g3/cancer-exp/plots/all_core_cancer_type_top488_confusion_norm.png`
