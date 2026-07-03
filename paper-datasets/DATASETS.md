# TabPFN Paper Datasets

This file lists the datasets used in the January 2025 TabPFN paper and labels them by task type.

Notes:

- Classification tasks are split into `binary` and `multiclass` based on the paper/OpenML benchmark metadata.
- All regression tasks in the paper benchmark are `single-target regression`.
- A few dataset names were normalized from OCR artifacts in the paper PDF. Those are noted inline.

## Classification Datasets

Paper benchmark: AutoML Benchmark.

| Dataset | Type | Classes | Notes |
|---|---|---:|---|
| ada | binary classification | 2 |  |
| australian | binary classification | 2 |  |
| blood-transfusion-service-center | binary classification | 2 |  |
| car | binary classification | 2 |  |
| churn | binary classification | 2 |  |
| cmc | multiclass classification | 3 |  |
| credit-g | binary classification | 2 |  |
| dna | multiclass classification | 3 |  |
| eucalyptus | multiclass classification | 5 |  |
| first-order-theorem-proving | multiclass classification | 6 |  |
| GesturePhaseSegmentationProcessed | multiclass classification | 5 | Paper OCR: `GesturePhase Segmentation Processed` |
| jasmine | binary classification | 2 |  |
| kc1 | binary classification | 2 | Paper OCR showed `kcl` |
| kr-vs-kp | binary classification | 2 |  |
| madeline | binary classification | 2 |  |
| mfeat-factors | multiclass classification | 10 |  |
| ozone-level-8hr | binary classification | 2 |  |
| philippine | binary classification | 2 |  |
| phoneme | binary classification | 2 |  |
| qsar-biodeg | binary classification | 2 |  |
| satellite | binary classification | 2 |  |
| segment | multiclass classification | 7 |  |
| sylvine | binary classification | 2 |  |
| steel-plates-fault | binary classification | 2 |  |
| vehicle | multiclass classification | 4 |  |
| wilt | binary classification | 2 |  |
| yeast | multiclass classification | 10 |  |
| wine-quality-white | multiclass classification | 7 |  |
| pc4 | binary classification | 2 |  |

Classification summary:

- Total datasets: 29
- Binary classification: 19
- Multiclass classification: 10

## Regression Datasets

Paper benchmark: AMLB + OpenML-CTR23.

| Dataset | Type | Notes |
|---|---|---|
| abalone | single-target regression |  |
| airfoil_self_noise | single-target regression |  |
| auction_verification | single-target regression |  |
| boston | single-target regression |  |
| cars | single-target regression |  |
| colleges | single-target regression |  |
| cpu_activity | single-target regression |  |
| concrete_compressive_strength | single-target regression | Paper OCR: `concrete compressive` |
| energy_efficiency | single-target regression |  |
| geographical_origin_of_music | single-target regression | Paper OCR split across two lines |
| grid_stability | single-target regression |  |
| kin8nm | single-target regression |  |
| house_prices_nominal | single-target regression |  |
| Mercedes_Benz_Greener_Manufacturing | single-target regression | Paper OCR split across multiple lines |
| Moneyball | single-target regression |  |
| MIP-2016-regression | single-target regression |  |
| pumadyn32nh | single-target regression | Paper OCR: `pumadyn3znh` |
| QSAR_fish_toxicity | single-target regression |  |
| quake | single-target regression |  |
| SAT11-HAND-runtime | single-target regression | Paper OCR fragment was truncated; verify exact OpenML spelling if needed |
| sensory | single-target regression |  |
| socmob | single-target regression |  |
| space_ga | single-target regression |  |
| student_performance | single-target regression |  |
| tecator | single-target regression |  |
| topo_2_1 | single-target regression |  |
| us_crime | single-target regression |  |
| yprop_4_1 | single-target regression |  |

Regression summary:

- Total datasets: 28
- Task type: single-target regression for all rows

