#!/usr/bin/env python3
"""Archive public TabFM documentation separately from research papers."""

from __future__ import annotations

import html.parser
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "official"
SOURCES = {
    "L27_tabfm_google_blog.txt": (
        "https://research.google/blog/introducing-tabfm-a-zero-shot-foundation-model-for-tabular-data/",
        "Google Research TabFM announcement",
        "html",
    ),
    "L28_tabfm_repository_readme.txt": (
        "https://raw.githubusercontent.com/google-research/tabfm/main/README.md",
        "Google Research TabFM repository README",
        "text",
    ),
}


class VisibleText(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden += 1
        elif tag in {"p", "div", "h1", "h2", "h3", "li", "br"} and self.hidden == 0:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.hidden:
            self.hidden -= 1
        elif tag in {"p", "div", "h1", "h2", "h3", "li"} and self.hidden == 0:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.hidden == 0 and data.strip():
            self.parts.append(data.strip())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, (url, title, kind) in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "Literature-source-archive/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", "replace")
            resolved = response.geturl()
        if kind == "html":
            parser = VisibleText()
            parser.feed(raw)
            content = "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())
        else:
            content = raw
        header = f"SOURCE: {title}\nURL: {resolved}\nARCHIVED: 2026-10-02\n\n"
        target = OUT / filename
        target.write_text(header + content + "\n", encoding="utf-8")
        print(filename, target.stat().st_size)


if __name__ == "__main__":
    main()
