#!/usr/bin/env bash
set -euo pipefail

: "${HF_TOKEN:?Set HF_TOKEN or inject it from Secret Manager}"

python paper/analysis/run_cloud_evaluation.py \
  --download-only \
  --dataset-dir "${TABR1_DATASET_DIR:-/tmp/tabr1_hf_dataset}" \
  --output-root "${TABR1_OUTPUT_DIR:-/tmp/tabr1_outputs}" \
  --threads "${TABR1_THREADS:-8}" \
  --memory-gb "${TABR1_MEMORY_GB:-12}"
