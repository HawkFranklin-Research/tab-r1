An architecture designed for tables
The transformer architecture is currently the favoured architecture for
flexible deep learning and foundation models4,5. Transformer models
work on sequences and combine information between sequence items
using so-called attention mechanisms25, allowing them to effectively
capture long-range dependencies and learn complex relationships in
data. Although transformer-based models can be applied to tabular
data26,27, TabPFN addresses two key limitations inherent to them. First,
as transformers are designed for sequences, they treat the input data
as a single sequence, not using the tabular structure. Second, machine
learning models are often used in a fit-predict model, in which a model
is fitted on the training set once and then reused for multiple test datasets. Transformer-based ICL algorithms, however, receive train and
test data in a single pass and thus perform training and prediction at
once. Thus, when a fitted model is reused, it has to redo computations
for the training set.
To better use the tabular structure, we propose an architecture that
assigns a separate representation to each cell in the table, inspired
by refs. 22,28. Our architecture, visualized in Fig. 1b, uses a two-way
attention mechanism, with each cell attending to the other features
in its row (that is, its sample) and then attending to the same feature
across its column (that is, all other samples). This design enables the
architecture to be invariant to the order of both samples and features
and enables more efficient training and extrapolation to larger tables
than those encountered during training, in terms of both the number
of samples and features.
To mitigate repeating computations on the training set for each test
sample in a fit-predict setting, our model can separate the inference
on the training and test samples. This allows us to perform ICL on the
training set once, save the resulting state and reuse it for multiple test
set inferences. On datasets with 10,000 training samples and 10 features, our optimized train-state caching results in inference speedups of

Tree

Discretization

for each to-be-generated sample. In step 2, we randomly sample feature and
target node positions in the graph, labelled F and T, respectively. In step 3,
we extract the intermediate data representations at the sampled feature and
target node positions. In step 4, we post-process the extracted data. c, We
retrieve the final datasets. We plot interactions of feature pairs and the node
colour represents the class of the sample.

around 300× on CPU (from 32 s to 0.1 s) and 6× on GPU. With 10× more
features (100), the speedups increase to 800× on CPU and 30× speedup
on GPU. These measurements focus solely on the core inference process, excluding pre-processing and ensembling steps detailed in the
section ‘Inference details’. The lower speedups on GPUs are because of
an underutilization of their massively parallel architecture.
We further optimize the memory and compute requirements of the
architecture by computing layer norms in half-precision, using flash
attention29, activation checkpointing and sequential computation of
the state. Our optimizations reduce the memory requirements by a
factor of four, resulting in less than 1,000 bytes per cell. This enables
the prediction on datasets with up to 50 million cells (for example,
5 million rows × 10 features) on a single H100 GPU.
For regression tasks, we use a piece-wise constant output distribution, following refs. 22,30, which allows our models to predict a probability distribution of target values instead of a single value, including,
for example, bimodal distributions.

Synthetic data based on causal models
The performance of TabPFN relies on generating suitable synthetic
training datasets that capture the characteristics and challenges of
real-world tabular data. To generate such datasets, we developed an
approach based on structural causal models (SCMs)31. SCMs provide a
formal framework for representing causal relationships and generative
processes underlying the data. By relying on synthetic data instead
of large collections of public tabular data, we avoid common problems of foundational models, such as privacy and copyright infringements, contaminating our training data with test data32 or limited data
availability.
As shown in Fig. 2, our generative pipeline first samples high-level
hyperparameters, such as dataset size, number of features and difficulty level, to govern the overall properties of each synthetic dataset.
Nature | Vol 637 | 9 January 2025 | 321


|x|

Step function

Homoscedastic Heteroscedastic b
noise
noise

True function

TabPFN

CatBoost (quantile)

0.6

0

0.4

–0.5
0.5

0.2

0

–0.2

0

–0.4

MLP

CatBoost

–0.5
0.5

Linear

0.8
Position on the wall (m)

0.5

x2

sin(x) + x

–0.6
0.5
1.0
Slit width (mm)

0

0.5
1.0
Slit width (mm)

0.5
1.0
Slit width (mm)

–0.8

–0.5
0.5

0.4

0

0.2

–0.5
0.5

0
–0.2

0

Position on the wall (m)

TabPFN

True function

a

–0.4
–0.5
–0.5

0

0.5 –0.5

0

0.5 –0.5

0

0.5 –0.5

0

0.5 –0.5

0

0.5 –0.5

Fig. 3 | The behaviour of TabPFN and a set of baselines on simple functions.
In all plots, we use orange for the ground truth and blue for model predictions.
a, Each column represents a different toy function, each having a single feature
(along the x-axis) and a target (along the y-axis). TabPFN can model a lot of

Guided by these hyperparameters, we construct a directed acyclic
graph specifying the causal structure underlying the dataset.
To generate each sample within a dataset, we propagate randomly
generated noise, called our initialization data, through the root nodes
of the causal graph. This initialization data are generated by sampling
from a random normal or uniform distribution with varying degrees
of non-independence between samples, see section ‘Initialization
data sampling’. As these data traverse the edges of the computational
graph, we apply a diverse set of computational mappings: small
neural networks with linear or nonlinear activations (for example,
sigmoid, ReLU (rectified linear unit), modulo, sine), discretization
mechanisms for generating categorical features and decision tree
structures to encode local, rule-based dependencies. At each edge,
we add Gaussian noise, introducing uncertainty into the generated
data. We save the intermediate data representations at each node
to be retrieved later. See section ‘Computational edge mappings’
for details.
After traversing the causal graph, we extract the intermediate representations at the sampled feature and target nodes, yielding a sample
consisting of feature values and an associated target value.
By incorporating various data challenges and complexities into the
synthetic datasets, we create a training ground that allows TabPFN to
develop strategies for handling similar issues in real-world datasets.
For instance, consider the case of missing values, commonly present
in tabular data. By exposing TabPFN to synthetic datasets with varying
patterns and fractions of missing values in our synthetic data generation process, the model learns effective ways of handling missing values that generalize to real-world datasets. We apply post-processing
techniques to further enhance the realism and challenge the robustness
of the learned prediction algorithms. This includes warping with the
Kumaraswamy distribution33, introducing complex nonlinear distortions and quantization mimicking discretized features. See section
‘Post-processing’ for details.
Through this generative process, we created a massive corpus of
around 100 million synthetic datasets per model training, each with a
unique causal structure, feature types and functional characteristics.


0

0.5

2
4
Slit separation (μm)

2
4
Slit separation (μm)

2
4
Slit separation (μm)

different functions, including noisy functions. b, TabPFN can model distributions
over outputs out of the box, which is exemplified by predicting the light
intensity pattern in a double-slit experiment after observing the positions of
1,000 photons.
