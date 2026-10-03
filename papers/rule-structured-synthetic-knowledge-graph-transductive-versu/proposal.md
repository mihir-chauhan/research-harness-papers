# Proposal

## Question
On a synthetic family-tree KG (500 people; parent, sibling, grandparent, uncle/aunt derived by rules) how do TransE and a 2-hop path-based message-passing model (Path-MP) compare on held-out triples of the training graph (transductive) versus on a fresh graph with new entities (inductive), measured by filtered MRR?

## Hypotheses (tests registered before the main runs)
- H1: Path-MP > TransE in transductive MRR. Test: paired t-test over 5 seeds (`rh compare`), alpha 0.05. Refuted if TransE >= Path-MP or p >= 0.05.
- H2: TransE collapses on new entities (MRR near the random level) while Path-MP loses <0.05 MRR absolute. Refuted if TransE inductive MRR clearly above chance, or Path-MP drop >= 0.05.
- H3: Fold-in (fit new entity vectors with frozen relations) lifts TransE inductive MRR substantially but stays below Path-MP. Paired tests on the inductive task.
- H4: Depth 2 is needed: 1-layer Path-MP is worse, 3 layers not better; training without target-edge removal is worse. Groups sweep_layers, abl_nodrop vs main.
- H5: inductive Path-MP MRR degrades as the observed fraction of the new graph shrinks (group sweep_density, 0.25/0.5/0.75 vs 1.0).

## Method
Path-MP: NBFNet-style query-conditioned message passing, L=2 layers, sum aggregation, 1-vs-all cross-entropy, target-edge removal during training. Baselines (all reimplemented here): TransE; TransE+fold-in; a hand-written one-step Horn-rule oracle that applies the generative rules to the observed graph (reference, not a learner).

## Tasks / metrics
Tasks: transductive (held-out 10% of units of graph 1) and inductive (held-out 10% of graph 2, entities never seen). Filtered MRR (ties split evenly), Hits@1, Hits@10, per-relation MRR. 5 seeds; each seed = different graph pair and split.

## Tuning
TransE: margin {1,2,4} x norm {L1,L2}; Path-MP: epochs {3,6} x lr {0.003,0.01}; chosen on validation MRR of graph-1 val split with separate graph seeds 100,101.

## Risks
Rules are redundant, so the problem may be easy (ceiling effects); the study then reports where the models differ (TransE, sparsity, depth).
