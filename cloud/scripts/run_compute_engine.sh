#!/usr/bin/env bash
set -euo pipefail

: "${HF_TOKEN:?Set HF_TOKEN in the VM environment}"

export TABR1_MAX_THREADS="${TABR1_MAX_THREADS:-16}"
export TABR1_MAX_MEMORY_GB="${TABR1_MAX_MEMORY_GB:-32}"

python paper/analysis/run_cloud_evaluation.py \
  --models "${TABR1_MODELS:-tabpfn_v2,tabpfn_v2_5,tabpfn_v2_6,tabpfn_v3,tabfm_default}" \
  --dataset-dir "${TABR1_DATASET_DIR:-/tmp/tabr1_hf_dataset}" \
  --output-root "${TABR1_OUTPUT_DIR:-/tmp/tabr1_outputs}" \
  --threads "${TABR1_THREADS:-8}" \
  --memory-gb "${TABR1_MEMORY_GB:-24}" \
  --device "${TABR1_DEVICE:-cuda}" \
  --confirm-full-run \
  --hf-results-repo "${HF_RESULTS_REPO:-HawkFranklin-Research/TABR1-Cancer-OS-Cloud-Results}"
