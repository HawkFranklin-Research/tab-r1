Comparison with tuned ensemble methods
We compare the performance of TabPFN with AutoGluon 1.0 (ref. 40),
which combines various machine learning models, including our baselines, into a stacked ensemble41, tunes their hyperparameters and then
generates the final predictions using post hoc ensembling (PHE)42,43. It
thus represents a different class of methods compared with individual
baselines.
To assess whether TabPFN can also be improved by a tuned ensemble
approach, we introduce TabPFN (PHE). TabPFN (PHE) automatically
combines only TabPFN models with PHE and tunes their hyperparameters using a random portfolio from our search space. We detail this
approach in the section ‘TabPFN (PHE)’.
