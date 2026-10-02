# L03: Figure and table review

Source: pdfs/L03.pdf, *Does combining numerous data types in multi-omics data improve or hinder performance in survival prediction?* (2024), DOI 10.1186/s12911-024-02642-9.

## Figure 1, printed counts and visual rank distributions, PDF page 7

Shows dataset-specific ranks for block combinations under random survival forest, block forest, and inverse-probability lasso. Lower ranks are better; the 31 block combinations are sorted by mean rank. Boxplots summarize ranks over 14 datasets. Individual boxplot medians are not numerically labeled, so only the direction and spread can be visually read. The combination using all five blocks is marked with a red outline in each panel.

## Figure 2, printed counts, PDF page 8

Among the 30 highest-ranked method/block combinations, plotted modality inclusion counts are:

| Modality | Count in top 30 |
|---|---:|
| mRNA | 27/30 |
| miRNA | 14/30 |
| Copy-number variation | 13/30 |
| Methylation | 14/30 |
| DNA sequencing / mutation | 8/30 |

If all 155 method/block combinations were equally likely to appear in the top 30, the expected count for a modality is 15.5. The paper reports a hypergeometric-test p-value of 5.9 x 10^-6 for the frequent appearance of mRNA in the top 30. This is printed in the adjacent main text, not in the plotted graphic. Lasso is highlighted as frequent among the best combinations, but the article notes that clinical covariates were not penalized, limiting direct comparison with other benchmark settings.

## Tables and equations

The downloaded PDF provides table text in reading order; the structured Europe PMC extraction for this source also preserves table rows and display-equation text. Check txt/L03.txt for Tables 1-3. Figure rank values are plotted but not individually printed, so do not report guessed exact ranks.

