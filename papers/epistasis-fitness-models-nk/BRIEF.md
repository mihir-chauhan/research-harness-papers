# How much epistasis can simple sequence-to-fitness models absorb? (simulated NK landscapes)

**Question.** On *simulated* random-neighbourhood NK landscapes, how do one-hot ridge (additive), pairwise-epistasis ridge, a small CNN and a small MLP trade off held-out Spearman and greedy-design success as K, alphabet size, sequence length and training size N vary?

**Decisions (author, no human available).** Main grid: (L,A) in {(15,4),(20,20)} x K in {0,1,2,4}, N=1000, 5 seeds (new landscape per seed); N sweep {250,500,2000,4000} (+1000 from main) on L15_A4_K2 and L20_A20_K1, 3 seeds; ablations on pair-feature penalty and an oracle interaction graph. Random-uniform train/test sequences, noiseless. K=3, other (L,A) combinations, and noise are out of scope (compute). Design step: best training sequence as parent, model ranks all single mutants, top 10 proposed.

**Hypotheses** H1-H5 with tests: see `proposal.md` (fixed before runs). **Baselines** reimplemented: Additive ridge, CNN, MLP, Random. **Metrics**: Spearman, design_hit, design_gain, fit time.
**Out of scope**: real proteins, language models, noise, extrapolation splits, active learning loops, any claim about biology.

**Deviations recorded after the runs.** The N sweep was run with 5 seeds (planned 3); only (L,A) = (15,4) and (20,20) were run, so L and A are confounded; see `experiments/PROTOCOL.md`.
