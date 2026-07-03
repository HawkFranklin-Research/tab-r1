# Batch Execution Information

## Execution Summary
- **Total Datasets:** 7
- **Successful:** 3
- **Failed:** 4
- **Skipped:** 3 (Already successful in previous turn)

## Status Breakdown

| Dataset | Status | Diagnosis / Reason |
| :--- | :--- | :--- |
| **ada** | SUCCESS (Skipped) | Successfully processed in the first pass. |
| **australian** | SUCCESS (Skipped) | Successfully processed in the first pass. |
| **chum** | SUCCESS (Skipped) | Successfully processed in the first pass. |
| **blood_transfusion** | FAILED | **Label Error:** Labels are `{1, 2}`. Scikit-learn ROC functions expect `{0, 1}`. |
| **car** | FAILED | **Multiclass Logic:** Mismatch between CatBoost's 2D prediction shape and the prediction saver's expectation. |
| **cmc** | FAILED | **Multiclass Logic:** Similar dimension error in the prediction persistence layer. |
| **credit-g** | FAILED | **Label Consistency:** Issues with mapping string/numeric labels during the plotting phase. |

## Technical Take on Failures

Our pipeline is technically robust but lacks a **"Data Normalization Layer"** in Phase 1. 

1. **The Binary Problem (`blood_transfusion`):** Many real-world datasets use `1/2` or `Y/N`. While models like TabPFN can handle this, standard visualization libraries (like the ROC curve in Phase 3) are strictly mathematically oriented toward `0` and `1`. 
   - *Fix:* Phase 1 should force-map all binary targets to `0` and `1`.

2. **The Multiclass Problem (`car`, `cmc`):** Baseline models (especially CatBoost) return different output shapes for multiclass predictions compared to binary. Our Phase 2 `artifacts.py` script was optimized for 1D arrays, causing a crash when encountering 2D multiclass outputs.
   - *Fix:* Update `artifacts.py` to be aware of task dimensionality.

3. **Data Preservation:** As per the instructions, we have successfully preserved all predictions for the 3 successful runs. This allowed us to generate the **Grid ROC** and **Mean Envelope** without rerunning the models.
