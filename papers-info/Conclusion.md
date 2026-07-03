Conclusion
TabPFN represents a major change in tabular data modelling, leveraging ICL to autonomously discover a highly efficient algorithm that
outperforms traditional human-designed approaches on datasets with
up to 10,000 samples and 500 features. This shift towards foundation
models trained on synthetic data opens up new possibilities for tabular
data analysis across various domains.
Potential future directions include scaling to larger datasets48,
handling data drift49, investigating fine-tuning abilities across related
tabular tasks50 and understanding the theoretical foundations of our
approach51. Future work could also explore creating specialized priors
to handle data types such as time series52 and multi-modal data, or
specialized modalities such as ECG, neuroimaging data53 and genetic
data. As the field of tabular data modelling continues to evolve, we

12.

13.
14.

15.

16.
17.

18.

Borisov, V. et al. Deep neural networks and tabular data: a survey. IEEE Trans. Neural Netw.
Learn. Syst. 35, 7499–7519 (2024).
van Breugel, B. & van der Schaar, M. Position: why tabular foundation models should
be a research priority. In Proc. 41st International Conference on Machine Learning
48976–48993 (PMLR, 2024).
Silver, D. et al. Mastering the game of go with deep neural networks and tree search.
Nature 529, 484–489 (2016).
Jumper, J. M. et al. Highly accurate protein structure prediction with AlphaFold. Nature
596, 583 – 589 (2021).
OpenAI. GPT-4 Technical Report. Preprint at https://arxiv.org/abs/2303.08774 (2023).
Friedman, J. H. Greedy function approximation: a gradient boosting machine. Ann. Stat.
1189–1232 (2001).
Chen, T. & Guestrin, C. Xgboost: A scalable tree boosting system. In Proc. 22nd ACM
SIGKDD International Conference on Knowledge Discovery and Data Mining (eds
Krishnapuram, B. et al.) 785–794 (ACM Press, 2016).
Ke, G. et al. Lightgbm: A highly efficient gradient boosting decision tree. In Proc. 30th
International Conference on Advances in Neural Information Processing Systems
(eds Guyon, I. et al.) 3149–3157 (Curran Associates, 2017).
Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. & Gulin, A. CatBoost: unbiased
boosting with categorical features. In Proc. 30th International Conference on Advances
in Neural Information Processing Systems (eds Bengio, S. et al.) 6639–6649 (Curran
Associates, 2018).
Lowe, D. G. Distinctive image features from scale-invariant keypoints. Int. J. Comput. Vis.
60, 91–110 (2004).
Dalal, N. & Triggs, B. Histograms of oriented gradients for human detection. In Proc. 2005
IEEE Computer Society Conference on Computer Vision and Pattern Recognition
(CVPR’05) 886–893 (IEEE, 2005).
Vaswani, A. et al. Attention is all you need. In Proc. 30th International Conference on
Advances in Neural Information Processing Systems (eds Guyon, I. et al.) 6000–6010
(Curran Associates, 2017).
Silver, D. et al. Mastering the game of go without human knowledge. Nature 550, 354–359
(2017).
Grinsztajn, L., Oyallon, E. & Varoquaux, G. Why do tree-based models still outperform
deep learning on typical tabular data? In Proc. 36th International Conference on Neural
Information Processing Systems Vol. 35, 507–520 (ACM, 2022).
McElfresh, D. et al. When do neural nets outperform boosted trees on tabular data? In
Proc. 37th International Conference on Neural Information Processing System Vol. 36,
76336–76369 (ACM, 2024).
Goodfellow, I., Bengio, Y. & Courville, A. Deep Learning (MIT Press, 2016).
Brown, T. et al. Language models are few-shot learners. In Proc. Advances in Neural
Information Processing Systems (eds Larochelle, H. et al.) Vol. 33, 1877–1901 (Curran
Associates, 2020).
Garg, S., Tsipras, D., Liang, P. S. & Valiant, G. What can transformers learn in-context? A case
study of simple function classes. In Proc. Advances in Neural Information Processing
Systems Vol. 35, 30583–30598 (ACM, 2022).

Nature | Vol 637 | 9 January 2025 | 325


19.

20.
21.
22.

23.

24.
25.

26.

27.

28.

29.

30.
31.
32.
33.
34.
35.
36.
37.
38.
39.
40.
41.

Akyürek, E., Schuurmans, D., Andreas, J., Ma, T. & Zhou, D. What learning algorithm is
in-context learning? Investigations with linear models. In Proc. The Eleventh International
Conference on Learning Representations (ICLR, 2023).
Von Oswald, J. et al. Transformers learn in-context by gradient descent. In Proc. 40th
International Conference on Machine Learning 35151–35174 (PMLR, 2023).
Zhou, H. et al. What algorithms can transformers learn? A study in length generalization.
In Proc. The Twelfth International Conference on Learning Representations (ICLR, 2024).
Müller, S., Hollmann, N., Pineda-Arango, S., Grabocka, J. & Hutter, F. Transformers
can do Bayesian inference. In Proc. The Tenth International Conference on Learning
Representations (ICLR, 2022).
Hollmann, N., Müller, S., Eggensperger, K. & Hutter, F. TabPFN: a transformer that solves
small tabular classification problems in a second. In Proc. The Eleventh International
Conference on Learning Representations (ICLR, 2023).
Kingma, D. & Ba, J. Adam: A method for stochastic optimization. In Proc. International
Conference on Learning Representations (ICLR, 2015).
Bahdanau, D., Cho, K. & Bengio, Y. Neural machine translation by jointly learning to align
and translate. In Proc. 3rd International Conference on Learning Representations
(eds Bengio, Y. & LeCun, Y.) (ICLR, 2015).
Gorishniy, Y., Rubachev, I., Khrulkov, V. & Babenko, A. Revisiting deep learning models
for tabular data. In Proc. Advances in Neural Information Processing Systems 34
(eds Ranzato, M. et al.) 18932–18943 (NeurIPS, 2021).
Zhu, B. et al. XTab: cross-table pretraining for tabular transformers. In Proc. 40th
International Conference on Machine Learning (eds Krause, A. et al.) 43181–43204
(PMLR, 2023).
Lorch, L., Sussex, S., Rothfuss, J., Krause, A. & Schölkopf, B. Amortized inference for
causal structure learning. In Proc. Advances in Neural Information Processing Systems
(eds Koyejo, S. et al.) Vol. 35, 13104–13118 (ACM, 2022).
Dao, T., Fu, D., Ermon, S., Rudra, A. & Ré, C. Flashattention: fast and memory-efficient
exact attention with io-awareness. In Proc. Advances in Neural Information Processing
Systems (eds Koyejo, S. et al.) Vol. 35, 16344–16359 (2022).
Torgo, L. & Gama, J. Regression using classification algorithms. Intell. Data Anal. 1, 275–292
(1997).
Pearl, J. Causality 2nd edn (Cambridge Univ. Press, 2009).
Jiang, M. et al. Investigating Data Contamination for Pre-training Language Models.
Preprint at https://arxiv.org/abs/2401.06059 (2024).
Kumaraswamy, P. A generalized probability density function for double-bounded random
processes. J. Hydrol. 46, 79–88 (1980).
Rosenblatt, F. Principles of Neurodynamics: Perceptrons and the Theory of Brain
Mechanisms. Report No. 1196-0-8 (Cornell Aeronautical Lab, 1961).
Young, T. I. The bakerian lecture. experiments and calculations relative to physical optics.
Philos. Trans. R. Soc. Lond. 94, 1–16 (1804).
Gijsbers, P. et al. AMLB: an AutoML benchmark. J. Mach. Learn. Res. 25, 1–65 (2024).
Fischer, S. F., Feurer, M. & Bischl, B. OpenML-CTR23 – a curated tabular regression
benchmarking suite. In Proc. AutoML Conference 2023 (Workshop) (AutoML, 2023).
Breimann, L. Random forests. Mach. Learn. 45, 5–32 (2001).
Cortes, C. & Vapnik, V. Support-vector networks. Mach. Learn. 20, 273–297 (1995).
Erickson, N. et al. Autogluon-tabular: robust and accurate automl for structured data.
Preprint at https://arxiv.org/abs/2003.06505 (2020).
Wolpert, D. Stacked generalization. Neural Netw. 5, 241–259 (1992).



42. Caruana, R., Niculescu-Mizil, A., Crew, G. & Ksikes, A. Ensemble selection from libraries
of models. In Proc. 21st International Conference on Machine Learning (ed. Greiner, R.)
(Omnipress, 2004).
43. Purucker, L. O. et al. Q(D)O-ES: Population-based quality (diversity) optimisation for post
hoc ensemble selection in AutoML. In Proc. International Conference on Automated
Machine Learning Vol. 224 (PMLR, 2023).
44. Hofmann, H. Statlog (German Credit Data). UCI Machine Learning Repository https://doi.
org/10.24432/C5NC77 (1994).
45. Duin, R. Multiple Features. UCI Machine Learning Repository https://doi.org/10.24432/
C5HC70 (1998).
46. Rajotte, J.-F. et al. Synthetic data as an enabler for machine learning applications in
medicine. iScience 25, 105331 (2022).
47. Lundberg, S. M. & Lee, S.-I. A unified approach to interpreting model predictions. In Proc.
Advances in Neural Information Processing Systems (eds Guyon, I. et al.) Vol. 30, 4765–4774
(Curran Associates, 2017).
48. Feuer, B. et al. TuneTables: context optimization for scalable prior-data fitted networks.
In Proc. 38th Conference on Neural Information Processing Systems (NeurIPS, 2024).
49. Helli, K., Schnurr, D., Hollmann, N., Müller, S. & Hutter, F. Drift-resilient tabPFN: In-context
learning temporal distribution shifts on tabular data. In Proc. 38th Conference on Neural
Information Processing Systems (NeurIPS, 2024).
50. Thomas, V. et al. Retrieval & fine-tuning for in-context tabular models. In Proc. 1st
Workshop on In-Context Learning at the 41st International Conference on Machine
Learning (ICML, 2024).
51. Nagler, T. Statistical foundations of prior-data fitted networks. In Proc. 40th International
Conference on Machine Learning (eds Krause, A. et al.) Vol. 202, 25660–25676 (PMLR,
2023).
52. Dooley, S., Khurana, G. S., Mohapatra, C., Naidu, S. V. & White, C. ForecastPFN: syntheticallytrained zero-shot forecasting. In Proc. 37th Conference on Advances in Neural Information
Processing Systems (eds Oh, A. et al.) (NeurIPS, 2023).
53. Czolbe, S. & Dalca, A. V. Neuralizer: General neuroimage analysis without re-training.
In Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition 6217–6230
(IEEE, 2023).
54. Wilcoxon, F. in Breakthroughs in Statistics: Methodology and Distribution (eds Kotz, S.
& Johnson, N. L.) 196–202 (Springer, 1992).
Publisher’s note Springer Nature remains neutral with regard to jurisdictional claims in
published maps and institutional affiliations.
Open Access This article is licensed under a Creative Commons Attribution
4.0 International License, which permits use, sharing, adaptation, distribution
and reproduction in any medium or format, as long as you give appropriate
credit to the original author(s) and the source, provide a link to the Creative Commons licence,
and indicate if changes were made. The images or other third party material in this article are
included in the article’s Creative Commons licence, unless indicated otherwise in a credit line
to the material. If material is not included in the article’s Creative Commons licence and your
intended use is not permitted by statutory regulation or exceeds the permitted use, you will
need to obtain permission directly from the copyright holder. To view a copy of this licence,
visit http://creativecommons.org/licenses/by/4.0/.
© The Author(s) 2025
