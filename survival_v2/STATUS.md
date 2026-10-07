# survival_v2 build status (updated 2026-10-07)

Nothing has been run on real data; no smoke test has been run. Nothing is committed.

## Done
- Whole pipeline: run_pipeline.py (prepare, folds, fit, external, metrics, analyze, figures; --smoke, --dry-run, --shard i/n,
  --confirm-full-run, --c5-root/--metabric-root, resumable), tte/*.py, tte/models/*.py, config/default.yaml.
- Per-patient predictions saved for every unit/model; all metrics recomputed from them.
- Cloud: Dockerfile, scripts/gcloud_launch.sh (one Spot VM per shard, GPU or CPU), scripts/gcloud_sync.sh. Not executed.
- README.md (design, data decisions, attribution caveat, running, outputs).
- Independent code audit (2026-10-07): no test-set leakage; risk signs correct; TabPFN 8.0.3 API usage confirmed. All of its
  confirmed bugs are fixed:
  1. pooled-fold verification was too strict (would have aborted the folds stage ~90% of the time) -> per-cancer event balance;
     checked on cohorts with the real sizes over 40 seeds: 0 failures;
  2. Uno C / td-AUC / Brier now use the target cancer's own training rows as censoring reference (identical across contexts A-D);
     Q4 uses the test cohort's censoring;
  3. temp files no longer match '*.parquet'; 4. all prediction/JSON writes are atomic and reads tolerant.
  Risks also addressed: metrics stage checks the rebuilt training size against the fit; the external stage reuses the loaded store;
  duplicate patient ids handled; TabFM probability cache cleared before each call; IPCW uses G(T-); analysis refuses ambiguous
  pairings and reports models dropped from the Friedman test; the planner keeps one spec per model key.

## Still to do
1. Smoke test on real data when the user says so: `python3 survival_v2/run_pipeline.py --smoke --confirm-full-run`.
   Never executed so far: TabPFN/TabFM code paths, prepare on the real c-5 files (~1.5 GB dense matrices), the cloud scripts.
2. Full run (local or cloud), then decide what enters the manuscript.
