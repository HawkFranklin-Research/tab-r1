from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Load one TABR1 fold bundle.")
    parser.add_argument("--dataset-root", type=Path, default=Path("."))
    parser.add_argument("--scope", required=True, choices=["per_cancer", "pooled"])
    parser.add_argument("--endpoint", required=True, choices=["os_3yr", "os_5yr", "extreme_os"])
    parser.add_argument("--cancer", required=True)
    parser.add_argument("--repeat", required=True, type=int)
    parser.add_argument("--fold", required=True, type=int)
    args = parser.parse_args()

    bundle = (
        args.dataset_root
        / "folds"
        / args.scope
        / args.endpoint
        / args.cancer
        / f"repeat_{args.repeat:02d}"
        / f"fold_{args.fold:02d}.tar.zst"
    )
    if not bundle.exists():
        raise FileNotFoundError(bundle)

    with tempfile.TemporaryDirectory(prefix="tabr1-fold-") as temporary:
        subprocess.run(["tar", "--zstd", "-xf", str(bundle), "-C", temporary], check=True)
        root = Path(temporary)
        train = pd.read_parquet(root / "train.parquet")
        validation = pd.read_parquet(root / "validation.parquet")
        test = pd.read_parquet(root / "test.parquet")
        print({"train": train.shape, "validation": validation.shape, "test": test.shape})


if __name__ == "__main__":
    main()
