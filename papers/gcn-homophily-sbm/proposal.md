# Proposal: when does message passing help on contextual SBM graphs?

**Question.** On a contextual stochastic block model (CSBM) with K=3 classes, N=900 nodes, mean degree 10, how do an MLP, a 2-layer GCN, a GCN with separate ego/neighbour weights (H2GCN idea) and label propagation (LP) rank as edge homophily h goes from 0 to 1 and feature informativeness mu in {0.5, 1, 2}? Is there a mid-homophily band where GCN < MLP?

**Setup.** Grid h in {0,0.1,...,1}, mu in {0.5,1,2}, 5 seeds (graph, features and split all resampled per seed). Metric: test accuracy (random 20/20/60 split, early stopping on validation). Uninformative-graph point is h=1/K=0.33.

**Hypotheses (tests fixed before the main runs).**
- H1 (mid-homophily dip): for h in {0.3,0.4,0.5} and mu=1, GCN test accuracy is below MLP. Test: paired two-sided t-test over the 5 seeds per cell (`rh compare`), alpha=0.05; supported if GCN-MLP is negative in the cells with p<0.05, inconclusive/refuted otherwise. Refuted if GCN >= MLP in all three cells.
- H2 (ego/neighbour separation fixes it): H2GCN is >= max(MLP, GCN) minus 0.02 absolute in every one of the 33 cells (mean over seeds). Refuted if some cell violates this.
- H3 (LP niche): LP is the best of the four only when h >= 0.8 and mu=0.5 (weak features); LP is worse than MLP for h <= 0.5. Refuted if LP wins at mu=2 or beats MLP at h<=0.5.
- H4 (crossover moves with informativeness): the lowest h at which GCN mean accuracy exceeds MLP mean accuracy is lower for weaker features (mu=0.5) than for stronger features (mu=2). Descriptive, from cell means at grid resolution 0.1; no inferential test.
- H5 (ablation): removing separation (tied weights) from H2GCN hurts at h in {0.1, 0.4} (mu=1) relative to full H2GCN; paired test as in H1. Adding 2-hop neighbourhoods is exploratory.

**Baselines.** MLP; GCN (Kipf & Welling); H2GCN-style (reimplemented, 1-hop, no jumping knowledge); LP (Zhou-style normalised propagation, alpha picked on validation). All in plain torch, same splits per seed; lr/dropout/weight decay chosen for the three trained models from the same 8-config grid on separate tuning graphs (seeds 100-102).

**Gap.** Many papers show GNN-vs-MLP results on benchmark graphs where homophily, feature quality, degree and splits are confounded; the CSBM lets one cross homophily with feature informativeness with all else fixed, which gives a controlled win-region map with seed-level uncertainty.
