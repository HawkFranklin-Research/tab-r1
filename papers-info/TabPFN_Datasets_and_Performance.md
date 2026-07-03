# TabPFN Datasets and Aggregate Performance

Source paper:

- `tabpfn-published-Jan25.pdf`

Paper context:

- Extended Data Table 3 lists the classification benchmark datasets.
- Extended Data Table 4 lists the regression benchmark datasets.
- Extended Data Tables 1 and 2 report benchmark-wide aggregate performance, not per-dataset scores.

## Classification Benchmark

TabPFN was evaluated on 29 classification datasets from the AutoML Benchmark.

| # | Dataset |
|---:|---|
| 1 | ada |
| 2 | australian |
| 3 | blood-transfusion-service-center |
| 4 | car |
| 5 | churn |
| 6 | cmc |
| 7 | credit-g |
| 8 | dna |
| 9 | eucalyptus |
| 10 | first-order-theorem-proving |
| 11 | GesturePhase Segmentation Processed |
| 12 | jasmine |
| 13 | kcl |
| 14 | kr-vs-kp |
| 15 | madeline |
| 16 | mfeat-factors |
| 17 | ozone-level-8hr |
| 18 | philippine |
| 19 | phoneme |
| 20 | qsar-biodeg |
| 21 | satellite |
| 22 | segment |
| 23 | sylvine |
| 24 | steel-plates-fault |
| 25 | vehicle |
| 26 | wilt |
| 27 | yeast |
| 28 | wine-quality-white |
| 29 | pc4 |

## Regression Benchmark

TabPFN was evaluated on 28 regression datasets from AMLB and OpenML-CTR23.

| # | Dataset |
|---:|---|
| 1 | abalone |
| 2 | airfoil_self_noise |
| 3 | auction_verification |
| 4 | boston |
| 5 | cars |
| 6 | colleges |
| 7 | cpu_activity |
| 8 | concrete_compressive_strength |
| 9 | energy_efficiency |
| 10 | geographical_origin |
| 11 | grid_stability |
| 12 | kin8nm |
| 13 | house_prices_nominal |
| 14 | Mercedes_Benz |
| 15 | Moneyball |
| 16 | MIP-2016-regression |
| 17 | pumadyn32nh |
| 18 | QSAR_fish_toxicity |
| 19 | quake |
| 20 | SAT11-HAND-runtime |
| 21 | sensory |
| 22 | socmob |
| 23 | space_ga |
| 24 | student_performance |
| 25 | tecator |
| 26 | topo_2_1 |
| 27 | us_crime |
| 28 | yprop_4_1 |

## Aggregate Performance

The paper reports normalized benchmark-wide scores, with 1.0 as the best method on a dataset and 0.0 as the worst, then averaged across datasets.

### Classification Summary

| Model | Norm ROC | Norm Acc | Norm F1 | Norm CE | Norm ECE | Mean Time (s) |
|---|---:|---:|---:|---:|---:|---:|
| TabPFN (PHE, 4h tuned) | 0.971 +/- 0.01 | 0.916 +/- 0.01 | 0.934 +/- 0.01 | 0.011 +/- 0.00 | 0.110 +/- 0.01 | 13754.896 +/- 126.74 |
| TabPFN (4h tuned) | 0.952 +/- 0.01 | 0.932 +/- 0.01 | 0.950 +/- 0.01 | 0.022 +/- 0.00 | 0.097 +/- 0.01 | 14428.307 +/- 4.98 |
| TabPFN (default) | 0.939 +/- 0.01 | 0.873 +/- 0.01 | 0.893 +/- 0.01 | 0.047 +/- 0.01 | 0.129 +/- 0.02 | 2.793 +/- 0.49 |
| AutoGluon (V1, BQ, 4h tuned) | 0.914 +/- 0.01 | 0.857 +/- 0.02 | 0.892 +/- 0.01 | 0.052 +/- 0.01 | 0.124 +/- 0.01 | 9660.060 +/- 514.65 |

### Regression Summary

| Model | Norm RMSE | Norm Spearman | Norm R2 | Norm MAE | Mean Time (s) |
|---|---:|---:|---:|---:|---:|
| TabPFN (PHE, 4h tuned) | 0.022 +/- 0.00 | 0.940 +/- 0.02 | 0.983 +/- 0.00 | 0.040 +/- 0.01 | 13556.550 +/- 147.29 |
| TabPFN (4h tuned) | 0.032 +/- 0.00 | 0.931 +/- 0.02 | 0.974 +/- 0.00 | 0.049 +/- 0.01 | 14438.452 +/- 8.79 |
| TabPFN (default) | 0.077 +/- 0.01 | 0.942 +/- 0.01 | 0.939 +/- 0.01 | 0.080 +/- 0.02 | 4.745 +/- 1.03 |
| AutoGluon (V1, BQ, 4h tuned) | 0.045 +/- 0.01 | 0.951 +/- 0.01 | 0.963 +/- 0.01 | 0.057 +/- 0.01 | 10199.980 +/- 446.07 |

## Important Note

The paper’s main tables are benchmark-wide summaries.
If you need per-dataset metric rows for every method, that is a separate extraction task from the underlying benchmark figures or the paper’s released result files.

