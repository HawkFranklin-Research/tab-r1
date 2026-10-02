# L17: Figure and table review

Source: pdfs/L17.pdf, *TabPFN-3: Technical Report* (2026 preprint), DOI 10.48550/arXiv.2605.13986.

## Figure 1, PDF page 1

TabArena largest subset covers 10,000-100,000 samples. The chart is an Elo leaderboard with a dashed AutoGluon 1.5 Extreme four-hour ensemble reference; individual bar values are not printed. The abstract reports TabPFN-3 improves on the prior TabPFN-2.5 by up to 20x in speed. TabPFN-3-Plus/Thinking is reported to gain 200 Elo overall and 420 Elo on the largest subset, and to be more than 10x faster than AutoGluon 1.5 Extreme.

## Figures 2-3, PDF page 3

Figure 2 gives the TabArena medium-data Pareto frontier for 15 datasets and 135 tasks. Figure 3 is a win-rate matrix with numeric percentages inside cells; the 12 x 12 entries are retained in the page extraction in txt/L17.txt. The report describes the tuned/Thinking configurations as winning against the listed alternatives; use extracted cells only after checking model/version order against the original matrix.

## Figure 4, PDF page 4

Printed capacity table:

| Model | Rows | Features | Classification parameters | Regression parameters |
|---|---:|---:|---:|---:|
| TabPFN-v1 | 1,000 | 100 | 26M | not listed |
| TabPFN-v2 | 10,000 | 500 | 7M | 11M |
| TabPFN-2.5 | 100,000 | 2,000 | 7M | 10M |
| TabPFN-2.6 | 100,000 | 2,000 | 11M | 13M |
| TabPFN-3 | 1,000,000 | 200; also 100,000/2,000 and 1,000/20,000 regimes | 53M | 58M |

The right comparison panel reports a Wilcoxon p < 0.0001 for TabPFN-3 versus TabPFN-2.5 across per-dataset TabArena scores. Point values are unlabeled.

## Figures 10-12, PDF page 13

Figure 10 covers 51 TabArena datasets up to 100,000 rows. Figure 11 plots total time per 1,000 samples against improvability; exact points are not labeled. Figure 12 is a numeric pairwise win-rate matrix and should be read with the model order printed on the panel. Adjacent prose reports +72 Elo for TabPFN-3 over Real-TabPFN-2.5 tuned and more than +100 Elo for Thinking over non-TabPFN models, while describing Thinking as about 10x faster than the four-hour AutoGluon 1.5 extreme ensemble.

## Figures 15-17, PDF pages 16-17

Figure 15 uses a 13-dataset benchmark up to 1M rows and 200 features (9 classification, 4 regression); plotted normalized values have confidence bars but no labels. Figure 16 shows scaling at 100k, 250k, 500k and 1M training rows with 95% bootstrap bands. TabPFN-3's visible classification curve is approximately 0.53, 0.70, 0.82 and 0.92 normalized score at those sizes; these are visual estimates, not printed values. Figure 17 reports normalized ROC-AUC one-vs-rest of 1.00 for TabPFN-3 on its synthetic many-class benchmark, with up to 100 classes and 9 datasets. The adjacent text reports TabICLv2 at 0.89 and TabPFN-2.5 at 0.83.

## Scope

This is a developer technical report. Its large-row results do not substitute for our biomedical evaluation, and its hardware/API settings differ from our CPU checkpoint runs.

