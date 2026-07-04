# Experiment 1: Per-Cancer Fixed-Window OS Event

This report is generated from saved prediction and metric artifacts. It does not rerun models.

## Run Configuration

```json
{
  "merged_from": [
    "/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/outputs_tabpfn",
    "/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/outputs_tabfm_pytorch"
  ],
  "experiment": "exp01_per_cancer_fixed_window"
}
```

## Dataset and Split Counts

| dataset | endpoint | source_cancers | n_total | n_train | n_val | n_test | class_0_train | class_1_train | class_0_test | class_1_test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BRCA_core_os_3yr_event_top100 | os_3yr | BRCA | 501 | 350 | 75 | 76 | 301 | 49 | 65 | 11 |
| BRCA_core_os_5yr_event_top100 | os_5yr | BRCA | 350 | 244 | 53 | 53 | 173 | 71 | 38 | 15 |
| ESCA_core_os_3yr_event_top100 | os_3yr | ESCA | 86 | 60 | 13 | 13 | 12 | 48 | 3 | 10 |
| HNSCC_core_os_3yr_event_top100 | os_3yr | HNSCC | 385 | 269 | 58 | 58 | 123 | 146 | 26 | 32 |
| HNSCC_core_os_5yr_event_top100 | os_5yr | HNSCC | 286 | 200 | 43 | 43 | 38 | 162 | 8 | 35 |
| LSCC_core_os_3yr_event_top100 | os_3yr | LSCC | 355 | 247 | 54 | 54 | 129 | 118 | 28 | 26 |
| LSCC_core_os_5yr_event_top100 | os_5yr | LSCC | 281 | 196 | 42 | 43 | 57 | 139 | 13 | 30 |
| LUAD_core_os_3yr_event_top100 | os_3yr | LUAD | 318 | 222 | 48 | 48 | 113 | 109 | 24 | 24 |
| LUAD_core_os_5yr_event_top100 | os_5yr | LUAD | 251 | 175 | 38 | 38 | 39 | 136 | 9 | 29 |

## Mean Metrics by Model

| model_name | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tabfm_default | 0.6845 | 0.6108 | 0.5377 | 0.6258 | 0.6674 | 0.3628 | 0.5151 | 0.6089 |
| tabpfn_v2 | 0.6714 | 0.5117 | 0.5210 | 0.6194 | 0.5933 | 0.3806 | 0.4870 | 0.5821 |
| tabpfn_v2_5 | 0.6774 | 0.5286 | 0.5051 | 0.6205 | 0.5999 | 0.3881 | 0.4940 | 0.5852 |
| tabpfn_v2_6 | 0.6749 | 0.5913 | 0.5240 | 0.6349 | 0.6519 | 0.3468 | 0.4993 | 0.5863 |
| tabpfn_v3 | 0.6779 | 0.5583 | 0.5420 | 0.6298 | 0.6193 | 0.3789 | 0.4991 | 0.5787 |

## Mean Metrics by Endpoint and Model

| endpoint | model_name | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| os_3yr | tabfm_default | 0.6308 | 0.5401 | 0.5096 | 0.5507 | 0.5940 | 0.4154 | 0.5047 | 0.6601 |
| os_3yr | tabpfn_v2 | 0.6101 | 0.4041 | 0.4744 | 0.5103 | 0.4679 | 0.4851 | 0.4765 | 0.6105 |
| os_3yr | tabpfn_v2_5 | 0.6209 | 0.4345 | 0.4538 | 0.5183 | 0.4798 | 0.4986 | 0.4892 | 0.6148 |
| os_3yr | tabpfn_v2_6 | 0.6266 | 0.5325 | 0.5007 | 0.5622 | 0.5800 | 0.4242 | 0.5021 | 0.6104 |
| os_3yr | tabpfn_v3 | 0.6182 | 0.4629 | 0.5000 | 0.5287 | 0.5014 | 0.4820 | 0.4917 | 0.6059 |
| os_5yr | tabfm_default | 0.7516 | 0.6992 | 0.5728 | 0.7197 | 0.7592 | 0.2970 | 0.5281 | 0.5449 |
| os_5yr | tabpfn_v2 | 0.7479 | 0.6463 | 0.5793 | 0.7558 | 0.7500 | 0.2500 | 0.5000 | 0.5466 |
| os_5yr | tabpfn_v2_5 | 0.7479 | 0.6463 | 0.5692 | 0.7482 | 0.7500 | 0.2500 | 0.5000 | 0.5483 |
| os_5yr | tabpfn_v2_6 | 0.7352 | 0.6649 | 0.5531 | 0.7257 | 0.7417 | 0.2500 | 0.4958 | 0.5561 |
| os_5yr | tabpfn_v3 | 0.7527 | 0.6775 | 0.5944 | 0.7562 | 0.7667 | 0.2500 | 0.5083 | 0.5447 |

## Dataset-Level Model Metrics

| dataset | endpoint | model_name | status | accuracy | f1 | roc_auc | pr_auc | sensitivity | specificity | balanced_accuracy | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BRCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v2 | success | 0.8553 | 0.0000 | 0.7217 | 0.3507 | 0.0000 | 1.0000 | 0.5000 | 0.3835 |
| BRCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_5 | success | 0.8553 | 0.0000 | 0.6420 | 0.3829 | 0.0000 | 1.0000 | 0.5000 | 0.3885 |
| BRCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_6 | success | 0.8684 | 0.1667 | 0.6420 | 0.4254 | 0.0909 | 1.0000 | 0.5455 | 0.3694 |
| BRCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v3 | success | 0.8684 | 0.1667 | 0.5664 | 0.3083 | 0.0909 | 1.0000 | 0.5455 | 0.3876 |
| BRCA_core_os_5yr_event_top100 | os_5yr | tabpfn_v2 | success | 0.7170 | 0.0000 | 0.6035 | 0.5108 | 0.0000 | 1.0000 | 0.5000 | 0.5805 |
| BRCA_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_5 | success | 0.7170 | 0.0000 | 0.5947 | 0.4603 | 0.0000 | 1.0000 | 0.5000 | 0.5763 |
| BRCA_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_6 | success | 0.7358 | 0.1250 | 0.5465 | 0.3997 | 0.0667 | 1.0000 | 0.5333 | 0.5829 |
| BRCA_core_os_5yr_event_top100 | os_5yr | tabpfn_v3 | success | 0.7358 | 0.1250 | 0.5842 | 0.4359 | 0.0667 | 1.0000 | 0.5333 | 0.5719 |
| ESCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v2 | success | 0.7692 | 0.8696 | 0.2333 | 0.6677 | 1.0000 | 0.0000 | 0.5000 | 0.5596 |
| ESCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_5 | success | 0.7692 | 0.8696 | 0.2333 | 0.6761 | 1.0000 | 0.0000 | 0.5000 | 0.5736 |
| ESCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_6 | success | 0.7692 | 0.8696 | 0.4000 | 0.8077 | 1.0000 | 0.0000 | 0.5000 | 0.5781 |
| ESCA_core_os_3yr_event_top100 | os_3yr | tabpfn_v3 | success | 0.7692 | 0.8696 | 0.5333 | 0.8072 | 1.0000 | 0.0000 | 0.5000 | 0.5507 |
| HNSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v2 | success | 0.5000 | 0.6588 | 0.4603 | 0.5169 | 0.8750 | 0.0385 | 0.4567 | 0.7067 |
| HNSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_5 | success | 0.5172 | 0.6500 | 0.4513 | 0.5143 | 0.8125 | 0.1538 | 0.4832 | 0.7071 |
| HNSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_6 | success | 0.5345 | 0.6582 | 0.5264 | 0.5792 | 0.8125 | 0.1923 | 0.5024 | 0.6899 |
| HNSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v3 | success | 0.5690 | 0.6988 | 0.4639 | 0.5403 | 0.9062 | 0.1538 | 0.5300 | 0.6936 |
| HNSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v2 | success | 0.8140 | 0.8974 | 0.6857 | 0.8910 | 1.0000 | 0.0000 | 0.5000 | 0.4527 |
| HNSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_5 | success | 0.8140 | 0.8974 | 0.6286 | 0.8790 | 1.0000 | 0.0000 | 0.5000 | 0.4653 |
| HNSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_6 | success | 0.8140 | 0.8974 | 0.6500 | 0.8864 | 1.0000 | 0.0000 | 0.5000 | 0.4518 |
| HNSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v3 | success | 0.8140 | 0.8974 | 0.6250 | 0.8847 | 1.0000 | 0.0000 | 0.5000 | 0.4609 |
| LSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v2 | success | 0.4259 | 0.4151 | 0.4464 | 0.4769 | 0.4231 | 0.4286 | 0.4258 | 0.7104 |
| LSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_5 | success | 0.4630 | 0.4528 | 0.4712 | 0.5001 | 0.4615 | 0.4643 | 0.4629 | 0.7113 |
| LSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_6 | success | 0.4815 | 0.5000 | 0.4670 | 0.4757 | 0.5385 | 0.4286 | 0.4835 | 0.7140 |
| LSCC_core_os_3yr_event_top100 | os_3yr | tabpfn_v3 | success | 0.4259 | 0.3922 | 0.4780 | 0.4864 | 0.3846 | 0.4643 | 0.4245 | 0.7040 |
| LSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v2 | success | 0.6977 | 0.8219 | 0.5987 | 0.8212 | 1.0000 | 0.0000 | 0.5000 | 0.5956 |
| LSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_5 | success | 0.6977 | 0.8219 | 0.5859 | 0.8210 | 1.0000 | 0.0000 | 0.5000 | 0.5960 |
| LSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_6 | success | 0.6279 | 0.7714 | 0.5333 | 0.7835 | 0.9000 | 0.0000 | 0.4500 | 0.6180 |
| LSCC_core_os_5yr_event_top100 | os_5yr | tabpfn_v3 | success | 0.6977 | 0.8219 | 0.6282 | 0.8518 | 1.0000 | 0.0000 | 0.5000 | 0.5938 |
| LUAD_core_os_3yr_event_top100 | os_3yr | tabpfn_v2 | success | 0.5000 | 0.0769 | 0.5104 | 0.5391 | 0.0417 | 0.9583 | 0.5000 | 0.6920 |
| LUAD_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_5 | success | 0.5000 | 0.2000 | 0.4714 | 0.5184 | 0.1250 | 0.8750 | 0.5000 | 0.6935 |
| LUAD_core_os_3yr_event_top100 | os_3yr | tabpfn_v2_6 | success | 0.4792 | 0.4681 | 0.4679 | 0.5230 | 0.4583 | 0.5000 | 0.4792 | 0.7007 |
| LUAD_core_os_3yr_event_top100 | os_3yr | tabpfn_v3 | success | 0.4583 | 0.1875 | 0.4583 | 0.5012 | 0.1250 | 0.7917 | 0.4583 | 0.6935 |
| LUAD_core_os_5yr_event_top100 | os_5yr | tabpfn_v2 | success | 0.7632 | 0.8657 | 0.4291 | 0.8003 | 1.0000 | 0.0000 | 0.5000 | 0.5576 |
| LUAD_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_5 | success | 0.7632 | 0.8657 | 0.4674 | 0.8326 | 1.0000 | 0.0000 | 0.5000 | 0.5555 |
| LUAD_core_os_5yr_event_top100 | os_5yr | tabpfn_v2_6 | success | 0.7632 | 0.8657 | 0.4828 | 0.8332 | 1.0000 | 0.0000 | 0.5000 | 0.5716 |
| LUAD_core_os_5yr_event_top100 | os_5yr | tabpfn_v3 | success | 0.7632 | 0.8657 | 0.5402 | 0.8525 | 1.0000 | 0.0000 | 0.5000 | 0.5521 |
| BRCA_core_os_3yr_event_top100 | os_3yr | tabfm_default | success | 0.8684 | 0.1667 | 0.5909 | 0.3590 | 0.0909 | 1.0000 | 0.5455 | 0.3820 |
| BRCA_core_os_5yr_event_top100 | os_5yr | tabfm_default | success | 0.7547 | 0.2353 | 0.5456 | 0.4103 | 0.1333 | 1.0000 | 0.5667 | 0.5693 |
| ESCA_core_os_3yr_event_top100 | os_3yr | tabfm_default | success | 0.7692 | 0.8696 | 0.5667 | 0.8611 | 1.0000 | 0.0000 | 0.5000 | 0.7137 |
| HNSCC_core_os_3yr_event_top100 | os_3yr | tabfm_default | success | 0.5000 | 0.6506 | 0.4471 | 0.5042 | 0.8438 | 0.0769 | 0.4603 | 0.6997 |
| HNSCC_core_os_5yr_event_top100 | os_5yr | tabfm_default | success | 0.7907 | 0.8831 | 0.5911 | 0.8697 | 0.9714 | 0.0000 | 0.4857 | 0.4757 |
| LSCC_core_os_3yr_event_top100 | os_3yr | tabfm_default | success | 0.5370 | 0.5455 | 0.4911 | 0.5279 | 0.5769 | 0.5000 | 0.5385 | 0.7113 |
| LSCC_core_os_5yr_event_top100 | os_5yr | tabfm_default | success | 0.6977 | 0.8169 | 0.6410 | 0.8306 | 0.9667 | 0.0769 | 0.5218 | 0.5900 |
| LUAD_core_os_3yr_event_top100 | os_3yr | tabfm_default | success | 0.4792 | 0.4681 | 0.4523 | 0.5010 | 0.4583 | 0.5000 | 0.4792 | 0.7937 |
| LUAD_core_os_5yr_event_top100 | os_5yr | tabfm_default | success | 0.7632 | 0.8615 | 0.5134 | 0.7682 | 0.9655 | 0.1111 | 0.5383 | 0.5445 |

## Cancer Subgroup Metrics

| dataset | model_name | cancer_type | n_test | class_0_test | class_1_test | pr_auc | sensitivity | specificity | balanced_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BRCA_core_os_3yr_event_top100 | tabpfn_v2 | BRCA | 76 | 65 | 11 | 0.3507 | 0.0000 | 1.0000 | 0.5000 |
| BRCA_core_os_3yr_event_top100 | tabpfn_v2_5 | BRCA | 76 | 65 | 11 | 0.3829 | 0.0000 | 1.0000 | 0.5000 |
| BRCA_core_os_3yr_event_top100 | tabpfn_v2_6 | BRCA | 76 | 65 | 11 | 0.4254 | 0.0909 | 1.0000 | 0.5455 |
| BRCA_core_os_3yr_event_top100 | tabpfn_v3 | BRCA | 76 | 65 | 11 | 0.3083 | 0.0909 | 1.0000 | 0.5455 |
| BRCA_core_os_5yr_event_top100 | tabpfn_v2 | BRCA | 53 | 38 | 15 | 0.5108 | 0.0000 | 1.0000 | 0.5000 |
| BRCA_core_os_5yr_event_top100 | tabpfn_v2_5 | BRCA | 53 | 38 | 15 | 0.4603 | 0.0000 | 1.0000 | 0.5000 |
| BRCA_core_os_5yr_event_top100 | tabpfn_v2_6 | BRCA | 53 | 38 | 15 | 0.3997 | 0.0667 | 1.0000 | 0.5333 |
| BRCA_core_os_5yr_event_top100 | tabpfn_v3 | BRCA | 53 | 38 | 15 | 0.4359 | 0.0667 | 1.0000 | 0.5333 |
| ESCA_core_os_3yr_event_top100 | tabpfn_v2 | ESCA | 13 | 3 | 10 | 0.6677 | 1.0000 | 0.0000 | 0.5000 |
| ESCA_core_os_3yr_event_top100 | tabpfn_v2_5 | ESCA | 13 | 3 | 10 | 0.6761 | 1.0000 | 0.0000 | 0.5000 |
| ESCA_core_os_3yr_event_top100 | tabpfn_v2_6 | ESCA | 13 | 3 | 10 | 0.8077 | 1.0000 | 0.0000 | 0.5000 |
| ESCA_core_os_3yr_event_top100 | tabpfn_v3 | ESCA | 13 | 3 | 10 | 0.8072 | 1.0000 | 0.0000 | 0.5000 |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v2 | HNSCC | 58 | 26 | 32 | 0.5169 | 0.8750 | 0.0385 | 0.4567 |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v2_5 | HNSCC | 58 | 26 | 32 | 0.5143 | 0.8125 | 0.1538 | 0.4832 |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v2_6 | HNSCC | 58 | 26 | 32 | 0.5792 | 0.8125 | 0.1923 | 0.5024 |
| HNSCC_core_os_3yr_event_top100 | tabpfn_v3 | HNSCC | 58 | 26 | 32 | 0.5403 | 0.9062 | 0.1538 | 0.5300 |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v2 | HNSCC | 43 | 8 | 35 | 0.8910 | 1.0000 | 0.0000 | 0.5000 |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v2_5 | HNSCC | 43 | 8 | 35 | 0.8790 | 1.0000 | 0.0000 | 0.5000 |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v2_6 | HNSCC | 43 | 8 | 35 | 0.8864 | 1.0000 | 0.0000 | 0.5000 |
| HNSCC_core_os_5yr_event_top100 | tabpfn_v3 | HNSCC | 43 | 8 | 35 | 0.8847 | 1.0000 | 0.0000 | 0.5000 |
| LSCC_core_os_3yr_event_top100 | tabpfn_v2 | LSCC | 54 | 28 | 26 | 0.4769 | 0.4231 | 0.4286 | 0.4258 |
| LSCC_core_os_3yr_event_top100 | tabpfn_v2_5 | LSCC | 54 | 28 | 26 | 0.5001 | 0.4615 | 0.4643 | 0.4629 |
| LSCC_core_os_3yr_event_top100 | tabpfn_v2_6 | LSCC | 54 | 28 | 26 | 0.4757 | 0.5385 | 0.4286 | 0.4835 |
| LSCC_core_os_3yr_event_top100 | tabpfn_v3 | LSCC | 54 | 28 | 26 | 0.4864 | 0.3846 | 0.4643 | 0.4245 |
| LSCC_core_os_5yr_event_top100 | tabpfn_v2 | LSCC | 43 | 13 | 30 | 0.8212 | 1.0000 | 0.0000 | 0.5000 |
| LSCC_core_os_5yr_event_top100 | tabpfn_v2_5 | LSCC | 43 | 13 | 30 | 0.8210 | 1.0000 | 0.0000 | 0.5000 |
| LSCC_core_os_5yr_event_top100 | tabpfn_v2_6 | LSCC | 43 | 13 | 30 | 0.7835 | 0.9000 | 0.0000 | 0.4500 |
| LSCC_core_os_5yr_event_top100 | tabpfn_v3 | LSCC | 43 | 13 | 30 | 0.8518 | 1.0000 | 0.0000 | 0.5000 |
| LUAD_core_os_3yr_event_top100 | tabpfn_v2 | LUAD | 48 | 24 | 24 | 0.5391 | 0.0417 | 0.9583 | 0.5000 |
| LUAD_core_os_3yr_event_top100 | tabpfn_v2_5 | LUAD | 48 | 24 | 24 | 0.5184 | 0.1250 | 0.8750 | 0.5000 |
| LUAD_core_os_3yr_event_top100 | tabpfn_v2_6 | LUAD | 48 | 24 | 24 | 0.5230 | 0.4583 | 0.5000 | 0.4792 |
| LUAD_core_os_3yr_event_top100 | tabpfn_v3 | LUAD | 48 | 24 | 24 | 0.5012 | 0.1250 | 0.7917 | 0.4583 |
| LUAD_core_os_5yr_event_top100 | tabpfn_v2 | LUAD | 38 | 9 | 29 | 0.8003 | 1.0000 | 0.0000 | 0.5000 |
| LUAD_core_os_5yr_event_top100 | tabpfn_v2_5 | LUAD | 38 | 9 | 29 | 0.8326 | 1.0000 | 0.0000 | 0.5000 |
| LUAD_core_os_5yr_event_top100 | tabpfn_v2_6 | LUAD | 38 | 9 | 29 | 0.8332 | 1.0000 | 0.0000 | 0.5000 |
| LUAD_core_os_5yr_event_top100 | tabpfn_v3 | LUAD | 38 | 9 | 29 | 0.8525 | 1.0000 | 0.0000 | 0.5000 |
| BRCA_core_os_3yr_event_top100 | tabfm_default | BRCA | 76 | 65 | 11 | 0.3590 | 0.0909 | 1.0000 | 0.5455 |
| BRCA_core_os_5yr_event_top100 | tabfm_default | BRCA | 53 | 38 | 15 | 0.4103 | 0.1333 | 1.0000 | 0.5667 |
| ESCA_core_os_3yr_event_top100 | tabfm_default | ESCA | 13 | 3 | 10 | 0.8611 | 1.0000 | 0.0000 | 0.5000 |
| HNSCC_core_os_3yr_event_top100 | tabfm_default | HNSCC | 58 | 26 | 32 | 0.5042 | 0.8438 | 0.0769 | 0.4603 |
| HNSCC_core_os_5yr_event_top100 | tabfm_default | HNSCC | 43 | 8 | 35 | 0.8697 | 0.9714 | 0.0000 | 0.4857 |
| LSCC_core_os_3yr_event_top100 | tabfm_default | LSCC | 54 | 28 | 26 | 0.5279 | 0.5769 | 0.5000 | 0.5385 |
| LSCC_core_os_5yr_event_top100 | tabfm_default | LSCC | 43 | 13 | 30 | 0.8306 | 0.9667 | 0.0769 | 0.5218 |
| LUAD_core_os_3yr_event_top100 | tabfm_default | LUAD | 48 | 24 | 24 | 0.5010 | 0.4583 | 0.5000 | 0.4792 |
| LUAD_core_os_5yr_event_top100 | tabfm_default | LUAD | 38 | 9 | 29 | 0.7682 | 0.9655 | 0.1111 | 0.5383 |

## Generated Plots

- `/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/reports/plots/mean_metrics_by_model.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/reports/plots/roc_auc_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/reports/plots/pr_auc_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/reports/plots/f1_dataset_model_heatmap.png`
- `/home/prime/Documents/g3/cancer-os-exp/exp01_per_cancer_fixed_window/reports/plots/log_loss_dataset_model_heatmap.png`
