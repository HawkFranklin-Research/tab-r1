# paper/ — what is where, and why

This folder holds **three versions of one study** plus everything that feeds them. They share
data, folds, results and tables, but differ in framing, figures and text. This file is the map.
It is deliberately independent of the root `README.md`.

Last updated 2026-10-03 (after the fold-aware re-analysis and the Extended Data C-index figure).

## 1. Which manuscript is which

| | File | Status | What it is |
|---|---|---|---|
| **v1** | `tabular_fm_paper.tex` / `.pdf` | **Superseded, kept for the record. Do not edit.** | The benchmark-style paper. Title "Tabular Foundation Models Learn the Cohort, Not the Patient…". HawkFranklin class (`hawkfranklin.cls`). Its five figures are in `figures/manuscript/`. The text began as a Gemini reconstruction (Sept 2026) and was rewritten on 2026-10-01. |
| **v2** | `reusability_report.tex` / `.pdf` | **Current source of truth.** Edit this one. | The same study re-framed as a *Nature Machine Intelligence*-style **Reusability Report**: reproduce TabPFN on its own benchmark data, reuse it on cancer survival, find the boundary. New main Figures 1–5 (`figures/reusability/`); the v1 figures become Extended Data Figs 1–5 (Fig 3 via a variant whose panel E compares estimators) and a new Extended Data Fig 6 gives the C-index. Citations audited against `literature/` and recorded in `literature/claim_adjudication.tsv`. |
| **v3** | `springer_nature/` | **Derived from v2. Format only.** | Synced on 2026-10-03 to the latest v2, including fold-aware results and Extended Data Fig. 6. Abstract, body, captions, citations and copied assets verified against the current snapshot. |

**Why three?** v1 was the original submission-ready draft. v2 reflects the decision (Oct 2026) to
present the work as a reproduction-plus-reuse study, which is what the work actually was. v3 was
generated so the same text can be submitted to a Springer Nature journal.

**Editing rule.** Scientific changes go into `reusability_report.tex` first. The Springer copy does
not update itself: `springer_nature/verify_migration.py` compares it with the snapshot and will
fail after any intentional text change until a new baseline is made (see
`springer_nature/README.md`). Tables 1–3 are shared by v1 and v2 (`tables/generated/*.tex`).

## 2. Figures

| Folder | Contents | Used by |
|---|---|---|
| `figures/reusability/` | **v2 main Figures 1–5** (`fig1_roadmap_and_design` … `fig5_within_cancer_effect`), **Extended Data Fig 6** (`ed_cindex_eligible_patients`), and `source_data/` (one CSV per panel; `foldaware_*` and `cindex_eligible_summary.csv` are the current within-cancer results; `legacy_patient_averaged/` holds the superseded estimator) | v2 |
| `figures/manuscript/` | v1 Figures 1–5 (`figure_01_…` to `figure_05_…`, pdf/png/svg), plus `figure_03_pooling_effect_ed.*`, the v2 Extended Data version of Fig 3 (panel E shows estimator sensitivity instead of the superseded patient-averaged effect) | v1 main; v2 Extended Data 1–5 |
| `figures/source_data/` | Source tables for the v1 figures, `model_fold_metrics.csv` (4,400 rows, the master per-fold table) and the within-cancer pooling-contrast tables | v1, v2 |
| `figures/full_evidence/`, `figures/full_study_design/` | Intermediate figures from 2026-08-30 | Superseded |
| `figures/benchmark_dashboard.png`, `dataset_diversity.png`, `cancer_survival_lifelines.png` | July single-split figures | **Do not use** — see warning |

> **Warning.** `make_paper_plots.py` (July) draws *simulated* ROC curves and adds `np.random`
> noise to box-plot data (the 2026-08-30 audit found this). Nothing from it, including
> `benchmark_dashboard.png` and `dataset_diversity.png`, is real data. `make_survival_plots.py`
> produced `cancer_survival_lifelines.png` from a single early split and is also unused.

## 3. Analysis code (`analysis/`)

Run everything from the repository root. Local runs are capped at 12 threads / 12 GB
(`analysis/resource_limits.py`).

**Pipeline that produced the results (v1 and v2 share it):**

| Script | Purpose |
|---|---|
| `prepare_leakage_safe_folds.py` | Builds the 400 frozen patient-grouped folds from the `../c-5` data → `analysis/generated_folds/` |
| `run_leakage_safe_fold_models.py` | Runs a model on the frozen folds (classical models locally; needs `--confirm-full-run`) |
| `run_cloud_evaluation.py`, `cloud_evaluation_colab.ipynb` | Same, packaged for the GCP VM (TabPFN, TabFM, AutoGluon); see `../cloud/` |
| `run_cohort_stress_tests.py`, `analyze_saved_cancer_results.py` | Shortcut controls (cancer type, zero pattern), permutations, held-out cancer. **Single historical split** (141–247 test patients) |
| `analyze_cancer_landscape.py`, `build_provenance_manifest.py` | Cohort tables; checksums |
| `build_manuscript_assets.py` | v1 Figures 1–5, **Tables 1–3** (both versions), Extended Data source tables |
| `make_evidence_figures.py`, `make_study_design_figures.py` | Aug 30 figures; superseded |
| `run_matched_baselines.py` | Fold-matched baselines on small datasets. One logged attempt hit a `TypeError`; no fold-matched results from it are used, and the reproduction numbers do *not* come from it (see §5) |

**v2-specific (`analysis/reusability/`):**

| Script | Purpose |
|---|---|
| `compute_reusability_statistics.py` | Reproduction table, Friedman/Nemenyi, paired differences from random forest. Also writes the **legacy** patient-averaged pooling estimator to `source_data/legacy_patient_averaged/` (used only for Extended Data Fig 3E). Reads saved results only |
| `fold_aware_contrast.py` | **Current within-cancer analysis.** Pooled-minus-cancer-specific change in ROC AUC and Harrell C-index, each test set scored on its own, patient-cluster bootstrap (2,000 draws), foundation-minus-tree difference, and the eligible-patient C-index table. Validated against scikit-learn and scikit-survival; ~30 s. Feeds Fig 5 and Extended Data Fig 6 |
| `build_reusability_figures.py` | The five v2 main figures |
| `../within_cancer_pooling_contrast.py` | **Superseded.** Patient-averaged within-cancer AUC (pools predictions across folds). Still feeds v1 Fig 3E; not used by v2 |
| `exploratory/` | Three read-only probes (C-index, fold-level AUC, rank-normalised AUC) and `NOTES_estimator_check.md`. Not used in any manuscript figure or table |

**Rebuild v2 from saved results (no model is run):**

```bash
python3 paper/analysis/build_manuscript_assets.py                    # tables, Extended Data
python3 paper/analysis/reusability/compute_reusability_statistics.py # reproduction, ranks (~1 min)
python3 paper/analysis/reusability/fold_aware_contrast.py            # within-cancer effect + C-index (~30 s)
python3 paper/analysis/reusability/build_reusability_figures.py      # Figures 1-5, ED Fig 6
cd paper && pdflatex reusability_report && bibtex reusability_report \
         && pdflatex reusability_report && pdflatex reusability_report
```

(v1: same, with `tabular_fm_paper`. v3: `bash paper/springer_nature/build.sh`.)

## 4. Data and results

| Path | What |
|---|---|
| `analysis/generated_folds/` | The 400 frozen folds. Each `test_metadata.csv` carries `OS_days` and `OS_event`, so survival times are available for every test patient. `fold_manifest.csv` lists them |
| `tables/source_data/full_fold_models/` | Classical-model runs (local) and their per-fold predictions |
| `tables/source_data/cloud_foundation_models/` | TabPFN v2–v3, TabFM and AutoGluon runs (cloud) and predictions |
| `tables/source_data/full_cancer/`, `full_stress/` | Shortcut controls, permutations, held-out diagnostics (historical split) |
| `tables/generated/` | Tables 1–3 as `.tex` and `.csv` |
| `../c-5/` (outside the repo) | Raw cohort data (TCGA/CPTAC), the one external dependency |

## 5. Where the reproduction numbers come from

The reproduction in v2 (Fig 2) is **not** produced by anything in `paper/analysis/`. It reads results
from earlier work outside this folder:

- `../results-s2/runs/` — TabPFN vs six baselines, one 15% test split per dataset.
- `../Evaluate-TABPFN/pfn3-test/` — TabPFN v1, v2, v2.5, v2.6, v3 (training capped at 1,024 rows).
- `../Evaluate-TABPFN/tabfm-test/` — TabFM.

`compute_reusability_statistics.py::reproduction_table()` gathers them. These runs are
**not fold-matched** across model families, which is why v2 calls the reproduction "directional".

## 6. Literature

- `literature/` — 40-source collection, extracted texts, and the evidence tables:
  `reusability_evidence_table.md`/`.tsv` (66 findings), `claim_evidence.tsv`,
  and **`claim_adjudication.tsv`** (what was done with each finding in v2). See `literature/README.md`.
- `../reference-papers/` (repo root) — the four NMI Reusability Reports used as editorial models,
  with text extractions and panel-by-panel figure notes; `STORY.md` compares their narratives.
- `REVISION_PLAN.md` — the plan that produced v2. Mostly executed; kept for the reasoning.
- `references.bib` — shared by v1 and v2 (v2 cites all 40 entries).

## 7. Follow-up pipeline and earlier experiments (outside `paper/`)

`../survival_v2/` (Oct 2026) is a separate censored-survival pipeline (C-index, all patients with follow-up, every model through the
same pseudo-observation / IPCW routes, pooling contexts, clinical vs omics, METABRIC). It reads c-5 directly, coalesces the duplicated
source blocks, and writes only to `survival_v2/outputs/`; nothing in `paper/` depends on it. See `survival_v2/README.md`.

### Earlier experiments

| Path | What it was |
|---|---|
| `../Evaluate-TABPFN/`, `../results-s2/`, `../results-satya/` | Apr–Jul 2026 small-dataset TabPFN reproductions |
| `../cancer-exp/`, `../cancer-os-exp/`, `../experiments/` | May–Jul single-split cancer experiments. `experiments/` mirrors the other two and adds `cancer-survival-exp/`. The Jul 24 "generalizable pan-cancer signal" claim came from here and was withdrawn |
| `../cloud/` | Dockerfile, scripts and cost report for the GCP runs |
| `../convey-vatsal-aug30.txt`, `../convey-vatsal2-aug30.txt`, `../results-agu30.txt` | The Aug 30 audit and shortcut finding |

A dedicated README for these folders has not been written; `../README.md` has the one-line
version of each.

## 8. Open issues (as of 2026-10-03)

1. **v3 synchronization resolved on 2026-10-03.** Working and flattened submission copies
   now include the fold-aware re-analysis, revised Fig. 5, Extended Data Fig. 3E and Fig. 6,
   and rewritten within-cancer text. All PDFs compile; the source ZIP compiles independently.
   Future edits to v2 still require an explicit sync (see `springer_nature/README.md`).
2. **v1 inherits the superseded estimator.** `tabular_fm_paper.tex` still reports the
   patient-averaged within-cancer losses (e.g. TabFM -0.084 at 5 years). Under within-test-set
   scoring this is -0.016. v1 is not to be submitted; do not reuse its Fig 3E or the sentences
   built on it. Details: `analysis/reusability/exploratory/NOTES_estimator_check.md`.
3. **The C-index is eligible-patient only.** It uses the saved horizon-classifier risk scores and
   patients' real survival times, so it is not a censoring-adjusted C-index over the whole cohort,
   and no censored time-to-event model has been fitted. A TabPFN survival check is planned, not run.
4. Exact package versions are not recorded (TODO in the Methods of v2).
5. L05 (case mix) cannot be cited until its correct full text is found; four other classics are
   cited generically only (`literature/claim_adjudication.tsv`).
6. Foundation-model-specific cost of pooling is supported for extreme survival only, and its ROC
   AUC interval touches zero (-0.043 to 0.003; Harrell C -0.036 to -0.007). The 3- and 5-year
   effects reported in earlier drafts were an estimator artefact.

Files ending `.aux .log .out .bbl .blg` are LaTeX build products and can be ignored.
