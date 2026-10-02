# Reusability report: Optimizing T count in general quantum circuits with AlphaTensor-Quantum

- **Journal / type:** Nature Machine Intelligence, Article (Reusability report). Vol. 8, January 2026, pp. 113–117
- **Authors:** Remmy Zen¹, Maximilian Nägele¹˒², Florian Marquardt¹˒² (¹Max Planck Institute for the Science of Light, Erlangen, Germany; ²Department of Physics, Friedrich-Alexander Universität Erlangen-Nürnberg, Erlangen, Germany). Correspondence: remmy.zen@mpl.mpg.de
- **Received:** 7 March 2025 · **Accepted:** 3 December 2025 · **Published online:** 31 December 2025
- **DOI:** https://doi.org/10.1038/s42256-025-01166-9
- **Source PDF:** `../s42256-025-01166-9.pdf` (5 pages). Page renders and figure crops are in `img/` (`page-1..5.png` at 150 dpi; `fig1.png`, `fig2.png`, `fig3.png`, `fig3a_c.png`, `fig3bd.png`, `fig4.png`, `table1.png` at 300 dpi).

---

## Reader's digest

**(a) Original paper being reused.** Ruiz, F. J. R. et al. "Quantum circuit optimization with AlphaTensor." *Nat. Mach. Intell.* 7, 374 (2025) (ref. 1; Google DeepMind). It claimed that AlphaTensor-Quantum, an AlphaZero/AlphaTensor-style RL agent that casts T-count minimisation as decomposition of a circuit's symmetric signature tensor (with optional "gadgets" that use ancilla qubits, and symmetrised axial attention), gets lower T counts than earlier optimisers on benchmark arithmetic circuits. The catch: it has to be trained separately for each circuit family.

**(b) What was reproduced.** They used DeepMind's public, partial re-implementation (TensorGame and network built on the open MCTX library rather than the unreleased AlphaZero/AlphaTensor code), with the default GitHub hyperparameters (batch 128 and 80 MCTS simulations, versus 2,048 and 800 in the original, which ran out of memory on a 40-GB A100). They tested the only 3 tensors that were released: Mod 5₄, NC Toff₃ and Barenco Toff₃.
- **Without gadgets:** all three match the reported values (7/13/13).
- **With gadgets:** Mod 5₄ matches (2). NC Toff₃ and Barenco Toff₃ do not: 12 versus 4 reported for both. Doubling the batch size and MCTS simulations gave 8 and 10.
- **Convergence and cost:** runs converge in about 3,000 steps (100–1,000 s). Time per training step grows exponentially with qubit number (about 34 s/step at 15 qubits on an A100), whereas the PyZX+TODD baseline takes about 0.06 s.
- **Not reproducible:** anything else, because there is no circuit-to-tensor code and no per-experiment hyperparameters.

**(c) What is new.** A new task: a "general agent" trained on random CNOT+T circuits with 5–8 qubits, which needs no retraining for a new circuit. They compare it with 4 per-qubit "single agents" and 3 training regimes (Demo only, RL only, Demo+RL). Each regime gets 100k steps, and each qubit number has 1,000 evaluation circuits. They add a new metric, the "improvement percentage" (the share of circuits with a strictly lower T count than the baseline).
- The general agent gets a lower mean T count than the single agents for every training type. Demo+RL is best and beats the baseline on average.
- The improvement percentage is above 45% for all agents. It falls with size: roughly 73% at N=5 down to about 23% at N=8. At N=8 every agent's average T count is worse than the baseline.
- Inference takes 19.4–22.8 s per circuit (a single rollout).
- On the 3 benchmark circuits, which the agent never saw, the Demo general agent matches all the reported optima (7/13/13 and 2/4/4).
- Robustness: results without gadgets are in Supplementary Fig. 2 (same trend). A single agent trained on all 3 released circuits performs the same (Supplementary Fig. 1).

**(d) Narrative arc.** (1) T count matters, and AlphaTensor-Quantum is strong but costly and tied to circuit families. (2) The original infrastructure cannot be accessed, but the partial public code reproduces the small cases, with a gap for gadgets. (3) Runtime scaling shows the cost explodes with qubit number, so per-circuit training only pays off for key primitives. (4) The fix: train once on random circuits of mixed size, giving a general agent. (5) It beats single agents and often beats the baseline, it is fast at inference, and it even recovers the benchmark optima. (6) It is a "middle ground" between classical optimisers and per-circuit AlphaTensor-Quantum, and could scale with more compute.

**(e) Figure jobs.**
- **Fig 1:** the reproduction scorecard (table plus training curves).
- **Fig 2:** cost and scaling argument (time per step versus qubits, against the baseline).
- **Fig 3:** the main new result (general vs single agents, training regimes, versus the baseline, broken down by N).
- **Fig 4:** efficiency payoff (inference and training time).
- **Table 1:** zero-shot transfer of the general agent back to the reproduction benchmarks, which closes the loop with Fig 1.

**(f) Tone.** Constructive and supportive with measured criticism.
- They blame the gaps on missing code, hyperparameters and compute rather than on flaws in the method ("further hyperparameter tuning could probably reproduce the original findings").
- They praise the code ("well documented and easy to use") while asking for exact hyperparameters and code.
- Limitations are phrased softly with hedges ("probably", "could be improved by hyperparameter tuning and longer training"). They stress that the results needed no tuning and used orders of magnitude less compute.
- The conclusion presents the general agent as a promising middle ground and suggests scaling up compute as the way forward.

**Structure stats.** About 4,300 words in total including references and boilerplate; the main text, Methods and captions are about 2,700. There are 4 main figures and 1 table, with no Extended Data (Supplementary Figs 1–2 are cited but not in the PDF), and 27 references. Headings: (untitled intro) / Reproducibility / Generalizability / Conclusion and discussion / Methods (Hyperparameters for reproducibility experiments; Dataset generation and training process for generalizability experiments) / Data availability / Code availability / References / Acknowledgements / Author contributions / Funding / Competing interests / Additional information.

**Minor artefacts noticed in the original:**
- "AlphaZero-Quantum" is written where AlphaTensor-Quantum is meant.
- "although potentially requiring some hyperparameter" is missing a word, presumably "tuning".
- Ref. 23 is cited in the text as MCTX, but the list entry is JAX (Bradbury et al.).
- Most of the Methods "Dataset generation" text repeats the Generalizability section word for word.

---

## Abstract

Quantum computing has the potential to solve problems that are intractable for classical computers, with possible applications in areas such as drug discovery and high-energy physics. However, the practical implementation of quantum computation is hindered by the complexity of executing quantum circuits on hardware. In particular, minimizing the number of T gates is crucial for implementing efficient quantum algorithms. AlphaTensor-Quantum¹ is a reinforcement-learning-based method designed to optimize the T count of quantum circuits by formulating the problem as a tensor decomposition task. Although it has demonstrated superior performance over existing methods on benchmark quantum arithmetic circuits, its applicability has so far been restricted to specific circuit families, requiring separate, time-intensive training for each new application. This report reproduces some of the key results of the original work and extends AlphaTensor-Quantum's capabilities to simplify random quantum circuits with varying qubit counts, eliminating the need for retraining on new circuits. Our experiments show that a general agent trained on five- to eight-qubit circuits achieves greater T-count reduction than previous methods for a large fraction of quantum circuits. Furthermore, we demonstrate that a general agent trained on circuits with varying qubit numbers outperforms agents trained on fixed qubit numbers, highlighting the method's generalizability and its potential for broader quantum circuit optimization tasks.

## Introduction (untitled in the original)

Reinforcement learning (RL)² is a framework for discovering optimal action sequences in decision-making problems in which the best strategy is unknown and often non-trivial. In recent years, deep RL has transformed problem-solving across multiple fields, such as robotics³, drug discovery⁴ and game playing, where AlphaZero⁵ surpassed human experts in board games such as Go and chess. This approach was later extended to tackle problems in the field of mathematics, where AlphaZero was adapted to discover a more efficient and provably correct algorithm for matrix multiplication⁶. The resulting agent, AlphaTensor, was trained to play a TensorGame with the goal of finding efficient tensor decompositions.

Quantum computation is an emerging technology promising exponential speed-ups over classical computation for certain problems such as cryptography⁷ and quantum simulation⁸. This has potentially extensive implications, from securing communications⁹ to advancing drug discovery¹⁰. However, a major bottleneck in practical quantum computing is the complexity of the quantum circuits required to implement quantum algorithms. In particular, the T gate—a fundamental quantum logic gate—is one of the most resource-intensive to implement¹¹˒¹². Despite this, T gates are essential for achieving universal quantum computation¹³. Therefore, reducing the T count of quantum circuits is crucial before implementing them on quantum hardware.

Several methods have been developed for optimizing quantum circuits¹⁴⁻¹⁷, including machine learning¹⁸ and RL techniques¹⁹⁻²¹. More recently, AlphaTensor-Quantum¹ extended AlphaTensor's capabilities into the field of quantum computing by formulating T-count optimization as a tensor decomposition problem. Unlike AlphaTensor, AlphaTensor-Quantum can incorporate domain-specific knowledge by using gadgets, which is a procedure to reduce T gates by using ancillary qubits, to enhance optimization efficiency. Additionally, AlphaTensor-Quantum introduces symmetrized axial attention layers in its neural network, which take advantage of the signature tensor's symmetry, thereby allowing it to scale to larger qubit numbers.

On a benchmark of quantum arithmetic circuits, AlphaTensor-Quantum has been shown to achieve a lower T count than previous existing methods, particularly when gadgets are incorporated. However, its training is limited to specific quantum circuits grouped by application. This means that the model must be retrained for each new type of application, resulting in increased computational cost. In this paper, we first evaluate the reproducibility of AlphaTensor-Quantum's results. We then extend its application to a more general quantum circuit optimization problem: training a single agent capable of optimizing random quantum circuits with varying numbers of qubits and gates. This approach enables faster optimization without the need for retraining on each new circuit. The general agent achieves a lower T count on a large fraction of circuits compared with the baseline and the agents trained on fixed qubit sizes.

## Reproducibility

The original publication on AlphaTensor-Quantum relies on AlphaTensor, which, in turn, builds on AlphaZero. Unfortunately, neither the code for AlphaZero nor AlphaTensor has been made publicly available at this time. In addition, the in-house computing resources and infrastructure being used at Google DeepMind for this project are beyond the scale and sophistication of what is available in an academic context.

Nevertheless, we have made (slightly revised) parts of their code available in a GitHub repository²², which includes implementations of the TensorGame and their neural network architecture, integrated into the publicly available Monte Carlo tree search (MCTS) framework MCTX²³ (as a replacement for AlphaZero). Again, we emphasize that the results presented in this paper were not obtained using this specific MCTS framework, and the implementation details differ, which may explain some of the discrepancies observed in our numerical experiments.

*[Transcription note: the sentence "we have made (slightly revised) parts of their code available" appears verbatim in the PDF. Ref. 22 is DeepMind's repository, so the "we" is odd, but it is kept as printed.]*

In addition to the code, the signature tensors for the circuits Mod 5₄ (five qubits), NC Toff₃ (seven qubits) and Barenco Toff₃ (eight qubits) from table 2 of ref. 1 are provided for testing in the GitHub repository. In the following, we aim to reproduce the results for these three circuits. Reproducing other findings proved challenging, as the authors of ref. 1 do not provide the code to generate signature tensors from a quantum circuit and do not specify the exact hyperparameters used for each experiment. The Methods discusses the hyperparameters.

We present the optimized T count and training time in Fig. 1a. We observe that the T count for NC Toff₃ and Barenco Toff₃ with gadgets is higher than that originally reported. By doubling the batch size and the number of MCTS simulations, the T count is reduced to 8 for NC Toff₃ and 10 for Barenco Toff₃, suggesting that further hyperparameter tuning could probably reproduce the original findings. It is also worth noting that in the original paper, AlphaZero-Quantum is trained on a family of circuit applications. For example, for the Barenco Toffoli application, AlphaZero-Quantum is trained on the Barenco Toff₃, Barenco Toff₄, Barenco Toff₅ and Barenco Toff₁₀ circuits. By contrast, in our case, the optimization of Barenco Toff₃ is trained only based on the Barenco Toff₃ circuit, because the circuits or the tensor representation of the circuits are not available. Figure 1b shows the evolution of T count throughout training. The T count converges after approximately 3,000 training steps, which takes between 100 and 1,000 s depending on the number of qubits. Additionally, we train a single agent to simultaneously simplify all the provided circuits, achieving the same performance (Supplementary Fig. 1).

> **Figure 1 caption (verbatim).** **Reproducing AlphaTensor-Quantum.** **a**, T count reported in the original paper along with the results from experiments using the provided code. The training time to reach optimal performance on an NVIDIA A100 GPU is given in the parentheses. The red numbers indicate where our experimental results do not match the originally reported values (see the main text). **b**, Evolution of T count during training. The light solid lines represent the reported result.

Figure 1a (table embedded in figure):

| Circuit (line style in b) | Without gadgets: Reported | Without gadgets: Experiment | With gadgets: Reported | With gadgets: Experiment |
|---|---|---|---|---|
| Mod 5₄ (red dotted) | 7 | 7 (104.7 s) | 2 | 2 (104.3 s) |
| NC Toff₃ (green dashed) | 13 | 13 (675.6 s) | 4 | **12** (576.2 s) *(red in original)* |
| Barenco Toff₃ (blue dash-dot) | 13 | 13 (1,158.5 s) | 4 | **12** (2,829.3 s) *(red in original)* |

### Figure 1 — visual analysis

- **Panel a (result, table).** A four-column comparison of reported and experimental T counts, split by without/with gadgets. Training time on an A100 is given in parentheses, and mismatches are printed in red. Each circuit row carries a coloured line-style key that links it to the curves in panel b: red dotted for Mod 5₄, green dashed for NC Toff₃, blue dash-dot for Barenco Toff₃.
  - Numbers: all six cells listed in the table above.
  - **Only in the figure:** the T count of 12 for both failing circuits and all six training times (104.7, 675.6, 1,158.5, 104.3, 576.2 and 2,829.3 s). The text only gives the range "between 100 and 1,000 s", even though Barenco Toff₃ with gadgets took 2,829.3 s, which is outside that range.
  - The follow-up values from doubling the batch size and MCTS simulations (8 and 10) are given only in the text, not in the figure.
  - Message: 4 of 6 settings reproduce exactly; with gadgets, the two larger circuits fall well short (12 versus 4).
- **Panel b (result, training curves).** Two stacked line plots (top: without gadgets, bottom: with gadgets). The y-axis is T count (ticks at 0 and 25) and the x-axis is training steps (0–about 50,000, ticks at 0, 20,000 and 40,000). There is one curve per circuit, with thick light horizontal lines showing the reported values.
  - Without gadgets: all curves drop from about 25–40 to their final values within a few thousand steps. The two Toffoli curves sit on the light reported line at 13, and Mod 5₄ sits on its reported line at about 7.
  - With gadgets: Mod 5₄ reaches about 2, on its reported line. The NC and Barenco curves plateau at about 12, clearly above the light reported line at 4. NC Toff₃ shows a short shoulder at about 14 before settling.
  - No error bars; single runs.
  - Message: training converges quickly (about 3,000 steps) and then stays flat, so the gadget gap is a plateau, not a matter of training too briefly.
- **Figure 1 overall:** the reproduction scorecard. A partial success that sets up the paper's balanced verdict: the method is reproducible at small scale, but matching the gadget results needs hyperparameters and compute that are unavailable.

Since the provided example tensors correspond to small numbers of qubits, we also examine the expected runtime of AlphaTensor-Quantum for larger circuits. In Fig. 2, we illustrate how the training time of AlphaTensor-Quantum scales with the number of qubits on different GPU devices using the provided hyperparameters. In this case, we fixed the task to optimize a random circuit in which the number of gates is fixed to be ten times the number of qubits and half of them are T gates. We observe that the training time for AlphaTensor-Quantum increases exponentially. This is probably due to the exponentially increasing number of possible actions for AlphaTensor-Quantum. In the original paper¹, the amount of sampled actions is, therefore, kept to a fixed maximum number, which is not implemented in the provided code. The baseline method using PyZX¹⁴˒²⁴ and TODD¹⁵ is several orders of magnitude faster than AlphaTensor-Quantum, which requires training for tens of thousands to several millions of steps per optimized circuit. Consequently, the computational overhead of running AlphaTensor-Quantum is probably justified only for important quantum circuit primitives that serve as building blocks for numerous applications.

> **Figure 2 caption (verbatim).** **Average time for one step of AlphaTensor-Quantum training with gadgets on different GPU devices.** Quadro RTX 6000 and Tesla V100 give an out-of-memory error for 15 qubits. We compare with the baseline PyZX¹⁴ and TODD¹⁵, which directly output the optimized circuit in the given time (for example, around 0.06 s for 15 qubits). By contrast, AlphaTensor-Quantum requires a large number of training steps (for example, between tens of thousands and several millions of steps in the original paper). Error bars, corresponding to one standard deviation across ten different circuits, are smaller than the marker size.

### Figure 2 — visual analysis

- **Single panel (result, line plot).** The x-axis is the number of qubits (5–15; ticks at 6, 8, 10, 12, 14). The y-axis is time in seconds per training step (0–about 42; ticks at 0, 10, 20, 30, 40).
  - Four series: Quadro RTX 6000 (red dotted, up-triangles), Tesla V100 (green dashed, down-triangles), A100 (blue dash-dot, crosses) and Baseline PyZX+TODD (black solid, filled circles). The colours echo the line styles of Fig. 1.
  - Error bars are ±1 s.d. over 10 circuits and are invisible (smaller than the markers).
  - Approximate values read from the plot (**none of these are in the text**):
    - Quadro: about 2.9 s at 10 qubits, 5.6 at 11, 10.7 at 12, 21 at 13 and 41.3 at 14.
    - V100: about 2.3, 4.2, 7.4, 14.8 and 29.5 at 10–14 qubits.
    - A100: about 1.5, 2.6, 4.6, 8.9, 17.2 and 33.7 at 10–15 qubits.
    - All GPUs are below about 1 s up to 9 qubits.
    - Baseline is flat at about 0; the caption quotes about 0.06 s at 15 qubits.
  - The Quadro and V100 series stop at 14 qubits because they run out of memory at 15.
  - No statistical test.
  - Message: the cost of each training step grows exponentially with qubit count and is orders of magnitude above the classical baseline's total runtime.
- **Figure 2 overall:** the cost argument. It shows why per-circuit training does not scale, and so motivates training one general agent instead (the next section).

## Generalizability

To improve the optimization efficiency of AlphaTensor-Quantum by eliminating the need for retraining on previously unseen circuits, we train it to simplify random quantum circuits spanning multiple qubit sizes. We refer to this agent as the general agent. We then compare its performance with agents trained separately for each qubit size. We refer to these agents as single agents. Note that the single agents are already more general than the AlphaTensor-Quantum agents used in ref. 1, which are trained on specific quantum circuit applications.

In our experiments, we use quantum circuits with five to eight qubits. Therefore, we train one general agent across all these qubit numbers and four separate single agents, each for a specific qubit number. AlphaTensor-Quantum is originally trained using a combination of supervised learning on synthetic demonstrations and RL on the target circuits. The dataset comprising synthetic demonstrations consists of randomly generated tensor/factorization pairs for the neural network to imitate. To evaluate the contribution of these components, we train our agents either only with synthetic demonstration data (Demo), only with RL data (RL) or with both (Demo + RL). The Methods provides details of the dataset generation and training process. For RL and Demo + RL, we use 100,000 random circuits for RL. We first focus on the AlphaTensor-Quantum version that includes gadgetization (Supplementary Fig. 2 shows the results without gadgetization). We train AlphaTensor-Quantum with the default hyperparameters for 100,000 steps. For each considered qubit number, we generate 1,000 random quantum circuits as the evaluation set. During evaluation, we always choose the most probable action predicted by the MCTS policy. As a baseline, we optimize these circuits with PyZX¹⁴ and then apply TODD¹⁵, as done in ref. 1.

We first evaluate the average T count in Fig. 3a for single and general agents trained with the three training types. The general agent consistently outperforms the single agents across all training types. Additionally, the Demo + RL agent achieves the lowest average T count, falling below the baseline, indicating that the mix of supervised demonstration and RL training is useful. Figure 3b presents the performance of the agents across different qubit sizes. As expected, the average final T count grows with the qubit number since the sampled initial circuits contain more T gates. However, the optimization is increasingly less effective compared with the baseline with a higher qubit count. In particular, the agents outperform the baseline for N = 5 and N = 6. However, the performance declines at N = 7, except when using Demo + RL training, and further deteriorates at N = 8, where all agents perform worse than the baseline on average, with only about 23% improvement. The performance could be improved by hyperparameter tuning and longer training.

Although Fig. 3a,b demonstrates the average T-count reduction, this alone does not fully capture how consistently the agents outperform the baseline. To address this issue, we introduce the improvement percentage metric, which measures the fraction of circuits in the evaluation set in which the agent achieves a strictly lower T count than the baseline. It is important to note that the input to the AlphaTensor-Quantum is already a circuit that is optimized with PyZX following the compilation method described in ref. 1. Figure 3c shows that all agents, in general, achieve an improvement above 45% compared with the baseline, with Demo + RL again outperforming the other training types. The general agent surpasses the single agent overall, except with the Demo + RL training type. Figure 3d further confirms that the trend discussed before that the improvement percentage declines as the circuit size increases. A significant improvement is observed for N = 5 and N = 6, whereas it diminishes for N = 7 and N = 8. A similar trend is observed for AlphaTensor-Quantum without gadgetization (Supplementary Fig. 2).

> **Figure 3 caption (verbatim).** **Evaluation of single (random circuits, fixed qubit number) and general (random circuits, varying qubit number) AlphaTensor-Quantum agents with gadgetization and three training types (Demo, only with RL and Demo + RL).** **a**, Average T count (lower is better) of the optimized quantum circuits in the evaluation set. The solid black line shows the average T count of the baseline method PyZX¹⁴ and TODD¹⁵. **b**, Average T count for each number of qubits. **c**, Average improvement percentage (higher is better), which shows the percentage of circuits that have a strictly lower T count when optimized with the agent compared with the baseline method. **d**, Average improvement percentage for each number of qubits. The error bars for **a** and **c** show the 95% confidence intervals over different numbers of qubits and for **b**, the 95% confidence intervals over 1,000 evaluation circuits.

### Figure 3 — visual analysis

All values below are approximate readings from the bars. The text gives only qualitative statements plus ">45%" and "about 23%".

- **Panel a (result, grouped bar chart).** The x-axis has three training types (Demo, RL, Demo+RL). The y-axis is mean T count (0–about 22). Bars are dark blue for the general agent and light blue for the single agent, with a horizontal black "Baseline" line at about 9.7. Error bars are 95% CI across qubit numbers, so n=4 qubit sizes, which explains why they are wide.
  - Demo: general about 18.9, single about 20.3.
  - RL: general about 9.8, single about 20.3. This is the largest general-versus-single gap.
  - Demo+RL: general about 9.1, single about 9.3. Both are below the baseline.
  - No significance tests.
  - Message: the general agent never does worse than the single agent, and only Demo+RL clearly beats the baseline on average.
- **Panel b (result, grouped bar charts, two sub-plots).** Left sub-plot: general agent; right: single agent. The x-axis is N = 5, 6, 7, 8 and the y-axis is mean T count (0–50). Bars: Demo (blue), RL (orange), Demo+RL (green), Baseline (red). Error bars are 95% CI over 1,000 circuits.
  - General agent (Demo / RL / Demo+RL / Baseline):
    - N5: about 5.2 / 5.2 / 5.2 / 7.0
    - N6: about 7.7 / 7.3 / 7.4 / 9.0
    - N7: about 15.2 / 10.2 / 10.0 / 10.8
    - N8: about 47.5 / 17 / 14.3 / 12.7
  - Single agents (Demo / RL / Demo+RL / Baseline):
    - N5: about 5.4 / 5.4 / 5.2 / 7.2
    - N6: about 8.1 / 8.1 / 7.1 / 9.2
    - N7: about 19 / 19 / 9.7 / 11.1
    - N8: about 48.7 / 48.7 / 15.8 / 12.7
  - Observation from the figure only: for the single agents, the Demo and RL bars look nearly identical at every N.
  - The Demo agent blows up at N=8, with a T count of about 48 against a baseline of about 13. The text does not mention this explicitly, and it drives the high Demo means in panel a.
  - Message: the agents beat the baseline at small N, and the advantage vanishes or reverses by N=8, most dramatically for Demo.
- **Panel c (result, grouped bar chart).** Same layout as panel a. The y-axis is improvement percentage (0–75) and error bars are 95% CI across qubit numbers.
  - Demo: general about 52.5%, single about 47%.
  - RL: general about 51.5%, single about 47.5%.
  - Demo+RL: general about 55.5%, single about 57.5%. Here the single agent is higher.
  - Message: on any given circuit, the agents beat the PyZX+TODD baseline about half the time; Demo+RL is best.
- **Panel d (result, grouped bar charts, two sub-plots).** Improvement percentage by N for the general agent (left) and single agents (right). Same colours as panel b, no error bars, no baseline bar.
  - General agent (Demo / RL / Demo+RL):
    - N5: about 73 / 73 / 73
    - N6: about 67 / 70.5 / 69
    - N7: about 44.5 / 47.5 / 50
    - N8: about 24.5 / 14 / 28.5. The mean of about 22% matches the text's "about 23%".
  - Single agents (Demo / RL / Demo+RL):
    - N5: about 68 / 68 / 74
    - N6: about 57 / 57 / 79
    - N7: about 40.5 / 40.5 / 57
    - N8: about 25.5 / 28 / 20
  - **Only in the figure:** all of these per-N values. Notably, the single-agent Demo+RL reaches about 79% at N=6, the highest value in the figure, and that is where the single agents beat the general agent.
  - Message: the share of circuits improved drops steadily as N grows, from about 70–75% to about 15–30%.
- **Visual design:** a 2×2 layout, with summary panels (a, c) on the left and per-N breakdowns (b, d) on the right. There are two separate colour schemes: blue shades for general/single and a tab10-style palette for training types. The legends sit at the bottom.
- **Figure 3 overall:** the core new result. Training once on mixed-size random circuits gives an agent that is at least as good as size-specific agents and often beats the classical pipeline, but its advantage shrinks as qubit number grows.

A key advantage of our agents is their fast execution time during evaluation. Unlike the original AlphaTensor-Quantum, which requires retraining for each circuit, a process that can take from a few minutes to several hours, our pretrained agents simplify circuits in a single rollout, averaging around 20 s (Fig. 4a).

> **Figure 4 caption (verbatim).** **Evaluation of training time and evaluation time.** **a**,**b**, Average time required on a single NVIDIA A100 GPU to simplify a single circuit during evaluation (**a**) and to train the agents for 100,000 steps (**b**).

Figure 4a (table embedded in figure):

| Number of qubits | 5 | 6 | 7 | 8 |
|---|---|---|---|---|
| Time (s) | 19.36 | 20.10 | 21.83 | 22.84 |

### Figure 4 — visual analysis

- **Panel a (result, table).** Mean wall-clock time on an A100 to simplify one circuit, by qubit number: 19.36, 20.10, 21.83 and 22.84 s.
  - **Only in the figure:** these exact values. The text says only "averaging around 20 s".
  - No n or s.d. given; the evaluation set is presumably 1,000 circuits per N.
  - Message: inference is fast and nearly flat with N, compared with minutes to hours of per-circuit retraining.
- **Panel b (result, grouped bar chart).** The x-axis has "General agent" followed by single agents for N = 5, 6, 7, 8. The y-axis is training time in hours for 100,000 steps (0–20). Bars: Demo (blue), RL (orange), Demo+RL (green).
  - Approximate readings, Demo / RL / Demo+RL:
    - General: about 12.4 / 18.3 / 12.2 h
    - N5: about 5.7 / 5.8 / 6.2 h
    - N6: about 5.8 / 5.7 / 6.2 h
    - N7: about 7.5 / 7.5 / 8.1 h
    - N8: about 12.0 / 9.7 / 13.6 h
  - **Only in the figure, and not discussed in the text:**
    - All the training-time values.
    - Training one general agent (about 12–18 h) costs less than training the four single agents combined (about 31–34 h for Demo+RL).
    - General-agent RL is the most expensive configuration.
  - No error bars.
  - Message: training costs a one-off half-day budget, comparable to a single 8-qubit agent.
- **Figure 4 overall:** the efficiency payoff. It backs the "orders of magnitude faster than retraining" claim and positions the general agent as practical.

Finally, in Table 1, we evaluate our general agents on the three target circuits in Fig. 1, which the agents never encountered before during training. The Demo agent finds the optimal T count both with and without gadgets, whereas the other two methods perform slightly worse.

**Table 1 | T count after optimizing benchmark circuits with the general agent trained using different training methods**

| Setting | Method | Mod 5₄ | NC Toff₃ | Barenco Toff₃ |
|---|---|---|---|---|
| Without gadgets | Reported | 7 | 13 | 13 |
| Without gadgets | Demo | **7** | **13** | **13** |
| Without gadgets | RL | **7** | 14 | 14 |
| Without gadgets | Demo + RL | 8 | 14 | 14 |
| With gadgets | Reported | 2 | 4 | 4 |
| With gadgets | Demo | **2** | **4** | **4** |
| With gadgets | RL | 7 | 15 | 13 |
| With gadgets | Demo + RL | 6 | 14 | 12 |

*Bold numbers indicate number matches with the reported values.*

### Table 1 — visual analysis

- **Role:** result. Zero-shot transfer of the general agent to the three benchmark circuits.
  - Visual design: the "Without gadgets" and "With gadgets" blocks are separated with beige shading, and matches are shown in bold.
  - **Numbers mostly only in the table:**
    - RL without gadgets gives 7/14/14.
    - Demo+RL without gadgets gives 8/14/14.
    - With gadgets, RL gives 7/15/13 and Demo+RL gives 6/14/12, both far from the reported 2/4/4.
  - The text calls this "slightly worse". That fits the no-gadget rows, but with gadgets the gap is large: for example 15 versus 4, and 7 versus 2.
  - Note that the Demo general agent (2/4/4) beats the per-circuit reproduction in Fig. 1a (2/12/12).
  - Message: a general agent trained only on demonstrations recovers the original paper's optima without any per-circuit training.
- **Table 1 overall:** closes the loop with Fig. 1. The general approach can match the original's headline numbers that direct reproduction missed.

## Conclusion and discussion

In this work, we first assess the reproducibility of AlphaTensor-Quantum¹. We find that the reproduction of small-scale experiments is feasible, although potentially requiring some hyperparameter. We then study the generalizability of AlphaTensor-Quantum for general quantum circuit optimization across different qubit sizes. Our approach eliminates the need for retraining on previously unseen circuits, accelerating the optimization process by orders of magnitude compared with the original AlphaTensor-Quantum approach trained on specific quantum circuit applications. From an application perspective, these agents can be integrated with traditional T-count optimizers to achieve further reductions in a large fraction of circuits.

Our experiments demonstrate that a general agent trained on circuits with varying qubit sizes outperforms single agents specialized for a fixed qubit size, highlighting its ability to generalize effectively to unseen circuits when trained on diverse data. The best results are obtained by combining supervised learning on demonstration data with RL. However, even agents trained solely on potentially suboptimal supervised demonstrations prove to be effective.

Note that the results presented in this paper are obtained without hyperparameter tuning and require several orders of magnitude less computation than the original AlphaTensor-Quantum training (for example, 10 times more training steps, 10 times more simulated trajectories per MCTS step, 16 times larger batch size and more than 3,600 tensor processing units used). This suggests a promising path for scaling to higher qubit numbers by increasing computational resources.

The code from ref. 22 is well documented and easy to use. Although this code differs from the code used to produce the results in ref. 1, the implementations of the symmetrized axial attention layers and the TensorGame environment provide valuable building blocks for future research. Integration with the MCTX MCTS library enables the rapid reproduction of some of the results from the original work. The additional GitHub repository²⁵ provides functionality to compute the signature tensor of a given quantum circuit and implements a post-processing pipeline to reconstruct the optimized circuits, which is crucial for their practical implementation. However, providing the exact hyperparameters and the exact code used in the original paper would enhance reproducibility and assist in choosing optimal hyperparameters for future work.

Looking ahead, AlphaTensor-Quantum has the potential to serve as a powerful framework for minimizing the T count of quantum circuit primitives when the computational cost is justified by their importance. Additionally, general agents such as those trained in this paper offer a promising middle ground between traditional T-count optimizers and the original AlphaTensor-Quantum approach, balancing computational efficiency and performance.

## Methods

### Hyperparameters for reproducibility experiments

In our experiments, we use the default hyperparameter given in the GitHub repository. For example, the batch size is 2,048 and the number of MCTS simulations is 800 in the original paper, whereas the GitHub implementation uses 128 for the batch size and 80 for the number of MCTS simulations. We have tried to use the hyperparameters from the original paper, but it gives an out-of-memory error. We run the experiments with the provided hyperparameters on a single NVIDIA A100 GPU with 40-GB memory.

### Dataset generation and training process for generalizability experiments

To create the training data, we generate random CNOT + T circuits with random number of qubits *N*, selecting the total number of gates uniformly between 5*N* and 15*N*, with T gates comprising between 20% and 60% of the total gate count. We then follow the quantum circuit compilation approach outlined in ref. 1, which applies an optimization algorithm in PyZX¹⁴ to reduce the initial T-gate count and extract the signature tensor as an input to AlphaTensor-Quantum. Additional details about compiling a general circuit into a circuit containing only CNOT + T gates are provided in supplementary section C.1 of ref. 1.

For RL and Demo + RL, we use 100,000 random circuits for RL. We first focus on the AlphaTensor-Quantum version that includes gadgetization (Supplementary Fig. 2 shows the results without gadgetization). We train AlphaTensor-Quantum with the default hyperparameters for 100,000 steps. For each considered qubit number, we generate 1,000 random quantum circuits as the evaluation set. During the evaluation, we always choose the most probable action predicted by the MCTS policy. As a baseline, we optimize these circuits with PyZX¹⁴ and then apply TODD¹⁵, as done in ref. 1.

## Data availability

The data for reproducing this work are available via Zenodo at https://doi.org/10.5281/zenodo.14887945 (ref. 26).

## Code availability

The code for reproducing this work is available via Zenodo at https://doi.org/10.5281/zenodo.17578393 (ref. 27).

## References

1. Ruiz, F. J. R. et al. Quantum circuit optimization with AlphaTensor. *Nat. Mach. Intell.* **7**, 374 (2025).
2. Sutton, R. S. & Barto, A. G. *Reinforcement Learning: An Introduction* 2nd edn (The MIT Press, 2018).
3. Tang, C. et al. Deep reinforcement learning for robotics: a survey of real-world successes. In *Proc. Thirty-Ninth AAAI Conference on Artificial Intelligence and Thirty-Seventh Conference on Innovative Applications of Artificial Intelligence and Fifteenth Symposium on Educational Advances in Artificial Intelligence* 3197 (AAAI Press, 2025).
4. Zhou, Z., Kearnes, S., Li, L., Zare, R. N. & Riley, P. Optimization of molecules via deep reinforcement learning. *Sci. Rep.* **9**, 10752 (2019).
5. Silver, D. et al. Mastering the game of Go without human knowledge. *Nature* **550**, 354 (2017).
6. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. *Nature* **610**, 47 (2022).
7. Shor, P. W. Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. *SIAM J. Comput.* **26**, 1484 (1997).
8. Daley, A. J. et al. Practical quantum advantage in quantum simulation. *Nature* **607**, 667 (2022).
9. Kimble, H. J. The quantum internet. *Nature* **453**, 1023 (2008).
10. Blunt, N. S. et al. Perspective on the current state-of-the-art of quantum computing for drug discovery applications. *J. Chem. Theory Comput.* **18**, 7001 (2022).
11. Campbell, E. T., Terhal, B. M. & Vuillot, C. Roads towards fault-tolerant universal quantum computation. *Nature* **549**, 172 (2017).
12. Beverland, M. E. et al. Assessing requirements to scale to practical quantum advantage. Preprint at https://arxiv.org/abs/2211.07629 (2022).
13. Nielsen, M. A. & Chuang, I. L. *Quantum Computation and Quantum Information* (Cambridge Univ. Press, 2010).
14. Kissinger, A. & van de Wetering, J. Reducing the number of non-Clifford gates in quantum circuits. *Phys. Rev. A* **102**, 022406 (2020).
15. Heyfron, L. & Campbell, E. T. An efficient quantum compiler that reduces T count. *Quantum Sci. Technol.* **4**, 015004 (2018).
16. Amy, M., Maslov, D. & Mosca, M. Polynomial-time T-depth optimization of Clifford+T circuits via matroid partitioning. *IEEE Trans. Comput.-Aided Design Integr. Circuits Syst.* **33**, 1476 (2014).
17. Abdessaeid, N. & Drechsler, R. *Reversible and Quantum Circuits: Optimization and Complexity Analysis* (Springer, 2018).
18. Daimon, S. et al. Quantum circuit distillation and compression. *Jpn. J. Appl. Phys.* **63**, 032003 (2024).
19. Fösel, T., Niu, M. Y., Marquardt, F. & Li, L. Quantum circuit optimization with deep reinforcement learning. Preprint at https://arxiv.org/abs/2103.07585 (2021).
20. Li, Z. et al. Quarl: a learning-based quantum circuit optimizer. *Proc. ACM Program. Lang.* **8**, 114 (2024).
21. Riu, J., Nogué, J., Vilaplana, G., Garcia-Saez, A. & Estarellas, M. P. Reinforcement learning based quantum circuit optimization via ZX-calculus. *Quantum* **9**, 1758 (2025).
22. DeepMind. alphatensor_quantum. *GitHub* https://github.com/google-deepmind/alphatensor_quantum (2025).
23. Bradbury, J. et al. JAX: composable transformations of Python+NumPy programs v.0.3.13 (2018); http://github.com/jax-ml/jax
24. Kissinger, A. & Van De Wetering, J. PyZX: large scale automated diagrammatic reasoning. *Electron. Proc. Theor. Comput. Sci.* **318**, 229 (2020).
25. Laakkonen, T. circuit-to-tensor. *GitHub* https://github.com/tlaakkonen/circuit-to-tensor (2025).
26. Zen, R., Naegele, M. & Marquardt, F. Data for optimizing T-count in general quantum circuits with AlphaTensor-Quantum. *Zenodo* https://doi.org/10.5281/zenodo.14887945 (2025).
27. Zen, R., Naegele, M. & Marquardt, F. Code for reusability report: optimizing T-count in general quantum circuits with AlphaTensor-Quantum. *Zenodo* https://doi.org/10.5281/zenodo.17578393 (2025).

## Acknowledgements

We thank J. Olle for fruitful discussions. This research is part of the Munich Quantum Valley, which is supported by the Bavarian state government with funds from the Hightech Agenda Bayern Plus.

## Author contributions

R.Z., M.N. and F.M. conceptualized and designed the study. R.Z. and M.N. coded and performed the experiments. R.Z., M.N. and F.M. interpreted the data. All authors wrote and revised the manuscript.

## Funding

Open access funding provided by Max Planck Society.

## Competing interests

All authors declare no competing interests.

## Additional information

**Supplementary information** The online version contains supplementary material available at https://doi.org/10.1038/s42256-025-01166-9.

**Correspondence** and requests for materials should be addressed to Remmy Zen.

**Peer review information** *Nature Machine Intelligence* thanks Elica Kyoseva and the other, anonymous, reviewer(s) for their contribution to the peer review of this work.

**License:** Open Access, Creative Commons Attribution 4.0 International (CC BY 4.0). © The Author(s) 2025.
