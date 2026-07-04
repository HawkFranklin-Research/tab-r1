# Experiment 3: Combined Extreme Survival Contrast

This report is generated from saved prediction and metric artifacts. It does not rerun models.

## Run Configuration

```json
{
  "merged_from": [
    "/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/outputs_tabpfn",
    "/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/outputs_tabfm_pytorch"
  ],
  "experiment": "exp03_combined_extreme_survival"
}
```

## Dataset and Split Counts

| dataset | endpoint | source_cancers | n_total | n_train | n_val | n_test | class_0_train | class_1_train | class_0_test | class_1_test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | extreme_os | BRCA,HNSCC,LSCC,LUAD | 937 | 655 | 141 | 141 | 230 | 425 | 50 | 91 |

## Mean Metrics by Model

| model_name | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tabfm_default | 0.7872 | 0.8404 | 0.8026 | 0.8821 | 0.8681 | 0.6400 | 0.7541 | 0.4852 |
| tabpfn_v2 | 0.7872 | 0.8404 | 0.7967 | 0.8823 | 0.8681 | 0.6400 | 0.7541 | 0.4953 |
| tabpfn_v2_5 | 0.7872 | 0.8404 | 0.8305 | 0.8938 | 0.8681 | 0.6400 | 0.7541 | 0.4850 |
| tabpfn_v2_6 | 0.7872 | 0.8404 | 0.8215 | 0.8935 | 0.8681 | 0.6400 | 0.7541 | 0.4874 |
| tabpfn_v3 | 0.7872 | 0.8404 | 0.8163 | 0.8953 | 0.8681 | 0.6400 | 0.7541 | 0.4865 |

## Mean Metrics by Endpoint and Model

| endpoint | model_name | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| extreme_os | tabfm_default | 0.7872 | 0.8404 | 0.8026 | 0.8821 | 0.8681 | 0.6400 | 0.7541 | 0.4852 |
| extreme_os | tabpfn_v2 | 0.7872 | 0.8404 | 0.7967 | 0.8823 | 0.8681 | 0.6400 | 0.7541 | 0.4953 |
| extreme_os | tabpfn_v2_5 | 0.7872 | 0.8404 | 0.8305 | 0.8938 | 0.8681 | 0.6400 | 0.7541 | 0.4850 |
| extreme_os | tabpfn_v2_6 | 0.7872 | 0.8404 | 0.8215 | 0.8935 | 0.8681 | 0.6400 | 0.7541 | 0.4874 |
| extreme_os | tabpfn_v3 | 0.7872 | 0.8404 | 0.8163 | 0.8953 | 0.8681 | 0.6400 | 0.7541 | 0.4865 |

## Dataset-Level Model Metrics

| dataset | endpoint | model_name | status | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | extreme_os | tabpfn_v2 | success | 0.7872 | 0.8404 | 0.7967 | 0.8823 | 0.8681 | 0.6400 | 0.7541 | 0.4953 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | extreme_os | tabpfn_v2_5 | success | 0.7872 | 0.8404 | 0.8305 | 0.8938 | 0.8681 | 0.6400 | 0.7541 | 0.4850 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | extreme_os | tabpfn_v2_6 | success | 0.7872 | 0.8404 | 0.8215 | 0.8935 | 0.8681 | 0.6400 | 0.7541 | 0.4874 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | extreme_os | tabpfn_v3 | success | 0.7872 | 0.8404 | 0.8163 | 0.8953 | 0.8681 | 0.6400 | 0.7541 | 0.4865 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | extreme_os | tabfm_default | success | 0.7872 | 0.8404 | 0.8026 | 0.8821 | 0.8681 | 0.6400 | 0.7541 | 0.4852 |

## Cancer Subgroup Metrics

| dataset | model_name | cancer_type | n_test | class_0_test | class_1_test | pr_auc | sensitivity | specificity | balanced_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2 | BRCA | 44 | 32 | 12 | 0.2446 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2 | HNSCC | 36 | 2 | 34 | 0.9662 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2 | LSCC | 35 | 10 | 25 | 0.8001 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2 | LUAD | 26 | 6 | 20 | 0.7716 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_5 | BRCA | 44 | 32 | 12 | 0.4866 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_5 | HNSCC | 36 | 2 | 34 | 0.9547 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_5 | LSCC | 35 | 10 | 25 | 0.8206 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_5 | LUAD | 26 | 6 | 20 | 0.7679 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_6 | BRCA | 44 | 32 | 12 | 0.3870 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_6 | HNSCC | 36 | 2 | 34 | 0.9565 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_6 | LSCC | 35 | 10 | 25 | 0.8073 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v2_6 | LUAD | 26 | 6 | 20 | 0.8109 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v3 | BRCA | 44 | 32 | 12 | 0.3107 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v3 | HNSCC | 36 | 2 | 34 | 0.9625 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v3 | LSCC | 35 | 10 | 25 | 0.8280 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabpfn_v3 | LUAD | 26 | 6 | 20 | 0.8087 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabfm_default | BRCA | 44 | 32 | 12 | 0.2096 | 0.0000 | 1.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabfm_default | HNSCC | 36 | 2 | 34 | 0.9346 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabfm_default | LSCC | 35 | 10 | 25 | 0.7913 | 1.0000 | 0.0000 | 0.5000 |
| ALL_core_extreme_os_death_lt3yr_survival_ge5yr_top75_no_cancer_feature | tabfm_default | LUAD | 26 | 6 | 20 | 0.8176 | 1.0000 | 0.0000 | 0.5000 |

## Generated Plots

- `/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/reports/plots/mean_metrics_by_model.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/reports/plots/roc_auc_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/reports/plots/pr_auc_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/reports/plots/f1_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp03_combined_extreme_survival/reports/plots/log_loss_dataset_model_heatmap.png`
