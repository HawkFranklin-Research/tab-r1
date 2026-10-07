"""EXPLORATORY (2026-10-03). Read-only on saved predictions; fits no model.

Question: c-5 stores most features twice, as source-specific blocks (one TCGA-only, one CPTAC-only, each missing for the
other source). The paper's harmoniser keeps one copy, so CPTAC patients can have all-zero feature vectors. Does the
within-cancer ROC AUC change when CPTAC test patients are excluded? Run from the repository root.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ.setdefault(v,"12")
import sys, warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
PAPER=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PAPER/"analysis"))
from within_cancer_pooling_contrast import prediction_path
m=pd.read_csv(PAPER/"figures/source_data/model_fold_metrics.csv"); m=m[m.roc_auc.notna()&(m.scope=="per_cancer")]
def auc(y,p): return roc_auc_score(y,p) if len(np.unique(y))==2 and len(y)>=4 else np.nan
rows=[]
for r in m.itertuples():
    p=prediction_path(pd.Series(dict(scope=r.scope,endpoint=r.endpoint,cancer=r.cancer,repeat=r.repeat,fold=r.fold,model_name=r.model_name,artifact_source=r.artifact_source)))
    if not p.exists(): continue
    d=pd.read_csv(p,usecols=["sample_id","y_true","probability"]); tc=d.sample_id.str.startswith("TCGA:").to_numpy()
    rows.append(dict(endpoint=r.endpoint,cancer=r.cancer,model=r.model_name,n=len(d),n_cptac=int((~tc).sum()),
        pos_cptac=int(d.y_true[~tc].sum()),auc_all=auc(d.y_true,d.probability),auc_tcga=auc(d.y_true[tc],d.probability[tc])))
x=pd.DataFrame(rows); x.to_csv(Path(__file__).parent/"output/source_block_check.csv",index=False)
fm=x.model.str.startswith("tab")
g=x.groupby(["endpoint","cancer"]).agg(test_n=("n","mean"),cptac_n=("n_cptac","mean"),cptac_pos=("pos_cptac","mean"),auc_all=("auc_all","mean"),auc_tcga_only=("auc_tcga","mean")).round(3)
g["diff"]=(g.auc_tcga_only-g.auc_all).round(3)
pd.set_option("display.width",200); print(g.to_string())
mm=x.groupby(["endpoint"]).agg(auc_all=("auc_all","mean"),auc_tcga=("auc_tcga","mean")).round(4); mm["diff"]=mm.auc_tcga-mm.auc_all; print("\nmean over all cancers/models:"); print(mm.to_string())
for fam,sel in [("foundation",fm),("others",~fm)]:
    y=x[sel]; print(fam,"auc_all %.4f auc_tcga_only %.4f diff %+.4f"%(y.auc_all.mean(),y.auc_tcga.mean(),y.auc_tcga.mean()-y.auc_all.mean()))
