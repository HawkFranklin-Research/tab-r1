"""Figures stage: plots from the analysis tables (and, for Kaplan-Meier panels, the saved external predictions).

Every figure is written as PDF and PNG to figures/, with the exact plotted numbers in figures/source_data/. Colours follow the
paper's reusability figures: foundation models blue, tree ensembles orange, linear/Cox models grey, references light grey.
A figure whose input table does not exist yet is skipped with a message, so the stage can run after a partial fit.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import pseudo as pseudo_mod
from .config import Cfg, Paths

INK, INK_2, INK_3, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
GROUP_COLOR = {"foundation": "#2a78d6", "tree": "#eb6834", "linear": "#52514e", "reference": "#b5b4af"}
ARM_COLOR = {"omics": "#2a78d6", "clinical": "#8a8984", "omics_clinical": "#4a3aa7"}
TERTILE_COLOR = ["#2a78d6", "#8a8984", "#eb6834"]


def _style():
    plt.rcParams.update({"font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "legend.fontsize": 6.5, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                         "grid.color": GRID, "grid.linewidth": 0.5, "axes.axisbelow": True, "legend.frameon": False,
                         "axes.titleweight": "bold", "axes.titlelocation": "left", "pdf.fonttype": 42})


def _save(fig, paths: Paths, stem: str, source: pd.DataFrame | None = None):
    paths.figures.mkdir(parents=True, exist_ok=True)
    (paths.figures / "source_data").mkdir(exist_ok=True)
    fig.savefig(paths.figures / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(paths.figures / f"{stem}.png", dpi=250, bbox_inches="tight")
    plt.close(fig)
    if source is not None:
        source.to_csv(paths.figures / "source_data" / f"{stem}.csv", index=False)


def _letter(ax, text):
    ax.text(-0.14, 1.04, text, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom")


def _read(paths: Paths, name: str, log, cohort: str | None = None) -> pd.DataFrame | None:
    path = paths.analysis / name
    if not path.exists():
        log(f"figures: {name} not found, skipping")
        return None
    frame = pd.read_csv(path)
    if cohort is not None and "cohort" in frame:
        frame = frame[frame["cohort"] == cohort]
    if frame.empty:
        log(f"figures: {name} has no rows for cohort {cohort}, skipping")
        return None
    return frame


def fig_q1(paths: Paths, log, cohort: str = "tcga"):
    s = _read(paths, "q1_summary.csv", log, cohort)
    if s is None:
        return
    macro = s[s.cancer == "macro"].sort_values("c_harrell_mean")
    per = s[s.cancer != "macro"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 0.22 * len(macro) + 1.6), gridspec_kw=dict(width_ratios=[1, 1.3], wspace=0.9))
    ax = axes[0]
    _letter(ax, "a")
    for i, r in enumerate(macro.itertuples()):
        pts = per[per.model_key == r.model_key]["c_harrell_mean"]
        ax.scatter(pts, [i] * len(pts), s=8, color=GROUP_COLOR.get(r.model_group, INK_3), alpha=0.4, linewidths=0)
        ax.scatter(r.c_harrell_mean, i, s=28, color=GROUP_COLOR.get(r.model_group, INK_3), zorder=3)
    ax.axvline(0.5, color=INK_3, ls=":", lw=0.8)
    ax.set_yticks(range(len(macro)), macro.model_key)
    ax.set_xlabel("Harrell C (mean over test sets; small dots: cancers)")
    ax.grid(axis="y", visible=False)
    ax = axes[1]
    _letter(ax, "b")
    heat = per.pivot_table(index="model_key", columns="cancer", values="c_harrell_mean").reindex(macro.model_key[::-1])   # top row = best, as in panel a
    im = ax.imshow(heat.to_numpy(), cmap="Greys", vmin=0.45, vmax=0.75, aspect="auto")
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            v = heat.iat[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.6, color="white" if v > 0.64 else INK)
    ax.set_xticks(range(heat.shape[1]), heat.columns)
    ax.set_yticks(range(heat.shape[0]), heat.index)
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02).set_label("Harrell C", fontsize=6.5)
    _save(fig, paths, f"q1_cindex_within_cancer_{cohort}", s)


def fig_q1_pooled(paths: Paths, log, cohort: str):
    p = _read(paths, "q1_pooled.csv", log, cohort)
    if p is None or "c_strat" not in p:
        return
    p = p.sort_values("c_harrell")
    fig, ax = plt.subplots(figsize=(4.2, 0.22 * len(p) + 1.2))
    for i, r in enumerate(p.itertuples()):
        c = GROUP_COLOR.get(r.model_group, INK_3)
        ax.plot([r.c_strat, r.c_harrell], [i, i], color=c, lw=1.4, alpha=0.7)
        ax.scatter(r.c_harrell, i, s=26, color=c, zorder=3)
        ax.scatter(r.c_strat, i, s=26, facecolor="white", edgecolor=c, linewidth=1.2, zorder=3)
    ax.axvline(0.5, color=INK_3, ls=":", lw=0.8)
    ax.set_yticks(range(len(p)), p.model_key)
    ax.set_xlabel("Harrell C on pooled test sets: all pairs (filled) vs same-cancer pairs only (open)")
    ax.grid(axis="y", visible=False)
    _save(fig, paths, f"q1_pooled_vs_within_{cohort}", p)


def _forest(ax, d: pd.DataFrame, label_col: str = "model_key"):
    for i, r in enumerate(d.itertuples()):
        c = GROUP_COLOR.get(getattr(r, "model_group", "linear"), INK_3)
        resolved = r.lo > 0 or r.hi < 0
        ax.plot([r.lo, r.hi], [i, i], color=c, lw=1.5)
        ax.scatter(r.diff, i, s=26, color=c if resolved else "white", edgecolor=c, linewidth=1.2, zorder=3)
    ax.axvline(0, color=INK_3, ls="--", lw=0.8)
    ax.set_yticks(range(len(d)), d[label_col])
    ax.grid(axis="y", visible=False)


def fig_q2(paths: Paths, log, cohort: str, metric: str = "c_harrell"):
    q2 = _read(paths, "q2_contrasts.csv", log, cohort)
    if q2 is None:
        return
    q2 = q2[(q2.cancer == "macro") & (q2.metric == metric)]
    contrasts = [c for c in ("B-A", "C-A", "C-B", "D-A") if c in set(q2.contrast)]
    order = q2[q2.contrast == contrasts[0]].sort_values("diff").model_key.tolist()
    fig, axes = plt.subplots(1, len(contrasts), figsize=(2.3 * len(contrasts) + 1, 0.22 * len(order) + 1.4), sharey=True,
                             gridspec_kw=dict(wspace=0.15))
    axes = np.atleast_1d(axes)
    for k, (ax, con) in enumerate(zip(axes, contrasts)):
        d = q2[q2.contrast == con].set_index("model_key").reindex(order).reset_index()
        _forest(ax, d)
        ax.set_title({"B-A": "naive pooling", "C-A": "standardised pooling", "C-B": "standardised vs naive", "D-A": "stratified targets"}[con], fontsize=7)
        if k == 0:
            _letter(ax, "a")
        ax.set_xlabel(f"Within-cancer change in {metric.replace('_', ' ')}")
    _save(fig, paths, f"q2_pooling_contexts_{cohort}", q2)


def fig_q3(paths: Paths, log, cohort: str, metric: str = "c_harrell"):
    q3 = _read(paths, "q3_increments.csv", log, cohort)
    if q3 is None:
        return
    d = q3[(q3.metric == metric) & (q3.contrast == "omics_clinical-clinical")]
    macro = d[d.cancer == "macro"].sort_values("diff")
    per = d[d.cancer != "macro"]
    fig, ax = plt.subplots(figsize=(4.4, 0.24 * len(macro) + 1.3))
    _forest(ax, macro)
    for i, mk in enumerate(macro.model_key):
        pts = per[per.model_key == mk]["diff"]
        ax.scatter(pts, [i + 0.25] * len(pts), s=6, color=INK_3, alpha=0.6, linewidths=0)
    ax.set_xlabel("Harrell C: clinical + omics minus clinical only (macro; grey dots: cancers)")
    _save(fig, paths, f"q3_omics_beyond_clinical_{cohort}", d)


def fig_q4(paths: Paths, log, km_model: str | None = None):
    q4 = _read(paths, "q4_summary.csv", log)
    if q4 is None:
        return
    directions = sorted(q4.direction.unique())
    fig, axes = plt.subplots(2, len(directions), figsize=(3.4 * len(directions), 5.4), gridspec_kw=dict(hspace=0.55, wspace=0.95))
    axes = np.atleast_2d(axes).reshape(2, len(directions))
    for j, direction in enumerate(directions):
        ax = axes[0, j]
        if j == 0:
            _letter(ax, "a")
        d = q4[q4.direction == direction]
        models = d.groupby("model_key").c_harrell.mean().sort_values().index.tolist()
        for i, mk in enumerate(models):
            for k, arm in enumerate(["clinical", "omics", "omics_clinical"]):
                r = d[(d.model_key == mk) & (d.arm == arm)]
                if r.empty:
                    continue
                r = r.iloc[0]
                y = i + (k - 1) * 0.22
                ax.plot([r.c_harrell_lo, r.c_harrell_hi], [y, y], color=ARM_COLOR[arm], lw=1.2)
                ax.scatter(r.c_harrell, y, s=16, color=ARM_COLOR[arm], zorder=3, label=arm if i == 0 else None)
        ax.axvline(0.5, color=INK_3, ls=":", lw=0.8)
        ax.set_yticks(range(len(models)), models)
        ax.set_title(direction.replace("_", " "), fontsize=7)
        ax.set_xlabel("Harrell C in the external cohort (95% patient bootstrap)")
        ax.grid(axis="y", visible=False)
        if j == len(directions) - 1:
            ax.legend(loc="lower right")
        ax = axes[1, j]
        if j == 0:
            _letter(ax, "b")
        _km_panel(ax, paths, direction, km_model)
    _save(fig, paths, "q4_external_validation", q4)


def _km_panel(ax, paths: Paths, direction: str, km_model: str | None):
    root = paths.external / "predictions" / direction / "omics_clinical"
    files = sorted(root.glob("seed*.parquet"))
    if not files:
        ax.set_axis_off()
        return
    pred = pd.read_parquet(files[0])
    models = pred.model.unique().tolist()
    candidates = [m for m in models if m not in ("km", "null_cancer", "null_source")]
    if not candidates:
        ax.set_axis_off()
        return
    chosen = km_model if km_model in candidates else next((m for pref in ("tabpfn_v3", "coxnet", "coxph") for m in candidates if pref in m), candidates[0])
    part = pred[pred.model == chosen]
    tert = pd.qcut(part["risk"].rank(method="first"), 3, labels=["low", "middle", "high"])
    grid = np.linspace(0, part["time"].max(), 200)
    for k, level in enumerate(["low", "middle", "high"]):
        sel = (tert == level).to_numpy()
        ax.step(grid / 365.25, pseudo_mod.km_survival(part["time"].to_numpy()[sel], part["event"].to_numpy()[sel], grid), where="post",
                color=TERTILE_COLOR[k], lw=1.3, label=f"{level} risk (n={sel.sum()})")
    try:
        from lifelines.statistics import multivariate_logrank_test

        p = multivariate_logrank_test(part["time"], tert.astype(str), part["event"]).p_value
        ax.text(0.02, 0.03, f"log-rank P = {p:.2g}", transform=ax.transAxes, ha="left", va="bottom", fontsize=6.5, color=INK_2)
    except Exception:
        pass
    ax.set_xlabel("Years")
    ax.set_ylabel("Overall survival")
    ax.set_ylim(0, 1.02)
    ax.set_title(f"{chosen} (clinical + omics), tertiles of predicted risk", fontsize=6.5)
    ax.legend(loc="upper right")


def fig_coverage(paths: Paths, log):
    c = _read(paths, "model_coverage.csv", log)
    if c is None:
        return
    cols = ["native_survival", "pseudo_observations", "ipcw_classifier"]
    fig, ax = plt.subplots(figsize=(3.6, 0.2 * len(c) + 1.0))
    ax.imshow(c[cols].astype(float).to_numpy(), cmap="Blues", vmin=0, vmax=1.6, aspect="auto")
    for i in range(len(c)):
        for j, col in enumerate(cols):
            ax.text(j, i, "yes" if c.iloc[i][col] else "-", ha="center", va="center", fontsize=6, color=INK if not c.iloc[i][col] else "white")
    ax.set_xticks(range(3), ["native\nsurvival", "pseudo-\nobservations", "IPCW\nclassifier"])
    ax.set_yticks(range(len(c)), c.model)
    ax.grid(False)
    _save(fig, paths, "model_coverage", c)


def run_figures(cfg: Cfg, paths: Paths, log=print) -> None:
    _style()
    for cohort in cfg["cohorts"]:
        fig_q1(paths, log, cohort)
        fig_q1_pooled(paths, log, cohort)
        fig_q2(paths, log, cohort)
        fig_q3(paths, log, cohort)
    fig_q4(paths, log)
    fig_coverage(paths, log)
    log(f"figures written to {paths.figures}")
