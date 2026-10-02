# L21: Figure and table review

Source: pdfs/L21.pdf, *Why do tree-based models still outperform deep learning on typical tabular data?* (2022), DOI not recorded in the existing bibliography.

## Figures 1-2, PDF page 5

The first figure compares hyperparameter-search progress for numerical-only datasets: 15 classification and 19 regression datasets. The second uses mixed numerical/categorical data: 7 classification and 14 regression datasets. Y axes are normalized test scores, x axes are random-search iterations on a logarithmic scale, and ribbons show min-max across 15 random search orders. The curves are not individually labeled with exact values; visually, boosted trees and random forests rise toward approximately 0.9-0.95 of best on several tasks, while MLP/ResNet/FT Transformer are more variable and often lower. The approximate curve readings should not be quoted as exact outcomes.

## Figures 4-5, PDF page 8

Figure 4 plots normalized test score as features are removed; Figure 5 shows that adding uninformative features degrades some neural models more sharply. Both use normalized 0-1 score axes and intervals over random search orders. No exact point values are printed. The visual supports the paper's described tabular inductive-bias discussion only; it is not a direct comparison with current tabular foundation models.

## Tables

The hyperparameter-space tables are included in txt/L21.txt. All reported plotted trends are qualitative; source exact coordinates are not supplied.

