"""Snapshot the report into Springer working and flattened submission formats."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAPER = ROOT.parent
TEMPLATE = ROOT / "template/sn-article-template"
WORK = ROOT / "working"
SUBMISSION = ROOT / "submission"

PREAMBLE = r"""\documentclass[pdflatex,sn-nature]{sn-jnl}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{array}
\usepackage{xcolor}
\usepackage{placeins}
\raggedbottom
\usepackage{url}
\setlength{\emergencystretch}{3em}
\hypersetup{hidelinks}
\begin{document}
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frontmatter(source: str) -> str:
    title = re.search(r"\\title\{([^\n]+)\}", source).group(1)
    keywords = re.search(r"\\keywords\{([^\n]+)\}", source).group(1)
    abstract = source.split(r"\begin{abstract}", 1)[1].split(r"\end{abstract}", 1)[0]
    abstract = abstract.strip().removeprefix(r"\noindent ")
    return (
        "\\title{" + title + "}\n"
        r"\author*[1]{\fnm{Vatsal P.} \sur{Patel}}\email{vatsal1@hawkfranklin.in}" "\n"
        r"\author[1]{\fnm{Satya Prakash} \sur{Mohanty}}" "\n"
        r"\affil[1]{\orgname{HawkFranklin Research}, \orgaddress{\country{India}}}" "\n"
        "\\abstract{" + abstract + "}\n"
        "\\keywords{" + keywords + "}\n"
        r"\maketitle" "\n"
        r"\raggedbottom" "\n"
    )


def prepare() -> None:
    source_path = PAPER / "reusability_report.tex"
    source = source_path.read_text()
    if (WORK / "main.tex").exists():
        raise SystemExit("Working copy exists; migration will not overwrite manual edits.")
    assets = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", source)))
    tables = sorted(set(re.findall(r"\\input\{([^}]+)\}", source)))
    records = []
    for relative in [*assets, *tables, "references.bib"]:
        original = PAPER / relative
        if not original.exists():
            raise FileNotFoundError(original)
        for target in (WORK, SUBMISSION):
            copied = target / relative
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, copied)
        records.append({"path": relative, "sha256": digest(original)})
    for target in (WORK, SUBMISSION):
        shutil.copy2(TEMPLATE / "sn-jnl.cls", target / "sn-jnl.cls")
        shutil.copy2(TEMPLATE / "bst/sn-nature.bst", target / "sn-nature.bst")
    style_path = WORK / "sn-nature.bst"
    style = style_path.read_text()
    start = style.index("FUNCTION {inproceedings}")
    end = style.index("FUNCTION {conference}", start)
    conference = style[start:end].replace(
        "format.editors output\nadd.blank",
        "format.editors output\n% Local fix: output leaves no string for add.blank.",
    ).replace('format.in.ed.booktitle "booktitle" output.check',
              'format.booktitle "booktitle" output.check')
    write(style_path, style[:start] + conference + style[end:])
    # Store an immutable migration snapshot, not a link to the live manuscript.
    shutil.copy2(source_path, ROOT / "source_snapshot.tex")
    body = source.split(r"\maketitle", 1)[1].split(r"\end{document}", 1)[0]
    body = body.replace(r"\bibliography{references}", "")
    body = body.replace(r"\clearpage", "")
    body = body.replace(r"\begin{figure}[p]", r"\begin{figure}[tbp]")
    body = body.replace(
        r"\resizebox{\linewidth}{!}{\input{tables/generated/table_02_model_auc_summary.tex}}",
        r"\footnotesize\setlength{\tabcolsep}{3pt}\input{tables/generated/table_02_model_auc_summary.tex}",
    )
    body = body.replace(
        r"\input{tables/generated/table_03_shortcut_summary.tex}",
        r"\footnotesize\setlength{\tabcolsep}{3pt}\input{tables/generated/table_03_shortcut_summary.tex}",
    )
    body = body.replace(r"\begin{edfigure}", r"\begin{figure}[p]")
    body = body.replace(r"\end{edfigure}", r"\end{figure}")
    body = body.replace(
        r"\section*{Extended Data}",
        "\\clearpage\n\\begingroup\n"
        "\\setcounter{figure}{0}\n"
        "\\renewcommand{\\figurename}{Extended Data Fig.}\n"
        "\\renewcommand{\\theHfigure}{extended.\\arabic{figure}}\n"
                    "\\section*{Extended Data}",
    ) + "\n\\endgroup\n"
    # Preserve vector assets while leaving room for captions on float pages.
    body = body.replace(
        r"\includegraphics[width=\linewidth]",
        r"\includegraphics[width=\linewidth,height=0.64\textheight,keepaspectratio]",
    )
    blocks = re.split(r"(?=\\section\*\{)", body)
    sections = []
    for block in blocks:
        if not block.strip():
            continue
        heading = re.match(r"\\section\*\{([^}]+)\}", block)
        name = re.sub(r"[^a-z0-9]+", "_", heading.group(1).lower()).strip("_")
        filename = f"sections/{len(sections)+1:02d}_{name}.tex"
        if name == "extended_data":
            block = block.replace(r"\section*{Extended Data}", "", 1)
            block = block.replace(
                r"\begin{figure}[p]",
                "\\begin{figure}[p]\n\\section*{Extended Data}", 1,
            )
            block = "\\clearpage\n\\begingroup\n\\setcounter{figure}{0}\n" \
                    "\\renewcommand{\\figurename}{Extended Data Fig.}\n" \
                    "\\renewcommand{\\theHfigure}{extended.\\arabic{figure}}\n" + block
        # The group opener belongs to Extended Data, not Competing interests.
        if name == "competing_interests":
            block = block.split(r"\begingroup", 1)[0].replace(r"\clearpage", "")
        write(WORK / filename, block.strip() + "\n")
        sections.append({"name": name, "path": filename})
    document = PREAMBLE + frontmatter(source) + "\n"
    for section in sections:
        if section["name"] == "extended_data":
            document += "\\bibliography{references}\n"
        document += "\\input{" + section["path"] + "}\n"
    document += "\\end{document}\n"
    write(WORK / "main.tex", document)
    write(ROOT / "migration_manifest.json", json.dumps({
        "source": str(source_path.relative_to(PAPER.parent)),
        "source_sha256": digest(source_path), "assets": records,
        "sections": sections, "policy": "Format-only snapshot; no scientific prose edits",
    }, indent=2) + "\n")


def export() -> None:
    manifest = json.loads((ROOT / "migration_manifest.json").read_text())
    main = (WORK / "main.tex").read_text()
    bbl = (WORK / "main.bbl").read_text()
    heading = main.split(r"\input{sections/", 1)[0]
    figures = []
    before_methods = []
    after_methods = []
    extended = ""
    in_methods = False
    for section in manifest["sections"]:
        text = (WORK / section["path"]).read_text()
        if section["name"] == "extended_data":
            extended = text
            continue
        if section["name"] == "methods":
            in_methods = True
        def move_figure(match: re.Match) -> str:
            figures.append(match.group())
            return ""
        text = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", move_figure, text, flags=re.S)
        text = re.sub(
            r"\\input\{([^}]+)\}",
            lambda m: (WORK / m.group(1)).read_text(), text,
        )
        (after_methods if in_methods else before_methods).append(text)
    submission = heading + "\n".join(before_methods) + "\n" + bbl + "\n"
    submission += "\n".join(after_methods)
    for i, figure in enumerate(figures):
        figure = re.sub(r"\\begin\{figure\}\[[^]]*\]", r"\\begin{figure}[p]", figure)
        if i == 0:
            figure = figure.replace(
                r"\begin{figure}[p]",
                "\\begin{figure}[p]\n\\section*{Figures and legends}", 1,
            )
        figures[i] = figure
    submission += "\n\\clearpage\n" + "\n".join(figures)
    submission += "\n" + extended + "\n\\end{document}\n"
    assert not re.search(r"\\(?:input|include|bibliography)\{", submission)
    write(SUBMISSION / "manuscript.tex", submission)
    # BibTeX source stays in working only; submitted references are inline.
    for relative in [*re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", submission),
                     "sn-jnl.cls", "sn-nature.bst"]:
        shutil.copy2(WORK / relative, SUBMISSION / relative)
    files = ["manuscript.tex", "sn-jnl.cls", "sn-nature.bst"] + sorted(set(
        re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", submission)
    ))
    with zipfile.ZipFile(ROOT / "submission_source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            archive.write(SUBMISSION / relative, relative)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "export"])
    args = parser.parse_args()
    (prepare if args.action == "prepare" else export)()
