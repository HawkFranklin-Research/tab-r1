"""Derive the anonymised manuscript for double-blind review from submission/manuscript.tex.

Writes submission/manuscript_WA.tex ("without authors"), compiles submission/manuscript_WA.pdf and packs
submission_source_WA.zip. Removes author names, affiliations and e-mail, the author-contribution names and every link to
the authors' repositories; Data and Code availability state that the material is shared with the editor only.
The script stops if any identifying string survives, so a later edit to the manuscript cannot leak identity silently.
"""
from __future__ import annotations

import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUBMISSION = ROOT / "submission"
SOURCE, TARGET = SUBMISSION / "manuscript.tex", SUBMISSION / "manuscript_WA.tex"

METHODS_LINK = re.compile(r"Analysis and visualization code is provided through the study repository on \\href\{[^{}]*\}\{[^{}]*\}\.")
METHODS_BLIND = "Analysis and visualization code has been shared with the editor (see Code availability)."

DATA_BLIND = (
    r"The TCGA and CPTAC data analysed in this study are publicly available from \href{https://www.cbioportal.org}{cBioPortal} "
    r"(TCGA PanCancer Atlas 2018 studies) and \href{https://www.linkedomics.org}{LinkedOmics}. The 400 frozen patient-grouped "
    "test sets, per-patient predictions for every model and test set, and source data for all figures and tables are deposited "
    "in a public repository. To preserve anonymity during double-blind peer review, its link has been shared with the editor "
    "only, and reviewers are welcome to request access through the editor."
)
CODE_BLIND = (
    "To comply with the journal's double-blind peer review guidelines, the code for data preparation, construction of the frozen "
    "test sets, model evaluation, statistical analysis and figure generation has been shared with the editor only. Reviewers "
    "are welcome to request access to it through the editor. The repository includes per-patient predictions for every model "
    "and test set, so all reported statistics, figures and tables can be regenerated without refitting any model."
)
LLM_SENTENCE = re.compile(r"Language-model assistance was used[^\n]*")

# Strings that must not appear anywhere in the anonymised source (names, initials, affiliations, places, organisation, links).
IDENTIFYING = [
    "HawkFranklin", "hawkfranklin", "tab-r1", "huggingface", "Vatsal", "Pravinbhai", "Satya", "Mohanty", "Bikram", "Bhakat",
    "Abhijeet", "Pravinkumar", "Jayeshbhai", "Ananya", "V.P.P.", "S.P.M.", "Burdwan", "Bethune", "Dehri", "Valsad", "Vadodara",
    "Baroda", "Purba Bardhaman", "34332477", "ea59fbc6", "\\author", "\\affil", "\\email",
]


def replace_section(text: str, heading: str, body: str) -> str:
    """Replace the paragraph that follows \\section*{heading}."""
    pattern = re.compile(r"(\\section\*\{" + re.escape(heading) + r"\}\n)([^\n]+)")
    if len(pattern.findall(text)) != 1:
        raise SystemExit(f"expected exactly one '{heading}' section")
    return pattern.sub(lambda m: m.group(1) + body.replace("\\", "\\\\").replace("\\\\", "\\"), text)


def main() -> None:
    text = SOURCE.read_text()
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(("\\author", "\\affil"))) + "\n"
    if len(METHODS_LINK.findall(text)) != 1:
        raise SystemExit("the Methods repository sentence changed; update METHODS_LINK")
    text = METHODS_LINK.sub(METHODS_BLIND, text)
    text = replace_section(text, "Data availability", DATA_BLIND)
    text = replace_section(text, "Code availability", CODE_BLIND)
    contributions = re.search(r"\\section\*\{Author contributions\}\n([^\n]+)", text)
    llm = LLM_SENTENCE.search(contributions.group(1))
    blind = "Author contributions are withheld for double-blind peer review." + (" " + llm.group(0) if llm else "")
    text = replace_section(text, "Author contributions", blind)
    text = text.replace(r"\hypersetup{hidelinks}", r"\hypersetup{hidelinks,pdfauthor={},pdfcreator={},pdfsubject={}}")
    leaks = [s for s in IDENTIFYING if s in text]
    leaks += [m.group(0) for m in re.finditer(r"\bPatel\b|\bPal\b", text)]
    if leaks:
        raise SystemExit(f"identifying strings remain in the anonymised manuscript: {sorted(set(leaks))}")
    TARGET.write_text(text)

    subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", TARGET.name], cwd=SUBMISSION, check=True,
                   stdout=subprocess.DEVNULL)
    info = subprocess.run(["pdfinfo", "manuscript_WA.pdf"], cwd=SUBMISSION, capture_output=True, text=True).stdout
    shown = subprocess.run(["pdftotext", "manuscript_WA.pdf", "-"], cwd=SUBMISSION, capture_output=True, text=True).stdout
    pdf_leaks = [s for s in IDENTIFYING[:24] if s in info or s in shown]
    if pdf_leaks:
        raise SystemExit(f"identifying strings remain in manuscript_WA.pdf: {pdf_leaks}")

    # Same LaTeX package as submission_source.zip, with the anonymised manuscript in place of the named one.
    with zipfile.ZipFile(ROOT / "submission_source.zip") as named, \
            zipfile.ZipFile(ROOT / "submission_source_WA.zip", "w", zipfile.ZIP_DEFLATED) as blind_zip:
        for item in named.namelist():
            if item == "manuscript.tex":
                blind_zip.write(TARGET, "manuscript_WA.tex")
            else:
                blind_zip.writestr(item, named.read(item))
    print("Anonymised manuscript written: submission/manuscript_WA.tex, manuscript_WA.pdf, submission_source_WA.zip")


if __name__ == "__main__":
    main()
