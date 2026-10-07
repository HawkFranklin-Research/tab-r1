"""EXPLORATORY (2026-10-03). Read-only on saved predictions; fits no model. Not used for any figure or table in the manuscript.
See NOTES_estimator_check.md. Run from the repo root.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(v,"12")
import sys, warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score
PAPER=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PAPER/"analysis"))
from within_cancer_pooling_contrast import prediction_path
m=pd.read_csv(PAPER/"figures/source_data/model_fold_metrics.csv"); m=m[m.roc_auc.notna()]
frames=[]
for r in m.itertuples():
    p=prediction_path(pd.Series(dict(scope=r.scope,endpoint=r.endpoint,cancer=r.cancer,repeat=r.repeat,fold=r.fold,model_name=r.model_name,artifact_source=r.artifact_source)))
    if not p.exists(): continue
    pr=pd.read_csv(p,usecols=["patient_id","cancer_type","y_true","probability"])
    pr["rank_score"]=pr.groupby("cancer_type").probability.transform(lambda s:(rankdata(s)-0.5)/len(s))  # percentile within fold & cancer
    pr["scope"]=r.scope; pr["endpoint"]=r.endpoint; pr["model"]=r.model_name
    frames.append(pr[["scope","endpoint","model","cancer_type","patient_id","y_true","probability","rank_score"]])
d=pd.concat(frames,ignore_index=True)
agg=d.groupby(["scope","endpoint","model","cancer_type","patient_id","y_true"],as_index=False)[["probability","rank_score"]].mean()
res=[]
for (e,mo,c),g in agg.groupby(["endpoint","model","cancer_type"]):
    w=g.pivot_table(index=["patient_id","y_true"],columns="scope",values=["probability","rank_score"]).dropna()
    if w.empty or "pooled" not in w["probability"].columns: continue
    y=w.index.get_level_values("y_true").to_numpy(int)
    if len(np.unique(y))<2: continue
    f=lambda col,sc: roc_auc_score(y,w[(col,sc)].to_numpy())
    res.append(dict(endpoint=e,model=mo,cancer=c,
        d_prob=f("probability","pooled")-f("probability","per_cancer"),
        d_rank=f("rank_score","pooled")-f("rank_score","per_cancer")))
r=pd.DataFrame(res).groupby(["endpoint","model"])[["d_prob","d_rank"]].mean()
fm=lambda x:x.startswith("tab"); tr=["random_forest","catboost","xgboost","lightgbm"]
pd.set_option("display.width",160)
for e in ["os_3yr","os_5yr","extreme_os"]:
    o=r.loc[e]; print("\n==",e); print(o.round(3).to_string())
    F=[x for x in o.index if fm(x)]
    print(f"  FM mean: raw-prob {o.loc[F].d_prob.mean():+.3f} | within-fold-rank {o.loc[F].d_rank.mean():+.3f}    trees: raw-prob {o.loc[tr].d_prob.mean():+.3f} | within-fold-rank {o.loc[tr].d_rank.mean():+.3f}")
