---
license: other
task_categories:
- tabular-classification
tags:
- cancer
- multiomics
- overall-survival
- tabular-foundation-models
- benchmark
pretty_name: TABR1 Cancer OS Leakage-Safe Folds v1
---

# TABR1 Cancer OS Leakage-Safe Folds v1

This private research dataset contains 400 frozen, patient-grouped evaluation folds for fixed-window and extreme-contrast overall-survival classification across BRCA, ESCA, HNSCC, LSCC, and LUAD cohorts.

## Scientific contract

- Five repeats and five outer folds per eligible task/cohort combination.
- Approximately 64% training, 16% validation, and 20% testing.
- Patient identifiers are grouped so a patient cannot cross splits within a fold.
- Clinical features are excluded.
- Feature selection is variance ranking fitted on training rows only.
- Pooled tasks use the exact common non-clinical feature universe across cancers.
- Decision thresholds must be selected using validation data only.

The endpoints are defined in `label_contract.json`. This is binary endpoint classification, not continuous censored-survival modeling.

## Contents

Every `folds/**/*.tar.zst` bundle contains:

```text
train.parquet
validation.parquet
test.parquet
train_metadata.parquet
validation_metadata.parquet
test_metadata.parquet
selected_features.parquet
feature_selection_statistics.parquet
fold_config.json
```

`manifest.csv` and `manifest.json` provide sample counts, class counts, patient-overlap audits, feature/modality summaries, bundle checksums, and portable bundle paths.

## Loading one fold

```bash
python examples/load_one_fold.py   --dataset-root .   --scope pooled   --endpoint os_3yr   --cancer ALL   --repeat 0   --fold 0
```

## Provenance and use restrictions

These are derived research artifacts from locally processed TCGA and CPTAC/LinkedOmics data. The repository is private while provenance, source terms, and redistribution requirements are reviewed. Users remain responsible for complying with the original data-source terms. Do not use these exploratory endpoints for clinical decision-making.
