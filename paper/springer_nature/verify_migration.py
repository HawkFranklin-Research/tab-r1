"""Check preservation and self-contained assets without running any experiment."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "migration_manifest.json").read_text())
original = root.parent / "reusability_report.tex"
assert hashlib.sha256(original.read_bytes()).hexdigest() == manifest["source_sha256"]
source = (root / "source_snapshot.tex").read_text()
sections = "\n".join(
    (root / "working" / entry["path"]).read_text()
    for entry in manifest["sections"]
)
submission = (root / "submission/manuscript.tex").read_text()
paragraphs = [
    line for line in source.split(r"\section*{Introduction}", 1)[1].splitlines()
    if line.strip() and not line.startswith(("\\", "%"))
]
assert all(line in sections and line in submission for line in paragraphs)
citations = lambda text: sorted(re.findall(r"\\cite\w*\{([^}]+)\}", text))
assert citations(source) == citations(sections) == citations(submission)
labels = lambda text: sorted(re.findall(r"\\label\{([^}]+)\}", text))
assert labels(source) == labels(sections) == labels(submission)
for entry in manifest["assets"]:
    for destination in ("working", "submission"):
        path = root / destination / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], path
assert not re.search(r"\\(?:input|include|bibliography)\{", submission)
assert submission.count(r"\begin{figure}") == 10
assert submission.count(r"\begin{table}") == 3
for path in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", submission):
    assert (root / "submission" / path).exists()
for directory, log in (("working", "main.log"), ("submission", "manuscript.log")):
    text = (root / directory / log).read_text()
    assert not re.search(r"^!|undefined|Overfull|LaTeX Warning|Package .* Warning", text, re.M)
print(f"Verified {len(paragraphs)} body paragraphs, citation groups, labels, "
      "10 figures, 3 tables, unchanged original and identical copied assets.")
