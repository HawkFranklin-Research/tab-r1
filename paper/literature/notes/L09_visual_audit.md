# L09: Figure and table review

Source: pdfs/L09.pdf, *Characterizing and Avoiding Negative Transfer* (CVPR 2019), DOI 10.1109/CVPR.2019.01155.

## Tables 1-2, PDF pages 6-7

Tables report classification accuracy (percent) with negative-transfer gaps in parentheses. Table 1 includes W-to-D and A-to-D transfer tasks at perturbation levels epsilon = 0.0, 0.3, 0.7, 0.9 and target-label proportions 0%, 10%, 30%, 50%. Table 2 reports four benchmark datasets at epsilon = 0.7 and 10% labeled target data. Exact cells and uncertainty values are retained in txt/L09.txt; the rendered pages confirm that table reading order and row grouping need inspection before reusing individual cells. The paper is a computer-vision transfer study, used here only as analogy.

## Figures 3-4, PDF pages 6-8

Figure 3 plots accuracy versus perturbation rate and amount of labeled target data; point values are not printed. Figure 4 is a t-SNE/domain visualization. The paper's text states that performance degrades as perturbation increases and negative transfer depends on target labels and domain divergence. No point-wise values are inferred from pixels.

