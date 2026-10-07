"""Synthetic stand-ins for the c-5 train_ready layout, the clinical master table and the METABRIC cBioPortal files.

They reproduce the structural features the pipeline must handle: duplicated source-specific feature blocks (TCGA-only and
CPTAC-only copies of the same id, each missing for the other source), a missing mask (1 = missing), clinical columns named
differently per source, an ESCA cohort without CPTAC, and survival times that depend on two RNA features and on the cancer.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

CANCERS = ["BRCA", "ESCA", "HNSCC", "LSCC", "LUAD"]
MODALITIES = ["rnaseq_gene", "cnv_log2", "cnv_gistic", "methylation_gene", "mutation_binary"]
GENES = [f"G{i:03d}" for i in range(40)]
SIGNAL = ("rnaseq_gene::GENE:G000", "rnaseq_gene::GENE:G001")


def _feature_ids() -> list[str]:
    return [f"{m}::GENE:{g}" for m in MODALITIES for g in GENES]


def make_c5(root: Path, n_per_cancer: int = 70, seed: int = 0) -> dict:
    """Write a miniature c-5 tree under ``root``; return the true signal for assertions."""
    rng = np.random.default_rng(seed)
    ids = _feature_ids()
    tr = root / "gpt" / "processed" / "train_ready"
    master_rows = []
    truth = {}
    for ci, cancer in enumerate(CANCERS):
        n = n_per_cancer if cancer != "ESCA" else n_per_cancer // 2 + 10
        n_cptac = 0 if cancer == "ESCA" else n // 5
        source = np.array(["CPTAC"] * n_cptac + ["TCGA"] * (n - n_cptac))
        latent = rng.normal(size=(n, len(ids))).astype(np.float32)
        mut = [i for i, f in enumerate(ids) if f.startswith("mutation_binary")]
        latent[:, mut] = (rng.random((n, len(mut))) < 0.2).astype(np.float32)
        lin = 0.9 * latent[:, ids.index(SIGNAL[0])] - 0.7 * latent[:, ids.index(SIGNAL[1])] + 0.3 * ci
        t_event = rng.exponential(1200 * np.exp(-lin))
        t_cens = np.where(source == "CPTAC", rng.uniform(100, 700, n), rng.uniform(300, 4000, n))
        time = np.minimum(t_event, t_cens).round(1) + 1
        event = (t_event <= t_cens).astype(float)
        truth[cancer] = {"lin": lin}
        # columns: CPTAC block (all ids), TCGA block (all ids), then two clinical features
        cols = ids + ids + ["clinical::AGE", "clinical::Stage_Stage II"]
        X = np.zeros((n, len(cols)), np.float32)
        M = np.zeros((n, len(cols)), np.uint8)
        cpt = source == "CPTAC"
        X[cpt, :len(ids)] = latent[cpt]
        M[~cpt, :len(ids)] = 1                    # CPTAC block missing for TCGA rows
        X[~cpt, len(ids):2 * len(ids)] = latent[~cpt]
        M[cpt, len(ids):2 * len(ids)] = 1         # TCGA block missing for CPTAC rows
        meth = [len(ids) + i for i, f in enumerate(ids) if f.startswith("methylation_gene")]
        M[np.flatnonzero(~cpt)[:2][:, None], np.array(meth)[None, :3]] = 1   # sprinkle a few genuinely missing cells
        X[M == 1] = 0.0
        X[:, -2] = rng.normal(60, 10, n)
        if cancer == "ESCA":                       # ESCA: no CPTAC; drop the CPTAC block entirely (single copies)
            keep = list(range(len(ids), 2 * len(ids))) + [len(cols) - 2, len(cols) - 1]
            cols = [cols[i] for i in keep]
            X, M = X[:, keep], M[:, keep]
        d = tr / cancer / "core"
        d.mkdir(parents=True, exist_ok=True)
        sp.save_npz(d / "X.npz", sp.csr_matrix(X))
        sp.save_npz(d / "missing_mask.npz", sp.csr_matrix(M))
        pd.DataFrame({"feature_index": range(len(cols)), "feature_id": cols}).to_csv(d / "feature_index.csv", index=False)
        pids = [f"{s}:{cancer}:P{j:04d}" for j, s in enumerate(source)]
        pd.DataFrame({"sample_id": pids, "patient_id": pids, "cohort_x": source, "cancer_x": cancer, "tissue": "tumor",
                      "cohort_y": source, "cancer_y": cancer, "OS_days": time, "OS_event": event,
                      "PFS_days": time, "PFS_event": event, "DSS_event": event, "DSS_days": time}).to_csv(d / "sample_index.csv", index=False)
        stages = np.array(["I", "II", "III", "IV"])[rng.integers(0, 4, n)]
        for j, pid in enumerate(pids):
            if source[j] == "CPTAC":
                master_rows.append({"patient_id": pid, "cohort": "CPTAC", "cancer": cancer, "Age": str(int(rng.integers(30, 85))),
                                    "Sex": "Female" if cancer == "BRCA" else "Male", "Stage": f"Stage {stages[j]}",
                                    "Path_Stage_pT": f"pT{rng.integers(1, 5)}", "Path_Stage_pN": f"pN{rng.integers(0, 4)}"})
            else:
                master_rows.append({"patient_id": pid, "cohort": "TCGA", "cancer": cancer, "AGE": float(rng.integers(30, 85)),
                                    "SEX": "Female" if cancer == "BRCA" else "Male", "AJCC_PATHOLOGIC_TUMOR_STAGE": f"STAGE {stages[j]}A",
                                    "PATH_T_STAGE": f"T{rng.integers(1, 5)}C", "PATH_N_STAGE": "NX" if j % 9 == 0 else f"N{rng.integers(0, 4)}"})
    cl = root / "gpt" / "processed" / "clinical"
    cl.mkdir(parents=True, exist_ok=True)
    master = pd.DataFrame(master_rows)
    for col in ("Age", "Sex", "Stage", "Path_Stage_pT", "Path_Stage_pN", "SEX", "AJCC_PATHOLOGIC_TUMOR_STAGE", "PATH_T_STAGE", "PATH_N_STAGE"):
        if col in master:
            master[col] = master[col].astype("string")
    master.to_parquet(cl / "patient_master.parquet", index=False)
    return truth


def make_metabric(root: Path, n: int = 150, seed: int = 1) -> None:
    rng = np.random.default_rng(seed)
    root.mkdir(parents=True, exist_ok=True)
    pids = [f"MB-{i:04d}" for i in range(n)]
    expr = rng.normal(8, 1, size=(len(GENES) + 3, n))
    lin = 0.9 * (expr[0] - 8) - 0.7 * (expr[1] - 8)
    t_event = rng.exponential(60 * np.exp(-lin))
    t_cens = rng.uniform(20, 250, n)
    months = np.minimum(t_event, t_cens).round(2) + 0.1
    status = np.where(t_event <= t_cens, "1:DECEASED", "0:LIVING")
    header = "#Patient Identifier\tx\n#desc\tx\n#STRING\tx\n#1\tx\n"
    pat = pd.DataFrame({"PATIENT_ID": pids, "AGE_AT_DIAGNOSIS": rng.uniform(30, 85, n).round(2), "OS_MONTHS": months, "OS_STATUS": status})
    smp = pd.DataFrame({"PATIENT_ID": pids, "SAMPLE_ID": pids, "TUMOR_STAGE": rng.choice(["0", "1", "2", "3", "4", ""], n)})
    with open(root / "data_clinical_patient.txt", "w") as f:
        f.write(header)
        pat.to_csv(f, sep="\t", index=False)
    with open(root / "data_clinical_sample.txt", "w") as f:
        f.write(header)
        smp.to_csv(f, sep="\t", index=False)
    symbols = GENES + ["G000", "EXTRA1", "EXTRA2"]            # one duplicated symbol and two not in TCGA
    frame = pd.DataFrame(expr, columns=pids)
    frame.insert(0, "Entrez_Gene_Id", range(len(symbols)))
    frame.insert(0, "Hugo_Symbol", symbols)
    frame.to_csv(root / "data_mrna_illumina_microarray.txt", sep="\t", index=False)


def synthetic_config(tmp: Path, c5: Path, metabric: Path) -> dict:
    """Config overrides for a small, fast, non-smoke run on the synthetic data (no foundation models)."""
    models = ["km", "null_cancer", "coxph", "coxnet", "rsf", "gbsa", "pseudo:ridge:rmst+h3+h5", "pseudo:random_forest:rmst+h3+h5",
              "ipcw:logistic", "ipcw:random_forest"]
    return {
        "paths": {"c5_root": str(c5), "metabric_root": str(metabric), "output_root": str(tmp / "outputs")},
        "folds": {"n_repeats": 2, "n_splits": 3, "seed": 7},
        "features": {"k": 12, "min_observed": {"tcga": 0.9, "all": 0.8}, "min_nonzero": 3, "preload": True},
        "questions": {"q1": {"contexts": ["A", "P"], "arms": ["omics"]}, "q2": {"contexts": ["B", "C", "D"], "arms": ["omics"]},
                      "q3": {"contexts": ["A"], "arms": ["clinical", "omics_clinical"]}, "q4": {"enabled": True}},
        "model_sets": {"q1": models, "q2": ["coxnet", "rsf", "pseudo:random_forest:rmst"], "q3": ["coxph", "coxnet", "pseudo:random_forest:rmst"],
                       "q4": ["km", "coxph", "coxnet", "pseudo:random_forest:rmst+h3+h5"]},
        "models": {"rsf": {"n_estimators": 30, "min_samples_leaf": 5, "max_features": "sqrt"},
                   "gbsa": {"n_estimators": 30, "learning_rate": 0.1, "max_depth": 2, "subsample": 0.8},
                   "regressor_random_forest": {"n_estimators": 30, "min_samples_leaf": 3, "max_features": 0.5},
                   "classifier_random_forest": {"n_estimators": 30, "min_samples_leaf": 3, "max_features": "sqrt"},
                   "coxnet": {"l1_ratio": 0.5, "n_alphas": 8, "alpha_min_ratio": 0.05, "inner_folds": 3, "max_iter": 20000}},
        "external": {"n_seeds": 1, "max_followup_days": 3650, "bootstrap": 50},
        "compute": {"threads": 2, "memory_gb": 0, "device": "cpu", "allow_cpu_large": True, "seed": 3},
        "cohorts": ["tcga", "all"],
    }
