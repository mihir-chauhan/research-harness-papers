# Lattice-protein design toy (brief)

**Seed.** Enumerate all self-avoiding conformations of 2D HP chains of length 16, compute ground states, train a sequence model to design sequences that fold uniquely to a target, compare a conditional autoregressive model with simulated annealing on the fraction of designs whose ground state is the target. Small CPU study, >=5 seeds, report negative/mixed results.

**Question.** On the exactly solvable 2D HP lattice (N=16), at an equal and explicit budget of ground-state-oracle calls per design, does a conditional autoregressive designer trained on (conformation, sequence) pairs generalise to held-out target conformations better than simulated annealing, and what drives its success?

**Decisions taken (recorded with `rh decide`).**
- Conformations are counted modulo rotation/reflection (802,075). Ground states of all 2^16 sequences are computed exactly by full enumeration (an exact oracle, table lookup).
- Success = the design's minimum-energy conformation is unique and equals the target. Budget K = number of oracle evaluations a method may use per design; the design returned is the best of K candidates under the same objective f (energy gap to the target plus a degeneracy penalty) for every system.
- Splits are by chain-reversal class: reading a chain backwards maps a conformation and its designing sequence to another valid pair, so a conformation and its reverse never straddle train/test (an earlier split without this leaked; see paper).
- A fixed DEV partition (20% of classes, seed-independent) is used only for tuning; per seed, 25% of the remaining classes are test targets.

**Hypotheses.** H1 (K=1: AR > random, contact heuristic), H2 (K=100: AR > SA), H3 (K=1000: SA >= AR), H4 (conditioning matters), H5 (reversal augmentation / more scored sequences help). Tests as in `proposal.md`.

**Systems.** Conditional AR designer (ours; transformer encoder-decoder), simulated annealing (reimplemented), random search, contact heuristic. Ablations: unconditional AR, no reversal augmentation, data-fraction sweep. Metrics: succ_k{1,10,100,1000} (fraction of held-out targets designed uniquely), per-regime (targets with one vs several designing sequences).

**Out of scope.** Other N, 3D lattices, other alphabets, real proteins, structure-prediction oracles, diffusion/RL designers.
