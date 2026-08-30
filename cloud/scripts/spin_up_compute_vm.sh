#!/usr/bin/env bash
# TAB-R1: High-Core CPU VM Provisioning & Auto-Execution Script on Google Cloud
# 
# Usage:
#   ./cloud/scripts/spin_up_compute_vm.sh [PROJECT_ID] [ZONE] [MACHINE_TYPE]
#
# Defaults:
#   PROJECT_ID: pelliscope-scout (or current gcloud config)
#   ZONE: europe-west4-a (or us-central1-a)
#   MACHINE_TYPE: c2-standard-30 (30 vCPUs, 120 GB RAM, High-Frequency CPU)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null || echo "pelliscope-scout")}"
ZONE="${2:-europe-west4-a}"
MACHINE_TYPE="${3:-c2-standard-30}"
VM_NAME="tabr1-cpu-evaluator"

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
echo "TAB-R1: GOOGLE COMPUTE ENGINE PROVISIONING"
echo "Project:      ${PROJECT_ID}"
echo "Zone:         ${ZONE}"
echo "Machine Type: ${MACHINE_TYPE} (High-Core CPU)"
echo "VM Name:      ${VM_NAME}"
echo "======================================================================"

# Create startup script for automated execution
STARTUP_SCRIPT=$(mktemp)
cat << 'EOF' > "${STARTUP_SCRIPT}"
#!/usr/bin/env bash
set -euo pipefail
exec > /var/log/tabr1_startup.log 2>&1

echo "--- [1/5] Updating system packages ---"
apt-get update && apt-get install -y git curl python3-pip python3-venv tmux zstd htop

echo "--- [2/5] Setting up workspace ---"
mkdir -p /opt/workspace
cd /opt/workspace
git clone https://github.com/HawkFranklin-Research/tab-r1.git
cd tab-r1

echo "--- [3/5] Setting up Python virtualenv ---"
python3 -m venv /opt/tabr1-env
source /opt/tabr1-env/bin/activate
pip install --upgrade pip
pip install -q "tabpfn>=8.0.0" "autogluon.tabular>=1.1.0" huggingface_hub pandas scikit-learn lightgbm xgboost catboost pyarrow

# Install local package & tabfm
pip install ./package
pip install './tabfm[pytorch]'

echo "--- [4/5] Running Model Evaluation on 400 Frozen Folds ---"
export HF_TOKEN="__HF_TOKEN_PLACEHOLDER__"
export TABR1_MODELS="tabpfn_v2,tabpfn_v2_5,tabpfn_v2_6,tabpfn_v3,tabfm_default,autogluon"

python paper/analysis/run_cloud_evaluation.py \
  --models "${TABR1_MODELS}" \
  --device cpu \
  --threads 28 \
  --memory-gb 100 \
  --autogluon-time-limit 180 \
  --output-root /opt/tabr1_results \
  --export-zip /opt/tabr1_results_completed.zip \
  --resume

echo "--- [5/5] Evaluation Complete! ---"
# Write completion flag
touch /opt/tabr1_complete.flag
EOF

# Inject HF token securely into the temp startup script
sed -i "s|__HF_TOKEN_PLACEHOLDER__|${HF_TOKEN}|g" "${STARTUP_SCRIPT}"

echo "Deploying Compute Engine VM: ${VM_NAME}..."
gcloud compute instances create "${VM_NAME}" \
    --project="${PROJECT_ID}" \
    --zone="${ZONE}" \
    --machine-type="${MACHINE_TYPE}" \
    --image-family="ubuntu-2204-lts" \
    --image-project="ubuntu-os-cloud" \
    --boot-disk-size="100GB" \
    --boot-disk-type="pd-balanced" \
    --scopes="https://www.googleapis.com/auth/cloud-platform" \
    --metadata-from-file="startup-script=${STARTUP_SCRIPT}"

rm -f "${STARTUP_SCRIPT}"

echo ""
echo "======================================================================"
echo "VM deployed successfully!"
echo "To monitor live logs, run:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${ZONE} --project=${PROJECT_ID} --command='tail -f /var/log/tabr1_startup.log'"
echo ""
echo "To copy results back when finished:"
echo "  gcloud compute scp ${VM_NAME}:/opt/tabr1_results_completed.zip ./ --zone=${ZONE} --project=${PROJECT_ID}"
echo "======================================================================"
