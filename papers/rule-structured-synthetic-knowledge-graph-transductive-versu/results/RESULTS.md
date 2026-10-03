# Results (5 seeds; numbers from results/tables and `rh values`)
- H1 supported: Path-MP MRR 0.988 vs TransE 0.658 transductive (paired p ~ 8e-6, rh compare). TransE has Hits@10 0.983 but Hits@1 0.424.
- H2 supported: TransE inductive MRR 0.011 (chance level); Path-MP 0.989 inductive, change +0.001 (p 0.79).
- H3 supported: fold-in 0.644 inductive (+0.633 vs frozen, p 6e-7), Path-MP +0.345 above fold-in (p 1e-5). Fold-in inductive ~ TransE transductive.
- H4 supported: 1 layer 0.004 (chance); 3 layers no difference detected (p 0.50 / 0.73); no query-edge removal 0.507 / 0.458.
- H5 supported for Path-MP (0.989, 0.934, 0.700, 0.292 at 100/75/50/25%); at 25% fold-in TransE has the higher mean (0.329), inconclusive (p 0.15).
Failure cases: Path-MP parent relation (0.964/0.960); TransE sibling/uncle (~0.49). The advisory `rh verdict` compares only against the oracle and is not informative here.
