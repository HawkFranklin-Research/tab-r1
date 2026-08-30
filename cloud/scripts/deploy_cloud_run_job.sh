#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:?Set REGION}"
: "${HF_SECRET:?Set HF_SECRET to the Secret Manager secret name}"

AR_REPOSITORY="${AR_REPOSITORY:-tabr1}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPOSITORY}/tabr1-cloud:latest"
JOB_NAME="${JOB_NAME:-tabr1-foundation}"
MODELS="${TABR1_MODELS:-tabpfn_v3}"
RESULTS_REPO="${HF_RESULTS_REPO:-HawkFranklin-Research/TABR1-Cancer-OS-Cloud-Results}"

gcloud builds submit --project "${PROJECT_ID}" --tag "${IMAGE}" .

gcloud run jobs deploy "${JOB_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --image "${IMAGE}" \
  --cpu 8 \
  --memory 32Gi \
  --gpu 1 \
  --tasks "${TABR1_TASKS:-16}" \
  --parallelism "${TABR1_PARALLELISM:-4}" \
  --task-timeout 24h \
  --max-retries 1 \
  --set-secrets "HF_TOKEN=${HF_SECRET}:latest" \
  --set-env-vars "TABR1_MODELS=${MODELS},HF_RESULTS_REPO=${RESULTS_REPO},TABR1_MAX_THREADS=8,TABR1_MAX_MEMORY_GB=32" \
  --args=--confirm-full-run,--device,cuda,--threads,8,--memory-gb,24
