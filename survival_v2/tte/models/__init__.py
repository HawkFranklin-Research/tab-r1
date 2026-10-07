"""Model registry: ``build_model('pseudo:tabpfn_v3:rmst+h5')`` etc."""

from __future__ import annotations

from .base import FitContext, SurvivalModel
from .classical import GBSA, RSF, CoxNet, CoxPH, KaplanMeier, NullGroup
from .foundation import (HORIZON_TOKENS, TABPFN_VERSIONS, IPCWClassifierModel, NativeTabPFNSurvival, PseudoObsModel)

SIMPLE = {"coxnet": CoxNet, "coxph": CoxPH, "rsf": RSF, "gbsa": GBSA, "km": KaplanMeier}
REGRESSORS = ["ridge", "random_forest", "catboost", *TABPFN_VERSIONS, "tabfm"]
CLASSIFIERS = ["logistic", "random_forest", "catboost", *TABPFN_VERSIONS, "tabfm"]
TARGETS = ("rmst", *HORIZON_TOKENS)


def parse_spec(spec: str) -> tuple[str, str, list[str]]:
    """Return (family, variant, targets) for a specification string; raises ValueError on a malformed one."""
    parts = str(spec).split(":")
    head = parts[0]
    if head in SIMPLE or head in ("null_cancer", "null_source"):
        if len(parts) != 1:
            raise ValueError(f"{spec!r}: '{head}' takes no arguments")
        return head, head, []
    if head == "pseudo":
        if len(parts) not in (2, 3) or parts[1] not in REGRESSORS:
            raise ValueError(f"{spec!r}: expected pseudo:<regressor>[:targets] with regressor in {REGRESSORS}")
        targets = parts[2].split("+") if len(parts) == 3 else ["rmst"]
        bad = [t for t in targets if t not in TARGETS]
        if bad:
            raise ValueError(f"{spec!r}: unknown target(s) {bad}; use {TARGETS}")
        return "pseudo", parts[1], targets
    if head == "native":
        if len(parts) != 2 or parts[1] not in TABPFN_VERSIONS:
            raise ValueError(f"{spec!r}: expected native:<{'|'.join(TABPFN_VERSIONS)}>")
        return "native", parts[1], []
    if head == "ipcw":
        if len(parts) != 2 or parts[1] not in CLASSIFIERS:
            raise ValueError(f"{spec!r}: expected ipcw:<classifier> with classifier in {CLASSIFIERS}")
        return "ipcw", parts[1], []
    raise ValueError(f"unknown model specification {spec!r}")


def normalise(spec: str) -> str:
    family, variant, targets = parse_spec(spec)
    return f"pseudo:{variant}:{'+'.join(targets)}" if family == "pseudo" else (spec if ":" in spec else family)


def build_model(spec: str) -> SurvivalModel:
    family, variant, targets = parse_spec(spec)
    if family in SIMPLE:
        model = SIMPLE[family]()
    elif family == "null_cancer":
        model = NullGroup("cancer")
    elif family == "null_source":
        model = NullGroup("source")
    elif family == "pseudo":
        model = PseudoObsModel(variant, targets)
    elif family == "native":
        model = NativeTabPFNSurvival(variant)
    else:
        model = IPCWClassifierModel(variant)
    return model


def is_foundation(spec: str) -> bool:
    family, variant, _ = parse_spec(spec)
    return variant in TABPFN_VERSIONS or variant == "tabfm"


def validate_specs(specs: list[str]) -> list[str]:
    return [normalise(s) for s in specs]


def model_key(spec: str) -> str:
    """Spec without pseudo-value targets ('pseudo:tabpfn_v3:rmst+h3+h5' -> 'pseudo:tabpfn_v3').

    The risk score of a pseudo model comes from its RMST regressor whatever extra targets are fitted, so results of
    specs that share a key are comparable across questions (Q1's context A serves as Q3's omics arm and Q2's reference).
    """
    family, variant, _ = parse_spec(spec)
    return f"pseudo:{variant}" if family == "pseudo" else normalise(spec)


def model_group(spec: str) -> str:
    """Coarse family used in figures: foundation, tree, linear, reference."""
    family, variant, _ = parse_spec(spec)
    if family in ("km", "null_cancer", "null_source"):
        return "reference"
    if variant in TABPFN_VERSIONS or variant == "tabfm":
        return "foundation"
    if family in ("rsf", "gbsa") or variant in ("random_forest", "catboost"):
        return "tree"
    return "linear"
