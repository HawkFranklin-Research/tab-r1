# survival_v2 — censored-survival evaluation of tabular foundation models

A separate, self-contained follow-up to the manuscript in `paper/`. The paper treats survival as fixed-horizon
classification (death by 3 or 5 years), which drops every patient censored before the horizon and cannot report a C-index.
This pipeline asks the same questions with censoring handled properly, every patient with follow-up kept, and every model —
four TabPFN versions, TabFM, tree ensembles, Cox models — compared through the same code path.

Nothing in `paper/` is read or modified except as noted. The fixed-horizon results stay exactly as they are.

## Questions

| | Question | Contexts / arms | Main output |
|---|---|---|---|
| Q1 | How well does each model rank patients' survival within one cancer, and how much does pooling inflate the pooled score? | A (one cancer), P (pooled folds) | Harrell / Uno C, time-dependent AUC, Brier; all-pairs vs same-cancer C |
| Q2 | Does adding the other cancers to the training set help prediction **within** a cancer? | A vs B (naive pooling) vs C (standardised pooling) [vs D] on identical test patients | paired change in within-cancer C, foundation-minus-tree difference |
| Q3 | Do omics add anything beyond age, sex and stage? | clinical, omics, omics + clinical | paired increment in C |
| Q4 | Does anything transfer to an independent cohort? | TCGA-BRCA → METABRIC and back | C in the external cohort, KM curves by predicted-risk tertile |

## How every model becomes a survival model

Only TabPFN has a (work-in-progress) survival head, so a fair comparison needs reductions that work for any model:

* **pseudo** — jackknife pseudo-observations of the restricted mean survival time (and of S(3y), S(5y)) turn censored outcomes into
  ordinary numbers; any regressor is trained on them (`tte/pseudo.py`, validated against brute force and lifelines).
* **ipcw** — horizon classifiers trained on rows resampled with inverse-probability-of-censoring weights; any classifier.
* **native** — TabPFN event classifier × event-time distribution (a re-implementation of `tabpfn_extensions.SurvivalTabPFN`, whose
  import fails with the installed scikit-learn). It labels censored patients as non-events; every result carries that flag.
* classical references: Cox elastic net, ridge Cox, random survival forest, gradient-boosted survival, Kaplan–Meier, cancer-only and
  source-only risk.

`analysis/model_coverage.csv` tabulates which route each model has. TabFM has no native survival route.

## Data decisions (and why)

* **Source: `../c-5/gpt/processed/train_ready`, trusted as delivered** (scaling, imputation, cohort centring by the c-5 pipeline).
* **Duplicated source blocks are coalesced.** c-5 stores most features twice: one TCGA-only and one CPTAC-only copy under the same id.
  The paper pipeline kept one copy, which left CPTAC patients with all-zero feature vectors
  (`paper/analysis/reusability/exploratory/NOTES_source_blocks.md`). Here each patient gets the value from its own source's copy.
  `missing_mask.npz` is 1 where a value is missing.
* **Primary cohort: TCGA only** (2,774 patients with overall survival, ~95k candidate features across RNA, CNV, methylation and
  mutation). CPTAC patients lack several assays and have about a year of follow-up (BRCA CPTAC: 2 deaths in 96). The `all` cohort
  (with CPTAC) is a sensitivity analysis: `--cohorts tcga,all`.
* **Clinical covariates** are harmonised from both naming schemes (`tte/clinical.py`); grade is excluded because only CPTAC has it.
* **Feature selection** happens inside each training set: |correlation| with the RMST pseudo-values, k = 100 with equal quotas per
  modality. Context C selects with within-cancer correlations so that features which only separate cancers score zero.
* **METABRIC** (`../c-5/metabric/brca_metabric`, cBioPortal DataHub, ODbL): microarray, so each cohort is z-scored on its own;
  only shared gene symbols are used; follow-up is censored at 10 years in both cohorts.

### Attribution caveat (Q2)
Context C differs from B in three ways at once: within-cancer feature selection, a cancer indicator, and missing values passed as
missing. A C − B difference shows the combined effect; context D adds a fourth change (cancer-stratified pseudo-values).

### Intervals
Paired contrasts resample the 25 test sets of each cancer. Test sets share training patients, so the intervals describe
fold-to-fold variation and are narrower than a population confidence interval. Q4 intervals are a patient bootstrap of the
external cohort.

## Running

```bash
python3 survival_v2/run_pipeline.py --dry-run                              # the plan: 650 units, 7,350 fits + Q4
python3 survival_v2/run_pipeline.py --stages prepare,folds                 # build the store and freeze folds (local)
python3 survival_v2/run_pipeline.py --smoke --confirm-full-run             # tiny real-data check -> outputs_smoke/
python3 survival_v2/run_pipeline.py --stages fit,external --confirm-full-run [--shard 0/4] [--device cuda]
python3 survival_v2/run_pipeline.py --stages metrics,analyze,figures       # always rebuildable from saved predictions
python3 -m pytest survival_v2/tests -q                                     # 24 tests, synthetic data, ~5 min
```

Local runs are capped at 12 threads / 12 GB (`TABR1_MAX_THREADS`, `TABR1_MAX_MEMORY_GB` raise the caps on a larger machine).
TabPFN v2–v2.6 refuse more than 1,000 rows on CPU; the pipeline sets `TABPFN_ALLOW_CPU_LARGE_DATASET=1`, but pooled contexts
(~2,200 training rows) are much faster on a GPU.

**Google Cloud:** run `prepare,folds` locally, then `scripts/gcloud_launch.sh N_SHARDS MACHINE ACCELERATOR` (one Spot VM per shard;
shard 0 also runs Q4), and `scripts/gcloud_sync.sh N_SHARDS` to copy results back. `Dockerfile` builds the same environment as an image.
Fits resume automatically after a Spot pre-emption.

## Outputs (`survival_v2/outputs/`, gitignored)

| Path | Contents |
|---|---|
| `store/` | coalesced matrices per cancer, feature table with observed fractions, samples, harmonised clinical, build report |
| `folds/` | frozen assignments, outcomes, manifest with SHA-256 (the fit stage refuses altered folds) |
| `predictions/<context>/<cohort>/<arm>/<cancer>/r<rep>_f<fold>.parquet` | one row per model × test patient: risk, S(3y), S(5y), raw regressor predictions |
| `runs/…json` | sizes, selected features, per-model status, timings, errors, known-bias flags |
| `external/` | Q4 predictions and runs |
| `metrics/` | `run_metrics.parquet`, `external_metrics.parquet`, `model_errors.csv` |
| `analysis/` | question tables (`q1_*`, `q2_*`, `q3_*`, `q4_*`, `runtime`, `model_coverage`) |
| `figures/` | PDF/PNG per figure plus `source_data/` |
| `logs/` | run logs and `environment.json` (package versions, device, git commit) |

## Code map

`run_pipeline.py` (CLI) → `tte/store.py`, `tte/clinical.py` (prepare) → `tte/folds.py` → `tte/runner.py` (fit; uses `pseudo.py`,
`selection.py`, `design.py`, `models/`) → `tte/external.py` (Q4) → `tte/evaluate.py` + `tte/metrics.py` → `tte/analysis.py` →
`tte/figures.py`. `config/default.yaml` holds every setting, including the model lists per question.

## Status
See `STATUS.md`. Written and tested on synthetic data; not yet run on the real data.
