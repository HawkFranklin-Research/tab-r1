#!/usr/bin/env bash
# TAB-R1: Automated Result Sync & VM Teardown Script
#
# Usage:
#   ./cloud/scripts/sync_results_from_vm.sh [PROJECT_ID] [ZONE] [AUTO_DELETE]

set -euo pipefail

PROJECT_ID="${1:-pelliscope-scout}"
ZONE="${2:-us-central1-a}"
VM_NAME="tabr1-c3-eval-worker"
AUTO_DELETE="${3:-false}" # Set to true to automatically delete the VM upon completion

TARGET_DIR="./paper/tables/source_data"
mkdir -p "${TARGET_DIR}"

echo "======================================================================"
echo "TAB-R1: MONITORING & RESULT SYNC"
echo "VM:         ${VM_NAME}"
echo "Zone:       ${ZONE}"
echo "Project:    ${PROJECT_ID}"
echo "Target Dir: ${TARGET_DIR}"
echo "======================================================================"

echo "Checking VM status and waiting for evaluation completion..."

NOT_FOUND_COUNT=0
while true; do
    # Check if instance is running
    STATUS=$(gcloud compute instances describe "${VM_NAME}" --zone="${ZONE}" --project="${PROJECT_ID}" --format="value(status)" 2>/dev/null || echo "NETWORK_ERROR")
    if [[ "${STATUS}" == "NETWORK_ERROR" ]]; then
        echo "[$(date +%T)] Network connection error checking VM. Retrying in 30s..."
        sleep 30
        continue
    elif [[ "${STATUS}" == "NOT_FOUND" || -z "${STATUS}" ]]; then
        NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
        if [[ ${NOT_FOUND_COUNT} -ge 5 ]]; then
            echo "VM ${VM_NAME} does not exist or has been deleted."
            exit 0
        fi
        sleep 30
        continue
    fi
    NOT_FOUND_COUNT=0

    # Check if completion flag exists on VM
    COMPLETE=$(gcloud compute ssh "${VM_NAME}" --zone="${ZONE}" --project="${PROJECT_ID}" --tunnel-through-iap --command="test -f /opt/tabr1_complete.flag && echo 'YES' || echo 'NO'" 2>/dev/null || echo "SSH_WAIT")

    if [[ "${COMPLETE}" == "YES" ]]; then
        echo ""
        echo "🎉 Evaluation is COMPLETE on VM!"
        echo "Downloading results package /opt/tabr1_results_completed.zip..."
        gcloud compute scp --tunnel-through-iap "${VM_NAME}:/opt/tabr1_results_completed.zip" "${TARGET_DIR}/tabr1_cloud_foundation_results.zip" --zone="${ZONE}" --project="${PROJECT_ID}"
        
        echo "Extracting results into ${TARGET_DIR}/cloud_foundation_models/..."
        mkdir -p "${TARGET_DIR}/cloud_foundation_models"
        unzip -q -o "${TARGET_DIR}/tabr1_cloud_foundation_results.zip" -d "${TARGET_DIR}/cloud_foundation_models"
        
        echo "Results successfully downloaded and extracted to: ${TARGET_DIR}/cloud_foundation_models"
        
        if [[ "${AUTO_DELETE}" == "true" ]]; then
            echo "Auto-deleting VM ${VM_NAME} to save credits..."
            gcloud compute instances delete "${VM_NAME}" --zone="${ZONE}" --project="${PROJECT_ID}" --quiet
            echo "VM deleted successfully."
        else
            echo ""
            echo "To delete the VM manually and stop billing, run:"
            echo "  gcloud compute instances delete ${VM_NAME} --zone=${ZONE} --project=${PROJECT_ID} --quiet"
        fi
        break
    else
        echo "[$(date +'%T')] Still running... (Status: ${STATUS}, Flag: ${COMPLETE}). Sleeping 30s..."
        sleep 30
    fi
done
