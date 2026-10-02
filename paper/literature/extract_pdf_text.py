#!/usr/bin/env python3
"""Extract searchable, page-separated text from collected literature PDFs."""

from __future__ import annotations

import csv
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "pdfs"
TEXT_DIR = ROOT / "txt"
MANIFEST = ROOT / "manifest.tsv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="Extract only this source ID; may be repeated")
    args = parser.parse_args()
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        records = {row["source_id"]: row for row in csv.DictReader(stream, delimiter="\t")}

    status_path = ROOT / "extraction_status.tsv"
    prior = {}
    if args.only and status_path.exists():
        with status_path.open(newline="", encoding="utf-8") as stream:
            prior = {row["source_id"]: [row["source_id"], row["pdf_pages"], row["status"], row["text_path"]]
                     for row in csv.DictReader(stream, delimiter="\t")}
    results = prior
    pdfs = sorted(PDF_DIR.glob("L*.pdf"))
    if args.only:
        selected = set(args.only)
        pdfs = [pdf for pdf in pdfs if pdf.stem in selected]
    for pdf in pdfs:
        source_id = pdf.stem
        record = records.get(source_id)
        if not record:
            results[source_id] = [source_id, "", "orphan_pdf", ""]
            continue
        info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
        pages = next((line.split(":", 1)[1].strip() for line in info.splitlines() if line.startswith("Pages:")), "unknown")
        extracted = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        target = TEXT_DIR / f"{source_id}.txt"
        header = (
            f"SOURCE ID: {source_id}\nTITLE: {record['title']}\nYEAR: {record['year']}\n"
            f"DOI: {record['doi']}\nPDF: ../pdfs/{pdf.name}\nPAGES: {pages}\n"
            "EXTRACTION: pdftotext -layout. Page breaks are form feeds. Check equations, tables, and figures against the PDF during visual audit.\n"
            + "=" * 78 + "\n\n"
        )
        target.write_text(header + extracted, encoding="utf-8")
        results[source_id] = [source_id, pages, "pdf_text_extracted", str(target.relative_to(ROOT))]

    with status_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["source_id", "pdf_pages", "status", "text_path"])
        writer.writerows(results[key] for key in sorted(results))
    print(f"Updated {len(pdfs)} PDF text(s); status index contains {len(results)} sources")


if __name__ == "__main__":
    main()
