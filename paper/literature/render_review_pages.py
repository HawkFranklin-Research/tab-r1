#!/usr/bin/env python3
"""Render figure/table pages from collected PDFs into temporary review sheets."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "pdfs"
OUT = Path(__file__).resolve().parents[2] / "tmp" / "pdfs" / "literature-review"
CAPTION = re.compile(r"^\s*(?:Figure|Fig\.?|Table)\s+(?:[A-Z]\.?|S?\d+(?:\.\d+)*)[.:|\s]", re.I)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = []
    for pdf_path in sorted(PDF_DIR.glob("L*.pdf")):
        pdf = fitz.open(pdf_path)
        pages = []
        for page_no, page in enumerate(pdf, 1):
            text = page.get_text("text")
            hits = [line.strip() for line in text.splitlines() if CAPTION.match(line)]
            if hits:
                pages.append((page_no, hits))
                for hit in hits:
                    inventory.append([pdf_path.stem, page_no, hit])
        rendered = []
        for page_no, hits in pages:
            page = pdf[page_no - 1]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image.thumbnail((960, 1240))
            canvas = Image.new("RGB", (980, 1280), "white")
            canvas.paste(image, ((980 - image.width) // 2, 28))
            ImageDraw.Draw(canvas).text((18, 8), f"{pdf_path.stem} | page {page_no}", fill="black")
            rendered.append(canvas)
        for start in range(0, len(rendered), 2):
            pair = rendered[start:start + 2]
            sheet = Image.new("RGB", (1960, 1280), "#e5e5e5")
            for idx, page_image in enumerate(pair):
                sheet.paste(page_image, (idx * 980, 0))
            out = OUT / f"{pdf_path.stem}_sheet_{start // 2 + 1:02d}.jpg"
            sheet.save(out, quality=92)
    with (ROOT / "visual_inventory.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["source_id", "pdf_page", "caption_line"])
        writer.writerows(inventory)
    print(f"Rendered {len(inventory)} caption lines from {len(list(PDF_DIR.glob('L*.pdf')))} PDFs into {OUT}")


if __name__ == "__main__":
    main()
