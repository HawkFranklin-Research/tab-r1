# Springer Nature format migration

Independent snapshot of the revised reusability report. The live manuscript,
bibliography, figures and experimental artifacts remain untouched. No models or
statistical analyses are run by this workflow.

## Files

- working/main.tex: Springer Nature document using pdflatex,sn-nature.
- working/sections/: ten editable section files, including Extended Data.
- working/main.pdf: reading copy with figures near the relevant text.
- working/figures/: five main figures and six Extended Data figures, copied.
- working/tables/: three copied table source files.
- working/references.bib: unchanged snapshot of the current bibliography.
- submission/manuscript.tex: flattened text and tables with inline references;
  main figures and legends appear at the end, followed by Extended Data.
- submission/manuscript.pdf: compilation preview of the flattened source.
- submission_source.zip: one manuscript, the class, bibliography style and eleven
  figure PDFs; no logs, independent sections or external bibliography required.
- source_snapshot.tex and migration_manifest.json: provenance and SHA256s.
- template/: unmodified December 2024 version 3.1 package.

## Rebuild

Edit the independent working files, then run:

~~~bash
bash paper/springer_nature/build.sh
~~~

The prepare action was used for the initial snapshot only and refuses to
overwrite an existing working manuscript. Export uses the current working section
files and generated bibliography. Edit references in working/references.bib,
not the generated inline references in submission/manuscript.tex.

To refresh the Springer version from the latest HawkFranklin manuscript, run
the sync action before building:

~~~bash
python paper/springer_nature/migrate_report.py sync
bash paper/springer_nature/build.sh
~~~

Sync preserves the preceding Springer working/submission files, snapshot and
manifest in archive/pre_sync_*.zip before replacing the generated copies.
The current snapshot includes the fold-aware contrast, corrected estimates,
estimator disclosure, revised Fig. 5, Extended Data Fig. 3E and C-index Fig. 6.

The preservation checker is deliberately strict for this format-only migration.
It compares body paragraphs, citation groups, labels and asset hashes with the
snapshot. Intentional scientific edits need a reviewed new baseline.

## Formatting Changes

Replaced HawkFranklin-specific front matter with Springer author commands,
retaining vatsal1@hawkfranklin.in. Removed branding, custom font styling and
report-number metadata. Scientific prose, numbers, captions, citation keys and
NA entries are preserved, including existing wording inconsistencies outside
this format-only task.

Main and Extended Data figures have separate numbering and PDF link targets.
Image dimensions preserve aspect ratio. Two wide tables use smaller typography
instead of nested resizing, which conflicted with table-caption handling.
The submission copy puts references before Methods and figures/legends at the end.

The supplied sn-nature.bst has two conference-entry stack defects with our
bibliography. Only the working copy was patched: an orphan add.blank was removed,
and conference titles use format.booktitle instead of the broken helper. The
vendor original remains in template/. Export copies the patched working style.
Bibliography metadata was not changed.

## Scope

These are format-migrated drafts, not certification of scientific or journal
policy compliance. Existing TODOs and unfinished checklists remain. Templates
describe review layouts, not final published layouts. Check the journal's current
article-type and submission instructions before upload.
