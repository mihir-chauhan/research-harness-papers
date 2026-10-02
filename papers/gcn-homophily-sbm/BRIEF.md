# When does message passing help? (contextual SBM study)

## Question
On contextual SBM graphs (K=3, N=900, mean degree 10, 16-d Gaussian features), over edge homophily h in {0,...,1} (step 0.1) and feature strength mu in {0.5,1,2}: where does each of MLP, GCN, an H2GCN-style ego/neighbour-separated GCN and label propagation win, and does GCN fall below the MLP at mid homophily?

## Hypotheses and tests
See proposal.md (H1-H5). Tests: paired t-test over 5 seeds per cell (H1, H5); cell-mean rules (H2, H3, H4).

## Method / baselines
All plain torch, reimplemented: MLP, GCN (Kipf&Welling), H2GCN-style (separate self/neighbour weights, 1-hop, no jumping knowledge), label propagation (Zhou-style, alpha chosen on validation). lr/dropout/weight decay chosen on separate tuning graphs from one shared grid.

## Tasks, metrics
33 cells (h x mu), 5 seeds, random 20/20/60 split, test accuracy at best-validation epoch.

## Ablations
H2GCN with tied self/neighbour weights; H2GCN with 2-hop neighbourhood (h in {0.1,0.4,0.9}, mu=1). Sensitivity sweep over mean degree if time allows.

## Decisions (open choices)
K=3 so the uninformative-graph point is h=1/3; uniform inter-class edges; H2GCN simplified (no jumping knowledge) to match the seed's "GCN with separate self and neighbour weights"; reference "method" for rh is GCN since no new method is proposed.

## Out of scope
Real benchmarks, deeper models, other heterophily methods (GPR-GNN etc.), large scale, theory.
