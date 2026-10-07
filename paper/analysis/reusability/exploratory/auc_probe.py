"""EXPLORATORY (2026-10-03). Read-only on saved predictions; fits no model. Not used for any figure or table in the manuscript.
See NOTES_estimator_check.md. Run from the repo root.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(v,"12")
import sys, warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
PAPER=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PAPER/"analysis"))
from within_cancer_pooling_contrast import prediction_path, load_patient_probabilities
m=pd.read_csv(PAPER/"figures/source_data/model_fold_metrics.csv"); m=m[m.roc_auc.notna()]
def auc(y,p):
    return roc_auc_score(y,p) if len(np.unique(y))==2 and len(y)>=4 else np.nan
rows=[]
for r in m[m.scope=="pooled"].itertuples():
    p=prediction_path(pd.Series(dict(scope=r.scope,endpoint=r.endpoint,cancer=r.cancer,repeat=r.repeat,fold=r.fold,model_name=r.model_name,artifact_source=r.artifact_source)))
    if not p.exists(): continue
    pr=pd.read_csv(p,usecols=["cancer_type","y_true","probability"])
    for cn,g in pr.groupby("cancer_type"):
        rows.append(dict(endpoint=r.endpoint,model=r.model_name,cancer=cn,fold=(r.repeat,r.fold),auc=auc(g.y_true,g.probability),n=len(g)))
d=pd.DataFrame(rows)
fold_pooled=d.groupby(["endpoint","model","cancer"]).auc.mean().groupby(["endpoint","model"]).mean()   # fold-level within-cancer AUC of pooled model
pc=m[m.scope=="per_cancer"].groupby(["endpoint","model_name","cancer"]).roc_auc.mean().groupby(["endpoint","model_name"]).mean()  # fold-level within-cancer AUC of cancer-specific model
pa=pd.read_csv(PAPER/"figures/source_data/figure_03_within_cancer_pooling_summary.csv").set_index(["endpoint","model_name"])
out=pd.DataFrame({"specific_foldlevel":pc,"pooled_foldlevel":fold_pooled.rename_axis(["endpoint","model_name"])}).dropna()
out["delta_foldlevel"]=out.pooled_foldlevel-out.specific_foldlevel
out["specific_patientavg"]=pa.mean_auc_cancer_specific; out["pooled_patientavg"]=pa.mean_auc_pooled
out["delta_patientavg"]=out.pooled_patientavg-out.specific_patientavg
pd.set_option("display.width",200)
for e in ["os_5yr","extreme_os","os_3yr"]:
    print("\n==",e); print(out.loc[e].round(3).to_string())
fm=[x for x in out.index.get_level_values(1).unique() if x.startswith("tab")]; tr=["random_forest","catboost","xgboost","lightgbm"]
for e in ["os_3yr","os_5yr","extreme_os"]:
    o=out.loc[e]
    print(f"{e}: FM mean delta fold-level {o.loc[[x for x in fm if x in o.index]].delta_foldlevel.mean():+.3f} vs patient-avg {o.loc[[x for x in fm if x in o.index]].delta_patientavg.mean():+.3f};  trees fold-level {o.loc[tr].delta_foldlevel.mean():+.3f} vs patient-avg {o.loc[tr].delta_patientavg.mean():+.3f}")
