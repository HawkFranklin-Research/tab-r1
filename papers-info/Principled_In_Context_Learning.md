Principled in-context learning
TabPFN leverages in-context learning (ICL)17, the same mechanism
that led to the astounding performance of large language models, to

Machine Learning Lab, University of Freiburg, Freiburg, Germany. 2Computational Medicine, Berlin Institute of Health at Charité, Universitätsmedizin Berlin, Berlin, Germany. 3Prior Labs,
Freiburg, Germany. 4Neuromedical AI Lab, Department of Neurosurgery, Medical Center - University of Freiburg, Faculty of Medicine, University of Freiburg, Freiburg, Germany. 5Medical
Physics, Department of Diagnostic and Interventional Radiology, Medical Center - University of Freiburg, Faculty of Medicine, University of Freiburg, Freiburg, Germany. 6ELLIS Institute
Tübingen, Tübingen, Germany. 7These authors contributed equally: Noah Hollmann, Samuel Müller. ✉e-mail: noah@priorlabs.ai; samuelgabrielmuller@gmail.com; fh@cs.uni-freiburg.de

1

Nature | Vol 637 | 9 January 2025 | 319


a

TabPFN is trained on synthetic data to take entire
datasets as inputs and predict in a forward pass

TabPFN can now be applied to arbitrary
unseen real-world datasets
Prediction

Xtrain

ytrain

TabPFN

Prediction
Xtrain

ytrain

Xtest

?

TabPFN

neural network
parameterized by T

Xtest

?

A synthetic dataset
–log qT (ytest |...)

ytest

Test

Input dataset

Predictions: ˆy test

2D TabPFN layer (12×)

x1

x2

y

1.2

6.1

3.0

8.9

9.1

3.1

1.0

2.9

6.7

33.3

2.2

?

We predict this entry

1D feature attention

1D sample attention

MLP

The vector is transformed
to a piece-wise constant
(Riemann) distribution
with an MLP

Density

Training rows

b

An arbitrary real-world dataset

Training loss to be optimized
across millions of datasets

Each node represents one entry in the table

5
0
10
Predicted y distribution

Fig. 1 | Overview of the proposed method. a, The high-level overview of TabPFN
pre-training and usage. b, The TabPFN architecture. We train a model to solve
more than 100 million synthetic tasks. Our architecture is an adaptation of the

standard transformer encoder that is adapted for the two-dimensional data
encountered in tables.

generate a powerful tabular prediction algorithm that is fully learned.
Although ICL was first observed in large language models, recent
work has shown that transformers can learn simple algorithms
such as logistic regression through ICL18–21. Prior-data Fitted Networks (PFNs) have shown that even complex algorithms, such as
Gaussian Processes and Bayesian Neural Networks, can be approximated with ICL22. ICL enables us to learn a wider space of possible
algorithms, including cases for which a closed-form solution does
not exist.
We build on a preliminary version of TabPFN23, which demonstrated
the applicability of in-context-learning17 for tabular data in principle
but had many limitations that rendered it inapplicable in most cases.
Based on a series of improvements, the new TabPFN scales to 50× larger
datasets; supports regression tasks, categorical data and missing
values; and is robust to unimportant features and outliers.
The key idea behind TabPFN is to generate a large corpus of synthetic
tabular datasets and then train a transformer-based12 neural network
to learn to solve these synthetic prediction tasks. Although traditional
approaches require hand-engineered solutions for data challenges
such as missing values, our method autonomously learns effective
strategies by solving synthetic tasks that include these challenges. This
approach leverages ICL as a framework for exemplar-based declarative
programming of algorithms. We design desired algorithmic behaviour
by generating diverse synthetic datasets that demonstrate the desired
behaviour and then train a model to encode an algorithm that satisfies
it. This shifts the algorithm design process from writing explicit instructions to defining input–output examples, opening up possibilities for
creating algorithms in various domains. Here, we apply this approach
to the high-impact field of tabular learning, generating a powerful
tabular prediction algorithm.
Our ICL approach differs fundamentally from standard supervised deep learning. Usually, models are trained per dataset, upd­
ating model parameters on individual samples or batches according
to hand-crafted weight-updating algorithms, such as Adam 24.

At inference time, the learned model is applied to test samples. By
contrast, our approach is trained across datasets and is applied to
entire datasets at inference time rather than individual samples. Before
being applied to real-world datasets, the model is once pre-trained
on millions of synthetic datasets representing different prediction
tasks. At inference time, the model receives an unseen dataset with
both labelled training and unlabelled test samples and performs
training and prediction on this dataset in a single neural network
forward pass.
Figures 1 and 2 outline our approach:
1. Data generation: we define a generative process (referred to as our
prior) to synthesize diverse tabular datasets with varying relationships between features and targets, designed to capture a wide range
of potential scenarios that our model might encounter. We sample
millions of datasets from the generative process. For each dataset,
a subset of samples has their target values masked, simulating a
supervised prediction problem. Further details of our prior design
are shown in the section ‘Synthetic data based on causal models’.
2. Pre-training: we train a transformer model, our PFN, to predict the
masked targets of all synthetic datasets, given the input features
and the unmasked samples as context. This step is done only once
during model development, learning a generic learning algorithm
that can be used to predict any dataset.
3. Real-world prediction: the resulting trained model can now be
applied to arbitrary unseen real-world datasets. The training samples
are provided as context to the model, which predicts the labels of
these unseen datasets through ICL.



Our approach also has a theoretical foundation as described in
ref. 22. It can be viewed as approximating Bayesian prediction for a
prior defined by the synthetic datasets. The trained PFN will approxî ∣X test, X train, ytrain) and
mate the posterior predictive distribution p(ytest
thus return a Bayesian prediction for the specified distribution over
artificial datasets used during PFN pre-training.

a Sample underlying parameters

b Build computational graph and graph structure

c Final datasets
F

F

T
Sample number of data points
4

Sample number of features
Sample number of nodes
Sample graph complexity

1

For each generated sample,
propagate initialization data
through the graph

Sample graph

2

Sample random feature (F)
and target (T) node positions, and

3

read off data at those positions

Postprocessing,
quantization and
warping

Connection types
Neural network

Fig. 2 | Overview of the TabPFN prior. a, For each dataset, we first sample
high-level hyperparameters. b, Based on these hyperparameters, we construct
a structural causal model that encodes the computational function generating
the dataset. Each node holds a vector and each edge in the computational
graph implements a function according to one of the connection types. In step 1,
using random noise variables we generate initialization data, which is fed into
the root nodes of the graphs and propagated through the computational graph
