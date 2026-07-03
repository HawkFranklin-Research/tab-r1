# tab-r1

Research workspace for TabPFN evaluation, reproduction, packaging, and cancer/multiomics benchmark exploration.

## What this repo tracks

- The high-level workspace structure and lightweight project notes.
- The `ev-tabpfn` package source under `package/`.
- Compact benchmark reports, plots, configs, and manifests from `results-s2/` and `results-satya/`.
- Pointers to embedded upstream repositories through Git submodules.

## Embedded repositories

This workspace references several nested repositories:

- `Evaluate-TABPFN`: HawkFranklin Research evaluation pipeline.
- `Accurate_Prediction_on_Small_Dataset_with_TabPFN_Research`: original intern/Satya reproduction work.
- `TabPFN`, `tabpfn-client`, `tabpfn-extensions`: Prior Labs repositories.
- `tabpfn_3`: Hugging Face model repository.

Clone with submodules when needed:

```bash
git clone --recurse-submodules git@github.com:HawkFranklin-Research/tab-r1.git
```

If already cloned:

```bash
git submodule update --init --recursive
```

## Large artifacts

Large raw datasets, model checkpoints, generated run folders, AutoGluon model payloads, archives, and PDFs are intentionally ignored by Git. Those should move to a dedicated storage layer such as Hugging Face Datasets or another artifact store.

## Important local result locations

- `results-s2/results/`: compact benchmark reports and plots from a Phase 1-4 run.
- `results-satya/results/`: compact reports from the Satya recreation run.
- `Evaluate-TABPFN/pfn3-test/reports/`: TabPFN generation-comparison report.
- `package/`: PyPI-style `ev-tabpfn` package source.
