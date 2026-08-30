#!/usr/bin/env python3
"""
Cloud & Distributed Evaluation Runner for Tabular Foundation Models.

Designed for Google Cloud Platform (Compute Engine / Spot VMs) and Google Colab.
Features:
- Automatic Hugging Face dataset download / unpacking
- Resume capability to recover from Spot preemption or Colab timeouts
- Batch slicing (--start-fold, --end-fold, --max-folds)
- Automatic aggregation of fold predictions and metrics
- Resource limits compliance (Max 12 threads, 12 GB RAM by default)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tarfile
import time
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd

# Add local package and analysis to path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parents[1]
PACKAGE_SRC = ROOT_DIR / "package" / "src"

for path in (SCRIPT_DIR, PACKAGE_SRC, ROOT_DIR / "tabfm"):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

from resource_limits import configure_process_limits
from run_leakage_safe_fold_models import AVAILABLE_MODELS, FOUNDATION_MODELS, execute_model, parse_list


def download_hf_dataset(repo_id: str, local_dir: Path, token: str | None = None) -> Path:
    """Download and extract packaged folds from Hugging Face Hub."""
    from huggingface_hub import snapshot_download

    print(f"Downloading dataset snapshot from Hugging Face: {repo_id}...")
    snapshot_path = snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=str(local_dir),
        token=token or os.environ.get("HF_TOKEN"),
    )
    snapshot_dir = Path(snapshot_path)

    # Check if archive exists and needs extraction
    for archive in snapshot_dir.glob("*.tar.gz"):
        print(f"Extracting archive: {archive.name}...")
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(path=local_dir)
    for archive in snapshot_dir.glob("*.zip"):
        print(f"Extracting zip archive: {archive.name}...")
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(path=local_dir)

    manifest_candidates = list(local_dir.rglob("fold_manifest.csv"))
    if not manifest_candidates:
        raise FileNotFoundError(f"Could not find fold_manifest.csv in downloaded dataset at {local_dir}")
    print(f"Found fold manifest: {manifest_candidates[0]}")
    return manifest_candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Cloud runner for Tabular Foundation Models on frozen folds.")
    parser.add_argument("--fold-manifest", default=None, help="Path to local fold_manifest.csv")
    parser.add_argument("--hf-repo", default=None, help="Hugging Face Dataset repo ID (e.g. HawkFranklin-Research/cancer-folds-400)")
    parser.add_argument("--hf-token", default=None, help="HF Token for private repo (or set HF_TOKEN env var)")
    parser.add_argument("--output-root", default="./cloud_outputs", help="Directory where model predictions and metrics will be saved")
    parser.add_argument("--models", default="tabpfn_v3,tabfm_default", help="Comma-separated model names")
    parser.add_argument("--max-folds", type=int, default=None, help="Maximum number of folds to run")
    parser.add_argument("--start-fold", type=int, default=0, help="0-based start index in fold manifest")
    parser.add_argument("--end-fold", type=int, default=None, help="End index in fold manifest (exclusive)")
    parser.add_argument("--tabfm-backend", default="pytorch", choices=["pytorch", "jax"])
    parser.add_argument("--autogluon-time-limit", type=int, default=300)
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"], help="PyTorch/CUDA acceleration device (default: auto)")
    parser.add_argument("--threads", type=int, default=12)
    parser.add_argument("--memory-gb", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", action="store_true", default=True, help="Skip already completed fold runs (default: True)")
    parser.add_argument("--no-resume", action="store_false", dest="resume", help="Disable skipping existing runs")
    parser.add_argument("--smoke", action="store_true", help="Run 1 fold smoke test")
    parser.add_argument("--export-zip", default=None, help="Optional path to zip outputs after completion")

    args = parser.parse_args()
    configure_process_limits(threads=args.threads, memory_gb=args.memory_gb)

    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    # Resolve manifest path
    manifest_path: Path
    if args.fold_manifest:
        manifest_path = Path(args.fold_manifest).expanduser().resolve()
    elif args.hf_repo:
        hf_dir = output_root / "hf_dataset"
        manifest_path = download_hf_dataset(args.hf_repo, hf_dir, token=args.hf_token)
    else:
        # Check canonical local generated_folds
        canonical_manifest = SCRIPT_DIR / "generated_folds" / "fold_manifest.csv"
        if canonical_manifest.exists():
            manifest_path = canonical_manifest
        else:
            parser.error("Must provide either --fold-manifest, --hf-repo, or run from a workspace with generated_folds.")

    manifest = pd.read_csv(manifest_path)
    models = parse_list(args.models)
    unknown = sorted(set(models) - set(AVAILABLE_MODELS))
    if unknown:
        parser.error(f"Unknown models: {', '.join(unknown)}. Available: {', '.join(AVAILABLE_MODELS)}")

    if args.smoke:
        args.max_folds = 1
        if not args.models or args.models == ",".join(AVAILABLE_MODELS):
            models = ["tabpfn_v3"]

    start_idx = args.start_fold
    end_idx = args.end_fold if args.end_fold is not None else len(manifest)
    manifest_slice = manifest.iloc[start_idx:end_idx]
    if args.max_folds is not None:
        manifest_slice = manifest_slice.head(args.max_folds)

    total_runs = len(manifest_slice) * len(models)
    print(f"\n{'='*70}")
    print(f"TAB-R1 CLOUD EVALUATION RUNNER")
    print(f"Folds to process: {len(manifest_slice)} (Indices {start_idx} to {start_idx + len(manifest_slice)})")
    print(f"Models to evaluate: {', '.join(models)}")
    print(f"Total planned runs: {total_runs}")
    print(f"Output directory: {output_root}")
    print(f"Resume existing: {args.resume}")
    print(f"Device: {args.device} | Threads: {args.threads} | Memory Limit: {args.memory_gb} GB")
    print(f"{'='*70}\n")

    rows: list[dict[str, Any]] = []
    run_idx = 0
    start_time = time.time()

    for _, fold in manifest_slice.iterrows():
        fold_desc = f"{fold['scope']}/{fold['endpoint']}/{fold['cancer']}/rep{int(fold['repeat'])}_fold{int(fold['fold'])}"
        for model_name in models:
            run_idx += 1
            run_dir = (
                output_root
                / str(fold["scope"])
                / str(fold["endpoint"])
                / str(fold["cancer"])
                / f"repeat_{int(fold['repeat']):02d}_fold_{int(fold['fold']):02d}"
                / model_name
            )
            result_file = run_dir / "result.json"

            if args.resume and result_file.exists():
                try:
                    cached = json.loads(result_file.read_text())
                    if cached.get("status") == "success":
                        print(f"[{run_idx}/{total_runs}] [CACHED] {fold_desc} -> {model_name} (AUC: {cached.get('roc_auc', 0.0):.4f})")
                        rows.append(cached)
                        continue
                except Exception:
                    pass

            print(f"[{run_idx}/{total_runs}] [RUNNING] {fold_desc} -> {model_name}...")
            res = execute_model(
                fold,
                model_name,
                output_root=output_root,
                seed=args.seed,
                threads=args.threads,
                tabfm_backend=args.tabfm_backend,
                autogluon_time_limit=args.autogluon_time_limit,
                device=args.device,
            )
            status_str = res.get("status", "unknown")
            if status_str == "success":
                print(f"[{run_idx}/{total_runs}] [SUCCESS] {fold_desc} -> {model_name} (AUC: {res.get('roc_auc', 0.0):.4f}, F1: {res.get('f1', 0.0):.4f}, Time: {res.get('fit_time_s', 0.0):.1f}s)")
            else:
                print(f"[{run_idx}/{total_runs}] [FAILED]  {fold_desc} -> {model_name} (Error: {res.get('error_type')}: {res.get('error_message')})")
            rows.append(res)

    elapsed = time.time() - start_time
    print(f"\nExecution completed in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes).")

    results_df = pd.DataFrame(rows)
    metrics_path = output_root / "all_fold_model_metrics.csv"
    results_df.to_csv(metrics_path, index=False)
    print(f"Saved consolidated metrics to: {metrics_path}")

    # Summary table
    if not results_df.empty and "roc_auc" in results_df.columns:
        summary = (
            results_df[results_df["status"] == "success"]
            .groupby(["model_name", "endpoint"])[["roc_auc", "pr_auc", "f1", "balanced_accuracy", "log_loss"]]
            .mean()
            .reset_index()
        )
        print("\nSummary Results (Mean Across Executed Folds):")
        print(summary.to_string(index=False))

    if args.export_zip:
        zip_path = Path(args.export_zip).expanduser().resolve()
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"\nCompressing outputs to {zip_path}...")
        shutil.make_archive(str(zip_path).removesuffix(".zip"), "zip", output_root)
        print(f"Created export archive: {zip_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
