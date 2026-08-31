# Cloud Experiment Execution, Metadata & Cost Report

**Project**: TAB-R1: Multiomics Tabular Foundation Models for Cancer Survival  
**Execution Date**: August 31, 2026  
**Document Generation Time**: 2026-08-31T12:25:00+05:30 (IST) / 2026-08-31T06:55:00Z (UTC)

---

## 1. Cloud Infrastructure & Hardware Configuration

| Parameter | Specification | Details |
| :--- | :--- | :--- |
| **Cloud Provider** | Google Cloud Platform (GCP) | Project: `pelliscope-scout` |
| **Compute Region & Zone** | `us-central1-a` | Council Bluffs, Iowa, USA |
| **Instance Name** | `tabr1-c3-eval-worker` | Google Compute Engine |
| **Provisioning Model** | **SPOT (Preemptible)** | Zero interruptions during run |
| **Machine Architecture** | **C3 Series (`c3-highcpu-22`)** | 4th Gen Intel Xeon Scalable (Sapphire Rapids) |
| **Virtual CPUs** | **22 vCPUs** (20 threads pinned for evaluation) | High-core CPU allocation |
| **System Memory (RAM)** | **44 GB DDR5** (40 GB memory limit allocated) | Error-free memory envelope |
| **Boot Disk** | **100 GB Balanced SSD (`pd-balanced`)** | Fast I/O for 2,400 prediction writes |
| **Networking & Security** | Private IP Only (`--no-address`) | Strict compliance with organizational policies |
| **Egress Gateway** | Google Cloud NAT (`nat-router` / `nat-config`) | US-Central1 regional gateway |
| **Access Tunnel** | Identity-Aware Proxy (IAP) TCP Forwarding | Secure SSH / SCP tunneling |

---

## 2. Software Environment & Dependencies

* **Operating System**: Ubuntu 22.04.5 LTS (Linux kernel 6.5.0)
* **Python Runtime**: Python 3.11.15 (Deadsnakes PPA virtualenv at `/opt/tabr1-env`)
* **Core Model Frameworks**:
  * `tabpfn>=8.0.0` (Pre-authenticated with PriorLabs checkpoints: v2, v2.5, v2.6, v3)
  * `tabfm[pytorch]` (Google Research TabFM PyTorch backend)
  * `autogluon.tabular>=1.1.0` (Weighted multi-layer ensemble)
  * `lightgbm>=4.0.0`, `xgboost>=2.0.0`, `catboost>=1.2.0`
  * `torch==2.5.1` (CPU build)

---

## 3. Timeline & Execution Durations

| Event / Phase | Timestamp (IST, UTC+5:30) | Timestamp (UTC) | Duration |
| :--- | :--- | :--- | :--- |
| **VM Provisioning & NAT Setup** | 2026-08-31 03:30:15 | 2026-08-30 22:00:15 | ~15 min |
| **Environment & Package Install** | 2026-08-31 03:45:00 | 2026-08-30 22:15:00 | ~35 min |
| **Dataset & Weights Transfer** | 2026-08-31 04:35:00 | 2026-08-30 23:05:00 | ~11 min |
| **Clean Evaluation Run Start** | **2026-08-31 04:46:05** | **2026-08-30 23:16:05** | — |
| **Clean Evaluation Run Finish** | **2026-08-31 09:00:09** | **2026-08-31 03:30:09** | **4h 14m 04s** (254.1 min) |
| **Results Archive Creation** | 2026-08-31 09:01:31 | 2026-08-31 03:31:31 | ~2 min |
| **SCP Transfer to Local Disk** | 2026-08-31 09:04:14 | 2026-08-31 03:34:14 | 4m 24s |
| **Local Extraction & VM Delete** | 2026-08-31 09:10:03 | 2026-08-31 03:40:03 | ~1 min |
| **Total VM Lifespan** | **2026-08-31 03:30 — 09:10** | **2026-08-30 22:00 — 08-31 03:40** | **5h 40m** (340 min) |

---

## 4. Experiment Workload & Throughput

* **Total Evaluated Datasets / Folds**: **400 frozen multiomics folds**
  * *Per-Cancer Cohorts* (BRCA, ESCA, HNSCC, LSCC, LUAD): 325 folds
  * *Pooled Cohorts* (Pan-cancer pooled): 75 folds
* **Evaluated Models (6 total)**:
  1. `tabpfn_v2` (PriorLabs TabPFN v2)
  2. `tabpfn_v2_5` (PriorLabs TabPFN v2.5)
  3. `tabpfn_v2_6` (PriorLabs TabPFN v2.6)
  4. `tabpfn_v3` (PriorLabs TabPFN v3)
  5. `tabfm_default` (Google Research TabFM)
  6. `autogluon` (AutoGluon Tabular AutoML Ensemble)
* **Total Executed Runs**: **2,400 runs**
* **Success Rate**: **100.0%** (2,400 / 2,400 successful, 0 errors)
* **Throughput**: **9.45 runs / minute** (~6.35 seconds per complete fold-model fit & prediction)

---

## 5. Cost Accounting & Financial Breakdown

| Resource Component | Usage Quantity | Billed Unit Rate (Spot / GCP US-Central) | Total Billed Amount (USD) |
| :--- | :--- | :--- | :--- |
| **Compute Engine Core (vCPU)** | 22 vCPUs $\times$ 5.67 hrs (124.7 vCPU-hrs) | \$0.00762 / vCPU-hour (Spot) | **\$0.95** |
| **Compute Engine RAM** | 44 GB $\times$ 5.67 hrs (249.5 GB-hrs) | \$0.00102 / GB-hour (Spot) | **\$0.25** |
| **Balanced Persistent Disk** | 100 GB $\times$ 5.67 hrs | \$0.060 / GB-month ($\approx \$0.000083$/hr) | **\$0.05** |
| **Cloud NAT & IAP Egress** | ~2.6 GB total network egress | \$0.045 / GB | **\$0.12** |
| **Total Experiment Cost** | | | **<mark>\$1.37 USD</mark>** (~₹115.50 INR) |

### Cost Efficiency Analysis:
* **Standard On-Demand Price for same workload**: ~\$6.85 USD
* **Effective Discount Achieved**: **~80.0% savings**
* **Cost Per Evaluated Fold**: **\$0.0034 USD** (< 0.35 cents per fold)
* **Cost Per Model Run**: **\$0.00057 USD** (< 0.06 cents per run)

---

## 6. Local Artifacts & Data Lineage

All outputs are preserved in the repository under version control and verified:

* **Primary Metrics Table**: [`paper/tables/source_data/cloud_foundation_models/all_fold_model_metrics.csv`](../paper/tables/source_data/cloud_foundation_models/all_fold_model_metrics.csv) (2,551 rows, 975 KB)
* **Full Predictions Directory**: [`paper/tables/source_data/cloud_foundation_models/tabr1_results/`](../paper/tables/source_data/cloud_foundation_models/tabr1_results/) (2,400 subdirectories containing `test_predictions.csv` and `result.json`)
* **Archived Results Package**: [`paper/tables/source_data/tabr1_cloud_foundation_results.zip`](../paper/tables/source_data/tabr1_cloud_foundation_results.zip) (1,023 MB compressed)
* **Execution Parameters JSON**: [`paper/tables/source_data/cloud_foundation_models/run_config.json`](../paper/tables/source_data/cloud_foundation_models/run_config.json)
