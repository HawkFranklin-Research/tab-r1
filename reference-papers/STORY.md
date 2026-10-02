# Four Reusability Reports, read as stories

All four papers are *Nature Machine Intelligence* **Reusability Reports**. Each takes a published
NMI method, re-runs it, pushes it somewhere new, and returns a verdict. Full text and
panel-by-panel figure notes are in each folder's `paper.md`; this file is about *how they tell
the story*.

| Folder | Reused method (original paper) | Field |
|---|---|---|
| `00757-8_scrna-transformers/` | scBERT (Yang et al., NMI 2022) | single-cell genomics |
| `00798-7_holography-unpaired/` | FMGAN (Lee et al., NMI 2023) | computational imaging |
| `00923-6_vgae-toxicity/` | NYAN (Lam et al., NMI 2023) | drug discovery |
| `01166-9_alphatensor-quantum/` | AlphaTensor-Quantum (Ruiz et al., NMI 2025) | quantum computing |

---

## 1. scBERT: "it works, but it is hungrier for balance than anyone said"

**What they reproduced.** They re-ran the authors' own code (commit `8ac7c1e`) on two of the
original datasets.
- Annotation matched closely: Zheng68k F1 0.677 vs 0.691 reported; MacParland 0.960 vs 0.959.
- Novel-cell-type detection did not reproduce: only plasma cells were flagged.

**What they added.**
- A harder dataset, NeurIPS 2022: 7 cell types, a 262–10,757 imbalance, and inter-type
  correlation of 0.91–0.99.
- A Seurat baseline: scBERT won (0.840 vs 0.816, P = 0.0004).
- Rebalancing experiments. Subsampling raised F1 from 0.640 to 0.704, and novel detection from
  0.087 to 0.319. Focal loss did nothing.
- A threshold sweep.
- A replication of the imbalance effect back on Zheng68k.

**The story in one line.** The model is good, but its behaviour is governed by something the
original authors underplayed, which is class distribution. Here is a cheap fix, and here it is
working again on the original data.

**Figure grammar.**
- Fig 1 makes the new arena look hard (overlapping UMAP, a correlation heatmap).
- Fig 2 is the whole argument in four panels: counts, then confusion matrices, then novel
  detection, then threshold.
- Fig 3 is the baselines and the failed alternative fix (focal loss).
- Fig 4 is a robustness sweep.
- Fig 5 closes the loop on the original dataset.
- The reproducibility evidence goes to Extended Data, not the main text.

**Tone.** It opens and closes with affirmation ("largely reproduce", "demonstrates the
potential"). The criticism is phrased as *"plays a more important role than initially
reported"*, which is firm without being hostile. It ends on a general lesson about transformers
plus a roadmap.

**Weak spots** (useful as warnings for us):
- The text and the figures disagree in places.
- The accuracy drops caused by rebalancing are never discussed.
- Train equals test in the reproduction, copied from the original paper.

## 2. FMGAN: "reliable inside a 10 mm window, and here is where it breaks"

**What they reproduced.** The bead dataset, with 5 seeds and 44 test images. The claims held:
FMGAN was best both in distribution (phase PCC 0.88) and out of distribution (0.90), with a
distance error of 0.3 ± 0.2 mm. PhaseGAN dropped out of distribution and CycleGAN failed.

**What they added.**
- Three simulated imperfect microscopes: noise, uniform blur, and tilted blur.
- A distance sweep from 2 to 26 mm.
- A variant, FMGAN†, with the optics built in.

**Results.**
- FMGAN collapses under tilted blur: phase PCC 0.09, distance error 13 mm.
- PhaseGAN copes (0.84), and FMGAN† recovers (0.91).
- The reliable distance window is about 7–18 mm.

**The story in one line.** The physics prior is the method's strength and also its boundary.
When the physics is known it wins. When it isn't, the more flexible competitor wins. Here is the
envelope in millimetres.

**Figure grammar.**
- Tables 1–3 carry every headline number.
- Fig 1 shows per-image *distributions* (KDEs). It is the only support for the "more consistent"
  claim.
- Fig 2 is qualitative proof, with hallucinated beads circled in red.
- Fig 3 is the envelope curve.
- Only 3 figures and no Methods section: the training details sit inside the Results.

**Tone.** "Highly reusable" is the headline. Every limitation comes with a mechanism (one
generator versus PhaseGAN's two; interference between beads) and with a remedy. The only direct
correction is a remark about learning rates. Note that the authors built PhaseGAN, the competitor
that wins under blur.

## 3. NYAN: "not only a generalist but also a specialist"

**What they reproduced.** They retrained on *half* the pretraining data (325k vs 650k
molecules), and still matched or beat the original on 3 of 4 tasks.
- BBB: 0.918 vs 0.932.
- Pgp: 0.949 vs 0.948.
- Tox21 (56 assays): 0.865 vs 0.856.
- Spearman correlation between original and reproduced scores: 0.83–0.93.

**What they added.**
- 30 toxicity datasets.
- A 10-way representation benchmark. NYAN came second to RDKit2D, with the difference not
  significant (Nemenyi test).
- An 8-way surrogate-model sweep, which found deep forest.
- A comparison with 6 state-of-the-art models. NYAN was third on AUROC but first on AUPRC (0.868
  vs 0.732).
- A new method, MT-NYAN, for 59-endpoint acute toxicity (R² 0.57 vs 0.54). A consensus ablation
  gave P = 3.9×10⁻¹⁰ (Wilcoxon).

**The story in one line.** A controlled set of substitutions that keeps the encoder fixed and
swaps everything around it, ending in a new state-of-the-art claim.

**Figure grammar.** This is the most "engineered" of the four.
- Fig 1 is a **workflow roadmap** that previews every later figure.
- Fig 2 is the reproducibility certificate (paired bars plus a correlation).
- Figs 3–5 each answer one substitution question.
- Fig 6 is the new method end to end: schematic, numbers, breadth, ablation with a p-value, and a
  t-SNE sanity check.
- Many headline numbers exist only inside the figures.

**Tone.** Purely supportive. Losses are recast as "second best". Limitations get one paragraph
framed as future work, and the conclusion is a slogan.

## 4. AlphaTensor-Quantum: "partly reproducible, unaffordable at scale; train once instead"

**What they reproduced.** Only 3 of DeepMind's circuit tensors had been released, and the
original hyperparameters ran out of memory.
- Without gadgets, all three matched.
- With gadgets, two failed: 12 vs the reported 4. A bigger budget brought them to 8 and 10.
- Cost per training step grows exponentially with qubit count (34 s/step at 15 qubits, versus
  0.06 s for the classical baseline).

**What they added.** A single *general* agent trained on random 5–8-qubit circuits.
- It is at least as good as size-specific agents.
- It beats the classical baseline on more than 45% of circuits, though only 23% at 8 qubits.
- Inference takes about 20 s.
- It recovers the benchmark optima without ever seeing them (Table 1).

**The story in one line.** The original is reproducible where the code exists, and its real
constraint is cost. A cheaper training regime keeps most of the value, and the agent even solves
the original benchmarks zero-shot.

**Figure grammar.**
- Fig 1 is the reproduction scorecard.
- Fig 2 is the cost argument that motivates the extension.
- Fig 3 is the main result.
- Fig 4 is the efficiency payoff.
- Table 1 loops back to Fig 1.

It uses a new, intuitive metric: the "improvement percentage", the share of circuits beaten.

**Tone.** Constructive. Gaps are blamed on missing code and compute ("further hyperparameter
tuning could probably reproduce…"). It praises the code ("well documented and easy to use") and
asks the original authors for exact hyperparameters. The conclusion is a "middle ground".

---

## What the four have in common

### The plot is always the same six beats
1. **The promise.** The field, the method, and the claim in the original authors' words, quoted.
2. **"In this report we…"** A roadmap paragraph that lists the experiments in the order they
   will appear. Every one of the four has it.
3. **Reproduction.** Re-run on the original data, with numbers side by side. Partial success is
   fine and is reported plainly (AlphaTensor-Quantum: 3 of 3 without gadgets, 1 of 3 with).
4. **New ground.** A new dataset, domain or stress test that the original never faced.
5. **The boundary.** One clear limitation with a *mechanism*: imbalance, unknown optics,
   compute scaling. Even NYAN, which has no real limitation, frames its losses as a ranking.
6. **The fix, and loop closure.** A cheap remedy (subsampling, FMGAN†, the general agent,
   MT-NYAN) that is tested, often with a p-value. Then the story returns to the original
   benchmark to show the fix holds there (Zheng68k; Table 1 in AlphaTensor-Quantum).

### What each figure position does
| Position | Job | Examples |
|---|---|---|
| Fig 1 | Set the ground: a roadmap, a scorecard, or why the new arena is hard | NYAN roadmap; AlphaTensor-Quantum scorecard; scBERT hard dataset; FMGAN distributions |
| Fig 2 | Either the reproduction certificate or the boundary argument | NYAN reproduction; AlphaTensor-Quantum cost; scBERT imbalance |
| Middle | One question per figure, answered with comparisons against baselines | NYAN Figs 3–5; scBERT Figs 3–4 |
| Last | The new contribution with an ablation or statistical test, then loop closure | MT-NYAN Fig 6; scBERT Fig 5; AlphaTensor-Quantum Table 1 |

Reading Fig 1 → Fig 2 → … → last gives the abstract on its own. Each figure has **one
message**, and its title is that message.

### House style
- **Short.** 3,100–6,000 words of body text, 3–6 main figures, 0–3 tables and 12–27 references.
  Abstracts are unstructured, 150–250 words, and end on a broader lesson.
- **Headings are claims** in scBERT and NYAN ("Subsampling improves scBERT's performance…").
- **Headline numbers in tables**, **distributions in figures**. FMGAN's KDEs and scBERT's box
  plots are used, not only means. Statistical tests appear where the claim is comparative: a
  paired t-test, Nemenyi, Wilcoxon.
- **The verdict is supportive with a boundary**: "highly reusable … however", "a middle ground",
  "more important than initially reported". Nobody writes a takedown.
- **Courtesy to the original authors**: they praise the code and make concrete requests
  (hyperparameters, circuit-to-tensor code).
- **Reproducibility hygiene**: a commit hash (scBERT), seeds, hardware, and the deviations from
  the original setup stated explicitly (AlphaTensor-Quantum's batch 128 vs 2,048).

### What they do badly (so we don't)
- Text and figures disagree, in scBERT and NYAN.
- Key numbers exist only inside figures, in NYAN.
- Their own losses are softened. FMGAN calls a 15-vs-4 result "slightly worse".
- No paper discloses an obvious interest. The FMGAN reviewers built PhaseGAN, the competitor
  that wins.

## How this maps onto tab-r1

Our project already *is* a reusability study. It just isn't told as one.

| Beat | What we have | Where |
|---|---|---|
| Promise | TabPFN (Hollmann et al., *Nature* 2025): strong small-data classification without tuning | `paper/`, `papers/` |
| Reproduction | 7 of TabPFN's benchmark datasets, re-run by Satya and by us. TabPFN 0.877 vs CatBoost 0.873. Generations v1→v3 at 0.862–0.871; TabFM 0.866 | `results-s2/`, `results-satya/`, `Evaluate-TABPFN/` (**not fold-matched yet, not in the paper**) |
| New ground | Cancer multiomics survival: 3,238 patients, 400 frozen test sets, 11 models | current paper |
| Boundary | Pooling across cancers: cohort shortcuts, and lower within-cancer ranking for foundation models (Fig 3E) | current paper |
| Fix and loop closure | **Missing.** The obvious candidate is pooling with per-cancer standardisation and no zero fingerprint, scored within cancer | `docs/future_work_survival_v2.md` (S2) |

The detailed section-by-section plan is in `paper/REVISION_PLAN.md`.
