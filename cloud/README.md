# TABR1 cloud execution

The pinned private input dataset is `HawkFranklin-Research/TABR1-Cancer-OS-LeakageSafe-Folds` at revision `0b26eb0bf0eae7558a6a659aea7829209b31854e`.

`HF_TOKEN` is required. On Cloud Run, inject it from Secret Manager. On Compute Engine, export it in the shell. Never place the token in an image, script argument, or Git repository.

## Validate the private dataset download

```bash
export HF_TOKEN=...
cloud/scripts/verify_hf_download.sh
```

## Compute Engine

```bash
export HF_TOKEN=...
export TABR1_MODELS=tabpfn_v3
cloud/scripts/run_compute_engine.sh
```

## Cloud Run Job

```bash
export PROJECT_ID=...
export REGION=...
export HF_SECRET=hf-token
export TABR1_MODELS=tabpfn_v3
cloud/scripts/deploy_cloud_run_job.sh
gcloud run jobs execute tabr1-foundation --region "$REGION" --project "$PROJECT_ID" --wait
```

Deploy separate jobs for AutoGluon and each foundation-model family to keep dependencies, cost, and resumability auditable. Completed metrics and predictions are uploaded to the private `HF_RESULTS_REPO`; AutoGluon model directories and downloaded fold caches are excluded.
