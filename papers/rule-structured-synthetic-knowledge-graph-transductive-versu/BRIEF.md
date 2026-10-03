# Rule-structured synthetic knowledge graph, transductive versus inductive

## Seed
Rule-structured synthetic knowledge graph, transductive versus inductive. Generate a family-tree knowledge graph (500 people, relations parent / sibling / grandparent / uncle derived by rules). Train TransE and a small path-based model (2-hop relational message passing) and test on held-out triples of the same graph and on a freshly generated graph with new entities; report MRR in both settings. Keep it a small CPU study with reimplemented baselines, at least 5 seeds where cheap, and report negative or mixed results plainly.

## Question
How do a tuned TransE, TransE with entity fold-in and a 2-layer query-conditioned relational message-passing model (Path-MP) compare in filtered MRR (a) on held-out triples of the training graph and (b) on an independently generated graph with new entities?

## Hypotheses (see proposal.md for tests)
H1 Path-MP > TransE transductively. H2 TransE collapses on new entities while Path-MP loses < 0.05 MRR. H3 Fold-in restores much of TransE's inductive loss but stays below Path-MP. H4 Path-MP needs depth 2 and query-edge removal during training. H5 Inductive Path-MP degrades as the observed fraction of the new graph shrinks.

## Method / baselines
Path-MP (NBFNet-style, reduced); TransE (reimplemented, tuned on validation graphs); TransE+fold-in; hand-written one-step rule oracle (reference).

## Tasks, metrics, protocol
Tasks: transductive, inductive. Filtered MRR (ties split evenly), Hits@1/10, per-relation MRR. 5 seeds, each seed = its own pair of 500-person graphs. 80/10/10 unit split; sibling pairs are one unit.

## Ablations
Depth (1, 2, 3 layers), no query-edge removal, observed-fraction sweep (25/50/75/100%).

## Decisions recorded (rh decide)
Uncle is gender-neutral (sibling of a parent); the inductive graph is a second independently generated 500-person graph split like graph 1; ties split evenly; TransE tuned in three rounds on validation graphs; Path-MP epochs tie broken toward the cheaper setting.

## Out of scope
Real benchmarks, new relations at test time, other embedding models (RotatE, ComplEx), GraIL/NBFNet/DRUM/ULTRA reimplementations, GPU.
