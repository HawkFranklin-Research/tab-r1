"""Copy every figure used by submission/manuscript.tex into portal/figures/, named by its number in the manuscript.

Figures are copied byte for byte (no regeneration); rerun after editing any figure. Unused files are never copied.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUBMISSION = ROOT / "submission"
OUT = ROOT / "portal" / "figures"

tex = (SUBMISSION / "manuscript.tex").read_text()
main, extended = tex.split(r"\section*{Extended Data}", 1)
pattern = r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
records = []
for prefix, block in (("Fig", main.split(r"\section*{Figures and legends}", 1)[1]), ("Extended_Data_Fig", extended)):
    for number, relative in enumerate(re.findall(pattern, block), start=1):
        source = SUBMISSION / relative
        target = OUT / f"{prefix}_{number}_{Path(relative).stem}{source.suffix}"
        shutil.copy2(source, target)
        records.append({"file": target.name, "source": relative,
                        "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        print(f"{target.name:<70} <- {relative}")
(OUT / "figure_manifest.json").write_text(json.dumps(records, indent=2) + "\n")
print(f"{len(records)} figures in {OUT.relative_to(ROOT.parent.parent)}")
