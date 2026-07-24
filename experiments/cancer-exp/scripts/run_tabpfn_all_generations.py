from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_PACKAGE_SRC = Path("/home/prime/Documents/g3/tab-r1/package/src")
DEFAULT_DATASETS_DIR = Path("/home/prime/Documents/g3/cancer-exp/datasets_top100")
DEFAULT_OUTPUT_ROOT = Path("/home/prime/Documents/g3/cancer-exp/outputs/tabpfn_all_generations_top100")
DEFAULT_LOG_DIR = Path("/home/prime/Documents/g3/cancer-exp/logs")
DEFAULT_LEGACY_V1_ROOT = Path("/tmp/TabPFN_v1")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all TabPFN generations on exported cancer CSVs.")
    parser.add_argument("--datasets-dir", default=str(DEFAULT_DATASETS_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--package-src", default=str(DEFAULT_PACKAGE_SRC))
    parser.add_argument("--legacy-v1-root", default=str(DEFAULT_LEGACY_V1_ROOT))
    parser.add_argument("--train-rows-cap", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    datasets_dir = Path(args.datasets_dir).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    package_src = Path(args.package_src).expanduser().resolve()
    legacy_v1_root = Path(args.legacy_v1_root).expanduser().resolve()
    log_dir = DEFAULT_LOG_DIR
    output_root.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    dataset_paths = sorted(
        str(path)
        for path in datasets_dir.glob("*.csv")
        if not path.name.startswith("manifest")
    )
    if not dataset_paths:
        raise FileNotFoundError(f"No exported CSV datasets found in {datasets_dir}")
    if not legacy_v1_root.exists():
        raise FileNotFoundError(f"Legacy TabPFN v1 root does not exist: {legacy_v1_root}")

    command = [
        sys.executable,
        "-m",
        "ev_tabpfn.cli",
        "compare-generations",
        "--datasets",
        *dataset_paths,
        "--target",
        "target",
        "--versions",
        "v1",
        "v2",
        "v2_5",
        "v2_6",
        "v3",
        "--output",
        str(output_root),
        "--seed",
        str(args.seed),
        "--train-rows-cap",
        str(args.train_rows_cap),
        "--legacy-v1-root",
        str(legacy_v1_root),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(package_src) + os.pathsep + env.get("PYTHONPATH", "")

    (log_dir / "tabpfn_all_generations_command.json").write_text(
        json.dumps(
            {
                "command": command,
                "dataset_count": len(dataset_paths),
                "output_root": str(output_root),
                "package_src": str(package_src),
                "legacy_v1_root": str(legacy_v1_root),
                "train_rows_cap": args.train_rows_cap,
                "seed": args.seed,
            },
            indent=2,
        )
    )
    with (log_dir / "tabpfn_all_generations_stdout.log").open("w") as stdout, (
        log_dir / "tabpfn_all_generations_stderr.log"
    ).open("w") as stderr:
        process = subprocess.run(command, env=env, cwd=str(output_root), stdout=stdout, stderr=stderr, check=False)
    print(json.dumps({"returncode": process.returncode, "output_root": str(output_root)}, indent=2))
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
