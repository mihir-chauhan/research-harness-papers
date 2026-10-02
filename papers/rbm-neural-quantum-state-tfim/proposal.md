# Proposal

## Question
On the periodic 1D TFIM (J=1, N=8-12), how do RBM wavefunctions at hidden density alpha in {1,2,4} compare with a mean-field product state and a Jastrow ansatz in energy error, order-parameter error and fidelity across the critical field, and how much does stochastic reconfiguration (SR) matter relative to plain SGD?

## Hypotheses (tests fixed before the main runs)
- H1 (ansatz): With SR, the RBM (alpha=2) has lower relative energy error than both mean-field and Jastrow on every task. Test: paired Wilcoxon/t-style comparison over 5 seeds from `rh compare` per task, plus the per-task mean ordering. Refuted if Jastrow-SR is not worse than RBM-SR(alpha=2) on some task with a clear margin (mean ordering reversed).
- H2 (optimiser): For the RBM (alpha=2), SR gives lower energy error than SGD at the same iteration and sample budget on every task. Refuted if SGD mean error <= SR mean error on any task.
- H3 (hidden density): With SR, energy error decreases monotonically with alpha in {1,2,4} on the critical-point tasks (Gamma=1). Refuted if alpha=4 mean error exceeds alpha=1 on N=8, 10 or 12.
- H4 (criticality): Magnetisation (|Mz|) and energy errors of mean-field and Jastrow peak near Gamma=1 on N=10. Refuted if the maximum error over the Gamma sweep is at |Gamma-1|>0.25 for the mean-field state.
- H5 (size): At Gamma=1 for RBM-SR the error does not grow from N=8 to N=12 (we only report, 3 sizes: inconclusive-by-design for trends).

## Method
Real-amplitude VMC: Metropolis sampling, local energy E_loc, gradient g=2<(E_loc-<E>)O>, update p<-p-eta g (SGD) or p<-p-eta (S+eps I)^{-1} g (SR). Ansaetze: mean-field exp(a.s); Jastrow exp(a.s+sum_{i<j}J_ij s_i s_j); RBM exp(a.s) prod_j 2cosh(b_j+W_j.s). Reference: sparse ED. Evaluation: exact enumeration of the variational state.

## Baselines
Mean-field, Jastrow (both reimplemented, trained with the same optimisers), plain SGD vs SR.

## Metrics
relative energy error (E-E0)/|E0|; |Mz| error; <sigma^x> error; infidelity; MC-estimated energy error as a consistency check.

## Novelty / honesty
Not a new method; a small controlled replication-style comparison. Closest work: [carleo2016solving]. No claim of novelty beyond the controlled grid.

## Amendments after registration (the hypotheses and tests above are unchanged)
- Learning-rate selection was revised twice (v1 -> v3; see `experiments/PROTOCOL.md`).
- After an independent audit of the single-start results: (a) the Jastrow ansatz is stored with one parameter per pair (N + N(N-1)/2), all Jastrow runs repeated; (b) every system is run from two starts (symmetric S and symmetry-broken B, a_i = 0.5 + noise) with the same rate and budget, and the lower-energy start is the reported state; the registered tests are applied to these selected states, and per-start results are reported as an ablation; (c) a sampling-free L-BFGS reference on the enumerated energy was added for mean-field, Jastrow and RBM alpha=2 to separate ansatz error from optimisation error.
