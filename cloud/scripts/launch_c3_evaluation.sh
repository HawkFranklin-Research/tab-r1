#!/usr/bin/env bash
# TAB-R1: C3-HighCPU-44 Automated Cloud Evaluation Setup
#
# Specs:
#   Machine: c3-highcpu-44 (44 vCPUs, 88 GB RAM)
#   Zone: us-central1-a (Lowest pricing tier)
#   Project: pelliscope-scout
#   Pricing: ~$0.43/hr (Spot) | ~$1.73/hr (On-Demand)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ID="${1:-pelliscope-scout}"
ZONE="${2:-us-central1-a}"
MACHINE_TYPE="${3:-c3-highcpu-22}"
PROVISIONING_MODEL="${4:-SPOT}" # SPOT or STANDARD
VM_NAME="tabr1-c3-eval-worker"

HF_TOKEN_FILE="/home/prime/Documents/hugging-face-read-token.txt"
if [[ -f "${HF_TOKEN_FILE}" ]]; then
    HF_TOKEN="$(cat "${HF_TOKEN_FILE}" | tr -d '[:space:]')"
else
    HF_TOKEN="${HF_TOKEN:-}"
fi

if [[ -z "${HF_TOKEN}" ]]; then
    echo "ERROR: Could not find Hugging Face token at ${HF_TOKEN_FILE} or in environment."
    exit 1
fi

echo "======================================================================"
echo "TAB-R1: C3 HIGH-CORE VM PROVISIONING"
echo "Project:            ${PROJECT_ID}"
echo "Zone:               ${ZONE} (Cheapest US Region)"
echo "Machine Type:       ${MACHINE_TYPE} (22 vCPUs / 44 GB RAM)"
echo "Provisioning Model: ${PROVISIONING_MODEL}"
echo "VM Name:            ${VM_NAME}"
echo "======================================================================"

# Create startup script for automated execution
STARTUP_SCRIPT=$(mktemp)
cat << 'EOF' > "${STARTUP_SCRIPT}"
#!/usr/bin/env bash
set -euo pipefail
exec > /var/log/tabr1_c3_startup.log 2>&1

echo "=== [1/5] System packages & dependencies ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y git curl python3-pip python3-venv tmux zstd htop libgomp1

echo "=== [2/5] Setting up workspace ==="
mkdir -p /opt/workspace
cd /opt/workspace
git clone https://github.com/HawkFranklin-Research/tab-r1.git
cd tab-r1

echo "=== [3/5] Setting up Python virtual environment ==="
python3 -m venv /opt/tabr1-env
source /opt/tabr1-env/bin/activate
pip install --upgrade pip setuptools wheel
pip install -q "tabpfn>=8.0.0" "autogluon.tabular>=1.1.0" huggingface_hub pandas scikit-learn lightgbm xgboost catboost pyarrow

# Install package & tabfm
pip install ./package
pip install './tabfm[pytorch]'

echo "=== [4/5] Running High-Core Evaluation across all 400 Frozen Folds ==="
export HF_TOKEN="__HF_TOKEN_PLACEHOLDER__"
export TABR1_MODELS="tabpfn_v2,tabpfn_v2_5,tabpfn_v2_6,tabpfn_v3,tabfm_default,autogluon"

python paper/analysis/run_cloud_evaluation.py \
  --models "${TABR1_MODELS}" \
  --device cpu \
  --threads 20 \
  --memory-gb 40 \
  --autogluon-time-limit 180 \
  --output-root /opt/tabr1_results \
  --export-zip /opt/tabr1_results_completed.zip \
  --resume

echo "=== [5/5] Full Evaluation Successfully Complete! ==="
touch /opt/tabr1_complete.flag
EOF

sed -i "s|__HF_TOKEN_PLACEHOLDER__|${HF_TOKEN}|g" "${STARTUP_SCRIPT}"

# Build provisioning args
EXTRA_FLAGS="--no-address"
if [[ "${PROVISIONING_MODEL}" == "SPOT" ]]; then
    EXTRA_FLAGS="${EXTRA_FLAGS} --provisioning-model=SPOT --instance-termination-action=STOP"
fi

echo "Creating VM instance in ${ZONE}..."
gcloud compute instances create "${VM_NAME}" \
    --project="${PROJECT_ID}" \
    --zone="${ZONE}" \
    --machine-type="${MACHINE_TYPE}" \
    --image-family="ubuntu-2204-lts" \
    --image-project="ubuntu-os-cloud" \
    --boot-disk-size="100GB" \
    --boot-disk-type="pd-balanced" \
    --scopes="https://www.googleapis.com/auth/cloud-platform" \
    --metadata-from-file="startup-script=${STARTUP_SCRIPT}" \
    ${EXTRA_FLAGS}

rm -f "${STARTUP_SCRIPT}"

echo ""
echo "======================================================================"
echo "VM ${VM_NAME} is CREATED and STARTING EXECUTION!"
echo ""
echo "Live Monitoring Command:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${ZONE} --project=${PROJECT_ID} --tunnel-through-iap --command='tail -f /var/log/tabr1_c3_startup.log'"
echo ""
echo "Automated Downloader Command:"
echo "  ./cloud/scripts/sync_results_from_vm.sh ${PROJECT_ID} ${ZONE}"
echo "======================================================================"

