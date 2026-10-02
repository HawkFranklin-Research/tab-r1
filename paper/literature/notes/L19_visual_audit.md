# Visual figure audit: L19

Source: `pdfs/L19.pdf`; viewed rendered pages 3, 5, 9, and 14 and the figure/table pages exposed in the contact sheets.

- Figures 1-4 (pp. 3-5): architecture, embedding, and representation-collapse illustrations. Figure 3 shows feature embeddings projected to two dimensions; Figure 4 compares representations with/without RoPE. These are explanatory or illustrative, not numeric benchmark panels.
- Figure 9 (p. 9): relative improvement distributions over 200 datasets for accuracy, AUC, and log loss. Exact per-dataset values are not printed; plotted spread should remain qualitative unless source data are obtained. Caption says green triangles are mean relative improvements.
- Figure 10 (p. 9): relative accuracy improvement across curriculum stages for 200 classification datasets. Individual points are not labeled; paper text reports mean rank progression 11.4 (ninth place), 7.6 (second), and 6.95 (first) across stages.
- Figure B.1 (p. 14): fit/predict runtime scaling on A100; text and plot label approximate speedups of 1.5x for small tables and 5.0x for large tables. Caption states each point is one dataset and only datasets with fewer than 30,000 samples are included because TabPFNv2 uses subsampling above that size.

Other performance figures visible in the PDF have unlabeled individual points. Do not transcribe estimated chart coordinates as exact values. Numeric claims should be sourced from printed tables or prose in `txt/L19.txt`.
