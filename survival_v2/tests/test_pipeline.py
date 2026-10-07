"""End-to-end and component tests on synthetic data (no real data, no foundation models, a few seconds each)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from sksurv.metrics import concordance_index_censored

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from synthetic import CANCERS, SIGNAL, make_c5, make_metabric, synthetic_config  # noqa: E402

from tte import metrics  # noqa: E402
from tte.config import Paths, load_config  # noqa: E402
from tte.store import coalesce_block  # noqa: E402


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("sv2")
    make_c5(tmp / "c5")
    make_metabric(tmp / "metabric")
    cfg_path = tmp / "config.yaml"
    base = yaml.safe_load((Path(__file__).resolve().parents[1] / "config" / "default.yaml").read_text())

    def merge(a, b):
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(a.get(k), dict):
                merge(a[k], v)
            else:
                a[k] = v
        return a

    cfg_path.write_text(yaml.safe_dump(merge(base, synthetic_config(tmp, tmp / "c5", tmp / "metabric"))))
    import run_pipeline

    assert run_pipeline.main(["--config", str(cfg_path), "--confirm-full-run", "--threads", "2", "--memory-gb", "0"]) == 0
    cfg = load_config(cfg_path)
    return cfg, Paths(cfg)


def test_coalesce_takes_each_rows_observed_copy():
    A = np.array([[1.0, 0.0], [0.0, 5.0]])
    MA = np.array([[0, 1], [1, 0]], np.uint8)
    B = np.array([[0.0, 2.0], [3.0, 0.0]])
    MB = np.array([[1, 0], [0, 1]], np.uint8)
    values, missing, both = coalesce_block(A, MA, B, MB)
    assert values.tolist() == [[1.0, 2.0], [3.0, 5.0]] and missing.sum() == 0 and both == 0


def test_store_coalesces_source_blocks(run):
    cfg, paths = run
    feats = pd.read_parquet(paths.store / "features.parquet")
    samples = pd.read_parquet(paths.store / "samples.parquet")
    assert feats["feature_id"].is_unique
    X = np.load(paths.store / "X_BRCA.npy")
    col = int(np.flatnonzero(feats["feature_id"] == SIGNAL[0])[0])
    brca = samples[samples.cancer == "BRCA"]
    cptac_rows = brca.loc[brca.source == "CPTAC", "row"].to_numpy()
    assert (X[cptac_rows, col] != 0).all(), "CPTAC rows must carry values after coalescing, not structural zeros"
    report = json.loads((paths.store / "store_report.json").read_text())
    assert report["coalescing"]["both_observed_cells"] == 0
    assert report["universes"]["tcga"]["n_features"] > 0


def test_clinical_harmonised_across_sources(run):
    cfg, paths = run
    clin = pd.read_parquet(paths.store / "clinical.parquet")
    assert clin["stage"].dropna().isin([1, 2, 3, 4]).all()
    assert clin["age"].notna().mean() > 0.95
    assert clin["n_stage"].isna().any()                    # 'NX' became missing


def test_folds_are_frozen_and_valid(run):
    cfg, paths = run
    from tte.folds import Folds

    folds = Folds(paths.folds)
    a = folds.assignments
    assert set(a.scope) == {"per_cancer", "pooled"}
    assert not a.groupby(["scope", "cohort", "cancer", "repeat"])["patient_id"].apply(lambda s: s.duplicated().any()).any()
    tcga = a[(a.cohort == "tcga")]
    assert tcga["patient_id"].str.startswith("TCGA:").all()


def test_paired_contexts_share_test_patients(run):
    cfg, paths = run
    a = pd.read_parquet(paths.predictions / "A/tcga/omics/HNSCC/r0_f0.parquet")
    b = pd.read_parquet(paths.predictions / "B/tcga/omics/HNSCC/r0_f0.parquet")
    assert set(a.patient_id) == set(b.patient_id)
    info = json.loads((paths.runs / "B/tcga/omics/HNSCC/r0_f0.json").read_text())
    assert len(info["train_cancers"]) == len(CANCERS)        # pooled training includes every cancer


def test_every_model_ran_and_predictions_complete(run):
    cfg, paths = run
    errors = pd.read_csv(paths.metrics / "model_errors.csv")
    assert errors.empty, errors.to_string()
    m = pd.read_parquet(paths.metrics / "run_metrics.parquet")
    assert {"A", "B", "C", "D", "P"} <= set(m.context)
    assert m["c_harrell"].notna().mean() > 0.95
    km = m[m.model == "km"]
    assert np.allclose(km["c_harrell"].dropna(), 0.5)


def test_models_recover_planted_signal(run):
    cfg, paths = run
    m = pd.read_parquet(paths.metrics / "run_metrics.parquet")
    A = m[(m.context == "A") & (m.arm == "omics") & (m.cohort == "tcga")]
    means = A.groupby("model")["c_harrell"].mean()
    assert means["coxnet"] > 0.62 and means["pseudo:random_forest:rmst+h3+h5"] > 0.6
    sel = json.loads((paths.runs / "A/tcga/omics/LUAD/r0_f0.json").read_text())["selection"]["features"]
    assert SIGNAL[0] in sel


def test_pooled_context_reports_stratified_c(run):
    cfg, paths = run
    m = pd.read_parquet(paths.metrics / "run_metrics.parquet")
    P = m[m.context == "P"]
    assert P["c_strat"].notna().all() and "c_BRCA" in P


def test_external_and_tables_and_figures(run):
    cfg, paths = run
    e = pd.read_parquet(paths.metrics / "external_metrics.parquet")
    assert set(e.direction) == {"tcga_to_metabric", "metabric_to_tcga"} and set(e.arm) == {"omics", "clinical", "omics_clinical"}
    for name in ("q1_summary.csv", "q1_vs_reference.csv", "q1_pooled.csv", "q2_contrasts.csv", "q2_family.csv", "q3_increments.csv",
                 "q4_summary.csv", "model_coverage.csv"):
        assert (paths.analysis / name).exists(), name
    q2 = pd.read_csv(paths.analysis / "q2_contrasts.csv")
    assert {"B-A", "C-A", "C-B", "D-A"} <= set(q2.contrast)
    for stem in ("q1_cindex_within_cancer_tcga", "q1_pooled_vs_within_tcga", "q2_pooling_contexts_tcga", "q3_omics_beyond_clinical_tcga",
                 "q1_cindex_within_cancer_all", "q4_external_validation", "model_coverage"):
        assert (paths.figures / f"{stem}.png").exists(), stem


def test_resume_skips_finished_units(run):
    cfg, paths = run
    from tte.limits import configure
    from tte.runner import RunEnv, enumerate_units, run_units

    env = RunEnv(cfg, paths, "cpu", 2, log=lambda *_: None)
    res = run_units(env, enumerate_units(cfg, ["q1"]))
    assert all(r["status"] == "skipped" for r in res)


def test_stratified_c_matches_sksurv_per_group():
    rng = np.random.default_rng(0)
    t = rng.exponential(100, 200)
    e = rng.random(200) < 0.6
    r = rng.normal(size=200)
    g = np.repeat(["a", "b"], 100)
    total, per = metrics.stratified_c(t, e, r, g)
    for level in ("a", "b"):
        s = g == level
        assert per[level] == pytest.approx(concordance_index_censored(e[s], t[s], r[s])[0])
    assert min(per.values()) - 1e-9 <= total <= max(per.values()) + 1e-9
