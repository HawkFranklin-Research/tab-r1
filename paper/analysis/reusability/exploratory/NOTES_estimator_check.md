# Estimator check for the within-cancer pooling effect (2026-10-03)

**Status: exploratory, and now superseded by `../fold_aware_contrast.py`, which implements the fold-level estimator with a bootstrap and feeds Fig 5 and Extended Data Fig 6 of `reusability_report.tex`.** The probes below are kept as the record of how the problem was found. Scripts read saved
predictions only and fit no model. Run each from the repository root, e.g.
`python3 paper/analysis/reusability/exploratory/rank_probe.py`. Printed results are stored in `output/`.

## Why this exists
Figure 5 of `reusability_report.tex` (and Fig 3E of v1) estimate how pooled training changes
within-cancer ROC AUC. That analysis (`within_cancer_pooling_contrast.py`) averages each patient's
predictions across the five repeats and then computes one AUC per cancer over all patients, so
predictions from different folds, produced by different models, are pooled. Table 2 instead
averages AUC computed inside each test set. This check asks whether the two give the same answer.

## Result
They do not. Mean change in within-cancer ROC AUC after pooled training (pooled minus
cancer-specific), averaged over models:

| Endpoint | Estimator | Foundation models | Tree ensembles | Foundation minus trees |
|---|---|---|---|---|
| 3-year | patient-averaged (paper) | −0.025 | +0.002 | −0.027 |
| | fold-level AUC (`auc_probe.py`) | +0.018 | +0.011 | +0.007 |
| | rank-normalised within fold (`rank_probe.py`) | +0.013 | +0.010 | +0.003 |
| | Harrell C, eligible patients (`cindex_probe.py`) | +0.017 | +0.004 | +0.013 |
| 5-year | patient-averaged (paper) | −0.041 | −0.011 | −0.030 |
| | fold-level AUC | −0.005 | −0.003 | −0.002 |
| | rank-normalised within fold | −0.016 | −0.010 | −0.006 |
| | Harrell C | −0.002 | +0.003 | −0.005 |
| Extreme | patient-averaged (paper) | −0.050 | −0.007 | −0.043 |
| | fold-level AUC | −0.030 | −0.009 | −0.021 |
| | rank-normalised within fold | −0.037 | −0.005 | −0.032 |
| | Harrell C | −0.014 | +0.008 | −0.022 |

Individual models, 5-year, pooled minus cancer-specific: TabFM −0.084 (paper) vs −0.016
(fold-level) vs −0.032 (rank-normalised); TabPFN v3 −0.070 vs −0.012 vs −0.024.

## Reading
- Pooling does not raise within-cancer ranking for any model family under any estimator
  (changes are near zero or negative). That part of the paper's message is unaffected.
- The large foundation-model losses at 3 and 5 years in the paper depend on pooling predictions
  across folds. Rank-normalising within each fold removes most of them; fold-level scoring removes
  nearly all. A plausible reading, not tested, is that in-context models' score scale depends on
  the composition of the training context and so shifts more between folds.
- A foundation-model-specific loss of roughly 0.02 to 0.03 (relative to trees) survives every
  fold-aware estimator, and a second metric (Harrell C), for **extreme survival only**.
- None of this has a confidence interval yet. Fold-level scoring needs a bootstrap that respects
  repeats before it can be quoted.

## Limits of the C-index here
Harrell C is computed on the eligible patients only (those with a defined label at the horizon),
using their real survival times and events. Patients censored before the horizon are not in the
saved predictions, so this is not a censoring-adjusted C-index over the whole cohort.
For the extreme endpoint, eligible patients are the extremes, which inflates pair separation.
Per-cancer Harrell C is 0.50 to 0.54 for every model, so within-cancer discrimination is small
under this metric too.

## Additional output (cindex_probe.txt)
Rank agreement between ROC AUC and Harrell C across models (Spearman): cancer-specific 0.75 / 0.67 / 0.85 and pooled 0.98 / 0.92 / 0.72 for 3-year / 5-year / extreme. (The final script gives 0.83 for cancer-specific 3-year because it scores within-cancer AUC at fold level.)
