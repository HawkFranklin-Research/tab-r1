# Experiment 2: Combined-Cancer Fixed-Window OS Event

This report is generated from saved prediction and metric artifacts. It does not rerun models.

## Run Configuration

```json
{
  "merged_from": [
    "/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/outputs_tabpfn",
    "/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/outputs_tabfm_pytorch"
  ],
  "experiment": "exp02_combined_fixed_window"
}
```

## Dataset and Split Counts

| dataset | endpoint | source_cancers | n_total | n_train | n_val | n_test | class_0_train | class_1_train | class_0_test | class_1_test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL_core_os_3yr_event_top94_no_cancer_feature | os_3yr | BRCA,ESCA,HNSCC,LSCC,LUAD | 1645 | 1151 | 247 | 247 | 678 | 473 | 145 | 102 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | os_5yr | BRCA,HNSCC,LSCC,LUAD | 1168 | 816 | 176 | 176 | 308 | 508 | 67 | 109 |

## Mean Metrics by Model

| model_name | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tabfm_default | 0.6778 | 0.6686 | 0.7136 | 0.6936 | 0.6870 | 0.6164 | 0.6517 | 0.5866 |
| tabpfn_v2 | 0.6758 | 0.6695 | 0.7208 | 0.6992 | 0.6919 | 0.6095 | 0.6507 | 0.5849 |
| tabpfn_v2_5 | 0.6960 | 0.6749 | 0.7200 | 0.7035 | 0.6723 | 0.6577 | 0.6650 | 0.5835 |
| tabpfn_v2_6 | 0.6818 | 0.6780 | 0.7155 | 0.7058 | 0.7017 | 0.6129 | 0.6573 | 0.5842 |
| tabpfn_v3 | 0.6778 | 0.6730 | 0.7192 | 0.6999 | 0.6968 | 0.6095 | 0.6532 | 0.5848 |

## Mean Metrics by Endpoint and Model

| endpoint | model_name | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| os_3yr | tabfm_default | 0.6397 | 0.5528 | 0.7334 | 0.6347 | 0.5392 | 0.7103 | 0.6248 | 0.5689 |
| os_3yr | tabpfn_v2 | 0.6356 | 0.5545 | 0.7283 | 0.6316 | 0.5490 | 0.6966 | 0.6228 | 0.5700 |
| os_3yr | tabpfn_v2_5 | 0.6761 | 0.5652 | 0.7427 | 0.6523 | 0.5098 | 0.7931 | 0.6515 | 0.5658 |
| os_3yr | tabpfn_v2_6 | 0.6478 | 0.5714 | 0.7358 | 0.6480 | 0.5686 | 0.7034 | 0.6360 | 0.5680 |
| os_3yr | tabpfn_v3 | 0.6397 | 0.5616 | 0.7308 | 0.6352 | 0.5588 | 0.6966 | 0.6277 | 0.5679 |
| os_5yr | tabfm_default | 0.7159 | 0.7845 | 0.6938 | 0.7524 | 0.8349 | 0.5224 | 0.6786 | 0.6044 |
| os_5yr | tabpfn_v2 | 0.7159 | 0.7845 | 0.7133 | 0.7667 | 0.8349 | 0.5224 | 0.6786 | 0.5997 |
| os_5yr | tabpfn_v2_5 | 0.7159 | 0.7845 | 0.6972 | 0.7548 | 0.8349 | 0.5224 | 0.6786 | 0.6012 |
| os_5yr | tabpfn_v2_6 | 0.7159 | 0.7845 | 0.6952 | 0.7637 | 0.8349 | 0.5224 | 0.6786 | 0.6003 |
| os_5yr | tabpfn_v3 | 0.7159 | 0.7845 | 0.7077 | 0.7645 | 0.8349 | 0.5224 | 0.6786 | 0.6017 |

## Dataset-Level Model Metrics

| dataset | endpoint | model_name | status | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL_core_os_3yr_event_top94_no_cancer_feature | os_3yr | tabpfn_v2 | success | 0.6356 | 0.5545 | 0.7283 | 0.6316 | 0.5490 | 0.6966 | 0.6228 | 0.5700 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | os_3yr | tabpfn_v2_5 | success | 0.6761 | 0.5652 | 0.7427 | 0.6523 | 0.5098 | 0.7931 | 0.6515 | 0.5658 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | os_3yr | tabpfn_v2_6 | success | 0.6478 | 0.5714 | 0.7358 | 0.6480 | 0.5686 | 0.7034 | 0.6360 | 0.5680 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | os_3yr | tabpfn_v3 | success | 0.6397 | 0.5616 | 0.7308 | 0.6352 | 0.5588 | 0.6966 | 0.6277 | 0.5679 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | os_5yr | tabpfn_v2 | success | 0.7159 | 0.7845 | 0.7133 | 0.7667 | 0.8349 | 0.5224 | 0.6786 | 0.5997 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | os_5yr | tabpfn_v2_5 | success | 0.7159 | 0.7845 | 0.6972 | 0.7548 | 0.8349 | 0.5224 | 0.6786 | 0.6012 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | os_5yr | tabpfn_v2_6 | success | 0.7159 | 0.7845 | 0.6952 | 0.7637 | 0.8349 | 0.5224 | 0.6786 | 0.6003 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | os_5yr | tabpfn_v3 | success | 0.7159 | 0.7845 | 0.7077 | 0.7645 | 0.8349 | 0.5224 | 0.6786 | 0.6017 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | os_3yr | tabfm_default | success | 0.6397 | 0.5528 | 0.7334 | 0.6347 | 0.5392 | 0.7103 | 0.6248 | 0.5689 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | os_5yr | tabfm_default | success | 0.7159 | 0.7845 | 0.6938 | 0.7524 | 0.8349 | 0.5224 | 0.6786 | 0.6044 |

## Cancer Subgroup Metrics

| dataset | model_name | cancer_type | n_test | class_0_test | class_1_test | pr_auc | sensitivity | specificity | balanced_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2 | BRCA | 77 | 68 | 9 | 0.2719 | 0.1111 | 1.0000 | 0.5556 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2 | ESCA | 12 | 1 | 11 | 0.9073 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2 | HNSCC | 62 | 29 | 33 | 0.5893 | 0.7879 | 0.3793 | 0.5836 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2 | LSCC | 47 | 27 | 20 | 0.5245 | 0.8500 | 0.1852 | 0.5176 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2 | LUAD | 49 | 20 | 29 | 0.5580 | 0.0345 | 0.8500 | 0.4422 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_5 | BRCA | 77 | 68 | 9 | 0.3134 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_5 | ESCA | 12 | 1 | 11 | 0.9255 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_5 | HNSCC | 62 | 29 | 33 | 0.6182 | 0.8485 | 0.3793 | 0.6139 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_5 | LSCC | 47 | 27 | 20 | 0.5108 | 0.6500 | 0.6296 | 0.6398 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_5 | LUAD | 49 | 20 | 29 | 0.5860 | 0.0000 | 0.9500 | 0.4750 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_6 | BRCA | 77 | 68 | 9 | 0.2215 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_6 | ESCA | 12 | 1 | 11 | 0.9536 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_6 | HNSCC | 62 | 29 | 33 | 0.5405 | 0.8182 | 0.3448 | 0.5815 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_6 | LSCC | 47 | 27 | 20 | 0.5334 | 1.0000 | 0.1481 | 0.5741 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v2_6 | LUAD | 49 | 20 | 29 | 0.5514 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v3 | BRCA | 77 | 68 | 9 | 0.2744 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v3 | ESCA | 12 | 1 | 11 | 0.9073 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v3 | HNSCC | 62 | 29 | 33 | 0.5757 | 0.8182 | 0.3448 | 0.5815 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v3 | LSCC | 47 | 27 | 20 | 0.5394 | 0.9500 | 0.1111 | 0.5306 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabpfn_v3 | LUAD | 49 | 20 | 29 | 0.5295 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2 | BRCA | 53 | 35 | 18 | 0.4263 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2 | HNSCC | 37 | 8 | 29 | 0.7901 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2 | LSCC | 51 | 16 | 35 | 0.8541 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2 | LUAD | 35 | 8 | 27 | 0.7192 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_5 | BRCA | 53 | 35 | 18 | 0.4304 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_5 | HNSCC | 37 | 8 | 29 | 0.7408 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_5 | LSCC | 51 | 16 | 35 | 0.7665 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_5 | LUAD | 35 | 8 | 27 | 0.7229 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_6 | BRCA | 53 | 35 | 18 | 0.3086 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_6 | HNSCC | 37 | 8 | 29 | 0.8475 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_6 | LSCC | 51 | 16 | 35 | 0.7282 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v2_6 | LUAD | 35 | 8 | 27 | 0.7230 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v3 | BRCA | 53 | 35 | 18 | 0.3516 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v3 | HNSCC | 37 | 8 | 29 | 0.7723 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v3 | LSCC | 51 | 16 | 35 | 0.8625 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabpfn_v3 | LUAD | 35 | 8 | 27 | 0.7176 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabfm_default | BRCA | 77 | 68 | 9 | 0.3322 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabfm_default | ESCA | 12 | 1 | 11 | 0.9536 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabfm_default | HNSCC | 62 | 29 | 33 | 0.5661 | 0.7879 | 0.3448 | 0.5664 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabfm_default | LSCC | 47 | 27 | 20 | 0.4905 | 0.9000 | 0.1852 | 0.5426 |
| ALL_core_os_3yr_event_top94_no_cancer_feature | tabfm_default | LUAD | 49 | 20 | 29 | 0.5749 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabfm_default | BRCA | 53 | 35 | 18 | 0.4125 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabfm_default | HNSCC | 37 | 8 | 29 | 0.7868 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabfm_default | LSCC | 51 | 16 | 35 | 0.7434 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_os_5yr_event_top75_no_cancer_feature | tabfm_default | LUAD | 35 | 8 | 27 | 0.7133 | 1.0000 | 0.0000 | 0.5000 |

## Generated Plots

- `/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/reports/plots/mean_metrics_by_model.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/reports/plots/roc_auc_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/reports/plots/pr_auc_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/reports/plots/f1_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp02_combined_fixed_window/reports/plots/log_loss_dataset_model_heatmap.png`
