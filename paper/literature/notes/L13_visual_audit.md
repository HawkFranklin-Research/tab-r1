# L13: Figure and table review

Source: pdfs/L13.pdf, *Batch Effect Confounding Leads to Strong Bias in Performance Estimates Obtained by Cross-Validation* (2014), DOI 10.1371/journal.pone.0100335.

## Figure 4, visual estimates, PDF page 8

This simulation has four confounding levels: none, intermediate, strong, and full. In the no-signal setting, outer/internal cross-validation misclassification appears near 0.55, 0.28, 0.05, and 0.00 as confounding increases, respectively; external evaluation remains near 0.50 across the four settings. These are approximate readings from the plotted scale, not reported exact estimates.

The lower panel shows fractions of selected variables by source: Wilcoxon selection is approximately 100% other with no confounding and approximately 100% batch-only under intermediate, strong, and full confounding. Lasso is approximately 99% other plus 1% batch-only without confounding; about 28% batch-only and 72% other at intermediate confounding; about 63% batch-only and 37% other at strong confounding; and 100% batch-only under full confounding. These bar heights are visually estimated from the 0-1 axis.

## Figure 6, visual estimates, PDF page 10

The simulation adds truly differentially expressed variables. Panel a shows internal misclassification rising under stronger confounding while external error stays close to chance; the plot is not numerically labeled at each point. Panel b displays selected-variable fractions. Values are only visually estimable from the 0-1 scale, and no exact numerical values are transcribed here. The caption states that bars average across classifiers and data-set replicates; error bars span one standard deviation.

## Other figures/tables

Figure 1 diagrams the four confounding levels; Figure 2 diagrams nested validation; Figures 3, 5, 7, and 8 address related simulation cases. Table and caption text are in txt/L13.txt. Numeric values from any unlabeled plot must remain estimates with the page and panel recorded.

