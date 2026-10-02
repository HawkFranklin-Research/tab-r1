# Revision plan: tab-r1 manuscript, modelled on four NMI Reusability Reports

Written 2026-10-02. This is a plan only; `tabular_fm_paper.tex` has not been edited.
Background is in `reference-papers/STORY.md`, which covers how the four reports are built, and
in each `reference-papers/*/paper.md`.

---

## 0. The strategic decision first

Our work already follows the reusability arc: we reproduced TabPFN, moved to a new domain, found
a boundary, and mapped it. The current draft hides the first step and lacks the last. There are
two ways to submit:

| | A. NMI Reusability Report (**recommended**) | B. Stand-alone Article or Analysis |
|---|---|---|
| Eligibility | Reports may revisit work "published in *Nature Machine Intelligence* or elsewhere", so TabPFN (*Nature* 2025) qualifies. They are "currently written by invitation", so this needs a **pre-submission enquiry** to the editors. | Open submission |
| What changes | Add a Reproducibility section, retitle "Reusability report: …", unstructured abstract, 3–5 figures, about 4,000–5,000 words | Keep the current structure, tighten it, and add the statistics below |
| Fit with our history | Exact: recreation, then validation with Satya, then the cancer extension | Good, but the reproduction work goes unused |

The journal's own description of the format (1,500–2,000 words, one or two figures, no abstract)
is out of date. All four recent examples have abstracts and run 3,100–6,000 words with 3–6
figures.

Everything below assumes **A**. Most of it improves B as well.

---

## 1. Title

Reusability-report titles are "Reusability report: [what was tested, in plain words]". They
avoid colon subtitles and claims.

- **Reusability report: Tabular foundation models for cancer survival prediction from
  multiomics** (recommended; 13 words, mostly the required prefix)
- Reusability report: TabPFN and TabFM on pan-cancer multiomics survival

If we go with B, use one of the short options from the earlier discussion, for example *Pooling
Cancers Inflates Tabular Foundation Model Survival Scores*.

## 2. Abstract

Currently it is structured (Background, Methods, Results, Conclusions) and about 300 words. All
four reports use an **unstructured paragraph of 150–250 words** with the same moves:

1. Field and promise (1 sentence).
2. The original method and claim, citing Hollmann et al. (1 sentence).
3. "Here we assess the reusability of…" (1 sentence).
4. The reproduction result, with a number (1 sentence).
5. The new domain and the headline number. Lead with pooled 3-year 0.721 (n = 1,645) and
   extreme 0.786 (n = 937), as you wanted (1–2 sentences).
6. The boundary with a number: cancer type alone 0.707; within-cancer drop −0.07 to −0.08 for
   foundation models (1–2 sentences).
7. The fix or the recommendation (1 sentence).
8. The broader lesson (1 sentence).

Keep your earlier rules: single means rather than ranges, and plain words ("which features were
zero", not "structural zeros").

## 3. Introduction (4 paragraphs, about 600 words)

The pattern across all four papers is: field, then the original method with its claims quoted,
then why this domain is a stress test, then **"In this report we…"** listing every experiment in
the order the figures appear.

- **¶1, tables and trees.** Keep the current paragraph, shortened.
- **¶2, TabPFN and TabFM.** Quote TabPFN's own claim ("accurate predictions on small data"). Cite
  TabPFN-2.5 and TabPFN-3 (L16, L17 in `paper/literature`), and TabFM as a software release.
  - Add L01 (*Established machine learning matches tabular foundation models in clinical
    predictions*, 2026). It is the closest competitor and reaches a similar conclusion on
    clinical tasks. We must position against it, not ignore it.
- **¶3, why cancer multiomics is a stress test.** Keep the cohort-confounding argument (Soneson,
  Bernau). Add L02 and L03 (Herrmann, and Wissel 2024: adding omics often doesn't help) and L10
  (shortcut learning, *NMI* 2020).
- **¶4, "In this report we…"** First, reproduce TabPFN on its own benchmark datasets. Second,
  evaluate four TabPFN generations, TabFM and seven comparators within five cancers. Third, pool
  the cancers and test the gain against shortcut controls. Fourth, ask whether pooling helps
  within a diagnosis. Fifth, [the fix, if run].
- **The personal paragraph** about the earlier optimistic reading becomes **one sentence** in
  ¶4. Reusability reports use "more important than initially reported"-style phrasing, not
  autobiography.

## 4. Results

### 4.1 NEW: "Reproducibility" (Figure 2, about 400 words)

This is what we did with Satya, and it is currently absent. The assets are the 7 TabPFN
benchmark datasets (`results-s2/`, `results-satya/`) and the generation comparison v1→v3 plus
TabFM (`Evaluate-TABPFN/pfn3-test`, `Evaluate-TABPFN/tabfm-test`).

- **Blocker:** these runs are **not fold-matched**, as `paper/analysis/README.md` says. Before
  they can be confirmatory, `paper/analysis/run_matched_baselines.py` must run on identical
  folds. That script crashed earlier with a `TypeError`, so it needs a fix and a small run. This
  is the cheapest high-value job left.
- **Report it NYAN-style:** published value against our value per dataset, plus a Spearman
  correlation, plus one honest line on any mismatch. The originally reported per-dataset numbers
  must come from Hollmann et al.'s supplementary tables (`papers-info/`).
- Partial reproduction is acceptable and normal: 7 of 29 datasets, as AlphaTensor-Quantum
  reproduced 3 tensors. State why 7.

### 4.2 Cohorts and design (keep; shorten to about 250 words)

Keep the numbers, including the split-size wording you liked: about 1,050 patients fitted and
330 tested per split, 1,645 in total.

### 4.3 Within one cancer (keep; add a statistical test)

- **Add a Friedman test with Nemenyi post-hoc and a critical-difference diagram across the 13
  tasks.** NYAN uses exactly this, and it gives the "no decisive winner" claim a p-value instead
  of an adjective. It can be computed from `model_fold_metrics.csv` in seconds.
- Keep "7 of 13 tasks; margins up to 0.044; losses at most 0.024".

### 4.4 Pooling lifts every model (keep, tighten)

### 4.5 Shortcut controls (keep; apply the critique's corrections)

- Rename to the **zero-pattern control**. It includes measured zeros
  (`analyze_saved_cancer_results.py:270`).
- State that the controls and permutations ran on the **historical single split** (n_test =
  247), so the comparison with benchmark AUCs is contextual, not matched.
- Drop the "three-quarters of the gain" ratio and report 0.667 next to the pooled scores.
- Rewrite the held-out caveat: the selection was label-free but included the held-out cancer,
  and its effect could go either way.

### 4.6 Within-cancer effect of pooling (keep; this is our Fig 3E "boundary")

- **Add the difference-in-differences:** the foundation-model drop minus the tree drop, with a
  bootstrap CI, from the same draws. The wording of the twist depends on it.
- Say "several foundation-model configurations" (4 of 30 intervals exclude zero, all of them
  foundation models at 5-year or extreme), and acknowledge the multiplicity.
- "Point estimates below 0.5", not "below chance".
- "Trees showed smaller estimated changes (≤0.04), with intervals spanning zero", not
  "unaffected".
- Borrow AlphaTensor-Quantum's device of an intuitive companion metric: **the share of cancers
  in which pooling lowered within-cancer AUC**, per model.

### 4.7 NEW, optional but decisive: "the fix" (about 300 words, a Figure 5 panel)

Every one of the four reports ends with a tested remedy, and our paper is the only one without
one. The minimal version needs **no new folds**:

- Use the existing pooled 5-year and extreme fold files.
- Within each fold, z-score every feature *within each cancer* using that cancer's training
  rows. Replace zero-pattern blocks with NaN or the cancer mean, and add a cancer one-hot.
- Run TabPFN v2.5 and v3, TabFM, random forest and CatBoost.
- Score within cancer exactly like Fig 3E.

The training sets are about 750 and 600 patients, under TabPFN's 1,000-row CPU limit, so it runs
locally within 12 cores and 12 GB. About 2 endpoints × 25 folds × 5 models.

Either outcome helps the paper:
- **It restores within-cancer AUC:** this is our FMGAN†, a diagnosed boundary plus a working
  remedy.
- **It doesn't:** we have shown the shortcut is not simply the zero fingerprint, which is
  stronger evidence for the boundary.

Needs your go-ahead (subsample first, as per our rules).

### 4.8 Probability and cost: move to Extended Data

The reports keep their main figures for the argument. Runtime and calibration become one
Extended Data figure.
- Fix the runtime text: say "pooled-task medians 11–38 s" or use Figure 5's all-fold medians of
  2.7–5.3 s, consistently.
- Drop "same CPU hardware": the classical models ran locally and the foundation models on the
  cloud VM.

## 5. Figures: from 5 × 6 panels to 4–5 focused figures

| New | Message (which is also the figure title) | Built from |
|---|---|---|
| **Fig 1** | Roadmap: the original claim, then reproduction, then the cancer extension, then the boundary, then the fix | New schematic (NYAN Fig 1 style) + current Fig 1 A/B/D/F |
| **Fig 2** | TabPFN reproduces on its own benchmarks | New: reported vs reproduced paired bars, Spearman, generation comparison |
| **Fig 3** | Within one cancer, no model wins decisively | Current Fig 2 B/C/D + new critical-difference diagram |
| **Fig 4** | Pooling lifts every model, and simple controls reach similar levels | Current Fig 3 A/B + Fig 4 A/B/D/E |
| **Fig 5** | Pooling lowered within-cancer ranking for foundation models [and the fix] | Current Fig 3E + per-cancer paired distributions + fix panel |
| ED Figs | Cohort detail, PR curves, calibration, runtime, feature modalities, confusion | Remaining panels |

Style rules taken from the four papers:
- One message per figure.
- Show **distributions** (paired per-fold or per-patient deltas as violins or strips), not only
  means.
- Put every headline number in a table or the text, never only inside a figure. NYAN and scBERT
  fail this.

## 6. Discussion (about 700 words)

The report pattern is: recap ("First … Second … Third …"), mechanism, verdict with an envelope,
courtesy and requests to the original developers, then future directions.

- **Verdict line, in FMGAN style:** "TabPFN reproduces and is reusable for single-cancer survival
  classification, where it is competitive with tuned tree ensembles. Its pooled pan-cancer scores
  should not be read as patient-level prognosis."
- **Mechanism:** keep the in-context hypothesis, explicitly labelled as a hypothesis, and how to
  test it (which the fix in §4.7 partly does).
- **Keep the stance but soften the absolutes**, as the critique suggested. "A pooled score
  answers a different question from the one asked once the diagnosis is known" replaces "no
  clinician asks". Extreme survival "does not estimate fixed-horizon performance" replaces
  "inappropriate".
- **NEW, courtesy plus requests** (AlphaTensor-Quantum style):
  - Praise what worked (TabPFN installed and ran without tuning; v3 removed the CPU row limit).
  - Request what would help reuse: CPU guidance for more than 1,000 rows in v2–v2.6, documented
    version differences, and a survival interface.
- **Future directions** in one paragraph, pointing to `docs/future_work_survival_v2.md`:
  censored time-to-event, clinical vs omics, METABRIC.

## 7. Methods

- Add a **Reproducibility experiments** subsection: datasets, versions, seeds, and deviations
  from Hollmann et al.
- **Pin versions** in scBERT style: TabPFN package version and commit, `tabpfn_3` checkpoint
  hash, `tabfm` commit, AutoGluon/CatBoost/XGBoost versions. These are in the submodule pointers
  and `cloud/` metadata.
- Fix the Table 2 caption: "macro-average of the three endpoint summaries".
- Name the two AUC summaries distinctly:
  - fold-mean AUC (Tables 1–3);
  - patient-averaged within-cancer AUC (Fig 5).

## 8. Length targets

| | Current | Target (A) |
|---|---|---|
| Body words | about 5,500 | 4,000–5,000 |
| Main figures | 5 (30 panels) | 4–5 (about 18 panels) |
| Tables | 3 | 2–3 (reproduction + shortcuts) |
| References | 26 | 30–40 (add L01–L04, L09, L10, L16, L17) |

## 9. Order of work

1. **Your decisions:** A or B; whether to run the fix (§4.7); whether to fix and run the
   fold-matched reproduction (§4.1).
2. **Statistics needing no runs** (minutes): difference-in-differences, Friedman/Nemenyi, share
   of cancers harmed.
3. Wording fixes from the critique (§4.5, §4.6, §4.8, §7).
4. Restructure the figures (§5) in `build_manuscript_assets.py`.
5. Rewrite the text section by section in the order Results → Discussion → Introduction →
   Abstract → Title, which is how the abstracts of all four reports read: written last, from
   the figures.
6. If A: draft a short pre-submission enquiry to *NMI*.
