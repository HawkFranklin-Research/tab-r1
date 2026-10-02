"""Curated source evidence and retrieval inventories; no experiment execution.

Numeric passage inventories are retrieval aids, not completed visual audits.
Keep the original text unchanged so all line locators remain reproducible.
"""
from __future__ import annotations

import csv
import hashlib
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
REPORT = REPO / "paper/reusability_report.tex"
SOURCES = list(csv.DictReader((ROOT / "manifest.tsv").open(), delimiter="\t"))
META = {s["source_id"]: s for s in SOURCES}
ROWS = []

CONTEXT = {
"L01": "Eight datasets / twelve binary tasks. Fig.1b, personally inspected PDF p3: FOSP colorectal registry EACH task n=91,795 p=72: 1-year survival positive72.0%; 3-year27.2%; 5-year20.4%; cancer-death39.7%; overall-death55.9%. Arasteh: amyloidosis n=2,142 p=1,877 positive50.0%; oesophageal cancer14,597/121/2.5%; hereditary hearing loss1,778/144/24.1%; metastatic disease788/15/28.3%. SEER: HCC-to-lung metastasis62,869/82/6.5%; osteosarcoma4,097/73/33.8%; renal-cell carcinoma139,528/78/34.3%. These are dataset totals, not split counts. Survival-positive coding differs from our death-positive coding. TabPFN v2.5 versus12 learners, HPO50iterations;100 bootstrap iterations; numeric -9 / categorical Missing imputation. TabPFN A10040GB versus CPU baselines. Per-split n remains NR until original split protocols reconciled.",
"L02": "18 TCGA cohorts; censored overall survival; clinical/CNV/miRNA/mutation/RNA, methylation omitted. Full Table2 n/p/events/block sizes below. Event-stratified outer10x5CV for11 datasets <92MB,5x5CV for7 >112MB; inner10fold or OOB method-specific. Thirteen learners including Kaplan-Meier and clinical Cox references; SGL omitted principal comparison for compute. Uno C-index and integrated Brier score (IBS), not ROC AUC. Across-dataset t-based95%CIs, not patient-level uncertainty.",
"L03": "14 TCGA cohorts; five omics blocks RNA/miRNA/methylation/mutation/CNV plus clinical;31 nonempty omics combinations x5methods=155 configurations. All cohort n/p/events/block sizes Table1 below. Clinical included/prioritised throughout. Train-fold RF importance selects <=2,500 features/block. Harrell C-index and IBS for censored OS. Modality combination is NOT pooling distinct cancer cohorts.",
"L04": "17 TCGA cohorts with seven modalities: clinical, expression, protein, CNV, methylation, mutation, miRNA. Per-cohort n/p in TableS1, not available in main extraction: NR, do not borrow L02 counts. Twelve models:8neural/4statistical. Clinical+expression versus all7, optional train-only PCA; separate1/3/5 Gaussian-noise blocks each10,000features and artificial true-survival-time predictor experiment. Outer5repeats x5folds; inner5fold; NN10%training validation,100epochs/patience10. Antolini C/IBS; parentheses STANDARD ERRORS. Dataset-mean paired Wilcoxon/Holm in specified families.",
"L06": "DVT diagnosis,13cross-sectional studies,n=10,002/events1,864. Development1,295=289events+1,006non-events(22%); validation8,707=1,575+7,132(18%) in12 studies, prevalence5%-39%. Eight logistic models with increasing predictors. Binary AUC case-mix standardisation using pairwise propensity weights;5,000 weighted bootstrap draws; REML/Hartung-Knapp meta-analysis and prediction intervals. Per-validation-study n in supplement NR. Simulations separate from real diagnostic counts.",
"L07": "Systematic methodological review:36articles;24/36 derived-predictor approaches; three method categories/eight strategies. Cross-sectional/longitudinal routine-care observation, not structurally absent omics assays. No pooled patient n, common benchmark or aggregate AUC effect.",
"L08": "Three settings: Gaussian simulated50covariates, lambda=.7/.3; semi-synthetic outcome on50 complete LBIDD covariates (1995 US infant-mortality records). EACH model100,000train/10,000validation/10,000independenttest;10reruns. MCAR, nonmonotone MAR, Gaussian self-masking MNAR, MAR-Y; source50%missingness -> target25% or0%, compared no-shift equivalents. Regression MSE, not prediction of real infant-death labels. Grid neural width/depth/rate/decay;1,000epochs/batch100/patience12. Table1 lists50variables, not50datasets.",
"L09": "Visual transfer: digits SVHN~73K->MNIST70K/10classes (USPS named but not main task); Office-31 total4,652/31classes, Webcam->DSLR,Amazon->DSLR,DSLR->Amazon; Office-Home~15,500/65classes, Art/Clipart/Product->RealWorld; VisDA additional synthetic-to-real task (per-domain n pending). Source all labelled; target50%training/50%testing; labelled fractions0/10/30/50%; Table2=10%,max3/class; perturbations0/.3/.7/.9. Eight transfer algorithms; accuracy%, NOT ROC AUC.",
"L10": "Shortcut-learning perspective, image/text examples; no one clinical cohort or common cancer AUC. Distinguishes benchmark success from intended generalisation. Numbers quoted from other studies require original-source attribution.",
"L11": "TCGA PanCancer11,286 tumours/33types with>=1assay. Aneuploidy10,522/10clusters; methylation10,814/3,139CpGs/25clusters; mRNA10,165/25clusters>=40samples; miRNA10,170/15clusters; RPPA7,858/32types/10clusters (LAML absent). Integrative iCluster28subtypes. Overlapping assay subsets, not additive cohorts. Per-cancer supplement counts NR. Unsupervised molecular taxonomy, not survival AUC.",
"L12": "Distinct examples: DVT12studies,n=10,014, per-study153-1,768, events1,897(19%); QRISK2 validation364practices (patient n NR in cited passage). Not identical to L06's13-study10,002 population. Random-effects performance meta-analysis; cluster/subgroup validation; internal-external leave-one-study-out proposal.",
"L13": "PETACC-3 background expression688patients x61,528features,E-MTAB-990. Semi-simulated80train/600validation balancedgroups; two training batches, group-batch allocation50/75/95/100%; null0DE versus alternative~1%DE; batch affects50%features;9settings x10replicates. Independent validation balanced/no batch. ComBat/nestedCV; batch removal beforeCV was examined, NOT an endorsement of our pipeline. Classification error, not survival ROC.",
"L14": "Eight breast microarray studies, complete Table1 n/ER-positive/follow-up below. Actual analysis ER-positive only, not full Table1 n. Censored distant-metastasis-free survival; Affymetrix arrays; six methods; study-pair matrix versus diagonal4foldCV. Simulations1,000collections/8resampledstudies/150patients perstudy,PH-generated outcomes. Gonen-Heller concordance, not binary ROC.",
"L16": "TabPFN-2.5 developer report: designed50Krows/2Kfeatures, exploratory benchmarks100Krows; design capacity NOT CPU1K safeguard. TabArena-Lite<=10K/500features versus all<=100K/2K; classification/regression separate. Tuning60configs versus200baselines; AutoGluon1.4extreme4h. Separate internal<=50K/500features, wide500-2Kfeatures, RealCause causal tasks and43fine-tuning real tables (not synthetic pretraining). Individual benchmark subsets/data cells remain pending where no printed table.",
"L17": "TabPFN-3 developer report v2,28May2026: TabArena51datasets<=100Krows; Medium15datasets/135tasks at10K-100K. Separate13scaling datasets (9classification/4regression) <=1Mtrain/200features,8h tree tuning; many-class synthetic9datasets<=100classes; relational/time-series/tabular-text/causal tasks distinct. Local checkpoint versus API Plus/Thinking distinct; AutoGluon1.5extreme4h elsewhere. Native regimes1M/200,100K/2K,1K/20K, not CPU execution guard.",
"L18": "Original TabPFN v2:29classification AMLB/28regression AMLB+OpenML-CTR23,<=10Krows/500features/10classes. Full n/p census visually transcribed below, PDFpp20-21. Ten seeds,90%train/10%test; random-search inner5fold,30s-4h. Eight CPUcores plus RTX2080Ti forTabPFN, othersCPU. AUC/RMSE normalised within dataset, best1/worst0, NOT raw AUC. Five additional Kaggle tasks and auxiliary suites are separate. Source identifies v2, not every evaluated generation.",
"L19": "TALENT200classificationdatasets120binary/80multiclass; main evaluation excludes15TabPFNv2developmentdatasets. Main<=10class subset171:112binary/59multiclass;116small<=10K,53large>10K; separate12>10class. Up to500Krows/500features inference, synthetic pretrain60K. Fixed benchmark splits; ICL train-only while other models usevalidation;32estimator ensemble;accuracy/AUC/logloss/ranks. All per-dataset n/p not reproduced in report, benchmark metadata needed.",
"L20": "Archived TabArena-v0.1 Nov2025:1,053candidates->51datasets,16models,~25million instances. Every dataset N/d/C in TableB.2 below (full N,not train n; preserve printed feature-count convention). TabPFNv2-compatible33<=10Ktrain/500features/10classes; TabICLclassification subset differs. Default/tuned/tuned+ensemble; validation design varies;4hAutoGluon1.3reference. Archived version, not today's leaderboard.",
"L21": "45reference datasets; overlapping numerical classification15/regression18 and categorical classification7/regression14 panels. AppendixA.1 census below. Mediumtraincap10K;large50K;d/n<.1;dropmissing;balance top2classes;remove high-cardinality categorical features. ~400HPOiterations/model/dataset,15search-order shuffles,20,000compute-hours;CPUtrees/GPUneural. Predates modern TFMs, not high-dimensional p>>n omics.",
"L22": "RF original13small UCI+3large real+4synthetic datasets; every train/test/input/class count Table1 below; small fixedtest n not given. Feature randomisation pernode/ensemble voting; OOB, strength/correlation theory. Algorithm citation, not our sklearn settings or evidence trees immune to shortcuts.",
"L23": "Allstate10Mtrain/4,227features;Higgs10Mtrain/28features;YahooLTRC473K/700features officialsplit;Criteo1.7Bprocessedtrain/67features. Separate Higgs-1M500trees,Allstate-size subsets,distributed/out-of-core experiments. Depth8/shrinkage.1 unless specified;binaryAUC/rankingNDCG@10;Table2-4 below. Different hardware/version/budgets from ours.",
"L24": "Allstate12M/4,228features;FlightDelay10M/700;LETOR2M/136;KDD1019M/29Mfeatures;KDD12119M/54Mfeatures. BinaryAUC exceptLETORNDCG@10. GOSS/EFB. Table2seconds PER ITERATION,not totalfit;Table3+-uncertainty type needs Methods confirmation, not assumed95%CI. Sparse feature dimensionality, not patients.",
"L25": "Ninebinarytasks:Adult,Amazon,Click,Epsilon,Appetency,Churn,Internet,Upselling,Kick;80%train+tuning/20%test;all learners ordered targetstatistics. Ordered/Plain distinct. Logloss/zero-oneerror,notAUC;Table2 below. Per-task n/p supplementarySectionD pending;NR in mainTable2. Paper settings do not verify our default boosting mode.",
"L26": "AutoML39datasets+11Kaggle=50tasks;1h/4h primary and8hKaggle. Tenfold framework versus first-fold comparisons distinguished (expensiveGCP onlyfirstfold); Kaggleprivateleaderboard excepthousepricespublic. All11Kaggle n/p/metrics TableS1below;39dataset individual sizes need benchmarkmetadata. CPUAWSm5.2xlarge primary,largeKagglem5.24xlarge384GiB/96vCPU. Our180second modernpreset NOT original4hensemble.",
"L27": "Official Google announcement, not peer-reviewed technical report. Synthetic SCMpretrain hundreds ofmillions tables;row/columnattention,rowcompression,ICL. TabArena38classification+13regression,n700-150K. Developer claims not independent cancer validation. Archive2026-10-02 differs from evaluated commit.",
"L28": "OfficialREADME archived2026-10-02;v1.0.0,JAX/PyTorch,Python>=3.11;codeApache2.0,weights noncommercial/nonproduction. Mainbranch snapshot not exact evaluated commit. Four training rows in tutorial are toydata, not experimental evidence.",
"L29": "Binary metrics paper with simulated balanced/imbalanced examples and biological miRNA tasks. Confusion-matrix TP/FP/FN/TN;precision=TP/(TP+FP),recall=TP/(TP+FN);PR no-skill reference prevalence. Biological per-dataset test sizes require full Methods/Table1 review; do not substitute toycounts. No survival benchmark;AP andtrapezoidalPRAUC not automatically identical.",
"L30": "Calibration methodological paper;binary risk, ideal intercept0/slope1,flexiblecurves. IVF/QRISK2/NICEFramingham examples contextual/cited, not common new benchmark. No clinical n comparable to ours. Lowerlogloss/Brier alone not calibration or utility.",
"L32": "TCGAbreast825overall inabstract;Methods800assayed>=1platform atfreeze;466samples/463patients common5of6platforms;348patients common6of6includingRPPA. Multiple-platform taxonomy, not fixed-horizon prediction. Source counts not our eligibleBRCA. Old visualnote348 plus muchlarger subtype n mixes denominators.",
"L33": "TCGA164oesophagealcarcinomas; joint analyses359gastricadenocarcinomas and36additionalGE-junctionadenocarcinomas;113oesophagealproteomic. Histology subgroups distinct. Molecularprofiling,notheld-out survivalmodel. Not our downloadedESCA raw/eligible counts.",
"L34": "TCGA279HNSCCtumours,multiomics/HPVpositive-negative/anatomicsites. Profiling/outcomeassociations,not our endpoint eligibility or prospective prediction. No uniform modeltrain/testsplit.",
"L35": "TCGA178lungSQCC copy/exome/expression/methylation;19WGS;159miRNA. LUSC=ourLSCCartifact label;publication denominators not current cohort. Driver/pathway analysis,notprediction validation.",
"L36": "TCGA230untreatedLUADpatients,tumour/matchednormal,multiomics. Driver/profiling;oncogene-positive143/negative31 are not complete230 population. No survivalAUC comparison.",
"L39": "TRIPOD+AI reporting guidance:27mainitems/52subitems,regression/MLdevelopment/evaluation. Checklist,notpredictive metric. Compliance requires completed mapping.",
"L40": "PROBAST+AI2025:16development/18evaluation signallingquestions,fourdomains participants+datasources/predictors/outcome/analysis;applicabilityfirstthree. Original2019tool20questions differs. Not low-risk certification.",
}

TABLE_RANGES = {
"L02":[(175,199),(230,246),(304,327),(331,354)],"L03":[(160,183)],"L04":[(81,107),(149,168),(174,192),(200,218)],
"L06":[(414,438)],"L14":[(65,82)],"L20":[(2492,2556)],"L21":[(640,729)],
"L22":[(402,429)],"L23":[(575,587),(610,619)],"L24":[(407,433)],
"L25":[(491,510)],"L26":[(442,469),(755,778)],"L29":[(808,823)],
}

CONTEXT["L01"] += " Methods p9: 70/30 stratified train/test split, datasets >100,000 downsampled to100,000 (RCC effective cohort cap100,000, not Fig1's139,528). Training only resampled100times; held-out test fixed;HPO selected once then fixed. Arasteh predefined-split wording also appears, so exact reconciled split n remains pending; do not infer70/30 as all-original-protocol replication. Additional100negative-control cycles."
CONTEXT["L03"] += " Outer five-fold CV repeated five times WITHOUT censoring-indicator stratification (authors explicitly acknowledge this). Models RSF, blockForest, lasso, IPF-lasso, prioritylasso; no DL models. Dataset bootstrap gives rank uncertainty; neither25folds nor155configurations are independent datasets."
CONTEXT["L09"] += " VisDA source152Ksynthetic/target72Kreal,12categories; five random repeats of each transfer task. Reported '+/-' values not labelled95%CI here."
CONTEXT["L20"] += " TabICL-compatible36classification datasets <=100K/500features. CPUAWSM6i.2xlarge8cores;GPUL40S48GB/8AMDEPYCcores;32GBRAM/100GBdisk each run."
CONTEXT["L29"] = "Simulation:1,000positives/1,000negatives balanced versus1,000/10,000imbalanced;1,000simulation reruns,curve medians; illustrative plots250+250scores. Independent miRNA testT1=819positives/11,060negatives andT2=111/13,444. Five tools MiRFinder,miPred,RNAmicro,ProMiR,RNAfold;T1real miRNAsversusshuffledsequences;T2C.elegansRNAzfunctional candidates. Table5 fullROC/PR below. No clinicalsurvival; no common train/test benchmark with ours; PRcurveAUC not automatically ouraverageprecision."

# Personally inspected image-only source tables, PDF pp20-21; explicit name:n/p.
CONTEXT["L18"] += """
 Classification dataset:n/features: ada:4147/48; Australian:690/14; blood-transfusion-service-center:748/4; car:1728/6; churn:5000/20; cmc:1473/9; credit-g:1000/20; dna:3186/180; eucalyptus:736/19; first-order-theorem-proving:6118/51; GesturePhaseSegmentationProcessed:9873/32; jasmine:2984/144; kc1:2109/21; kr-vs-kp:3196/36; madeline:3140/259; mfeat-factors:2000/216; ozone-level-8hr:2534/72; pc4:1458/37; philippine:5832/308; phoneme:5404/5; qsar-biodeg:1055/41; Satellite:5100/36; segment:2310/16; steel-plates-fault:1941/27; sylvine:5124/20; vehicle:846/18; wilt:4839/5; wine-quality-white:4898/11; yeast:1484/8.
 Regression dataset:n/features: abalone:4177/8; airfoil_self_noise:1503/5; auction_verification:2043/7; boston:506/13; cars:804/17; colleges:7063/44; concrete_compressive_strength:1030/8; cpu_activity:8192/21; energy_efficiency:768/8; geographical_origin_of_music:1059/116; grid_stability:10000/12; house_prices_nominal:1460/79; kin8nm:8192/8; Mercedes_Benz_Greener_Manufacturing:4209/376; MIP-2016-regression:1090/144; Moneyball:1232/14; pumadyn32nh:8192/32; QSAR_fish_toxicity:908/6; quake:2178/3; SAT11-HAND-runtime-regression:4440/116; sensory:576/11; socmob:1156/5; space_ga:3107/6; student_performance:649/30; tecator:240/124; topo_2_1:8885/266; us_crime:1994/126; yprop_4_1:8885/251.
"""

def add(sid, finding, values, metric, section, anchor, use, support, limitation="", status="supported_text", mode="contextual"):
    ROWS.append(dict(source_id=sid,finding=finding,published_values=values,
        metric_definition=metric,report_section=section,sentence_anchor=anchor,
        proposed_use=use,support_search=support,limitations=limitation,
        verification_status=status,comparison_suitability=mode))

add("L01","Independent clinical evaluation finds inconsistent superiority","Better 2/12, below 10/12; differences generally within 0.02 AUROC; median runtime 5.53x best ML","Binary AUROC; hardware-confounded runtime","Introduction;Discussion","An independent clinical comparison","Retain; limit clinical-reusability verdict to actual inputs/endpoints","5.53","Different predictors/endpoints,budgets,GPU versusCPU.")
add("L01","All twelve rounded task AUROCs, inspected PDF","Literature/TabPFN/bestML: metastatic .94/.92/.94;hearingloss .76/.77/.77;oesophageal .98/.95/.96;amyloid .95/.92/.94;RCC .84/.86/.87;osteosarcoma .75/.80/.81;HCC .82/.83/.83;overall-death .87/.87/.88;cancer-death .86/.87/.87;5yr .89/.89/.90;3yr .86/.87/.88;1yr .85/.85/.87","Rounded printed AUROCs;CI endpoints NR","Discussion","Our verdict is that TabPFN","Use selected clinical examples contextually,not cross-paper ranking","Fig. 2","Literature values secondary;rounding hides differences;do not estimate CI endpoints.","supported_visual_PDF_p4")
add("L02","Clinical baseline can match molecular integration","Table4 clinicalCoxC=.618[.588,.648],IBS=.175[.156,.194];blockForestC=.620[.584,.656],IBS=.174[.153,.195];CoxBoostfavclinicalC=.618[.589,.646],IBS=.174[.156,.192]","UnoC/IBS;95%t-based dataset intervals","Introduction;Discussion","do not reliably improve","Support clinical-only comparator rationale,not absence of molecular biology","Table 4","SourceDiscussionIBS.172 conflicts Table4.174;retainTable4/flag;not ROC.")
add("L02","Compute and prioritisation differ by model","Meanruntime minutes blockForest80;CoxBoostfav13;CoxBoost14;ranger10;lasso8;ipflasso33;prioritylasso32;favpriority39;grridge28;glmboost12","Evaluation runtime,not clinical inference","Discussion;Methods","tree ensembles matched","Discuss budget and clinical-input asymmetry","80","SGL time table/prose units ambiguous;not oursCPU fit timing.")
add("L03","More modalities need not help censored survival prediction","31omics combinations x5methods=155 configurations,14cohorts","HarrellC/IBS;modality combination","Introduction;Discussion","Pooling lifts every capable model","Explain input heterogeneity separately from pooling cancers","31","Not evidence for the causal mechanism of our pooled ICL result.")
add("L03","Selection performed inside training folds","<=2,500features/block byRFimportance;500trees usual,10,000for verywide blocks","Feature-selection protocol","Methods","100 features","Contrast train-only choices,not same preprocessing","2,500","Our100variance features differ from supervised RFimportance.")
add("L04","Adding modalities can harm multiomics performance","BlockForestC.637(SE.0059)->.619(.0060),IBS.162(.0020)->.164(.0021);ElasticnetC.599(.0061)->.589(.0060);RSFC.601(.0055)->.575(.0059)","AntoliniC/IBS;STANDARD ERRORS","Discussion","survival prediction was difficult","Add integration/robustness context","Mean Antolini","Clinical variables present;no direct rawROC comparison.")
add("L04","Noise ablation and training-only dimensionality reduction","1/3/5noise blocks each10,000features;25outer test splits;17dataset-mean pairs;pairedWilcoxon/Holm","Artificial experiments and test unit","Discussion;Methods","The hypothesis is directly testable","Cite proposed ablation design;do not describe ours as executed","Gaussian noise","True-survival-time input is artificialinformativeness,not deployable prediction.")
add("L06","Case mix changes discrimination without necessarily invalidating coefficients","Model1AUC.70[.66,.74];model8.82[.80,.84];model1PI.55-.82->standardised.64-.72;tau.29->.08","Binaryc-statistic;95%CI versusPI","Discussion","pan-cancer scores","Add counterargument:pooledtarget legitimate,but not within-cancer question","0.55 to 0.82","DVTdiagnosis;our analysis does not implement propensity weighting.")
add("L06","Standardisation weights pairs and requires overlap","Eq8: weighted concordance sum I(pi+>pi-)wi+wi-/sumwi+wi-;5,000weighted bootstrap","StandardisedAUC method","Discussion;Methods","Scored within each cancer","Distinguish stratified scoring from reweighting","standardized c-statistic","Positivity required;method not our implemented estimand.",mode="methodological")
add("L07","Missingness may be legitimately informative","36articles;24/36 derived-predictor methods;3categories/8strategies","Review counts,not pooled effect","Discussion","That pattern mixes measured zeros","Add counterargument,care-process versus assay missingness","24 of 36","Does not identify our structural-zero mechanism.")
add("L08","Missingness-shift robustness depends on mechanism","50%->25%/0%;100Ktrain/10Kval/10Ktest;10reruns;50covariates","Regression MSE relative Bayes/complete-data references","Discussion","removing the zero fingerprint","Add deployment-shift context without claiming all missingness spurious","100, 000 samples","LBIDD outcomes artificial;unlabelled violin medians NR.")
add("L09","Negative transfer defined relative to target-only learning","Table2epsilon=.7,labelledtarget10%,<=3/class;target50/50train/test;0/10/30/50%label settings","Accuracy transfer gap,notROC","Discussion","pooled training lowered","Use conceptual analogy for paired within-cancer contrast","negative transfer gap","Vision adaptation != pooled tabular ICL;no causal attention evidence.")
add("L10","Shortcut framework is evaluation-dependent","No own aggregate clinical effect;conceptual cases","Benchmark versus intended generalisation","Introduction;Discussion","cohort identity","Retain framework;avoid proof/shared biology absence claims","shortcut","Does not establish attention mechanism.")
add("L11","Cell of origin structures molecular taxonomy","11,286tumours/33types;platform n10,522/10,814/10,165/10,170/7,858;28integrative subtypes","Unsupervised clusters,not survivalAUC","Introduction;Discussion","zero pattern identifies almost perfectly","Explain recoverable biological identity,not just technicalbatch","11,286","Shared cross-tissue subtypes exist;not survivalconfounding proof.")
add("L12","Average validation can hide between-site heterogeneity","DVT E/O1.02[.79,1.32],I2=97%,PI.38-2.72;c-statisticPI.64-.73;QRISK2C.83[.826,.833],I2=80.9%,PI.76-.88","E/Ocalibration,c-statistic;CI !=PI","Discussion","Its pooled pan-cancer scores","Add subgroup-reporting rationale","1.02","Illustrative different studies;not our frozen controls.")
add("L12","Internal-external validation checks setting-specific transport","Leaveoneofkstudiesout,kcycles;typicalIPDk<10;cluster-rich dataholdout>=20clusters","Validation recommendation","Discussion;Methods","held-out cancer","Separate historical diagnostic from completeexternal validation","internal-external cross validation","Citation cannot repair pooledfeaturepreselection.",mode="methodological")
add("L13","Batch-label confounding can bias CV without true gene signal","80train/600validation;61,528features;group-batch allocation50/75/95/100%;null0DE/~1%DE","Classificationerror/CVbias,semi-simulation","Introduction;Discussion","cohort structure","Retain bounded genomicconfounding citation","688 patients","Different split protocol and ComBat-beforeCV;not exact ours control.")
add("L14","Within-study CV need not predict cross-study ranking","SimulatedmeanCV~.65vsCSV~.55;CAL/MSKcross-studyC~.5;1,000collections","CensoredDMFSconcordance;source approximations","Introduction;Discussion","held-out","Add precedent without claimingours external TFMvalidation","close to 0.65","ER-positive breast;not raw binaryROC;approx remainsapprox.")
add("L16","TabPFN2.5 capacity and reported subset winrates","Designed50Krows/2Kfeatures;100%smallclassificationwinsvsdefaultXGB;87%largerclassification/85%regression","Benchmark winrates,not clinicalROC","Introduction;Methods","Later releases extended","Retain version citation;separate capacity fromCPUguard","87%","L17 retrospective100K versusL16designed50K scopes distinct.")
add("L16","Default,tuned and distilled models not interchangeable","60configsTFM/200baselines;4hAutoGluon1.4ensemble;MLP/TreeEns distillations","Elo/normalisedperformance/time","Reproducibility;Discussion","The margins were small","Narrow defaultCPUreproduction claim","60 random configs","Our checkpointnot RealTabPFN/distillation/4hAutoML.")
add("L17","Local v3 versus API Thinking claims","1M/200features;13scalingdatasets9class/4reg;Thinking>200Elooverall/420largestsubset;up to20xfasterv2.5","Elo and relative hardware timing","Introduction;Methods;Discussion","Later releases extended","Do not attribute API Thinking resultstolocalmodel","420 Elo","Developerclaim,differenthardware/budgets.")
add("L18","Original effect is a normalised benchmark advantage","Classificationdefault.939vsCatBoost.752(delta.187);tuned.952vs.822(delta.130);regressionnormalisedRMSE.923vs.872default,.968vs.875tuned","Best-worst normalisation;regression orientedhighbetter","Reproducibility","The central claim reproduced","Qualifydirectionalreproduction,not .877raw versus .939normalised","0.939","Our6vsoriginal29classification;one15%test vs10seeds10%test.")
add("L18","Original speed promise has hardware and budget conditions","Classification2.8s/regression4.8saverage versus4hbaselines;5,140x/3,000x reported speedup;>100Msynthetic tasks","Runtime and syntheticpretraining count","Introduction;Reproducibility;Methods","while taking seconds","Retain secondsclaim with hardware","2.8 s","8CPUcores plus2080Ti;not CPU universal latency.")
add("L18","Context attention does not prove nearest-row shortcut mechanism","12layers alternatingfeature/sampleattention;syntheticSCMprior;no task-specific weight fitting","Architecture","Discussion","training rows most similar","Qualify nearest-row/cohort-mean hypothesis explicitly","sample attention","No measuredattention or causalablation inours.",mode="methodological")
add("L19","Scalability rankings depend on subset","171<=10classes;116<=10K/53>10K;12>10classes separate;1.5xsmall/3-10xlargespeedup claims","Accuracy/AUC/logloss andGPUtime","Introduction;Discussion","different architecture","Optional backgroundonly;not evaluatedarm","171 datasets","200-corpusnot171main-subset;15developmentexcluded.")
add("L20","Validation,tuning and ensembles change comparative claims","51of1,053;16models;~25Minstances;33TFMv2-compatible","Elo/normalisedscore;archivev0.1","Reproducibility;Discussion","tuned tree ensembles","Do not callourdefault trees tuned;explain limitedbudget","33 datasets","Not equivalence evidence;fullNnottrainN.")
add("L21","Classical-tree benchmark excludes p>>n regime","45datasets;traincap10K/large50K;d/n<.1;~400HPO/15shuffles","Testaccuracy/R2normalised","Introduction","Tree ensembles","Retain classical benchmarkwithregimequalification","d/n ratio","Balancedlowdimensional data;predatesmodernTFMs.")
add("L22","RF ensemble randomisation","13small+3largereal+4synthetic;randompernodefeatureselection","OOB/generalisation error theory","Methods;Discussion","random feature subsets","Restrict RFdescription toRF,notallboosters","random selection of features","No evidence RFcausallyimmune tocohortshortcuts.",mode="methodological")
add("L23","Scalable regularised boosting","Higgs1M500trees:XGB AUC.8304/secpertree.6841;sklearn.8302/28.51;YahooNDCG.7892/secpertree.826","AUCversusNDCG;per-tree time","Methods","XGBoost","Retain algorithm only,notclinical effectiveness","0.8304","Physics/ranking/clicks differentpredictors/populations.",mode="methodological")
add("L24","GOSS/EFB reduce boosting costs","LightGBM sec/iterationAllstate.28,Flight.22,LETOR.31,KDD102.85,KDD1212.67;AUC.6093/.7846/.78732/.7051;LETORNDCG.5275","Per-iteration time;Table3uncertaintyneedsdefinition","Methods","LightGBM","Retain algorithm citation","0.78732","Sparsemillionsfeaturesnot our100featuredata.",mode="methodological")
add("L25","Ordered statistics address internal prediction shift","CatBoostTable2logloss/error:Adult.270/.127;Amazon.139/.044;Click.392/.156;Epsilon.265/.109;Appetency.072/.018;Churn.232/.072;Internet.209/.094;Upselling.166/.049;Kick.286/.095","Logloss/error,notAUC","Methods","CatBoost","Distinguish internal targetleakage from outerfeatureselection","Ordered TS","Orderedpaper mode maydifferfromourdefaultPlain.",mode="methodological")
add("L26","AutoML architecture and timebudget","39+11tasks;1h/4h/8h;primarybest23/39;99.3%Kagglecompetitors oneexample","1-AUC/logloss/competitionmetrics","Introduction;Methods;Discussion","AutoGluon","Cite architecture;describeour180sec presetfromconfig","23/39","2020paper notfullmodernrelease docs;privatecompetitionnotours.")
add("L27","TabFM hybrid synthetic ICL","HundredsofmillionsSCMtables;row/columnattention->compression->ICL;38classification+13regression,n700-150K","Developer architecture/benchmarkannouncement","Introduction;Methods;Discussion","TabFM applies the same","Retain official source,not fabricated technicalreport","Row compression","Cannot establish observed harmmechanism;numericchartsnotfullyaudited.",mode="methodological")
add("L28","Software source and weight license differ","Python>=3.11,JAX/PyTorch;codeApache2.0;weightsnoncommercial/nonproduction","Version/licensing as archived","Methods;Code availability","TabFM","Cite repo and evaluatedcommit separately","License notice","Mutablemain snapshotnot evaluatedcommit.",mode="methodological")
add("L29","PR interpretation depends on prevalence","PrecisionTP/(TP+FP);recallTP/(TP+FN);no-skillpositivefraction","PRversusROC;AP!=trapezoidalAUC","Methods;Discussion","PR AUC","Retain definition;stateouractualAP andeventprevalence","precision","Cannotrank differentendpoints byrawPRscore.",mode="methodological")
add("L30","Discrimination not calibration","Idealintercept0/slope1;curvespredictedvsobservedrisk","Calibrationversusprobabilistic accuracy","Discussion;Methods","probability estimates were slightly better","Describe lowerBrier/logloss without claiming clinicalcalibration","calibration","No ownmatched cancer cohort;not significance/equivalence evidence.",mode="methodological")
add("L32","BRCA provenance denominators","825overall;800>=1platform;466samples/463patients5of6;348patients6of6","Counts,notmodelmetrics","Reusability;Methods","TCGA","Useours manifestforcurrentn","825","Distinguishsamples/patients andassayintersection.",mode="provenance")
add("L33","ESCA histology and platform cohorts","164oesophageal,359gastric,36GEjunction,113proteomic","Profiling counts","Reusability;Methods;Discussion","ESCA","Cite provenance;qualify homogeneous-cancerwording","164","Countsnotours eligibility;not externalprediction.",mode="provenance")
add("L34","HNSCC molecular heterogeneity","279profiled;HPV andanatomicsubgroups","Profiling counts","Reusability;Methods","HNSCC","Retain provenance,notclinicalinputcontrolclaim","279","Ourclinicalconfoundersnotnecessarilymeasured.",mode="provenance")
add("L35","LSCC artifact label means LUSC","178profiled,19WGS,159miRNA","Platformsubsetcounts","Reusability;Methods","LSCC","Clarify standard naming","178","Not our endpointn.",mode="provenance")
add("L36","LUAD provenance","230untreatedpatients;drivercoverageto76%","Profiling/alterationfrequency","Reusability;Methods","LUAD","Retain provenance;omit irrelevant drivermetricsfromperformanceResults","230","Biologicalpercentagesnot modelAUC.",mode="provenance")
add("L39","Reporting checklist requirements","27mainitems/52subitems","Reportingguidance","Methods;Supplement","Reporting followed TRIPOD","Retainonlywith item-levelmapping,otherwiseguidanceconsulted","27 main items","Citationnot checklist compliance.",mode="methodological")
add("L40","Updated quality/bias/applicability tool","16development/18evaluationquestions;4domains","PROBAST+AI2025","Methods;Discussion;Supplement","risk of bias considered","Document explicit risk/applicability assessment","16 targeted","Notcertification;bibkey2024 != publication2025.",mode="methodological")

add("L01","Clinical comparison uncertainty is conditional on a fixed test set","70/30 split; cap 100,000 total before split; 100 TRAINING bootstrap refits; 50 HPO iterations selected once; additional 100 negative-control iterations","Mean AUROC/CIs over training variability, not patient-test bootstrap","Discussion;Methods","An independent clinical comparison","Include uncertainty-design distinction in any numerical clinical comparison","test set remained fixed","Our saved-prediction patient bootstrap estimates a different conditional uncertainty; original Arasteh split wording also needs reconciliation.")
add("L02","Per-cancer differences may be small despite clinical-only comparator","Table5: BRCA best C .643 vs clinical .637; ESCA clinical-only C .574; HNSC best .582 vs .554; LUAD .665 vs .663; LUSC .537 vs .531. All18 rows and IBS/intervals retained in context cell.","Uno C-index; source Table5 intervals explicitly NOT valid95%CIs because dependentCV iterations","Discussion","Within a single cancer","Add cohort-specific contextual examples without equivalence or direct AUC ranking","not valid confidence intervals","Winner per metric chosen retrospectively; selected best method differs by endpoint; do not promote dependent-fold intervals to patient CIs.")
add("L02","No statistically resolved aggregate superiority over clinical reference","BlockForest vs clinical: paired two-sided P=.86 for C-index,.78 for IBS; vs clinical-favoured CoxBoost P=.81/.95","Dataset-mean paired t tests; absence of significance not equivalence","Discussion","at least as good","Use to qualify similar magnitudes, not to establish equivalence","0.81 and 0.86","Our Nemenyi nonsignificance likewise does not show noninferiority.")
add("L02","Structured methods can avoid discounting small clinical blocks","Table6 BRCA structured/naive C .598/.512, IBS .152/.187; LUAD C .636/.539, IBS .181/.194; LUSC C .501/.457, IBS .220/.229; all18 datasets retained","Average over method families; not one model's scores","Discussion","random feature subsets","Discuss input-group imbalance as alternative to a unique ICL mechanism","0.1273 and 0.0002","Not causal proof for our attention or pooled-cancer effect; family averages differ in architecture.")
add("L03","Top omics combinations favour expression but do not justify all-modalities claims","Among 155 configurations, top30 IBS combinations: DNAseq only8; mRNA enrichment P=5.9x10^-6; expected15.5 occurrences per block under null","Hypergeometric enrichment of selected rank combinations","Discussion","extreme survival","Optional discussion of modality informativeness; do not confuse target selection with modality selection","5.9","Top30 retrospective ranking; supplementary counts/figure are not all numerically reconstructed; does not explain cohort pooling.")
add("L03","An important comparison-design limitation is stated by authors","25 outer splits = five repeats xfivefolds, without censoring-indicator stratification; R4.1.2","Evaluation-design detail","Discussion;Methods","Frozen evaluation","Document why benchmark protocols are not numerically interchangeable","without stratification","Clinical variables included in this source, omitted from our molecular comparison; conditional population differs.")
add("L04","Statistical and neural survival methods differ in probabilistic scoring","Clinical+GEX IBS BlockForest .162(SE.0020), PriorityLasso .166(.0022), RSF .167(.0020), Elasticnet .167(.0021); neural .171-.176, except relevant Table1 exact rows retained","Integrated Brier score under censoring, not a pure calibration metric","Discussion","probability estimates were slightly better","Compare probabilistic accuracy cautiously; qualify source's calibration interpretation","calibrated worse","IBS includes discrimination/resolution; source wording is not proof that lower Brier alone is calibration.")
add("L06","Case-mix weighting does not always reduce heterogeneity","Model8 tau .17 unstandardised versus .28 standardised; model1 .29 versus .08","Between-study SD on logit c-statistic scale","Discussion","pan-cancer scores","Use balanced explanation: direction depends on model and target population","0.28","Not universal correction; coefficients and sampling heterogeneity interact.")
add("L08","Outcome-dependent missingness changes the robustness assumptions","MCAR/nonmonotone MAR/self-masking MNAR/MAR-Y; shifts50%->25%/0%; Bayes/complete-data references distinct","Theoretical missingness assumptions and regressionMSE","Discussion","That pattern mixes measured zeros","Do not identify observed molecular zero as missing by definition; keep genuinezeros separate","MAR-Y","Our assay zero mask has not been shown to satisfy any of these mechanisms.")
add("L09","Gated adaptation example limits harmful transfer","A->D,epsilon=.9,labelledtarget30%: DANN accuracy51.3 +/-4.3; DANNgate80.6 +/-1.8; gap28.4 versus -0.9","Accuracy percentage points over five repeats; +/-definition pending","Discussion","The hypothesis is directly testable","Conceptual target-only baseline/remedy example, not a cancer numerical comparison","51.3","Negative transfer gap definition must be retained; not ours mean ROC delta.")
add("L16","Version capacity should not be described as a context failure at1,000patients","Table1 recommended v1 1,000rows/100features/depth8; v2 10,000/500/depth12; v2.5 50,000/2,000/depth18-24","Recommended table size, not evaluation CPUexecution guard","Methods;Discussion","CPU","If limitations discussed, distinguish safeguard from architectural parsing limit","recommended maximum sizes","NA remains NA; no refitting requested; L17 describes additional newer regimes.")
add("L19","Benchmark validation use differs between model families","ICL train-only; conventional models usevalidation early-stopping/tuning;15development datasets excluded;32estimator ensemble","Evaluation conditions, not a performance value","Reproducibility;Discussion","one split","Define what reproduced claim is and what has not been reproduced","training data only","Our default comparisons not this TALENT protocol; TabICL is not an evaluated arm.")
add("L20","Runtime comparisons are hardware-specific and missing-score methods differ","32GBRAM/100GBdisk; CPU8coreAWSM6i.2xlarge; L40S48GB forGPU; live leaderboard additionally imputes absent datasets","Resource budget; supplementary leaderboard treatment","Reproducibility;Discussion","NA","Retain our transparent NA treatment; do not adopt imputation for absent model configurations","impute","This source's live leaderboard rule is not permission to fabricate our scores.")
add("L25","Ordered mode is especially helpful on small datasets but not a claim about cohort confounding","Table3 AdultPlainlogloss .272(+1.1%); Amazon .139(-0.6%); Epsilon .266(+0.6%); Orderedabout1.7x slower thanPlain inEpsilon runtime comparison","Logloss relative changes; algorithm-mode runtime","Discussion;Methods","Tree ensembles split greedily","Separate boosting-mode target leakage from proposed pooling mechanism","1.7","Paper's orderedtargetstatistics not variance-selection audit; RFsubsampling description not alltree methods.")
add("L26","Headline AutoML averages use common successful subsets","Table2 AutoGluon rank1.8438/rescaledloss.1385/runtime201min on4hbenchmark; Table3 Kaggle rank1.7143/percentile.7041/runtime202min","Rescaledloss/meanrank on common subsets, not raw clinicalAUC","Reproducibility;Discussion","AutoGluon","Explain why our default180secAutoML cannot reproduce a4hensemble leaderboard claim","1.8438","Tables have different denominators; Kaggle means common7competitions notall11; source statuses not ours NA.")
add("L29","Same high ROC can mask low precision under imbalance","T1 MiRFinder ROC.992/PR.945;miPred.991/.976;RNAmicro.858/.559;ProMiR.974/.801;RNAfold.964/.670. T2 .772/.106;.707/.024;.886/.054;.711/.035;.706/.015 respectively.","ROC-AUC and PR-curve AUC; no95%CIs printed inTable5","Discussion;Methods","PR AUC","Use methodological illustration only; include correct classcount denominators","0.992*","Not a clinical benchmark; no model-family inference from microRNA tool results.")
add("L29","Prevalence changes the meaning of an identical ROC point","Balanced1,000pos/1,000neg:500TP/160FP at50%TPR,16%FPR;imbalanced1,000/10,000:500TP/1,600FP","Illustrative confusion counts, not observed clinicalcohort","Discussion;Methods","PR AUC","Explain prevalence-aware reporting without declaring ROC inherentlyinvalid","1 600 FPs","Counts from constructed score distributions; do not confuse with our pooled predictions.")

for sid in ("L05","L15","L31","L37","L38"):
    CONTEXT[sid] = "Correct full-text extraction unavailable. Exact population sizes, protocol and empirical values NR. Do not infer from metadata or quarantined L31 wrong-source files."
    add(sid,META[sid]["relevance_note"],"NR: correct source unavailable","Unverified",
        META[sid]["manuscript_location"],
        {"L05":"pan-cancer scores","L15":"100 features","L31":"Brier","L37":"Cancer cohorts and outcomes","L38":"CPTAC"}[sid],
        "Keep proposed role pending correct-source full text","",
        META[sid]["comparison_limit"],"unverified_full_text_unavailable","pending")

def read_source(sid):
    paths = sorted((ROOT/"official").glob(sid+"*.txt")) if sid in ("L27","L28") else [ROOT/"txt"/(sid+".txt")]
    if not paths or not paths[0].exists():
        return None,[]
    content = paths[0].read_text().split("VISUAL FIGURE VALUE AUDIT")[0]
    return paths[0],content.splitlines()

def citation_key(meta,bib):
    doi=meta["doi"].lower()
    for entry in re.split(r"(?=@\w+\s*\{)",bib):
        match=re.match(r"@\w+\s*\{\s*([^,]+)",entry)
        if match and doi!="na" and doi in entry.lower():
            return match.group(1)
    return meta["existing_bib_key"]

def write_tsv(path,rows,fields):
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fields,delimiter="\t",extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def md(value):
    return html.escape(str(value)).replace("|","&#124;").replace("\n","<br>")

def main():
    report_lines=REPORT.read_text().splitlines()
    bib=(REPO/"paper/references.bib").read_text()
    inventory=ROOT/"evidence_inventory"
    inventory.mkdir(exist_ok=True)
    coverage=[]
    for source in SOURCES:
        sid=source["source_id"]
        path,lines=read_source(sid)
        excerpts=[]
        for i,line in enumerate(lines,1):
            if re.search(r"\d",line) and re.search(r"dataset|sample|patient|cohort|train|test|valid|auc|accuracy|loss|brier|concord|c-index|table|figure|bootstrap|repeat|fold|interval|missing|feature|%|\|",line,re.I):
                excerpts.append(f"L{i}: {line}")
        dossier="# Retrieval inventory, NOT completed visual/claim audit\n"
        dossier+=f"Source {sid}: {source['title']}; DOI {source['doi']}\n"
        dossier+="Original text line numbers. Numbers may be citations, secondary reports,\ntoy examples, or ambiguous table columns. Verify context before citing.\n\n"
        dossier+="\n".join(excerpts) if lines else "Correct full text unavailable; no empirical values verified."
        (inventory/f"{sid}_quantitative_passages.txt").write_text(dossier+"\n")
        blocks=[]
        for lo,hi in TABLE_RANGES.get(sid,[]):
            assert len(lines)>=hi
            blocks.append(f"Original text lines{lo}-{hi}:\n"+"\n".join(lines[lo-1:hi]))
        if blocks:
            CONTEXT[sid]+="\nSOURCE TABLE EXTRACTS (original layout; inspect ambiguous column alignment before use):\n"+"\n".join(blocks)
        coverage.append(dict(source_id=sid,text_path=str(path.relative_to(REPO)) if path else "NA",
            source_sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path else "NA",
            findings=sum(r["source_id"]==sid for r in ROWS),quantitative_passages=len(excerpts),
            review_scope="Selected main-text findings/table passages, NOT exhaustive figures/supplements" if lines else "Correct text unavailable"))
    for index,row in enumerate(ROWS,1):
        meta=META[row["source_id"]]
        row.update(evidence_id=f"E{index:03d}",citation_key=citation_key(meta,bib),
            title=meta["title"],doi=meta["doi"],year=meta["year"],
            population_datasets_evaluation=CONTEXT[row["source_id"]])
        path,lines=read_source(row["source_id"])
        hits=[i for i,l in enumerate(lines,1) if row["support_search"] and row["support_search"].lower() in l.lower()]
        row["source_locator"]=(str(path.relative_to(REPO))+":"+ ",".join(map(str,hits[:5]))) if path and hits else (str(path.relative_to(REPO))+"; named table/section, specific passage pending") if path else "NA"
        if "visual" in row["verification_status"]:
            row["source_locator"]="paper/literature/pdfs/L01.pdf:p4,Fig2a; personally inspected labels"
        matches=[(i,l) for i,l in enumerate(report_lines,1) if row["sentence_anchor"].lower() in l.lower()]
        if matches:
            i,line=next(((i,l) for i,l in matches if not l.startswith("\\noindent")),matches[0])
            row["report_location"]=f"paper/reusability_report.tex:{i}"
            sentences=re.split(r"(?<=[.!?])\s+",line)
            row["current_sentence"]=next((s for s in sentences if row["sentence_anchor"].lower() in s.lower()),line)
        else:
            row["report_location"]="Proposed insertion: "+row["report_section"]
            row["current_sentence"]="No exact anchor; proposed section-level addition"
        row["supporting_passage"]="\n".join(f"L{i}: {lines[i-1]}" for i in hits[:2]) if hits else "See named table/page or unavailable status; no exact passage captured."
        if row["verification_status"] == "supported_text" and not hits:
            row["verification_status"] = "selected_finding_specific_passage_pending"
        row["claim_verdict"] = "Pending sentence-level adjudication; source finding is not certification of current wording"
        if not path:
            row["claim_verdict"] = "Unverified: correct-source full text unavailable"
        elif row["current_sentence"].startswith("No exact anchor"):
            row["claim_verdict"] = "Proposed addition, not an existing citation verdict"
        row["limitations"]+=" Exhaustive figure/supplement audit remains pending."
    assert {r["source_id"] for r in ROWS}==set(META)
    fields=["evidence_id","source_id","citation_key","doi","year","title","finding","published_values","metric_definition","population_datasets_evaluation","supporting_passage","source_locator","comparison_suitability","report_section","report_location","current_sentence","proposed_use","verification_status","claim_verdict","limitations"]
    write_tsv(ROOT/"reusability_evidence_table.tsv",ROWS,fields)
    write_tsv(ROOT/"evidence_review_coverage.tsv",coverage,list(coverage[0]))
    write_tsv(ROOT/"claim_evidence.tsv",ROWS,["evidence_id","source_id","citation_key","report_section","report_location","current_sentence","finding","source_locator","supporting_passage","verification_status","claim_verdict","proposed_use","limitations"])
    header="""# Reusability report: literature evidence working table

One row per selected useful finding from the 40-source collection. This is a **first curated evidence pass**, not an exhaustive certification of every number, figure, supplement or current citation. No manuscript prose, bibliography, experiment or prediction was modified.

The matching TSV is the lossless working version. Multiple dataset sizes and evaluation settings stay in the SAME context cell. NR means not recovered/not reported, never zero. Source-table blocks retain original layout and ambiguities. Source hashes and review scope are in evidence_review_coverage.tsv. Original extracted-text line numbers remain unchanged.

No external source here matches every condition needed to rank its performance directly against our cancer fixed-horizon ROC AUC. Contextual numerical comparisons require original populations, outcomes, metrics, budgets and hardware. Normalised AUC is not raw AUC; concordance is not fixed-horizon AUC; SE is not CI; prediction interval is not CI.

**Unresolved:** L05/L15/L31/L37/L38 lack correct-source full text; wrong-source L31 downloads excluded. XML-only sources lack local PDF visual review. Unavailable supplements/per-cohort counts/unlabelled chart values remain pending. Numeric passage inventories are retrieval aids, not verified findings.

**Visually recovered:** L01 Fig1b p3 contains all12 task n/p/prevalence, Fig2a p4 all rounded AUROCs; L18 Extended Data Tables3-4 pp20-21 contain all29 classification and28 regression n/p. Earlier notes are not automatically source evidence. L01 3-year literature AUROC is0.86, not the old note's0.85. No unlabelled chart points guessed.

**Report boundaries:** six-data directional reproduction != full original replication; default trees != tuned; nonsignificance != equivalence; context attention != demonstrated nearest-row mechanism; five-cohort classification != general clinical reusability; guidance citations != checklist compliance.

## Section roles

| Section | Evidence role |
|---|---|
| Introduction | Promise, independent clinical experience, classical strength, biomedical heterogeneity |
| Reproducibility | Original model/version, benchmark population, splits, budgets, normalisation |
| Reusability | Provenance and cohort structure; own artifacts support own measured results |
| Discussion | Multiomics precedents, case mix, missingness, negative transfer, bounded clinical conclusions |
| Methods | Algorithms, metrics, preprocessing, inference version and reporting guidance |

## Finding table
"""
    display=[("evidence_id","ID"),("source_id","Source"),("citation_key","Bib key"),("doi","DOI"),("year","Year"),("finding","Finding"),("published_values","Reported values"),("metric_definition","Metric/uncertainty"),("population_datasets_evaluation","All datasets/sizes/predictors/outcomes/evaluation settings"),("source_locator","Source location"),("report_section","Report section"),("report_location","Report line"),("current_sentence","Current sentence/insertion"),("comparison_suitability","Comparison class"),("proposed_use","Proposed use"),("verification_status","Status"),("limitations","Limits")]
    output=[header,"| "+" | ".join(label for _,label in display)+" |","| "+" | ".join("---" for _ in display)+" |"]
    output.extend("| "+" | ".join(md(r[k]) for k,_ in display)+" |" for r in ROWS)
    output.append("\n## Editorial models, not cancer numerical comparators\n\n| DOI/year | Local source | Role | Status |\n|---|---|---|---|")
    templates=[("10.1038/s42256-023-00757-8","2023","00757-8_scrna-transformers","Original reproduction -> imbalanced new domain -> tested remedy"),
        ("10.1038/s42256-024-00798-7","2024","00798-7_holography-unpaired","Reproduction -> shifted conditions -> explicit model extension and assumptions"),
        ("10.1038/s42256-024-00923-6","2024","00923-6_vgae-toxicity","Original/reproduced scorecard -> new-domain baseline comparison"),
        ("10.1038/s42256-025-01166-9","2025","01166-9_alphatensor-quantum","Public-code limitations -> compute boundary -> bounded general-agent remedy")]
    for doi,year,directory,role in templates:
        output.append(f"| {doi}/{year} | reference-papers/{directory}/paper.md | {role} | Editorial analogy only; digest includes annotations/visual estimates, not independently audited numerical evidence. |")
    output.append("\n## Additional method-source gaps\n\nDemsar2006statistical is cited but outside the40-source collection; Friedman/Nemenyi assumptions and critical-difference calculation need a separate source audit. TabPFN-v1 attribution needs its original version source. No new model computation is required.\n")
    (ROOT/"reusability_evidence_table.md").write_text("\n".join(output)+"\n")
    print(f"Wrote {len(ROWS)} finding rows /40sources,4editorial templates,5unavailable correct texts.")

if __name__=="__main__":
    main()
