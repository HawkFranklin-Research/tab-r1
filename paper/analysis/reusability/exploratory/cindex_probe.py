"""EXPLORATORY (2026-10-03). Read-only on saved predictions; fits no model. Not used for any figure or table in the manuscript.
See NOTES_estimator_check.md. Run from the repo root.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(v,"12")
import sys, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd
from sksurv.metrics import concordance_index_censored
REPO=Path(__file__).resolve().parents[4]; PAPER=REPO/"paper"
sys.path.insert(0,str(PAPER/"analysis"))
from within_cancer_pooling_contrast import prediction_path
FOLDS=PAPER/"analysis/generated_folds"
m=pd.read_csv(PAPER/"figures/source_data/model_fold_metrics.csv")
m=m[m.roc_auc.notna()]
def c(time,event,risk):
    event=event.astype(bool)
    if event.sum()<2 or (~event).sum()<1 or len(time)<5: return np.nan
    try: return concordance_index_censored(event,time,risk)[0]
    except Exception: return np.nan
rows=[]; surv={}
for r in m.itertuples():
    p=prediction_path(pd.Series(r._asdict()|{"scope":r.scope,"endpoint":r.endpoint,"cancer":r.cancer,"repeat":r.repeat,"fold":r.fold,"model_name":r.model_name,"artifact_source":r.artifact_source}))
    if not p.exists(): continue
    meta=pd.read_csv(FOLDS/r.scope/r.endpoint/r.cancer/f"repeat_{int(r.repeat):02d}_fold_{int(r.fold):02d}"/"test_metadata.csv",usecols=["sample_id","patient_id","OS_days","OS_event","cancer_type"])
    pr=pd.read_csv(p,usecols=["sample_id","probability"]).merge(meta,on="sample_id")
    for pid,t,e in zip(pr.patient_id,pr.OS_days,pr.OS_event): surv[pid]=(t,e)
    overall=c(pr.OS_days.to_numpy(float),pr.OS_event.to_numpy(float),pr.probability.to_numpy())
    within=np.nan
    if r.scope=="pooled":
        vals=[c(g.OS_days.to_numpy(float),g.OS_event.to_numpy(float),g.probability.to_numpy()) for _,g in pr.groupby("cancer_type")]
        within=np.nanmean(vals)
    rows.append(dict(scope=r.scope,endpoint=r.endpoint,cancer=r.cancer,model=r.model_name,roc_auc=r.roc_auc,c_all=overall,c_within=within))
d=pd.DataFrame(rows); d.to_csv("paper/analysis/reusability/exploratory/output/fold_c.csv",index=False)
print("runs scored:",len(d))
pc=d[d.scope=="per_cancer"].groupby(["endpoint","model"])[["roc_auc","c_all"]].mean()
po=d[d.scope=="pooled"].groupby(["endpoint","model"])[["roc_auc","c_all","c_within"]].mean()
from scipy.stats import spearmanr
for e in ["os_3yr","os_5yr","extreme_os"]:
    a=pc.loc[e]; b=po.loc[e]
    print(f"\n== {e}: per-cancer  Spearman(rank AUC, rank C) over models = {spearmanr(a.roc_auc,a.c_all)[0]:.2f}; pooled = {spearmanr(b.roc_auc,b.c_all)[0]:.2f}")
    print(pd.concat([a.add_prefix('pc_'),b.add_prefix('po_')],axis=1).round(3).to_string())
