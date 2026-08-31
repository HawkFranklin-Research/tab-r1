# Full Leakage-Safe Classical Model Results

All values are macro-averages across independently generated patient-grouped folds. Feature selection was fitted on training rows only, and classification thresholds were selected using validation data only.

- Fold records: 400
- Model/fold runs: 2000
- Successful runs: 2000
- Failed runs: 0

## Overall Macro-Average Across 400 Folds

| model_name          |   n_fold_runs |   accuracy_mean |   balanced_accuracy_mean |   f1_mean |   roc_auc_mean |   pr_auc_mean |   log_loss_mean |   brier_mean |   fit_time_s_mean |
|:--------------------|--------------:|----------------:|-------------------------:|----------:|---------------:|--------------:|----------------:|-------------:|------------------:|
| random_forest       |           400 |          0.5708 |                   0.5638 |    0.5511 |         0.5946 |        0.6729 |          0.5872 |       0.1916 |            0.3566 |
| catboost            |           400 |          0.5644 |                   0.5647 |    0.5354 |         0.5927 |        0.6744 |          0.5745 |       0.1915 |            1.7631 |
| xgboost             |           400 |          0.5654 |                   0.5618 |    0.5415 |         0.5885 |        0.6671 |          0.7279 |       0.2199 |            0.1933 |
| lightgbm            |           400 |          0.5715 |                   0.5580 |    0.5434 |         0.5850 |        0.6644 |          0.8730 |       0.2304 |            0.0897 |
| logistic_regression |           400 |          0.5228 |                   0.5150 |    0.4813 |         0.5245 |        0.6214 |          0.6490 |       0.2143 |            0.0112 |

## Per-Cancer Tasks

| endpoint   | model_name          |   n_fold_runs |   balanced_accuracy_mean |   roc_auc_mean |   pr_auc_mean |   log_loss_mean |   brier_mean |
|:-----------|:--------------------|--------------:|-------------------------:|---------------:|--------------:|----------------:|-------------:|
| extreme_os | catboost            |           100 |                   0.5428 |         0.5884 |        0.7301 |          0.5361 |       0.1719 |
| extreme_os | random_forest       |           100 |                   0.5434 |         0.5830 |        0.7272 |          0.5616 |       0.1718 |
| extreme_os | lightgbm            |           100 |                   0.5423 |         0.5720 |        0.7180 |          0.8723 |       0.2055 |
| extreme_os | xgboost             |           100 |                   0.5426 |         0.5709 |        0.7204 |          0.6965 |       0.1951 |
| extreme_os | logistic_regression |           100 |                   0.5193 |         0.5377 |        0.6963 |          0.5911 |       0.1850 |
| os_3yr     | xgboost             |           125 |                   0.5254 |         0.5440 |        0.5567 |          0.7700 |       0.2454 |
| os_3yr     | random_forest       |           125 |                   0.5207 |         0.5432 |        0.5534 |          0.6185 |       0.2105 |
| os_3yr     | catboost            |           125 |                   0.5214 |         0.5362 |        0.5574 |          0.6114 |       0.2100 |
| os_3yr     | lightgbm            |           125 |                   0.5219 |         0.5341 |        0.5550 |          0.8642 |       0.2521 |
| os_3yr     | logistic_regression |           125 |                   0.4961 |         0.5063 |        0.5282 |          0.6606 |       0.2235 |
| os_5yr     | lightgbm            |           100 |                   0.5294 |         0.5557 |        0.7019 |          0.9057 |       0.2302 |
| os_5yr     | random_forest       |           100 |                   0.5399 |         0.5555 |        0.7091 |          0.5839 |       0.1897 |
| os_5yr     | xgboost             |           100 |                   0.5355 |         0.5526 |        0.7007 |          0.7478 |       0.2201 |
| os_5yr     | catboost            |           100 |                   0.5403 |         0.5510 |        0.7069 |          0.5736 |       0.1898 |
| os_5yr     | logistic_regression |           100 |                   0.5209 |         0.5272 |        0.6811 |          0.6180 |       0.2004 |

## Pooled Tasks

| endpoint   | model_name          |   n_fold_runs |   balanced_accuracy_mean |   roc_auc_mean |   pr_auc_mean |   log_loss_mean |   brier_mean |
|:-----------|:--------------------|--------------:|-------------------------:|---------------:|--------------:|----------------:|-------------:|
| extreme_os | catboost            |            25 |                   0.7306 |         0.7819 |        0.8392 |          0.5239 |       0.1691 |
| extreme_os | random_forest       |            25 |                   0.7234 |         0.7808 |        0.8468 |          0.5441 |       0.1701 |
| extreme_os | xgboost             |            25 |                   0.7161 |         0.7680 |        0.8286 |          0.6482 |       0.1889 |
| extreme_os | lightgbm            |            25 |                   0.7096 |         0.7619 |        0.8198 |          0.8333 |       0.2019 |
| extreme_os | logistic_regression |            25 |                   0.5263 |         0.5223 |        0.6694 |          0.7930 |       0.2607 |
| os_3yr     | random_forest       |            25 |                   0.6629 |         0.7160 |        0.6000 |          0.6031 |       0.2083 |
| os_3yr     | catboost            |            25 |                   0.6611 |         0.7129 |        0.6075 |          0.6078 |       0.2101 |
| os_3yr     | xgboost             |            25 |                   0.6502 |         0.7007 |        0.5875 |          0.6914 |       0.2309 |
| os_3yr     | lightgbm            |            25 |                   0.6507 |         0.6981 |        0.5849 |          0.8296 |       0.2504 |
| os_3yr     | logistic_regression |            25 |                   0.5267 |         0.5359 |        0.4588 |          0.7093 |       0.2525 |
| os_5yr     | catboost            |            25 |                   0.7038 |         0.7485 |        0.8087 |          0.5655 |       0.1884 |
| os_5yr     | random_forest       |            25 |                   0.6981 |         0.7471 |        0.8077 |          0.5739 |       0.1889 |
| os_5yr     | xgboost             |            25 |                   0.6835 |         0.7337 |        0.7894 |          0.6794 |       0.2110 |
| os_5yr     | lightgbm            |            25 |                   0.6710 |         0.7192 |        0.7717 |          0.8729 |       0.2307 |
| os_5yr     | logistic_regression |            25 |                   0.5460 |         0.5419 |        0.6635 |          0.7418 |       0.2559 |

## Interpretation Contract

- Overall rows are fold-macro-averages, not one pooled patient-level score.
- Repeated folds reuse patients across repeats; `n_fold_runs` is the number of fitted folds, not the number of unique patients.
- PR AUC must be interpreted alongside endpoint prevalence.
- The pooled tasks remain subject to the separately measured cancer-identity and structural-missingness shortcut controls.
