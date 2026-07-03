Foundation model with interpretability
Apart from its strong predictive performance, TabPFN exhibits key
foundation model abilities, such as data generation, density estimation, learning reusable embeddings and fine-tuning. We showcase
these abilities through proof-of-concept experiments on the German Credit Dataset44, which contains credit risk information and the
mfeat-factors45 dataset classifying handwritten digits based on a tabular
representation.
TabPFN can estimate the probability density function of numerical
features, as shown in Fig. 6a, and the probability mass function of categorical features. Computing the sample densities enables anomaly
detection to identify issues such as fraud, equipment failures, medical
emergencies or low-quality data.
TabPFN also allows synthesizing new tabular data samples that mimic
real-world dataset characteristics as shown in Fig. 6b. This enables applications such as data augmentation or privacy-preserving data sharing46.
The architecture of TabPFN yields meaningful feature representations that can be reused for downstream tasks such as data

80

High density
Medium density (10th percentile)
Low density (2nd percentile)

70

Synthetic data generation

Actual samples
Generated samples

70

60

60

50

50

c

Embedded data + PCA

20

Finetuned TabPFN predictions

Y

30

Original data + PCA

PCA 2

Age

Age

40

30

Fine-tuning data

Default TabPFN predictions
PCA 1

40

d
Y

80

b

Y

Data density estimation

PCA 2

a

20
0

5,000
10,000
15,000
Credit_amount

0

5,000
10,000
15,000
Credit_amount

PCA 1

Prediction

X
Ground truth

Training sample

Fig. 6 | Showcase of the application of TabPFN as tabular foundation model.
a,b, On the German Credit Dataset, we perform data density estimation (a) and
generation of new synthetic samples (b). c, We show our learned embeddings
are useful representations of each sample on the handwritten digits dataset

(mfeat-factors) with different classes forming different clusters. d, We
demonstrate fine-tuning TabPFN for a specific set of tasks. Fine-tuned on a
dataset containing various sine curves (top), we see the model makes more
accurate predictions on another sine curve dataset.

imputation and clustering. We extract and visualize learned embeddings from the mfeat-factors dataset in Fig. 6c, showing improved
class separation compared with the raw data on the first two principal
components.
Furthermore, we demonstrate the ability of TabPFN to improve performance through fine-tuning on related datasets. Unlike tree-based
methods, the neural architecture of TabPFN enables fine-tuning on
specific dataset classes. We conduct proof-of-concept experiments
using sine curve datasets with varying offsets between fine-tuning and
test data. Figure 6d shows an example fine-tuning result. Our analysis
across 50 runs (Extended Data Fig. 4) shows that TabPFN successfully
transfers knowledge even when labels differ significantly between
fine-tuning and test tasks, with performance improving as distributions
become more similar. This could, for example, enable fine-tuning for a
range of datasets from medical studies to obtain an improved general
model for medical diagnosis tasks. For details, refer to section ‘Foundation model abilities’.
Finally, we have developed a methodology to easily interpret the
predictions of TabPFN. Interpretability is crucial for building trust
and accountability when deploying models in high-stakes domains.
We support the computation of feature importance through SHAP47
(Shapley Additive Explanations), a game-theoretic approach to
explain predictions. SHAP values represent the contribution of each
feature to the output of the model. Extended Data Fig. 3 compares
the feature importance and impact for logistic regression, CatBoost
and TabPFN. TabPFN achieves high accuracy while learning simple,
interpretable feature relationships. By contrast, logistic regression is
interpretable but less accurate, whereas CatBoost is accurate but qualitatively less interpretable because of complex, non-smooth decision
boundaries.

believe that foundation models, such as TabPFN, will play a key part in
empowering researchers. To facilitate the widespread use of TabPFN,
in the section ‘User guide’ we discuss how to use it effectively.

Online content
Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions
and competing interests; and statements of data and code availability
are available at https://doi.org/10.1038/s41586-024-08328-6.
1.
2.

3.
4.
5.
6.
7.

8.

9.

10.
11.
