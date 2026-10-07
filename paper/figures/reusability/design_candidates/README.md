# Figure 1A candidate

The raster candidate is now superseded by the simplified vector schematic in
`paper/analysis/reusability/build_reusability_figures.py`. It remains here as a
design reference only. The active PDFs use vector labels and shapes for panel A;
the complete Figure 1 PNG is exported at 300 DPI, matching the other panels.

`fig1_panel_a_schematic.png` is an AI-generated illustrative workflow, not experimental data. On 8 October 2026 it was incorporated into Figure 1A in all three manuscript versions. Other panels remain code-generated.

The schematic shows benchmark reproduction, separate cohort training, pooled training with cohort/missingness diagnostics, and paired scoring within diagnosis. Matrices, patient icons and rank connections are conceptual, not observations or measured rankings. Model icons are examples, not the complete eleven-model taxonomy.

Generated with the built-in image generation tool on 7 October 2026. Inaccurate automatically introduced modality headings were corrected to Molecular features.

## Initial Prompt

Use case: scientific-educational.
Create a publication-quality candidate for panel A of a cancer multiomics machine-learning reusability report. A very wide horizontal scientific schematic, pure white background, flat precise vector-like drawing, legible dark sans-serif labels, restrained blue, teal, orange and grey. Four evenly spaced stages connected left to right by slim arrows. Convey operations visually rather than four boxes of prose. No outer boxes, no decorative medical equipment, no gradients, no invented numeric performance plots. This is a study roadmap, not a claimed biological mechanism.
Stage 1 heading exactly "1  Reproduce". Draw miniature tabular benchmark datasets feeding two distinct model-family symbols: a transformer attention grid and a branching tree ensemble. Below, small label exactly "Original tabular benchmarks".
Stage 2 heading exactly "2  Within cancer". Draw FIVE compact distinct-colored patient groups, each paired with a tiny molecular-feature table, with a common model/evaluation symbol. Label groups exactly "BRCA", "ESCA", "HNSCC", "LSCC", "LUAD". Below, label exactly "Cancer-specific training".
Stage 3 heading exactly "3  Pool cancers". Merge the same five colors into one combined patient-feature matrix; include visible differently structured blank blocks to suggest cohort-specific missingness, not invented values. Two small diagnostic symbols underneath: cohort-colored identity tag and a binary missingness mask. Below, labels exactly "Pooled training" and "Cohort and missingness controls".
Stage 4 heading exactly "4  Score within diagnosis". Show the combined matrix separating back into the SAME five color-coded groups. Beside one illustrative same-color patient group, draw two aligned sets of ranked patient icons, connected patient-by-patient with fine grey lines, labelled exactly "Cancer-specific" and "Pooled". This means paired scoring of the same patients, not improvement or deterioration. Below, label exactly "Same patients, paired comparison".
Make model icons consistent between stages. Counts and detailed experimental protocol are deliberately omitted since adjacent quantitative panels supply those facts. Spacious crisp balanced composition suitable for a horizontal strip above three quantitative panels. No main figure title, no panel letter, no watermark. Do not copy any existing published illustration.

## Correction Prompt

Remove all Clinical, Mutation, CNV, Expression and Methylation headings above both combined matrices. Replace them with Molecular features. Preserve stages, cohort names, colors, white background, model illustrations, missingness mask and paired-ranking drawings; add no numeric results.

## Before Inclusion

Check label legibility at final panel size and state in the caption that the matrices are schematic. Detailed counts, budgets, permutation and held-out-cancer controls remain in the text and adjacent panels.
