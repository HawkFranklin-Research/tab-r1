import numpy as np
import pytest
from lifelines import KaplanMeierFitter
from lifelines.utils import restricted_mean_survival_time

from tte import pseudo

HORIZONS = {"s3": 1095.0, "s5": 1825.0}
TAU = 1825.0


def _data(n=60, seed=0, ties=True):
    rng = np.random.default_rng(seed)
    time = rng.exponential(1500, n)
    cens = rng.exponential(2500, n)
    event = time <= cens
    time = np.minimum(time, cens)
    if ties:
        time = np.round(time / 50) * 50 + 1.0      # forces tied times, including event/censor ties
    return time, event


def test_km_matches_lifelines():
    time, event = _data(120, 1)
    kmf = KaplanMeierFitter().fit(time, event)
    q = np.array([100.0, 800.0, 1095.0, 1825.0, 4000.0])
    assert np.allclose(pseudo.km_survival(time, event, q), kmf.survival_function_at_times(q).to_numpy(), atol=1e-12)
    assert abs(pseudo.km_rmst(time, event, TAU) - restricted_mean_survival_time(kmf, t=TAU)) < 1e-8


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
@pytest.mark.parametrize("ties", [False, True])
def test_pseudo_values_equal_brute_force_jackknife(seed, ties):
    time, event = _data(50, seed, ties)
    got = pseudo.pseudo_values(time, event, HORIZONS, TAU)
    n = len(time)
    full_s = {k: pseudo.km_survival(time, event, h)[0] for k, h in HORIZONS.items()}
    full_r = pseudo.km_rmst(time, event, TAU)
    for i in range(n):
        keep = np.arange(n) != i
        for k, h in HORIZONS.items():
            want = n * full_s[k] - (n - 1) * pseudo.km_survival(time[keep], event[keep], h)[0]
            assert got[k][i] == pytest.approx(want, abs=1e-9), (k, i)
        want = n * full_r - (n - 1) * pseudo.km_rmst(time[keep], event[keep], TAU)
        assert got["rmst"][i] == pytest.approx(want, abs=1e-6), ("rmst", i)


def test_pseudo_values_average_to_km_estimate():
    time, event = _data(400, 5, ties=False)
    got = pseudo.pseudo_values(time, event, HORIZONS, TAU)
    for k, h in HORIZONS.items():
        assert got[k].mean() == pytest.approx(pseudo.km_survival(time, event, h)[0], abs=0.02)
    assert got["rmst"].mean() == pytest.approx(pseudo.km_rmst(time, event, TAU), rel=0.02)


def test_pseudo_values_stratified_matches_per_stratum_and_keeps_order():
    time, event = _data(80, 7, ties=False)
    strata = np.where(np.arange(80) % 2 == 0, "a", "b")
    got = pseudo.pseudo_values(time, event, HORIZONS, TAU, strata=strata)
    for level in ("a", "b"):
        sel = strata == level
        part = pseudo.pseudo_values(time[sel], event[sel], HORIZONS, TAU)
        for k in part:
            assert np.allclose(got[k][sel], part[k])


def test_degenerate_inputs_do_not_crash():
    time = np.array([10.0, 20.0, 30.0, 40.0])
    event = np.zeros(4, bool)          # no events at all
    out = pseudo.pseudo_values(time, event, HORIZONS, TAU)
    assert np.allclose(out["s3"], 1.0)
    assert np.isfinite(out["rmst"]).all()


def test_ipcw_weights_zero_for_early_censoring_and_positive_otherwise():
    time = np.array([100.0, 200.0, 500.0, 2000.0, 2500.0, 300.0])
    event = np.array([1, 0, 1, 0, 1, 1], bool)
    w = pseudo.ipcw_weights(time, event, 1095.0)
    assert w[1] == 0.0                              # censored at 200 < 1095
    assert (w[[0, 2, 3, 5]] > 0).all()              # died before h, or followed beyond h
    assert w[4] > 0                                 # alive at the horizon (died later)
    lab = pseudo.horizon_label(time, event, 1095.0)
    assert lab.tolist() == [1, 0, 1, 0, 0, 1]
