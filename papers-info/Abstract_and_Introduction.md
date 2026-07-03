Accurate predictions on small data with a
tabular foundation model
https://doi.org/10.1038/s41586-024-08328-6
Received: 17 May 2024

Noah Hollmann1,2,3,7 ✉, Samuel Müller1,7 ✉, Lennart Purucker1, Arjun Krishnakumar1,
Max Körfer1, Shi Bin Hoo1, Robin Tibor Schirrmeister4,5 & Frank Hutter1,3,6 ✉

Accepted: 31 October 2024
Published online: 8 January 2025
Open access
Check for updates

Tabular data, spreadsheets organized in rows and columns, are ubiquitous across
scientific fields, from biomedicine to particle physics to economics and climate
science1,2. The fundamental prediction task of filling in missing values of a label
column based on the rest of the columns is essential for various applications as
diverse as biomedical risk models, drug discovery and materials science. Although
deep learning has revolutionized learning from raw data and led to numerous
high-profile success stories3–5, gradient-boosted decision trees6–9 have dominated
tabular data for the past 20 years. Here we present the Tabular Prior-data Fitted
Network (TabPFN), a tabular foundation model that outperforms all previous
methods on datasets with up to 10,000 samples by a wide margin, using substantially
less training time. In 2.8 s, TabPFN outperforms an ensemble of the strongest
baselines tuned for 4 h in a classification setting. As a generative transformer-based
foundation model, this model also allows fine-tuning, data generation, density
estimation and learning reusable embeddings. TabPFN is a learning algorithm that is
itself learned across millions of synthetic datasets, demonstrating the power of this
approach for algorithm development. By improving modelling abilities across diverse
fields, TabPFN has the potential to accelerate scientific discovery and enhance
important decision-making in various domains.

Throughout the history of artificial intelligence, manually created
algorithmic components have been replaced with better-performing
end-to-end learned ones. Hand-designed features in computer vision,
such as SIFT (Scale Invariant Feature Transform)10 and HOG (Histogram
of Oriented Gradients)11, have been replaced by learned convolutions;
grammar-based approaches in natural language processing have been
replaced by learned transformers12; and the design of customized opening and end-game libraries in game playing has been superseded by
end-to-end learned strategies3,13. Here we extend this end-to-end
learning to the ubiquitous domain of tabular data.
The diversity of tabular data sets them apart from unprocessed
modalities such as text and images. While in language modelling for
example the meaning of a word is consistent across documents, in
tabular datasets the same value can mean fundamentally different
things. A drug discovery dataset, for example, might record chemical
properties, whereas another dataset in materials science might document thermal and electric properties. This specialization leads to a
proliferation of smaller, independent datasets and associated models.
To illustrate, on the popular tabular benchmarking website openml.org,
76% of the datasets contain less than 10,000 rows at the time of writing.
Deep learning methods have traditionally struggled with tabular
data, because of the heterogeneity between datasets and the heterogeneity of the raw data itself: Tables contain columns, also called features,
with various scales and types (Boolean, categorical, ordinal, integer,

floating point), imbalanced or missing data, unimportant features,
outliers and so on. This made non-deep-learning methods, such as
tree-based models, the strongest contender so far14,15.
However, these traditional machine learning models have several drawbacks. Without substantial modifications, they yield poor
out-of-distribution predictions and poor transfer of knowledge from
one dataset to another16. Finally, they are hard to combine with neural
networks, as they do not propagate gradients.
As a remedy, we introduce TabPFN, a foundation model for smallto medium-sized tabular data. This new supervised tabular learning
method can be applied to any small- to moderate-sized dataset and
yields dominant performance for datasets with up to 10,000 samples
and 500 features. In a single forward pass, TabPFN significantly outperforms state-of-the-art baselines on our benchmarks, including
gradient-boosted decision trees, even when these are allowed 4 h of
tuning, a speedup of 5,140× (classification) and 3,000× (regression).
Finally, we demonstrate various foundation model characteristics
of TabPFN, including fine-tuning, generative abilities and density
estimation.
