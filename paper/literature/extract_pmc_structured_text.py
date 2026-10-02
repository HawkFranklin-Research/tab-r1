#!/usr/bin/env python3
"""Extract open PMC full text, equations, tables, and figure captions as text."""

from __future__ import annotations

import csv
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.tsv"
PMC_IDS = {
    "L01": "PMC13599330", "L02": "PMC8138887", "L03": "PMC11370316",
    "L04": "PMC10162996", "L07": "PMC7810439", "L12": "PMC4916924",
    "L14": "PMC4058929", "L15": "PMC124442", "L18": "PMC11711098",
    "L11": "PMC5957518", "L37": "PMC6066282",
    "L39": "PMC11019967", "L40": "PMC11931409",
}


def clean_text(element: ET.Element) -> str:
    return " ".join(" ".join(element.itertext()).split())


def render_table(table: ET.Element) -> str:
    lines = []
    for row in table.iter():
        if row.tag.rsplit("}", 1)[-1] != "tr":
            continue
        cells = []
        for cell in list(row):
            if cell.tag.rsplit("}", 1)[-1] in {"td", "th"}:
                cells.append(clean_text(cell))
        if cells:
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        records = {row["source_id"]: row for row in csv.DictReader(stream, delimiter="\t")}
    statuses = []
    for source_id, pmcid in PMC_IDS.items():
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
        request = urllib.request.Request(url, headers={"User-Agent": "Literature-text-extraction/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                xml_bytes = response.read()
            root = ET.fromstring(xml_bytes)
            chunks = []
            for node in root.iter():
                tag = node.tag.rsplit("}", 1)[-1]
                if tag in {"title", "p", "abstract"} and clean_text(node):
                    chunks.append(clean_text(node))
                elif tag == "disp-formula":
                    chunks.append("[DISPLAY EQUATION] " + clean_text(node))
                elif tag == "table-wrap":
                    label = next((clean_text(child) for child in node if child.tag.endswith("label")), "")
                    caption = next((clean_text(child) for child in node if child.tag.endswith("caption")), "")
                    table = next((child for child in node.iter() if child.tag.endswith("table")), None)
                    block = f"[TABLE {label}] {caption}\n{render_table(table)}" if table is not None else f"[TABLE {label}] {caption}"
                    chunks.append(block)
                elif tag == "fig":
                    label = next((clean_text(child) for child in node if child.tag.endswith("label")), "")
                    caption = next((clean_text(child) for child in node if child.tag.endswith("caption")), "")
                    graphics = [g.attrib.get("{http://www.w3.org/1999/xlink}href", "") for g in node.iter() if g.tag.endswith("graphic")]
                    chunks.append(f"[FIGURE {label}; IMAGE REVIEW REQUIRED] {caption} [image refs: {', '.join(graphics)}]")
            title = records[source_id]["title"]
            header = f"SOURCE ID: {source_id}\nTITLE: {title}\nPMC: {pmcid}\nSOURCE: Europe PMC full-text XML\n"
            out = ROOT / "txt" / f"{source_id}.txt"
            out.write_text(header + "\n\n" + "\n\n".join(chunks) + "\n", encoding="utf-8")
            statuses.append([source_id, pmcid, "xml_text_extracted", str(out.relative_to(ROOT)), len(xml_bytes)])
            print(source_id, "extracted", len(xml_bytes), flush=True)
        except (urllib.error.URLError, TimeoutError, OSError, ET.ParseError) as exc:
            statuses.append([source_id, pmcid, f"unavailable:{type(exc).__name__}", "", 0])
            print(source_id, "unavailable", type(exc).__name__, flush=True)
        time.sleep(0.2)
    with (ROOT / "pmc_extraction_status.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["source_id", "pmcid", "status", "text_path", "xml_bytes"])
        writer.writerows(statuses)


if __name__ == "__main__":
    main()
