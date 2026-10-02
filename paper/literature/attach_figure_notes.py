#!/usr/bin/env python3
"""Add reviewed figure-value notes to each source's extracted text file."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "\n\n" + "=" * 78 + "\nVISUAL FIGURE VALUE AUDIT\n" + "=" * 78 + "\n\n"


def main() -> None:
    attached = 0
    for note_path in sorted((ROOT / "notes").glob("L*_visual_audit.md")):
        source_id = note_path.name.split("_", 1)[0]
        text_path = ROOT / "txt" / f"{source_id}.txt"
        if not text_path.exists():
            continue
        current = text_path.read_text(encoding="utf-8")
        note = note_path.read_text(encoding="utf-8")
        if "VISUAL FIGURE VALUE AUDIT" in current:
            current = current.split(MARKER, 1)[0]
        text_path.write_text(current.rstrip() + MARKER + note, encoding="utf-8")
        attached += 1
    print(f"Attached visual audit blocks to {attached} extracted texts")


if __name__ == "__main__":
    main()
