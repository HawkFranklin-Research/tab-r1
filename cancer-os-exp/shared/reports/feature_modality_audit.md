# Feature Modality Audit

- Input root: `/home/prime/Documents/g3/c-5/gpt/processed/train_ready`
- View: `core`
- Top-variance feature cap: `100`

## Summary

| cancer   | view   |   total_features |   clinical_features |   nonclinical_features |   selected_top_variance_features | feature_prefix_counts                                                                                                                | selected_prefix_counts                                     |
|:---------|:-------|-----------------:|--------------------:|-----------------------:|---------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------|
| BRCA     | core   |           279248 |                 192 |                 279056 |                              100 | {"clinical": 192, "cnv_gistic": 84003, "cnv_log2": 84495, "methylation_gene": 13065, "mutation_binary": 28172, "rnaseq_gene": 69321} | {"rnaseq_gene": 100}                                       |
| ESCA     | core   |           102573 |                 250 |                 102323 |                              100 | {"clinical": 250, "cnv_gistic": 25087, "cnv_log2": 25087, "methylation_gene": 13066, "mutation_binary": 20014, "rnaseq_gene": 19069} | {"cnv_gistic": 45, "cnv_log2": 31, "methylation_gene": 24} |
| HNSCC    | core   |           294521 |                 235 |                 294286 |                              100 | {"clinical": 235, "cnv_gistic": 84509, "cnv_log2": 84509, "methylation_gene": 26019, "mutation_binary": 27861, "rnaseq_gene": 71388} | {"cnv_gistic": 10, "methylation_gene": 90}                 |
| LSCC     | core   |           297207 |                 228 |                 296979 |                              100 | {"clinical": 228, "cnv_gistic": 84495, "cnv_log2": 84495, "methylation_gene": 26013, "mutation_binary": 29591, "rnaseq_gene": 72385} | {"cnv_gistic": 34, "cnv_log2": 66}                         |
| LUAD     | core   |           297658 |                 210 |                 297448 |                              100 | {"clinical": 210, "cnv_gistic": 84495, "cnv_log2": 84495, "methylation_gene": 26015, "mutation_binary": 29998, "rnaseq_gene": 72445} | {"methylation_gene": 100}                                  |

## All Feature Prefix Counts

| cancer   | view   | modality         |   count |
|:---------|:-------|:-----------------|--------:|
| BRCA     | core   | clinical         |     192 |
| BRCA     | core   | cnv_gistic       |   84003 |
| BRCA     | core   | cnv_log2         |   84495 |
| BRCA     | core   | methylation_gene |   13065 |
| BRCA     | core   | mutation_binary  |   28172 |
| BRCA     | core   | rnaseq_gene      |   69321 |
| ESCA     | core   | clinical         |     250 |
| ESCA     | core   | cnv_gistic       |   25087 |
| ESCA     | core   | cnv_log2         |   25087 |
| ESCA     | core   | methylation_gene |   13066 |
| ESCA     | core   | mutation_binary  |   20014 |
| ESCA     | core   | rnaseq_gene      |   19069 |
| HNSCC    | core   | clinical         |     235 |
| HNSCC    | core   | cnv_gistic       |   84509 |
| HNSCC    | core   | cnv_log2         |   84509 |
| HNSCC    | core   | methylation_gene |   26019 |
| HNSCC    | core   | mutation_binary  |   27861 |
| HNSCC    | core   | rnaseq_gene      |   71388 |
| LSCC     | core   | clinical         |     228 |
| LSCC     | core   | cnv_gistic       |   84495 |
| LSCC     | core   | cnv_log2         |   84495 |
| LSCC     | core   | methylation_gene |   26013 |
| LSCC     | core   | mutation_binary  |   29591 |
| LSCC     | core   | rnaseq_gene      |   72385 |
| LUAD     | core   | clinical         |     210 |
| LUAD     | core   | cnv_gistic       |   84495 |
| LUAD     | core   | cnv_log2         |   84495 |
| LUAD     | core   | methylation_gene |   26015 |
| LUAD     | core   | mutation_binary  |   29998 |
| LUAD     | core   | rnaseq_gene      |   72445 |

## Selected Top-Variance Prefix Counts

| cancer   | view   | modality         |   count |
|:---------|:-------|:-----------------|--------:|
| BRCA     | core   | rnaseq_gene      |     100 |
| ESCA     | core   | cnv_gistic       |      45 |
| ESCA     | core   | cnv_log2         |      31 |
| ESCA     | core   | methylation_gene |      24 |
| HNSCC    | core   | cnv_gistic       |      10 |
| HNSCC    | core   | methylation_gene |      90 |
| LSCC     | core   | cnv_gistic       |      34 |
| LSCC     | core   | cnv_log2         |      66 |
| LUAD     | core   | methylation_gene |     100 |
