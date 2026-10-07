#!/usr/bin/env bash
# survival_v2 on Google Cloud: create one VM per shard, copy code + data, run the pipeline in tmux, results stay on the VM disk.
# Follows the conventions of cloud/scripts/launch_c3_evaluation.sh (project, zone, Spot), but the data are uploaded with
# `gcloud compute scp` instead of Hugging Face, and the fit stage is split across shards.
#
# Usage:
#   survival_v2/scripts/gcloud_launch.sh [N_SHARDS] [MACHINE] [ACCELERATOR] [PROJECT] [ZONE]
#   e.g. survival_v2/scripts/gcloud_launch.sh 4 g2-standard-8 nvidia-l4 pelliscope-scout us-central1-a     (GPU, recommended)
#        survival_v2/scripts/gcloud_launch.sh 4 c3-highcpu-22 none                                       (CPU only)
# Then:  survival_v2/scripts/gcloud_sync.sh N_SHARDS ...   to pull results back and merge them into survival_v2/outputs.
#
# Order of work: run `prepare,folds` ONCE locally first (folds must be identical on every shard; they are uploaded with the store).
set -euo pipefail

N_SHARDS="${1:-4}"
MACHINE="${2:-g2-standard-8}"
ACCEL="${3:-nvidia-l4}"
PROJECT="${4:-pelliscope-scout}"
ZONE="${5:-us-central1-a}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${ROOT}/survival_v2/outputs"

for f in store/store_report.json folds/manifest.json; do
  [[ -f "${OUT}/${f}" ]] || { echo "missing ${OUT}/${f}: run 'python3 survival_v2/run_pipeline.py --stages prepare,folds' locally first"; exit 1; }
done
echo "folds sha256: $(python3 -c "import json;print(json.load(open('${OUT}/folds/manifest.json'))['sha256'][:16])")"

BUNDLE="$(mktemp -d)/sv2_bundle.tar.gz"
tar -C "${ROOT}" -czf "${BUNDLE}" survival_v2/run_pipeline.py survival_v2/tte survival_v2/config survival_v2/requirements.txt \
    survival_v2/outputs/store survival_v2/outputs/folds package tabfm
tar -C "$(dirname "$(python3 -c "import yaml;print(yaml.safe_load(open('${ROOT}/survival_v2/config/default.yaml'))['paths']['metabric_root'])")")" \
    -czf "$(dirname "${BUNDLE}")/metabric.tar.gz" brca_metabric
echo "bundle: $(du -h "${BUNDLE}" | cut -f1)"

ACC_FLAGS=()
if [[ "${ACCEL}" != "none" ]]; then
  ACC_FLAGS=(--accelerator="type=${ACCEL},count=1" --maintenance-policy=TERMINATE)
fi

for ((i = 0; i < N_SHARDS; i++)); do
  VM="sv2-worker-${i}"
  echo "=== ${VM} (${MACHINE}, ${ACCEL}) ==="
  gcloud compute instances create "${VM}" --project="${PROJECT}" --zone="${ZONE}" --machine-type="${MACHINE}" \
      --image-family=common-cu124-ubuntu-2204-py310 --image-project=deeplearning-platform-release \
      --boot-disk-size=150GB --provisioning-model=SPOT --instance-termination-action=STOP \
      --metadata=install-nvidia-driver=True "${ACC_FLAGS[@]}"
done

echo "waiting for SSH..."
sleep 60
for ((i = 0; i < N_SHARDS; i++)); do
  VM="sv2-worker-${i}"
  gcloud compute scp "${BUNDLE}" "$(dirname "${BUNDLE}")/metabric.tar.gz" "${VM}:~/" --zone="${ZONE}" --project="${PROJECT}"
  DEVICE=$([[ "${ACCEL}" == "none" ]] && echo cpu || echo cuda)
  # shard 0 also runs the external stage; every shard writes its own predictions; metrics/analysis run locally after sync
  STAGES=$([[ ${i} -eq 0 ]] && echo "fit,external" || echo "fit")
  gcloud compute ssh "${VM}" --zone="${ZONE}" --project="${PROJECT}" --command "
    set -e
    mkdir -p tab-r1 data && tar -xzf sv2_bundle.tar.gz -C tab-r1 && tar -xzf metabric.tar.gz -C data
    python3 -m pip install -q -r tab-r1/survival_v2/requirements.txt && python3 -m pip install -q ./tab-r1/package './tab-r1/tabfm[pytorch]'
    cd tab-r1
    export TABR1_MAX_THREADS=\$(nproc) TABR1_MAX_MEMORY_GB=0
    tmux new-session -d -s sv2 \"python3 survival_v2/run_pipeline.py --stages ${STAGES} --shard ${i}/${N_SHARDS} --device ${DEVICE} \
        --threads \$(nproc) --memory-gb 0 --metabric-root \$HOME/data/brca_metabric --confirm-full-run 2>&1 | tee ~/sv2_shard${i}.log; touch ~/sv2_done\"
  "
  echo "${VM}: started shard ${i}/${N_SHARDS} (${STAGES})"
done
echo "monitor: gcloud compute ssh sv2-worker-0 --zone=${ZONE} --project=${PROJECT} --command='tail -f ~/sv2_shard0.log'"
