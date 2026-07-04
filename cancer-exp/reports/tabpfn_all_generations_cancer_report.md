# TabPFN Generation Comparison on Cancer Multiomics

- Output root: `/home/prime/Documents/g3/cancer-exp/outputs/tabpfn_all_generations_top100`
- Dataset source: `/home/prime/Documents/g3/cancer-exp/datasets_top100`
- Feature cap: 100 non-clinical top-variance features per exported dataset, required so legacy TabPFN v1 can run.
- Compared generations: v1, v2, v2.5, v2.6, v3.
- All prediction CSVs and raw `.npz` prediction files are saved under each run directory.

## Mean Metrics By Generation

| model_name   |   accuracy |       f1 |   roc_auc |   log_loss |
|:-------------|-----------:|---------:|----------:|-----------:|
| tabpfn_v1    |   0.817707 | 0.512411 |  0.777403 |   0.35245  |
| tabpfn_v2    |   0.821824 | 0.613253 |  0.788935 |   0.338918 |
| tabpfn_v2_5  |   0.820667 | 0.614446 |  0.788212 |   0.327196 |
| tabpfn_v2_6  |   0.822279 | 0.586107 |  0.785418 |   0.32616  |
| tabpfn_v3    |   0.829351 | 0.567595 |  0.785355 |   0.321549 |

## Mean Metrics By Task Family And Generation

| task_family   | model_name   |   accuracy |        f1 |   roc_auc |   log_loss |
|:--------------|:-------------|-----------:|----------:|----------:|-----------:|
| cancer_type   | tabpfn_v1    |   0.835391 | 0.813457  |  0.97912  | 0.441934   |
| cancer_type   | tabpfn_v2    |   0.895062 | 0.905109  |  0.991808 | 0.193059   |
| cancer_type   | tabpfn_v2_5  |   0.895062 | 0.905109  |  0.991809 | 0.201484   |
| cancer_type   | tabpfn_v2_6  |   0.895062 | 0.905057  |  0.991808 | 0.192794   |
| cancer_type   | tabpfn_v3    |   0.895062 | 0.90503   |  0.991809 | 0.190706   |
| os_event      | tabpfn_v1    |   0.66944  | 0.0627451 |  0.559596 | 0.605907   |
| os_event      | tabpfn_v2    |   0.66574  | 0.246099  |  0.580121 | 0.603549   |
| os_event      | tabpfn_v2_5  |   0.663427 | 0.248485  |  0.578675 | 0.606806   |
| os_event      | tabpfn_v2_6  |   0.66665  | 0.191818  |  0.573088 | 0.601667   |
| os_event      | tabpfn_v3    |   0.680794 | 0.154799  |  0.572961 | 0.599304   |
| source        | tabpfn_v1    |   0.998619 | 0.999231  |  0.999233 | 0.0132576  |
| source        | tabpfn_v2    |   0.998619 | 0.999231  |  0.999233 | 0.0445941  |
| source        | tabpfn_v2_5  |   0.998619 | 0.999231  |  0.999233 | 0.0091108  |
| source        | tabpfn_v2_6  |   0.998619 | 0.999231  |  0.999233 | 0.0151172  |
| source        | tabpfn_v3    |   0.998619 | 0.999231  |  0.999233 | 0.00706571 |

## Dataset-Level Metrics

| dataset                    | model_name   | version   | task_type   | status   |   accuracy |        f1 |   roc_auc |    log_loss | task_family   |
|:---------------------------|:-------------|:----------|:------------|:---------|-----------:|----------:|----------:|------------:|:--------------|
| ALL_core_cancer_type_top95 | tabpfn_v1    | v1        | multiclass  | success  |   0.835391 | 0.813457  |  0.97912  | 0.441934    | cancer_type   |
| ALL_core_cancer_type_top95 | tabpfn_v2    | v2        | multiclass  | success  |   0.895062 | 0.905109  |  0.991808 | 0.193059    | cancer_type   |
| ALL_core_cancer_type_top95 | tabpfn_v2_5  | v2_5      | multiclass  | success  |   0.895062 | 0.905109  |  0.991809 | 0.201484    | cancer_type   |
| ALL_core_cancer_type_top95 | tabpfn_v2_6  | v2_6      | multiclass  | success  |   0.895062 | 0.905057  |  0.991808 | 0.192794    | cancer_type   |
| ALL_core_cancer_type_top95 | tabpfn_v3    | v3        | multiclass  | success  |   0.895062 | 0.90503   |  0.991809 | 0.190706    | cancer_type   |
| BRCA_core_os_event_top100  | tabpfn_v1    | v1        | binary      | success  |   0.870787 | 0         |  0.551473 | 0.394416    | os_event      |
| BRCA_core_os_event_top100  | tabpfn_v2    | v2        | binary      | success  |   0.870787 | 0         |  0.599719 | 0.376451    | os_event      |
| BRCA_core_os_event_top100  | tabpfn_v2_5  | v2_5      | binary      | success  |   0.870787 | 0         |  0.568864 | 0.380119    | os_event      |
| BRCA_core_os_event_top100  | tabpfn_v2_6  | v2_6      | binary      | success  |   0.870787 | 0         |  0.586676 | 0.374284    | os_event      |
| BRCA_core_os_event_top100  | tabpfn_v3    | v3        | binary      | success  |   0.870787 | 0         |  0.532118 | 0.38185     | os_event      |
| BRCA_core_source_top100    | tabpfn_v1    | v1        | binary      | success  |   0.994475 | 0.996923  |  0.996933 | 0.0273885   | source        |
| BRCA_core_source_top100    | tabpfn_v2    | v2        | binary      | success  |   0.994475 | 0.996923  |  0.996933 | 0.0238367   | source        |
| BRCA_core_source_top100    | tabpfn_v2_5  | v2_5      | binary      | success  |   0.994475 | 0.996923  |  0.996933 | 0.0238834   | source        |
| BRCA_core_source_top100    | tabpfn_v2_6  | v2_6      | binary      | success  |   0.994475 | 0.996923  |  0.996933 | 0.0267177   | source        |
| BRCA_core_source_top100    | tabpfn_v3    | v3        | binary      | success  |   0.994475 | 0.996923  |  0.996933 | 0.0241594   | source        |
| ESCA_core_os_event_top100  | tabpfn_v1    | v1        | binary      | success  |   0.571429 | 0         |  0.432292 | 0.691358    | os_event      |
| ESCA_core_os_event_top100  | tabpfn_v2    | v2        | binary      | success  |   0.607143 | 0.266667  |  0.502604 | 0.694518    | os_event      |
| ESCA_core_os_event_top100  | tabpfn_v2_5  | v2_5      | binary      | success  |   0.571429 | 0.333333  |  0.520833 | 0.685433    | os_event      |
| ESCA_core_os_event_top100  | tabpfn_v2_6  | v2_6      | binary      | success  |   0.535714 | 0.434783  |  0.536458 | 0.705978    | os_event      |
| ESCA_core_os_event_top100  | tabpfn_v3    | v3        | binary      | success  |   0.607143 | 0.352941  |  0.578125 | 0.681655    | os_event      |
| HNSCC_core_os_event_top100 | tabpfn_v1    | v1        | binary      | success  |   0.631579 | 0.313725  |  0.61819  | 0.649873    | os_event      |
| HNSCC_core_os_event_top100 | tabpfn_v2    | v2        | binary      | success  |   0.652632 | 0.47619   |  0.647276 | 0.635204    | os_event      |
| HNSCC_core_os_event_top100 | tabpfn_v2_5  | v2_5      | binary      | success  |   0.642105 | 0.5       |  0.65097  | 0.652754    | os_event      |
| HNSCC_core_os_event_top100 | tabpfn_v2_6  | v2_6      | binary      | success  |   0.642105 | 0.46875   |  0.637581 | 0.638605    | os_event      |
| HNSCC_core_os_event_top100 | tabpfn_v3    | v3        | binary      | success  |   0.652632 | 0.421053  |  0.62373  | 0.646927    | os_event      |
| HNSCC_core_source_top100   | tabpfn_v1    | v1        | binary      | success  |   1        | 1         |  1        | 0.00621619  | source        |
| HNSCC_core_source_top100   | tabpfn_v2    | v2        | binary      | success  |   1        | 1         |  1        | 0.0213962   | source        |
| HNSCC_core_source_top100   | tabpfn_v2_5  | v2_5      | binary      | success  |   1        | 1         |  1        | 0.00126432  | source        |
| HNSCC_core_source_top100   | tabpfn_v2_6  | v2_6      | binary      | success  |   1        | 1         |  1        | 0.00992281  | source        |
| HNSCC_core_source_top100   | tabpfn_v3    | v3        | binary      | success  |   1        | 1         |  1        | 1.4954e-05  | source        |
| LSCC_core_os_event_top100  | tabpfn_v1    | v1        | binary      | success  |   0.606742 | 0         |  0.555026 | 0.658855    | os_event      |
| LSCC_core_os_event_top100  | tabpfn_v2    | v2        | binary      | success  |   0.606742 | 0.313725  |  0.569841 | 0.662189    | os_event      |
| LSCC_core_os_event_top100  | tabpfn_v2_5  | v2_5      | binary      | success  |   0.662921 | 0.318182  |  0.578307 | 0.653657    | os_event      |
| LSCC_core_os_event_top100  | tabpfn_v2_6  | v2_6      | binary      | success  |   0.617978 | 0.0555556 |  0.539947 | 0.655584    | os_event      |
| LSCC_core_os_event_top100  | tabpfn_v3    | v3        | binary      | success  |   0.606742 | 0         |  0.545503 | 0.65395     | os_event      |
| LSCC_core_source_top100    | tabpfn_v1    | v1        | binary      | success  |   1        | 1         |  1        | 0.0109783   | source        |
| LSCC_core_source_top100    | tabpfn_v2    | v2        | binary      | success  |   1        | 1         |  1        | 0.00651492  | source        |
| LSCC_core_source_top100    | tabpfn_v2_5  | v2_5      | binary      | success  |   1        | 1         |  1        | 0.000870094 | source        |
| LSCC_core_source_top100    | tabpfn_v2_6  | v2_6      | binary      | success  |   1        | 1         |  1        | 0.00680396  | source        |
| LSCC_core_source_top100    | tabpfn_v3    | v3        | binary      | success  |   1        | 1         |  1        | 1.71975e-05 | source        |
| LUAD_core_os_event_top100  | tabpfn_v1    | v1        | binary      | success  |   0.666667 | 0         |  0.640999 | 0.635033    | os_event      |
| LUAD_core_os_event_top100  | tabpfn_v2    | v2        | binary      | success  |   0.591398 | 0.173913  |  0.581165 | 0.649382    | os_event      |
| LUAD_core_os_event_top100  | tabpfn_v2_5  | v2_5      | binary      | success  |   0.569892 | 0.0909091 |  0.574402 | 0.662067    | os_event      |
| LUAD_core_os_event_top100  | tabpfn_v2_6  | v2_6      | binary      | success  |   0.666667 | 0         |  0.564776 | 0.633884    | os_event      |
| LUAD_core_os_event_top100  | tabpfn_v3    | v3        | binary      | success  |   0.666667 | 0         |  0.585328 | 0.632135    | os_event      |
| LUAD_core_source_top100    | tabpfn_v1    | v1        | binary      | success  |   1        | 1         |  1        | 0.00844717  | source        |
| LUAD_core_source_top100    | tabpfn_v2    | v2        | binary      | success  |   1        | 1         |  1        | 0.126629    | source        |
| LUAD_core_source_top100    | tabpfn_v2_5  | v2_5      | binary      | success  |   1        | 1         |  1        | 0.0104253   | source        |
| LUAD_core_source_top100    | tabpfn_v2_6  | v2_6      | binary      | success  |   1        | 1         |  1        | 0.0170244   | source        |
| LUAD_core_source_top100    | tabpfn_v3    | v3        | binary      | success  |   1        | 1         |  1        | 0.00407131  | source        |

## Generated Plots

- `/home/prime/Documents/g3/cancer-exp/plots/all_generations_top100/all_generations_mean_metric_heatmap.png`
- `/home/prime/Documents/g3/cancer-exp/plots/all_generations_top100/all_generations_task_family_bars.png`
- `/home/prime/Documents/g3/cancer-exp/plots/all_generations_top100/all_generations_dataset_accuracy.png`
