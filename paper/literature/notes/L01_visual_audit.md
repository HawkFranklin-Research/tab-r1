# L01: Figure and table review

Source: pdfs/L01.pdf, *Established machine learning matches tabular foundation models in clinical predictions* (2026), DOI 10.1186/s12911-026-03654-3.

## Figure 2, printed values, PDF page 4

Panel a is a radar chart comparing literature AUROC, TabPFN, and best classical ML for 12 binary tasks. The plotted labels are:

| Task | Literature | TabPFN | Best ML |
|---|---:|---:|---:|
| Metastatic disease | 0.94 | 0.92 | 0.94 |
| Hereditary hearing loss | 0.76 | 0.77 | 0.77 |
| Esophageal cancer | 0.98 | 0.95 | 0.96 |
| Amyloidosis | 0.95 | 0.92 | 0.94 |
| Renal cell carcinoma | 0.84 | 0.86 | 0.87 |
| Osteosarcoma | 0.75 | 0.80 | 0.81 |
| Hepatocellular carcinoma | 0.82 | 0.83 | 0.83 |
| Overall death | 0.87 | 0.87 | 0.88 |
| Cancer death | 0.86 | 0.87 | 0.87 |
| 5-year survival | 0.89 | 0.89 | 0.90 |
| 3-year survival | 0.85 | 0.87 | 0.88 |
| 1-year survival | 0.85 | 0.85 | 0.87 |

The numeric point labels are printed on the image. Panel b shows 95% confidence intervals for the AUROC difference between TabPFN and the best ML model. Exact interval endpoints are not printed beside each task; they must not be estimated as exact from the pixels. The paper reports TabPFN as best in 16.7% of tasks and most differences within +/-0.02 in its abstract.

## Figure 3, visual-only runtime plot, PDF page 6

Axes: runtime normalized to logistic regression, logarithmic scale, approximately 0.03 to 300; AUROC normalized to logistic regression, approximately 0.7 to 1.65. Individual points and class means are not numerically labeled, so no exact per-point values are transcribed. The mean markers for TabPFN and TabPFN-HPO appear around 1.24-1.25 normalized AUROC and roughly 30-50 normalized runtime; these are visual estimates only. The figure caption says means exclude logistic regression and error bars are 95% CIs.

## Tables

Tables 1 and 2 are present in txt/L01.txt in PDF reading order. Table 2 contains evaluated model families and hyperparameter settings. Verify column alignment against the page before reusing any table value.

