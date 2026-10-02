# L08: Figure and table review

Source: pdfs/L08.pdf, *Robust prediction under missingness shifts* (2024 preprint), DOI 10.48550/arXiv.2406.16484.

## Figure 2, PDF page 7

Shows change in MSE relative to the analytical Bayes predictor for 25% target missingness, for no shift and for models trained under a 50%-to-25% missingness shift. Panels separate non-monotone MAR and Gaussian self-masking MNAR, each at high and low feature correlation. The plot marks 10 random reruns. Most distributions have no printed numeric labels; x-axis tick ranges are approximately 0-0.5 depending on panel. One arrow is explicitly labeled 0.88. Do not infer exact medians from the plotted violins.

## Figures 3-4, PDF page 9

Figure 3 plots change in MSE from complete-data prediction in simulated data, with x-axis extending to about 4. Figure 4 shows MSE on semi-simulated LBIDD data, with x-axis about 0.25-0.75. Point/violin values are not individually labeled. Adjacent prose reports that NeuMiss repeatedly performs worse than a simple mean model, with MSE approximately 1.28 in the high-missingness setting.

## Figures 5-7, PDF pages 17-18

Figures compare 25% and 50% target missingness against Bayes or complete-data predictors. The plots explicitly clip some outlying results for readability; axes show change in MSE. Individual points are not printed as numbers. The authors' text describes MIWAE/MICE+Y as strong in some Y-dependent settings and NeuMISE as remaining close to complete-data performance in both high- and low-correlation simulations. Treat this as evidence that informative missingness can carry prediction signal under some deployment settings, not as evidence about structural zero-filled omics tables.

## Equations and tables

Displayed equations, Table 1 (50 variables), and Tables 2-4 are in txt/L08.txt. The rendered PDF confirms equations are laid out as mathematical expressions. Numerical graph values lacking labels remain unreported rather than guessed.

