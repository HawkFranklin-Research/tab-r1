"""Configuration loading and output-path helpers."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

PKG_ROOT = Path(__file__).resolve().parents[1]          # survival_v2/
REPO_ROOT = PKG_ROOT.parent                              # repository root
DEFAULT_CONFIG = PKG_ROOT / "config" / "default.yaml"


class Cfg(dict):
    """A dict with attribute access and dotted lookup: ``cfg.get_path('features.k')``."""

    def __getattr__(self, item: str) -> Any:
        try:
            value = self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc
        return Cfg(value) if isinstance(value, dict) else value

    def get_path(self, dotted: str, default: Any = None) -> Any:
        node: Any = self
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node


def _deep_update(base: dict, new: dict) -> dict:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def resolve(path: str | Path, root: Path = REPO_ROOT) -> Path:
    path = Path(path).expanduser()
    return path if path.is_absolute() else (root / path)


def load_config(path: str | Path | None = None, overrides: dict | None = None, smoke: bool = False) -> Cfg:
    """Load YAML, apply dict overrides, and (in smoke mode) apply the ``smoke:`` block."""
    with open(resolve(path) if path else DEFAULT_CONFIG) as handle:
        raw = yaml.safe_load(handle)
    cfg = copy.deepcopy(raw)
    if overrides:
        _deep_update(cfg, overrides)
    cfg["smoke_mode"] = bool(smoke)
    if smoke:
        s = cfg["smoke"]
        cfg["cancers"] = list(s["cancers"])
        cfg["folds"]["n_repeats"] = int(s["n_repeats"])
        cfg["features"]["k"] = int(s["k"])
        cfg["paths"]["output_root"] = str(cfg["paths"]["output_root"]).replace("outputs", "outputs_smoke")
        cfg["external"]["n_seeds"] = int(s["external_n_seeds"])
    return Cfg(cfg)


class Paths:
    """Resolved output locations for one run."""

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        self.root = resolve(cfg["paths"]["output_root"])
        self.c5 = resolve(cfg["paths"]["c5_root"])
        self.train_ready = self.c5 / cfg["paths"]["train_ready"]
        self.clinical_master = self.c5 / cfg["paths"]["clinical_master"]
        self.metabric = resolve(cfg["paths"]["metabric_root"])
        self.store = self.root / "store"
        self.folds = self.root / "folds"
        self.predictions = self.root / "predictions"
        self.runs = self.root / "runs"
        self.external = self.root / "external"
        self.metrics = self.root / "metrics"
        self.analysis = self.root / "analysis"
        self.figures = self.root / "figures"
        self.logs = self.root / "logs"

    def ensure(self) -> "Paths":
        for p in (self.store, self.folds, self.predictions, self.runs, self.external, self.metrics, self.analysis,
                  self.figures, self.logs):
            p.mkdir(parents=True, exist_ok=True)
        return self


def horizons(cfg: Cfg) -> dict[str, float]:
    return {k: float(v) for k, v in cfg["horizons_days"].items()}
