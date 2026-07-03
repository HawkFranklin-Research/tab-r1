# Final Benchmark Evaluation Summary

This table summarizes the performance across all successfully evaluated datasets in this batch.

  ┌────────────┬───────────────┬───────────────┬───────────────────┐
  │ Model      │ ROC_AUC        │ ACCURACY       │ Mean Fit Time (s) │
  ├────────────┼───────────────┼───────────────┼───────────────────┤
  │ autogluon  │ 0.861 ± 0.11   │ 0.811 ± 0.17   │ 9.611            s │
  │ catboost   │ 0.873 ± 0.11   │ 0.823 ± 0.17   │ 1.093            s │
  │ lightgbm   │ 0.854 ± 0.12   │ 0.811 ± 0.18   │ 0.223            s │
  │ logistic_regression │ 0.797 ± 0.09   │ 0.736 ± 0.13   │ 0.011            s │
  │ random_forest │ 0.855 ± 0.11   │ 0.813 ± 0.17   │ 0.264            s │
  │ tabpfn     │ 0.877 ± 0.10   │ 0.829 ± 0.17   │ 0.446            s │
  │ xgboost    │ 0.863 ± 0.11   │ 0.818 ± 0.17   │ 0.525            s │
  └────────────┴───────────────┴───────────────┴───────────────────┘

*Note: Mean ± Std Dev computed across all successful runs.*
