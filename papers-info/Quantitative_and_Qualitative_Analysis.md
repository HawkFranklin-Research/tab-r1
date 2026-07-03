Qualitative analysis
We first analyse the behaviour of TabPFN on toy problems to build
intuition and disentangle the impact of various dataset characteristics.
As regression problems are easier to visualize, we focus on these in our
qualitative analysis. In Fig. 3a, we compare TabPFN with a diverse set of
standard predictors, with all methods using default settings.
Linear (ridge) regression can naturally model only linear functions,
leading to simple and interpretable predictions but catastrophic failure
on many of the toy functions. Multilayer perceptrons (MLPs)34 perform
worse on datasets with highly non-smooth patterns14. This is especially
apparent for the step function. TabPFN, by contrast, models either
function type, smooth or non-smooth, out of the box. This includes
a good approximation to step functions despite TabPFN being a neural network. CatBoost9, representative of tree-based methods, fits
only piece-wise constant functions. Although this leads to approximation errors and unintuitive predictions, it avoids catastrophic
failures.
The main advantage of TabPFN over all baselines is its inherent ability to model uncertainty at no extra cost. Whereas classical regression
methods output a single real-valued prediction, TabPFN returns a target
distribution, capturing the uncertainty of predictions. These uncertainty modelling abilities of TabPFN extend beyond simple distributions and can handle complex, multi-modal distributions. Figure 3b
shows this by modelling the density of light reaching a detector screen
in a double-slit experiment35 for different slit distances and widths. In
this classic experiment, photons are sent through two slits creating a
multi-modal intensity pattern because of the wave-like interference
behaviour of light. TabPFN predicts these intricate patterns in just
a single forward pass, requiring only 1.2 s. By contrast, traditional
methods such as CatBoost require training multiple quantile models
at different quantiles and reconstructing the distribution from these
predictions. Even after tuning CatBoost specifically for this task, it
produced substantially worse predictions compared with TabPFN,
see Fig. 3b. With default settings, CatBoost requires 169.3 s and yields
further deteriorated results. Qualitatively, we observe that TabPFN is

Default

Normalized
negative RMSE

Tuned (4 h)

Normalized
R2

Magnification

TabPFN

CatBoost (default)

LGBM
CB
XGB
RF

Catboost
stronger

0.6
0.4

TabPFN
stronger

0.2

Tuned (4 h)

1.0

Default

0.25 0.50 0.75 1.00
TabPFN (default)

0.6

TabPFN

CatBoost (default)

0.7

0.4

XGB

0.8

0.8

Catboost
stronger

0.6
0.4

TabPFN
stronger

0.2

0
Default

XGB

CatBoost

LightGBM

RF

0.9
0.8
0.7
0.6

0.25 0.50 0.75 1.00
TabPFN (4 h tuned)

Wilcoxon P < 0.001

Catboost
stronger

TabPFN
stronger

0

0
Tuned (4 h)

0

Wilcoxon P = 0.0153

0.6

0.2

TabPFN
stronger

1.0

RF
LGBM
CB

Regression

XGB
TabPFN

0.6

RF
LGBM
CB

0.7

0.4

Catboost
stronger

Tuned (4 h)

0.25 0.50 0.75 1.00
TabPFN (default)

Fig. 4 | Comparison of TabPFN on our test benchmarks, containing datasets
with up to 10,000 samples and 500 features. Performance was normalized
per dataset before aggregation using all baselines; intervals represent the 95%
confidence interval. Wilcoxon P refers to the two-sided Wilcoxon signed-rank
test P value54. a, Average performance of the default as well as the tuned versions
of TabPFN and our baselines. All methods are tuned for ROC AUC or RMSE,
respectively, thus decreasing the representativeness of the secondary metrics.
LGBM, LightGBM; MLP, multilayer perceptron; SVM, support vector machines;

more accurate in predicting very low densities and has fewer artefacts
compared with CatBoost.

Quantitative analysis
We quantitatively evaluate TabPFN on two dataset collections: the
AutoML Benchmark36 and OpenML-CTR2337. These benchmarks comprise diverse real-world tabular datasets, curated for complexity, relevance and domain diversity. From these benchmarks, we use the 29
classification datasets and 28 regression datasets that have up to 10,000
samples, 500 features and 10 classes. We further evaluated additional
benchmark suites from refs. 14,15, as well as five Kaggle competitions
from the Tabular Playground Series.
We compared TabPFN against state-of-the-art baselines, including
tree-based methods (random forest38, XGBoost (XGB)7, CatBoost9,
LightGBM8), linear models, support vector machines (SVMs)39 and
MLPs34.
Evaluation metrics include ROC AUC (area under the receiver operating characteristic curve; One-vs-Rest) and accuracy for classification,
and R2 (coefficient of determination) and negative RMSE (root mean
squared error) for regression. Scores were normalized per dataset,
with 1.0 representing the best and 0.0 the worst performance with
respect to all baselines.
For each dataset and method, we ran 10 repetitions with different random seeds and train–test splits (90% train, 10% test). We tuned hyperparameters using random search with five-fold cross-validation, with
time budgets ranging from 30 s to 4 h. All methods were evaluated using
eight CPU cores, with TabPFN additionally using a consumer-grade GPU
(RTX 2080 Ti; other methods did not benefit from this, see Extended
Data Fig. 2d). TabPFN was pre-trained once using eight NVIDIA RTX
2080 GPUs over 2 weeks, allowing for ICL on all new datasets in a single
forward pass. These modest computational requirements make similar
research accessible to academic labs. For details, refer to the section
‘Detailed evaluation protocol’.

0

0.25 0.50 0.75 1.00
TabPFN (4 h tuned)

300 900
5
30 60
Average fit + predict time (s)

1

Per dataset normalized RMSE comparison
of Catboost and TabPFN

Magnification

0.9

0.8

TabPFN

Wilcoxon P < 0.001

0.8

0.6

c

0

1.0

Lin
MLP
SVM
RF
LGBM
CB
XGB
TabPFN

Regression

0.6

0.8

0
Default

0.9

0.8

0

0.7

0.4
0.2

1.0

0.2

0.6

0

1.0

0.8

Lin
MLP
SVM
RF
LGBM
CB
XGB
TabPFN

0.6

Wilcoxon P < 0.001
1.0

0.9

0.8
Classification

TabPFN

0.7

0.4

0

RF

0.6

Lin
MLP
SVM
RF
LGBM
CB
XGB
TabPFN

Classification

0.8

LGBM
CB
XGB

1.0
0.9

0.8

0.2

Per dataset normalized ROC comparison
of Catboost and TabPFN

Magnification

Normalized ROC AUC

1.0

b
1.0

TabPFN

Normalized negative RMSE

Normalized
accuracy

Magnification

CatBoost (4h tuned)

1.0

CatBoost (4 h tuned)

Normalized
ROC AUC

Lin
MLP
SVM
RF
LGBM
CB
XGB
TabPFN

a

XGB

CatBoost

3,600 14,400

LightGBM

RF

1.0
0.9
0.8
0.7
0.6
0.5

1

5
300 900 3,600 14,400
30 60
Average fit + predict time (s)

RF, random forest; CB, CatBoost; XGB, XGBoost; Lin, logistic regression for
classification and ridge regression for regression tasks. Plots on the right-hand
side show a magnified analysis of the strongest baselines considered. b, A perdataset comparison of TabPFN with its strongest baseline, CatBoost. Each dot
is the average score on one dataset. c, The impact of hyperparameter tuning for
the considered methods. The x-axis shows the average time required to fit and
predict with the algorithm.

Comparison with state-of-the-art baselines
Figure 4a demonstrates the strong out-of-the-box performance of
TabPFN compared with tuned and default configurations of XGBoost,
CatBoost and a random forest. For classification tasks, TabPFN surpasses CatBoost, the strongest default baseline, by 0.187 (0.939 compared with 0.752) in normalized ROC AUC in the default setting and by
0.13 (0.952 compared with 0.822) in the tuned setting. For regression,
TabPFN outperforms CatBoost in normalized RMSE by 0.051 (0.923
compared with 0.872) in the default setting and by 0.093 (0.968 compared with 0.875) in the tuned setting. In Fig. 4b, we show per-dataset
comparisons. Although for some datasets CatBoost outperforms
TabPFN, TabPFN wins on most of the datasets.
Figure 4c shows how the performance of TabPFN and the baselines
improve with more time spent on hyperparameter search. The default
of TabPFN, taking 2.8 s on average for classification and 4.8 s for regression, outperforms all baselines, even when tuning them for 4 h—a
speedup of 5,140× and 3,000×, respectively. We show comparisons
on a larger number of metrics in Extended Data Tables 1 and 2.
As shown in Extended Data Fig. 2, similar to our primary benchmarks,
TabPFN substantially outperformed all baselines on the benchmarks of
refs. 14,15. The benchmark of ref. 14 is particularly noteworthy because
on this benchmark, tree-based methods were previously found to excel.
Moreover, we show in Extended Data Table 6 that default TabPFN
outperforms default CatBoost on all five Kaggle competitions with
less than 10,000 training samples from the latest completed Tabular
Playground Series.
Evaluating diverse data attributes
In Fig. 5a,b, we show the robustness of TabPFN to dataset characteristics that are traditionally hard to handle for neural-network-based
approaches14,23.
Figure 5a provides an analysis of the performance of TabPFN across
various dataset types. First, we add uninformative features (randomly
Nature | Vol 637 | 9 January 2025 | 323


a

Uninformative features

0.6
0.4
0.2
0

Dropping samples

Categorical features
No
Yes

Missing values?
No
Yes

Dropping features

Number of samples

Number of features

0.2
Autogluon

0.95
0.90

0.6

AutoGluon

0.5

0.85
CatBoost
0.80

fa
ul
t)
de

ef
au
lt)

Li
ne
a

r(

fa
ul
t)

(d

M
LP

ef
au
lt)
(d
PF
N

at
Bo
o

C

Ta
b

de

fa
ul
t)

ef
au
lt)

de

r(

Li
ne
a

(d

de

LP

C
Dataset win rate
on RMSE
Wilcoxon P = 0.0101

0.4

TabPFN
(PHE)

0.3
0.2

0.75

M

ef
au
lt)
0.7

TabPFN

at
Bo
o

(d
TabPFN (PHE)

Number of features
1–19
20–39
40–500

Autogluon

Normalized negative RMSE

TabPFN
(PHE)

Normalized ROC AUC

0.4

PF
N
0.8

1.00

0.8

0.6

Ta
b

Li
ne
a

d

Dataset win rate
on ROC AUC
Wilcoxon P = 0.0024

st
(

fa
ul
t)

ef
au
lt)

de

r(

fa
ul
t)

(d

de

M
LP

ef
au
lt)
(d
PF
N

at
Bo
o

25

C

Ta
b

Li
ne
a

st
(

fa
ul
t)
de

r(

fa
ul
t)

25

ef
au
lt)

(d

de

LP

(d

Fraction kept (%)
100
50

C

at
Bo
o

st
(

ef
au
lt)

Fraction kept (%)
100
50

fa
ul
t)

Number of samples
1–1,999
2,000–3,999
4,000–10,000

0.4

st
(

0.6

PF
N
Ta
b

Categorical features

0.8

0

0

Missing values

Outlier Fraction
0
100
10,000

Fraction (%)
0
90

1.0

0.2

c

b

Outlier factor

0.8

M

Normalized average performance
(ROC AUC and negative RMSE)

1.0

TabPFN (PHE)

0.975

TabPFN

0.950

AutoGluon
0.925
0.900
CatBoost

0.875

0.1
5

30 60

300 900 3,600 14,400

Average fit + predict time (s)

0

5

30 60

300 900 3,600 14,400

Average fit + predict time (s)

Fig. 5 | Robustness across datasets and performance comparison with
tuned ensembles. a, A comparison of modified datasets. We can see that
TabPFN is not more vulnerable to the modifications compared with baselines.
We also see that TabPFN reproduces the accuracy of CatBoost (default) with
only half the training samples provided. Here we normalize scores per dataset
(sharing one normalization across all modifications of one experiment) to
avoid negative outliers. b, We split the test datasets by data characteristics and

analyse the performance per subgroup. c, Classification performance. Left,
the win rate of TabPFN (PHE) against AutoGluon (with one tie excluded); right,
the ROC AUC score over time for tuning each method, with the first marker
representing the default configuration for the non-ensembling methods.
d, Regression performance presented as in c but using the RMSE metric.
Intervals represent the 95% confidence interval and Wilcoxon P refers to the
two-sided Wilcoxon signed-rank test P value 54.

shuffled features from the original dataset) and outliers (multiply each
cell with 2% probability with a random number between 0 and the outlier factor). The results show that TabPFN is very robust to uninformative features and outliers, something typically hard for neural networks,
as can be seen with the MLP baseline. Second, although dropping either
samples or features hurts the performance of all methods, with half
the samples TabPFN still performs as well as the next best method
using all samples.
In Fig. 5b, we split our test datasets into subgroups and perform
analyses per subgroup. We create subgroups based on the presence of
categorical features, missing values, number of samples and number of
features in the datasets. The sample- and feature-number subgroups
are split such that a third of the datasets fall into each group. We can
see that none of these characteristics strongly affect the performance
of TabPFN relative to the other methods. However, we note that these
results should not be taken as evidence that TabPFN scales well beyond
the 10,000 samples and 500 features considered here. We show four
further ablations in Extended Data Fig. 1.

Figure 5c–d compares the performance of TabPFN, TabPFN (PHE),
AutoGluon and CatBoost. For TabPFN (PHE) and AutoGluon, we start
with a minimal budget of 300 s for tuning because AutoGluon otherwise does not reliably return results. In just 2.8 s, TabPFN (default)
outperforms AutoGluon for classification tasks, even if AutoGluon is
allowed up to 4 h, a 5.140× speedup. TabPFN (PHE) further improves
performance leading to an average normalized ROC AUC score of 0.971,
compared with 0.939 for TabPFN (default) and 0.914 for AutoGluon.
For regression tasks, tuning hyperparameters is more important. Here,
TabPFN (PHE) outperforms AutoGluon (allowed 4 h) after its minimal
tuning budget of 300 s, a 48× speedup.
