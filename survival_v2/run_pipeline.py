#!/usr/bin/env python3
"""survival_v2 master pipeline: one script, runnable whole or stage by stage, locally or on a cloud VM.

Stages (default: all, in this order)
    prepare   build the compact store from c-5 (coalesced source blocks, observed fractions, harmonised clinical)
    folds     build and freeze the 5 x 5 patient-grouped folds (+ SHA-256 manifest)
    fit       fit every model on every training set of the requested questions; saves per-patient predictions (resumable)
    external  Question 4: TCGA-BRCA <-> METABRIC
    metrics   recompute all metrics from the saved predictions
    analyze   question-level tables with paired contrasts and intervals
    figures   plots + source data

Examples
    python survival_v2/run_pipeline.py --dry-run                                   # print the plan, run nothing
    python survival_v2/run_pipeline.py --smoke --confirm-full-run                  # tiny end-to-end check (outputs_smoke/)
    python survival_v2/run_pipeline.py --stages prepare,folds                      # data only
    python survival_v2/run_pipeline.py --stages fit --questions q1 --shard 0/4 --confirm-full-run   # one of four workers
    python survival_v2/run_pipeline.py --stages metrics,analyze,figures            # rebuild results from saved predictions

The fit and external stages refuse to start without --confirm-full-run (the project rule: nothing large runs unannounced).
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tte.config import Paths, load_config  # noqa: E402

ALL_STAGES = ["prepare", "folds", "fit", "external", "metrics", "analyze", "figures"]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None, help="YAML config (default: survival_v2/config/default.yaml)")
    p.add_argument("--stages", default="all", help=f"comma list from {ALL_STAGES} or 'all'")
    p.add_argument("--questions", default="q1,q2,q3,q4", help="comma list of q1,q2,q3,q4")
    p.add_argument("--models", default=None, help="comma list of model specs overriding the configured model sets")
    p.add_argument("--cohorts", default=None, help="comma list overriding config cohorts (tcga, all)")
    p.add_argument("--shard", default="0/1", help="i/n: run every n-th unit starting at i (parallel workers)")
    p.add_argument("--threads", type=int, default=None)
    p.add_argument("--memory-gb", type=int, default=None, help="address-space limit; 0 disables")
    p.add_argument("--device", default=None, choices=["auto", "cpu", "cuda"])
    p.add_argument("--output-root", default=None, help="override paths.output_root")
    p.add_argument("--c5-root", default=None, help="override paths.c5_root (needed only by the prepare stage)")
    p.add_argument("--metabric-root", default=None, help="override paths.metabric_root (needed only by the external stage)")
    p.add_argument("--smoke", action="store_true", help="tiny run using the config's smoke block (writes outputs_smoke/)")
    p.add_argument("--dry-run", action="store_true", help="print the work plan and exit")
    p.add_argument("--force", action="store_true", help="rebuild store/folds and refit units even if outputs exist")
    p.add_argument("--confirm-full-run", action="store_true", help="required for the fit and external stages")
    return p.parse_args(argv)


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=Path(__file__).parent).stdout.strip()
    except Exception:
        return "unknown"


def environment_record(device: str) -> dict:
    rec = {"python": platform.python_version(), "platform": platform.platform(), "device": device, "git": git_commit()}
    for mod in ("numpy", "pandas", "sklearn", "sksurv", "tabpfn", "torch", "catboost", "lifelines"):
        try:
            rec[mod] = __import__(mod).__version__
        except Exception:
            rec[mod] = None
    return rec


def main(argv=None) -> int:
    args = parse_args(argv)
    overrides: dict = {}
    if args.output_root:
        overrides.setdefault("paths", {})["output_root"] = args.output_root
    if args.c5_root:
        overrides.setdefault("paths", {})["c5_root"] = args.c5_root
    if args.metabric_root:
        overrides.setdefault("paths", {})["metabric_root"] = args.metabric_root
    if args.cohorts:
        overrides["cohorts"] = args.cohorts.split(",")
    cfg = load_config(args.config, overrides, smoke=args.smoke)
    paths = Paths(cfg).ensure()
    stages = ALL_STAGES if args.stages == "all" else [s.strip() for s in args.stages.split(",")]
    unknown = set(stages) - set(ALL_STAGES)
    if unknown:
        raise SystemExit(f"unknown stage(s): {sorted(unknown)}")
    questions = [q.strip() for q in args.questions.split(",") if q.strip()]
    models = [m.strip() for m in args.models.split(",")] if args.models else None
    shard = tuple(int(x) for x in args.shard.split("/"))
    comp = cfg["compute"]
    threads = args.threads or int(comp["threads"])
    memory = int(comp["memory_gb"]) if args.memory_gb is None else args.memory_gb
    log_path = paths.logs / f"run_{time.strftime('%Y%m%d_%H%M%S')}_shard{shard[0]}of{shard[1]}.log"

    def log(msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(log_path, "a") as handle:
            handle.write(line + "\n")

    from tte.models import validate_specs
    from tte.runner import enumerate_units

    for q in ("q1", "q2", "q3", "q4"):
        validate_specs(cfg["model_sets"][q])
    if models:
        validate_specs(models)

    if args.dry_run:
        plan = enumerate_units(cfg, [q for q in questions if q != "q4"], models)
        by_ctx: dict = {}
        fits = 0
        for unit, specs in plan:
            by_ctx.setdefault((unit.context, unit.cohort, unit.arm), [0, set()])
            by_ctx[(unit.context, unit.cohort, unit.arm)][0] += 1
            by_ctx[(unit.context, unit.cohort, unit.arm)][1].update(specs)
            fits += len(specs)
        print(f"output root: {paths.root}\nstages: {stages}\nquestions: {questions}\nunits: {len(plan)}; model fits: {fits}")
        for (ctx, cohort, arm), (n, specs) in sorted(by_ctx.items()):
            print(f"  context {ctx} cohort {cohort} arm {arm}: {n} units x {len(specs)} models")
        print("  q4 external: 2 directions x 3 arms x", cfg["external"]["n_seeds"], "seeds" if "q4" in questions else "(not requested)")
        return 0

    from tte.limits import configure

    device = configure(threads, memory, args.device or comp["device"], bool(comp["allow_cpu_large"]))
    (paths.logs / "environment.json").write_text(json.dumps(environment_record(device), indent=2))
    log(f"survival_v2 start: stages={stages} questions={questions} shard={shard} device={device} threads={threads} smoke={args.smoke}")

    if "prepare" in stages:
        from tte.store import build_store

        build_store(cfg, paths, force=args.force, log=log)
    if "folds" in stages:
        import pandas as pd

        from tte.folds import build_assignments, outcome_table, write_folds

        if (paths.folds / "manifest.json").exists() and not args.force:
            log("folds already frozen; use --force to rebuild (this changes every downstream result)")
        else:
            samples = pd.read_parquet(paths.store / "samples.parquet")
            samples = samples[samples["cancer"].isin(cfg["cancers"])]
            outcomes = outcome_table(samples, cfg)
            manifest = write_folds(build_assignments(outcomes, cfg), outcomes, cfg, paths.folds)
            log(f"folds frozen: {manifest['n_rows']} assignments, sha256 {manifest['sha256'][:12]}")
    if ("fit" in stages or "external" in stages) and not args.confirm_full_run:
        raise SystemExit("fit/external stages need --confirm-full-run (use --dry-run to see the plan first)")
    env = None
    if "fit" in stages:
        from tte.runner import RunEnv, run_units

        env = RunEnv(cfg, paths, device, threads, log=log)
        plan = enumerate_units(cfg, [q for q in questions if q != "q4"], models)
        run_units(env, plan, shard=shard, force=args.force)
    if "external" in stages and "q4" in questions and cfg["questions"]["q4"]["enabled"]:
        if shard[0] != 0:
            log("external stage runs on shard 0 only")
        else:
            from tte.external import run_external
            from tte.store import ArrayStore

            store = env.store if env is not None else ArrayStore(paths, cfg, cancers=[c for c in cfg["cancers"]])
            if "BRCA" not in store.cancers:
                log("external stage needs BRCA in the store; skipped")
            else:
                run_external(cfg, paths, store, device, threads, models_override=models, force=args.force, log=log)
    if "metrics" in stages:
        from tte.evaluate import external_metrics, internal_metrics

        if any(paths.predictions.rglob("*.parquet")):
            internal_metrics(cfg, paths, log=log)
        external_metrics(cfg, paths, log=log)
    if "analyze" in stages:
        from tte.analysis import run_analysis

        run_analysis(cfg, paths, log=log)
    if "figures" in stages:
        from tte.figures import run_figures

        run_figures(cfg, paths, log=log)
    log("survival_v2 done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
