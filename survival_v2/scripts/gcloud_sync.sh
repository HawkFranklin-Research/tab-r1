#!/usr/bin/env bash
# Pull survival_v2 predictions/runs from the shard VMs into survival_v2/outputs, then (optionally) delete the VMs.
# Prediction files are per unit, so shards never collide; merging is a plain copy.
#
# Usage: survival_v2/scripts/gcloud_sync.sh N_SHARDS [PROJECT] [ZONE] [DELETE=false]
# Afterwards, locally:  python3 survival_v2/run_pipeline.py --stages metrics,analyze,figures
set -euo pipefail
N_SHARDS="${1:?number of shards}"
PROJECT="${2:-pelliscope-scout}"
ZONE="${3:-us-central1-a}"
DELETE="${4:-false}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${ROOT}/survival_v2/outputs"

for ((i = 0; i < N_SHARDS; i++)); do
  VM="sv2-worker-${i}"
  if gcloud compute ssh "${VM}" --zone="${ZONE}" --project="${PROJECT}" --command "test -f ~/sv2_done" 2>/dev/null; then
    echo "${VM}: finished"
  else
    echo "${VM}: still running (partial results will be copied; rerun this script later)"
  fi
  gcloud compute ssh "${VM}" --zone="${ZONE}" --project="${PROJECT}" --command \
      "cd tab-r1/survival_v2/outputs && tar -czf ~/sv2_results_${i}.tar.gz predictions runs external logs 2>/dev/null || true"
  gcloud compute scp "${VM}:~/sv2_results_${i}.tar.gz" "/tmp/" --zone="${ZONE}" --project="${PROJECT}"
  tar -xzf "/tmp/sv2_results_${i}.tar.gz" -C "${OUT}"
  if [[ "${DELETE}" == "true" ]]; then
    gcloud compute instances delete "${VM}" --zone="${ZONE}" --project="${PROJECT}" --quiet
  fi
done
echo "merged into ${OUT}; next: python3 survival_v2/run_pipeline.py --stages metrics,analyze,figures"
