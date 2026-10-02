#!/usr/bin/env python3
"""Fetch public full-text PDFs listed in the literature manifest."""

from __future__ import annotations

import concurrent.futures
import csv
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "pdfs"
MANIFEST = ROOT / "manifest.tsv"
USER_AGENT = "Research-paper-literature-collection/1.0 (mailto:vatsal1@hawkfranklin.in)"

# Public publisher, repository, or conference PDF endpoints. Entries that need
# authentication, subscription access, or an unverified location are omitted.
PDF_URLS = {
    "L01": "https://link.springer.com/content/pdf/10.1186/s12911-026-03654-3.pdf",
    "L02": "https://academic.oup.com/bib/article-pdf/22/3/bbaa167/38657332/bbaa167.pdf",
    "L03": "https://link.springer.com/content/pdf/10.1186/s12911-024-02642-9.pdf",
    "L04": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10162996/pdf/main.pdf",
    "L05": "https://academic.oup.com/aje/article-pdf/172/8/971/770544/kwq223.pdf",
    "L06": "https://dspace.library.uu.nl/bitstream/handle/1874/449595/Statistics_in_Medicine_-_2023_-_Jong_-_Propensity_based_standardization_to_enhance_the_validation_and_interpretation_of.pdf?sequence=1",
    "L06": "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/sim.9817",
    "L07": "https://academic.oup.com/jamia/article-pdf/28/1/155/35885573/ocaa242.pdf",
    "L08": "https://arxiv.org/pdf/2406.16484",
    "L09": "https://openaccess.thecvf.com/content_CVPR_2019/papers/Wang_Characterizing_and_Avoiding_Negative_Transfer_CVPR_2019_paper.pdf",
    "L10": "https://arxiv.org/pdf/2004.07780",
    "L11": "https://www.cell.com/cell/pdf/S0092-8674(18)30302-7.pdf",
    "L12": "https://www.bmj.com/content/bmj/353/bmj.i3140.full.pdf",
    "L13": "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0100335&type=printable",
    "L14": "https://academic.oup.com/bioinformatics/article-pdf/30/12/i105/48926888/bioinformatics_30_12_i105.pdf",
    "L16": "https://arxiv.org/pdf/2511.08667",
    "L17": "https://arxiv.org/pdf/2605.13986",
    "L18": "https://www.nature.com/articles/s41586-024-08328-6.pdf",
    "L19": "https://raw.githubusercontent.com/mlresearch/v267/main/assets/qu25d/qu25d.pdf",
    "L20": "https://arxiv.org/pdf/2506.16791",
    "L21": "https://arxiv.org/pdf/2207.08815",
    "L22": "https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf",
    "L23": "https://arxiv.org/pdf/1603.02754",
    "L24": "https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf",
    "L25": "https://proceedings.neurips.cc/paper_files/paper/2018/file/14491b756b3a51daac41c24863285549-Paper.pdf",
    "L26": "https://arxiv.org/pdf/2003.06505",
    "L29": "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0118432&type=printable",
    "L30": "https://bmcmedicine.biomedcentral.com/counter/pdf/10.1186/s12916-019-1466-7.pdf",
    "L31": "https://www.osti.gov/servlets/purl/1886020",
    "L32": "https://www.nature.com/articles/nature11412.pdf",
    "L33": "https://www.nature.com/articles/nature20805.pdf",
    "L34": "https://www.nature.com/articles/nature14129.pdf",
    "L35": "https://www.nature.com/articles/nature11404.pdf",
    "L36": "https://www.nature.com/articles/nature13385.pdf",
    "L37": "https://www.cell.com/cell/pdf/S0092-8674(18)30229-0.pdf",
    "L38": "https://www.cell.com/cell/pdf/S0092-8674(23)00780-8.pdf",
    "L39": "https://www.bmj.com/content/bmj/385/bmj-2023-078378.full.pdf",
    "L40": "https://www.bmj.com/content/bmj/388/bmj-2024-082505.full.pdf",
}


def fetch(item: tuple[str, str]) -> tuple[str, str, str, int]:
    source_id, url = item
    target = DEST / f"{source_id}.pdf"
    if target.exists() and target.read_bytes().startswith(b"%PDF-"):
        return source_id, "already_present", url, target.stat().st_size
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            content_type = response.headers.get("Content-Type", "")
            payload = response.read()
            final_url = response.geturl()
        if not payload.startswith(b"%PDF-"):
            return source_id, "not_pdf", final_url, len(payload)
        target.write_bytes(payload)
        return source_id, "downloaded", final_url, len(payload)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return source_id, f"unavailable:{type(exc).__name__}", url, 0


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        records = {row["source_id"]: row for row in csv.DictReader(stream, delimiter="\t")}
    items = [(source_id, url) for source_id, url in PDF_URLS.items()]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch, items):
            results.append(result)
            print("\t".join(map(str, result)), flush=True)

    log = ROOT / "download_status.tsv"
    with log.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["source_id", "title", "status", "bytes", "resolved_url"])
        for source_id, status, resolved_url, size in results:
            writer.writerow([source_id, records[source_id]["title"], status, size, resolved_url])
    time.sleep(0.1)
    print(f"Downloaded {sum(status == 'downloaded' for _, status, _, _ in results)} / {len(results)} PDFs; status table: {log}")


if __name__ == "__main__":
    main()
