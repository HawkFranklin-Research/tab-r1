# tab-r1

Can tabular foundation models (TabPFN v2 / v2.5 / v2.6 / v3, Google TabFM) predict cancer
survival from multiomics better than classical learners, and is any gain real biology or
cohort structure?

This is a research workspace, not a library. It holds code, data products, results and the
manuscript for one study, plus the earlier experiments that led to it.

## The short version of the story

1. **Apr–May 2026: does TabPFN hold up on small tables?** We reproduced the TabPFN paper on
   7 public classification datasets. TabPFN was marginally best (mean ROC AUC 0.877 vs
   CatBoost 0.873). See `Evaluate-TABPFN/` and `results-s2/`.
2. **May–Jul 2026: cancer multiomics, single splits.** Five cancers, 3,238 patients, from TCGA
   and CPTAC. Within one cancer, survival is hard (ROC AUC ≈ 0.55). Pooling cancers lifted
   AUC to 0.74–0.83, and a July draft read this as a "generalizable pan-cancer survival
   signal". See `cancer-exp/` and `cancer-os-exp/`.
3. **Aug 30, 2026: the audit.** We found feature-selection leakage and mock ROC curves. We also
   found that cancer identity alone (AUC 0.707) or the pattern of missing data alone (0.745)
   predicts pooled 3-year survival about as well as the models. The pan-cancer claim was
   withdrawn. See `convey-vatsal-aug30.txt` and `convey-vatsal2-aug30.txt`.
4. **Aug 31, 2026: leakage-safe rebuild.** We froze 400 patient-grouped test sets (16 tasks ×
   5 repeats × 5 folds) and evaluated 11 models on identical splits: classical models
   locally, foundation models and AutoGluon on GCP. See `paper/analysis/` and `cloud/`.
5. **Sep 2026: manuscript.** The manuscript is `paper/tabular_fm_paper.tex`.
6. **Next: true time-to-event survival.** The new work is pooled-context transfer, clinical
   versus omics, and external validation. See `survival_v2/` once it exists.

## Where things are

```
tab-r1/
├── paper/                         ← CURRENT STUDY: manuscript + everything that feeds it
│   ├── tabular_fm_paper.tex       manuscript (class: hawkfranklin.cls, refs: references.bib)
│   ├── analysis/                  all analysis code for the paper (see analysis/README.md)
│   │   ├── prepare_leakage_safe_folds.py     builds the 400 frozen folds from c-5 data
│   │   ├── run_leakage_safe_fold_models.py   runs any model on the frozen folds
│   │   ├── run_cloud_evaluation.py           same, packaged for the GCP VM
│   │   ├── run_cohort_stress_tests.py        leave-one-cancer/source-out, permutations
│   │   ├── analyze_saved_cancer_results.py   bootstrap CIs + shortcut controls
│   │   ├── build_manuscript_assets.py        ← regenerates Figures 1–5 and Tables 1–3
│   │   ├── resource_limits.py                caps threads / memory (12 cores, 12 GB)
│   │   └── generated_folds/                  the 400 frozen folds + fold_manifest.csv
│   ├── figures/manuscript/        final Figure 1–5 (pdf/png/svg)
│   ├── figures/source_data/       one CSV per figure panel; model_fold_metrics.csv (4,400 rows)
│   ├── tables/generated/          Tables 1–3 (.tex + .csv)
│   └── tables/source_data/        raw results: full_fold_models/ (classical, local),
│                                  cloud_foundation_models/ (TabPFN, TabFM, AutoGluon, GCP)
│
├── cloud/                         Dockerfile + scripts used to run foundation models on GCP
│   ├── scripts/                   launch VM, run, sync results back
│   ├── hf-datasets/               frozen folds packaged as a Hugging Face dataset
│   └── EXPERIMENT_METADATA_AND_COST_REPORT.md
│
├── cancer-exp/                    May–Jun: first cancer experiments (cancer type, source,
│                                  OS event, mutation status). Mutation tasks are where
│                                  TabPFN wins most clearly (not in the paper).
├── cancer-os-exp/                 Jul: single-split survival experiments
│   ├── exp01_per_cancer_fixed_window/
│   ├── exp02_combined_fixed_window/        the pooled result that was later retracted
│   └── exp03_combined_extreme_survival/
├── experiments/                   mirror of cancer-exp/ and cancer-os-exp/ (+ AutoGluon
│                                  model files) and cancer-survival-exp/ (first 3y/5y labels)
│
├── Evaluate-TABPFN/               [submodule] small-dataset TabPFN reproduction study
├── package/                       ev_tabpfn: the evaluator from that study as a pip package
├── results-satya/, results-s2/    Apr 30 re-runs of the small-dataset benchmark
├── papers/, papers-info/,         TabPFN / TabPFN-3 / TabICL papers and section splits used
│   paper-datasets/                as references; *.pdf at root are the same papers
├── healthcare_tabpfn_usecases.csv 98 published TabPFN healthcare applications (lit. survey)
│
├── TabPFN/, tabpfn-client/,       [submodules] model code. tabpfn-extensions contains
│   tabpfn-extensions/, tabpfn_3/  SurvivalTabPFN (unused so far). tabpfn_3 = v3 checkpoints
├── tabfm/                         [submodule] google-research/tabfm
├── Accurate_Prediction_on_...     [submodule] third-party TabPFN small-data study
│
└── convey-vatsal*-aug30.txt,      working notes: the Aug 30 audit, the shortcut finding,
    results-agu30.txt              and the full local run summary
```

Unrelated to the study (tooling that landed at the root): `gke-mcp`, `gke-mcp_Linux_x86_64.tar.gz`,
`checksums.txt`, `LICENSE` (from gke-mcp), `catboost_info/`, `tabpfn_demo_local.py`,
`last-gemini.txt`.

## Data: outside this folder

The cancer data lives in a sibling repo, **`../c-5`**:

| Path | What |
|---|---|
| `c-5/tcga-5/` | cBioPortal PanCancer Atlas 2018 archives: BRCA, ESCA, HNSC, LUAD, LUSC |
| `c-5/cptac-5/` | LinkedOmics CPTAC downloads (no CPTAC ESCA) |
| `c-5/gpt/processed/train_ready/{CANCER}/core/` | `X.npz` (sparse), `missing_mask.npz`, `sample_index.csv` (OS/DSS/PFS/DFS days + events), `feature_index.csv` |
| `c-5/gpt/processed/clinical/` | `patient_master.parquet` (age, sex, stage, …; TCGA and CPTAC use different column names) |
| `c-5/EXTRA.data.txt` | candidate external cohorts (e.g. METABRIC for breast) |

Cohorts (core view): BRCA 1,206 · ESCA 182 · HNSCC 631 · LSCC 595 · LUAD 624 = **3,238 patients**.
Modalities: RNA-seq, CNV, methylation, mutation, clinical.

Many scripts hard-code `/home/prime/Documents/g3/...` paths. Several scripts under
`experiments/` and `cancer-os-exp/` also point at `g3/cancer-*` folders that have since moved
inside this repo.

## Key numbers (paper version)

| | n | Best ROC AUC |
|---|---|---|
| Within one cancer (macro-average) | 13 tasks | ≈ 0.56–0.57 (all models close) |
| Pooled 3-year OS | 1,645 (≈1,053 train / 329 test per split) | 0.721 TabFM, 0.716 random forest |
| Pooled 5-year OS | 1,168 | 0.754 TabPFN v3 |
| Pooled extreme (death < 3y vs alive > 5y) | 937 | 0.786 TabPFN v3 |
| Cancer identity only (3y / 5y / extreme) | same | 0.707 / 0.703 / 0.809 |
| Missing-data pattern only | same | 0.745 / 0.704 / 0.824 |
| Pooled model scored *within* each cancer, 5y | per cancer | TabPFN v3 0.44–0.48, random forest 0.51–0.58 |

## Reproducing the paper

```bash
python3 paper/analysis/build_manuscript_assets.py        # figures + tables from saved results
cd paper && pdflatex tabular_fm_paper.tex && bibtex tabular_fm_paper \
         && pdflatex tabular_fm_paper.tex && pdflatex tabular_fm_paper.tex
```

Model runs read the frozen folds, and full-scale runs require `--confirm-full-run`. See
`paper/analysis/README.md`. Local work is capped at 12 CPU threads and 12 GB RAM.

## Known gaps

- Survival is framed as fixed-horizon classification only. There is no C-index or censored
  modelling yet.
- Patients censored before the horizon are dropped. Only 1,645 of 3,238 patients are used at
  3 years.
- Clinical covariates (age, stage) were never used.
- No foundation model was tested on a held-out cancer or an external cohort.
- Pooled 3-year TabPFN v2/v2.5/v2.6 are missing because the runs hit the CPU >1,000-row
  guard (`TABPFN_ALLOW_CPU_LARGE_DATASET=1` fixes this).
