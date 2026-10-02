# L29: Figure and table review

Source: pdfs/L29.pdf, *The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets* (2015), DOI 10.1371/journal.pone.0118432.

## Figure 5, printed values, PDF page 13

Two scenarios use 1,000 positives with either 1,000 or 10,000 negatives. The ER- operating point corresponds to 500 true positives (50%) in both scenarios, with 160 false positives (16%) at 1,000 negatives and 1,600 false positives (16%) at 10,000 negatives. In the PR examples, 75% are correctly predicted as positive in the balanced case, versus 25% in the imbalanced case. The cost-curve settings are C(-|+) = 1 and C(+|-) = 1 for the balanced case, and 91 and 9 for the imbalanced case. These figures demonstrate how the same ROC operating point can imply different precision under prevalence shift.

## Figure 7 and Table 5, PDF page 17

Table 5 prints ROC-AUC and PR-AUC values:

| Model | T1 ROC | T1 PR | T2 ROC | T2 PR |
|---|---:|---:|---:|---:|
| MiRFinder | 0.992* | 0.945 | 0.772 | 0.106* |
| miPred | 0.991 | 0.976* | 0.707 | 0.024 |
| RNAmicro | 0.858 | 0.559 | 0.886* | 0.054 |
| ProMiR | 0.974 | 0.801 | 0.711 | 0.035 |
| RNAfold | 0.964 | 0.670 | 0.706 | 0.015 |

The asterisk marks the best value in each column. Figure 7 curves have no additional numeric labels; the table is the source of exact values.

## Other figures/tables

All five tables are in txt/L29.txt. Figures 1-4 are explanatory, Figures 5-7 contain the relevant numeric demonstrations. Table values were checked visually against PDF page 17.

