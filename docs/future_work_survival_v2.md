# Future work: censored survival, transfer, clinical value, external validation

Status: **idea only, deferred until the current manuscript is under review.** Nothing here has
been implemented or run. Written 2026-10-01.

## Why

The current paper treats survival as fixed-horizon classification. That drops every patient
censored before the horizon: 1,645 of 3,238 patients are usable at 3 years and 1,168 at 5
years. The result is a clean benchmark that leaves four questions open:

1. Does the ranking of models hold when censoring is modelled properly and nearly all
   patients are scored?
2. Can a pooled context be made to *help* within-cancer prediction, instead of hurting it
   (paper Fig. 3E)?
3. Do omics add anything beyond age and stage?
4. Does anything survive transfer to an independent cohort?

## Design principle: one estimator wrapper for every model

Every comparison must cover **all** models in the paper: TabPFN v2, v2.5, v2.6, v3, TabFM,
AutoGluon and the five classical learners, run through the same code path. Model-specific
survival heads (e.g. `SurvivalTabPFN` in tabpfn-extensions) are excluded for two reasons:

- They exist for only some models, so they break the comparison.
- `SurvivalTabPFN` treats censored patients as non-events. CPTAC follow-up is about 1 year
  versus 5+ years in TCGA, so this would re-introduce a cohort shortcut through follow-up
  length.

Two survival reductions use only the `fit`/`predict_proba` (or `predict`) interface that every
model already has:

| Reduction | Needs | How censoring is handled |
|---|---|---|
| **A. IPCW horizon classification** (primary) | any classifier | Patients censored before horizon *h* get weight 0. Events and long survivors are weighted by 1/Ĝ(T or h), where Ĝ is the Kaplan–Meier censoring distribution fitted on training patients only. Models without a `sample_weight` argument (check TabPFN/TabFM) use weighted resampling of the training context instead. Fit at h = 1, 2, 3, 5 years and combine into a risk score. |
| **B. Pseudo-observation regression** (secondary) | any regressor | Each training patient gets a jackknife pseudo-value of restricted mean survival time (Andersen & Klein 2007), which is ordinary regression on one row per patient. Applies only to models with a regression mode; whether TabFM has one is still to be checked. |

Classical survival references, included as *comparators* rather than the main arms: Cox
elastic-net, random survival forest and gradient-boosted survival (scikit-survival).

## The four studies

**S1: Censored survival benchmark.**
- Data: OS for all five cancers, 3,171 patients and 915 events. DSS (TCGA only, 2,642
  patients) is secondary.
- Metrics: Harrell and Uno C-index, time-dependent AUC at 3 and 5 years, integrated Brier
  score.
- Pooled models are also scored with a **within-cancer stratified C-index**, which only
  compares pairs of patients who have the same cancer.

**S2: Pooling that helps?** For each target cancer, on the same test patients, compare three
training contexts:
- (A) that cancer only;
- (B) naive pooling, as in the paper;
- (C) pooled, with per-cancer z-scoring, features observed in ≥90% of *every* cancer (using
  `missing_mask.npz`, not zeros), a cancer one-hot, and missing values left as NaN.

The primary result is the within-cancer C-index difference C − A, paired across folds with a
bootstrap CI. A positive C − A would be the first evidence of real pan-cancer transfer.

**S3: Clinical versus omics.**
- Clinical covariates: age, sex, stage, T, N. These need harmonising first: TCGA uses
  `AGE`/`AJCC_PATHOLOGIC_TUMOR_STAGE`, CPTAC uses `Age`/`Stage`, and the
  `clinical::*_Unknown` one-hots encode the data source.
- Arms: clinical only, omics only, clinical + omics.
- Primary result: the C-index of clinical + omics minus clinical only.

**S4: METABRIC external validation (breast).**
- METABRIC (about 1,900 patients) has long follow-up. It has to be downloaded from cBioPortal
  (`brca_metabric`) into `../c-5`.
- Train on TCGA-BRCA and test on METABRIC, then the reverse.
- TCGA uses RNA-seq and METABRIC uses microarrays: intersect genes and z-score within each
  cohort.

## Data facts already checked

| Endpoint | Patients | Events | Notes |
|---|---|---|---|
| OS | 3,171 | 915 | BRCA 153/1,180 · ESCA 76/182 · HNSCC 252/624 · LSCC 229/575 · LUAD 205/610 |
| DSS | 2,642 | 456 | none for CPTAC |

- Missingness is recorded in `c-5/gpt/processed/train_ready/*/core/missing_mask.npz`, which
  the paper's folds did not use.
- `scikit-survival` is not installed.
- TabPFN refuses more than 1,000 training rows on CPU unless
  `TABPFN_ALLOW_CPU_LARGE_DATASET=1` is set.

## Planned code layout (`survival_v2/`, separate from `paper/`)

```
tte/data.py      loaders using missing_mask; OS/DSS targets; harmonised clinical table
tte/folds.py     patient-grouped folds stratified by cancer × event, 5×5, manifest + SHA-256
tte/features.py  in-fold: observed-everywhere filter, per-modality caps, per-cancer z-scoring
tte/reduce.py    IPCW horizon wrapper and pseudo-value wrapper around any sklearn-style model
tte/metrics.py   C-index (Harrell, Uno, within-cancer stratified), td-AUC, IBS, paired bootstrap
run.py           --study s1..s4 --smoke --max-threads 12 --confirm-full-run
figures.py       S1 C-index forest plot; S2 paired C − A per cancer; S3 clinical/omics
                 increments; S4 KM curves by predicted risk tertile on METABRIC
```

The paper code is reused where it fits: `resource_limits.py`, patient grouping, and modality
parsing from `prepare_leakage_safe_folds.py`.

## Order

1. Smoke test on HNSCC and LUAD (1 repeat × 2 folds, ≤200 training rows, ≤12 threads), then
   project the cost of the full run.
2. S1 and S2 share the same folds. S3 adds clinical columns. S4 waits on the download.
3. Full TabPFN/TabFM runs go on the existing GCP image (`cloud/`).

## Novelty check before claiming anything

Search the literature for "TabPFN survival", "in-context learning survival analysis", "IPCW
foundation model" and "pseudo-observations TabPFN". The arXiv preprint "Survival In-Context"
(2603.29475) is already listed in `healthcare_tabpfn_usecases.csv`.
