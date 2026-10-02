# L16: Figure and table review

Source: pdfs/L16.pdf, *TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models* (2025 preprint; revised 2026), DOI 10.48550/arXiv.2511.08667.

## Figure 1, visual comparison, PDF page 1

Plots TabArena-lite Elo scores for default, tuned, and tuned-plus-ensembled models. The horizontal dashed line marks the four-hour AutoGluon 1.4 extreme ensemble including TabPFNv2. The bars have no exact numeric labels, so no precise Elo values are transcribed from their heights. The abstract gives the authors' headline settings: up to 50,000 rows and 2,000 features, 100% win rate against default XGBoost on small/medium classification datasets and 87% on larger datasets up to 100,000 rows and 2,000 features (85% for regression).

## Figures 3-4, PDF pages 7-8

Leaderboard bars show TabArena-lite classification and regression results for datasets under 10,000 rows/500 features and across all datasets up to 100,000 rows/2,000 features. Figure 5 compares internal benchmark methods through normalized accuracy/AUROC and normalized RMSE/R2. Figure 6 shows corresponding regression results. Plotted bars have error bars but lack printed numeric values; the paper describes the comparison but exact chart readings must not be guessed.

## Figures 7-8, PDF page 9

Figure 7 compares TabPFN-2.5 distillations as MLP/tree ensembles against baselines; values are normalized and lack data labels. Figure 8 uses training rows up to 50,000 and features up to 900 in time heatmaps. Color bars report inference time about 4-289 seconds for one H100 and 2-93 seconds for four H100s over the shown grid. Individual cells are color-coded, not printed numerically.

## Tables

Table 1 model variants/capacity and Table 2 hyperparameter settings are in txt/L16.txt; Table 1 was visually checked. This is a developer technical report, so the benchmark claims should be presented as the authors' reported results, not independent evidence.

