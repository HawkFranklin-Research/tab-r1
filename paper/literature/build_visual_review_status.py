#!/usr/bin/env python3
"""Build an honest per-source status index for the second-pass figure review."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> None:
    sources = rows(ROOT / "manifest.tsv")
    captions: dict[str, int] = {}
    for item in rows(ROOT / "visual_inventory.tsv"):
        source_id = item["source_id"]
        captions[source_id] = captions.get(source_id, 0) + 1

    output = ROOT / "visual_review_status.tsv"
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(
            ["source_id", "title", "pdf_status", "text_status", "caption_inventory_rows", "visual_review_status", "note_path"]
        )
        for source in sources:
            source_id = source["source_id"]
            note = ROOT / "notes" / f"{source_id}_visual_audit.md"
            pdf = ROOT / "pdfs" / f"{source_id}.pdf"
            text = ROOT / "txt" / f"{source_id}.txt"
            if source_id == "L31":
                pdf_status = "wrong source quarantined; correct PDF unavailable"
                text_status = "wrong-source extraction quarantined"
                review_status = "not_reviewed_correct_source_unavailable"
            elif source_id in {"L27", "L28"}:
                pdf_status = "not_applicable_official_software_source"
                text_status = "official documentation archived"
                review_status = "official_source_text_archived; no paper figures"
            else:
                pdf_status = "downloaded" if pdf.exists() else "no_pdf"
                text_status = "extracted" if text.exists() else "no_local_full_text"
                if note.exists():
                    review_status = "partial_manual_review; not exhaustive"
                elif pdf.exists():
                    review_status = "not_reviewed"
                else:
                    review_status = "not_reviewed_no_pdf"
            writer.writerow(
                [source_id, source["title"], pdf_status, text_status, captions.get(source_id, 0), review_status,
                 f"notes/{note.name}" if note.exists() else "NA"]
            )
    print(f"Wrote {output.relative_to(ROOT)} for {len(sources)} sources")


if __name__ == "__main__":
    main()
