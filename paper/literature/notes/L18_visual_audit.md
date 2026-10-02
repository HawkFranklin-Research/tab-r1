# L18: Figure and table review

Source: pdfs/L18.pdf, *Accurate predictions on small data with a tabular foundation model* (2025), DOI 10.1038/s41586-024-08328-6.

## Figure 4, printed comparative values, PDF page 5

The nearby Results text reports the plotted normalized scores:

| Task / setting | TabPFN | CatBoost |
|---|---:|---:|
| Classification, default normalized ROC AUC | 0.939 | 0.752 |
| Classification, tuned normalized ROC AUC | 0.932 | 0.822 |
| Regression, default normalized negative RMSE | 0.923 | 0.872 |
| Regression, tuned normalized negative RMSE | 0.968 | 0.875 |

Figure 4b reports Wilcoxon p < 0.001 for default and tuned classification, p = 0.0153 for default regression, and p < 0.001 for tuned regression. Figure 4c plots performance against fit-plus-predict time; labels are not attached to each plotted point. Prose reports 2.8 s average classification time and 4.8 s for regression, and approximately 15,000x and 3,000x speedups over four-hour tuning budgets, respectively. These are the paper's reported quantities, not pixel estimates.

## Figure 5, printed comparative values, PDF page 6

The authors report TabPFN PHE average normalized ROC AUC 0.971, versus 0.939 for default TabPFN and 0.914 for AutoGluon. Figure 5c reports Wilcoxon p = 0.0024. For regression, the reported speedup over four-hour AutoGluon is 48x; Figure 5d reports p = 0.0101. Plot points are not individually labeled.

## Figures 1-3 and 6, PDF pages 2-3 and 7

These show synthetic prior construction, benchmark behavior, dataset-property robustness and demonstrations. Figure 2 is a schematic. Figures 1, 4-6 contain plotted values but most individual bars or points are unlabeled; the plotted panels have been visually inspected and the exact summary values reported in adjacent prose above are preserved. Do not estimate individual bars as exact.

