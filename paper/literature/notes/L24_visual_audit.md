# Visual figure audit: L24

Source: `pdfs/L24.pdf`; viewed rendered page 7 (journal pagination).

- Figures 1 and 2 show time-AUC and time-NDCG curves for Flight Delay and LETOR. Curves are not accompanied by pointwise numeric labels, so no values were visually estimated.
- Tables 1-4 on the inspected pages contain dataset sizes, training times, test AUC/NDCG, and sampling-ratio comparisons. Exact cells are transcribed in `txt/L24.txt`; use those tables, not curve read-offs, for quantitative claims.
- The text reports LightGBM speedups of 2.1x, 2.6x, 1.6x, 14x, and 13x over the stated baselines on Allstate, Flight Delay, LETOR, KDD10, and KDD12, respectively; KDD10 and KDD12 baseline runs were out of memory.

The inspected figures are quantitative but lack labeled coordinates; text/table values are preferred.
