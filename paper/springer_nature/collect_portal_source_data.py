"""Write portal uploads for the tables and the figure source data of submission/manuscript.tex.

portal/tables/       Table_<n>_<name>.csv and .xlsx, one per table in the manuscript (values as generated, full precision)
portal/source_data/  Source_Data_Fig_<n>.xlsx and Source_Data_Extended_Data_Fig_<n>.xlsx: a "README" sheet, then one sheet per
                     data file plotted in that figure (copied unchanged from the paper's source-data CSVs)

Only figures and tables that appear in the manuscript are exported. Nothing is recomputed; rerun after regenerating any CSV.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
PAPER = ROOT.parent
SUBMISSION = ROOT / "submission"
REUSE = "figures/reusability/source_data"
LEGACY = "figures/source_data"
TABLES = "tables/generated"

# Data files behind each figure, keyed by the figure file the manuscript includes (see the generators:
# analysis/reusability/build_reusability_figures.py for figures/reusability, analysis/build_manuscript_assets.py for figures/manuscript).
FIGURE_DATA = {
    "fig1_roadmap_and_design": [f"{TABLES}/table_01_cohort_characteristics.csv"],
    "fig2_reproduction": [f"{REUSE}/reproduction_auc.csv", f"{REUSE}/fig2_baseline_auc.csv", f"{REUSE}/fig2_generation_auc.csv"],
    "fig3_within_cancer": [f"{REUSE}/fig3a_task_auc.csv", f"{REUSE}/paired_delta_vs_rf.csv", f"{REUSE}/within_cancer_ranks.csv",
                           f"{REUSE}/within_cancer_friedman.csv"],
    "fig4_pooling_and_controls": [f"{REUSE}/fig4a_scope_means.csv", f"{REUSE}/fig4b_controls.csv",
                                  f"{LEGACY}/figure_04_permutation_distributions.csv", f"{LEGACY}/figure_04_cohort_separability.csv",
                                  f"{TABLES}/table_03_shortcut_summary.csv"],
    "fig5_within_cancer_effect": [f"{REUSE}/foldaware_pooling_summary.csv", f"{REUSE}/foldaware_pooling_did.csv",
                                  f"{REUSE}/foldaware_pooling_per_cancer.csv"],
    "figure_01_cohort_and_design": [f"{LEGACY}/figure_01_cohort_flow.csv", f"{LEGACY}/figure_01_class_counts.csv",
                                    f"{LEGACY}/figure_01_modality_composition.csv"],
    "figure_02_within_cancer_performance": [f"{LEGACY}/figure_02_within_cancer_model_summary.csv",
                                            f"{LEGACY}/figure_02_within_cancer_auc_heatmap.csv", f"{LEGACY}/figure_02_paired_auc_delta.csv",
                                            f"{LEGACY}/figure_02_pr_auc_lift.csv", f"{LEGACY}/figure_02_runtime_pareto.csv"],
    # Extended Data variant: panels a-d as in the original figure 3, panel e compares the two estimators of the pooling change
    "figure_03_pooling_effect_ed": [f"{LEGACY}/figure_03_pooling_shift.csv", f"{LEGACY}/figure_03_roc_curves.csv",
                                    f"{LEGACY}/figure_03_pr_curves.csv", f"{LEGACY}/figure_03_pooled_auc_heatmap.csv",
                                    f"{REUSE}/legacy_patient_averaged/pooling_did.csv", f"{REUSE}/foldaware_pooling_did.csv"],
    "figure_04_shortcut_stress_tests": [f"{LEGACY}/figure_04_shortcut_controls.csv", f"{LEGACY}/figure_04_cohort_separability.csv",
                                        f"{LEGACY}/figure_04_heldout_diagnostics.csv", f"{LEGACY}/figure_04_permutation_distributions.csv",
                                        f"{LEGACY}/figure_04_model_minus_shortcut.csv"],
    "figure_05_probabilistic_and_compute": [f"{LEGACY}/figure_05_calibration_curves.csv",
                                            f"{LEGACY}/figure_05_pooled_probabilistic_metrics.csv",
                                            f"{LEGACY}/figure_05_feature_modalities_across_folds.csv", f"{LEGACY}/figure_05_runtime.csv"],
    "ed_cindex_eligible_patients": [f"{REUSE}/cindex_eligible_summary.csv"],
}


def sheet_name(path: str, used: set[str]) -> str:
    stem = Path(path).stem
    if "legacy_patient_averaged" in path:
        stem = "earlier_estimator_" + stem
    name = re.sub(r"^(figure_0\d_|fig\d[a-z]?_)", "", stem)[:31]
    while name in used:
        name = name[:29] + f"_{len(used)}"
    used.add(name)
    return name


def printed_table(path: Path) -> pd.DataFrame:
    """The table exactly as typeset: header row before \\midrule, rows up to \\bottomrule, values as printed (NA kept)."""
    body = path.read_text().split(r"\toprule", 1)[1].split(r"\bottomrule", 1)[0]
    header, rows = body.split(r"\midrule", 1)
    split = lambda line: [cell.strip() for cell in line.strip().removesuffix(r"\\").split("&")]
    lines = [split(line) for line in rows.strip().splitlines() if line.strip()]
    def cell(text: str):
        """Numbers become numbers in the spreadsheet (1206 stays an integer, 0.707 keeps its printed digits); NA and text stay text."""
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return text

    text = pd.DataFrame(lines, columns=split(header))
    return text, text.map(cell)


def figures_in_order(tex: str) -> list[tuple[str, int, str, str]]:
    main, extended = tex.split(r"\section*{Extended Data}", 1)
    main = main.split(r"\section*{Figures and legends}", 1)[1]
    out = []
    for kind, block in (("Fig", main), ("Extended_Data_Fig", extended)):
        for n, match in enumerate(re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}.*?\\caption\{\\textbf\{([^}]*)\}",
                                              block, re.S), start=1):
            out.append((kind, n, Path(match.group(1)).stem, match.group(2).rstrip(".")))
    return out


def main() -> None:
    tex = (SUBMISSION / "manuscript.tex").read_text()
    out_tables, out_source = ROOT / "portal" / "tables", ROOT / "portal" / "source_data"
    for folder in (out_tables, out_source):
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*"):
            old.unlink()

    # the submission flattens tables inline, so the table list comes from the main manuscript; the counts must agree
    tables = re.findall(r"\\input\{tables/generated/(table_0(\d)_[a-z_]+)\.tex\}", (PAPER / "reusability_report.tex").read_text())
    if len(tables) != tex.count(r"\begin{table"):
        raise SystemExit(f"{len(tables)} tables in reusability_report.tex but {tex.count(chr(92) + 'begin{table')} in the submission")
    for stem, number in tables:
        printed, values = printed_table(PAPER / TABLES / f"{stem}.tex")
        full = pd.read_csv(PAPER / TABLES / f"{stem}.csv")
        if len(printed) != len(full):
            raise SystemExit(f"{stem}: {len(printed)} printed rows but {len(full)} rows in the CSV")
        name = f"Table_{number}_{stem.split('_', 2)[2]}"
        printed.to_csv(out_tables / f"{name}.csv", index=False)          # character for character as typeset
        with pd.ExcelWriter(out_tables / f"{name}.xlsx", engine="xlsxwriter") as writer:
            sheet = f"Table {number}"
            values.to_excel(writer, index=False, sheet_name=sheet)
            book, ws = writer.book, writer.sheets[sheet]
            for j, column in enumerate(printed.columns):               # show the printed number of decimals (0.550, not 0.55)
                decimals = printed[column].str.extract(r"^-?\d+\.(\d+)$")[0].dropna().str.len()
                fmt = book.add_format({"num_format": "0." + "0" * int(decimals.max())} if len(decimals) else {})
                ws.set_column(j, j, max(12, len(column) + 2), fmt)
            full.to_excel(writer, index=False, sheet_name="full_precision")
        print(f"{name}: {printed.shape[0]} rows x {printed.shape[1]} columns (as printed; full precision in the .xlsx)")

    for kind, number, stem, title in figures_in_order(tex):
        files = FIGURE_DATA[stem]
        label = f"{kind.replace('_', ' ')}. {number}"
        target = out_source / f"Source_Data_{kind}_{number}.xlsx"
        used: set[str] = {"README"}
        readme = [{"item": "Figure", "value": f"{label}: {title}"}, {"item": "Figure file", "value": f"{stem}.pdf"}]
        with pd.ExcelWriter(target) as writer:
            sheets = []
            for path in files:
                frame = pd.read_csv(PAPER / path)
                name = sheet_name(path, used)
                sheets.append((name, frame))
                readme.append({"item": f"sheet '{name}'", "value": f"{frame.shape[0]} rows; from paper/{path}"})
            pd.DataFrame(readme).to_excel(writer, sheet_name="README", index=False)
            for name, frame in sheets:
                frame.to_excel(writer, sheet_name=name, index=False)
        print(f"{target.name:<40} {len(files)} sheet(s)  {title}")


if __name__ == "__main__":
    main()
