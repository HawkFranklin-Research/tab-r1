#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
(cd working && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex)
python migrate_report.py export
(cd submission && latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex)
python verify_migration.py
