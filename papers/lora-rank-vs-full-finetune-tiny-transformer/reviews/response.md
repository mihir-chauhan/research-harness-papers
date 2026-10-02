# Response to audit

1. **Major, LoRA vs full FT at N=100/300.** Chose to remove the claim rather than re-tune per N. Abstract, conclusion, ablations text and RESULTS.md now say the comparison is inconclusive: paired t-tests over 3 seeds (recomputed from the registry: p = 0.24, 0.27 at N=100 for r=1, r=4; 0.14, 0.065 at N=300) are all above 0.05, and the full-FT rate was tuned at N=2000 only, so the ordering may depend on it. The auditor's lr 1e-3 probes are not in the registry and are not quoted.
2. **Minor, rank-failure artifacts.** Abstract, setup, results (H2) now say the LoRA rate was tuned at r=4 only and the failures at ranks 1, 2, 8 may be artifacts of reusing it. No per-rank re-tuning was run.
3. **Minor, grid edge.** Setup and limitations name the four systems (full, LoRA, last block, head) whose selected rates remain at the upper edge; only scratch is interior.
4. **Minor, H3.** Re-labelled "not supported, uninformative because of a floor effect" in results, abstract, introduction, RESULTS.md; limitations notes the single-task-token pretraining; contribution (i) softened.
5. **Minor, H1 rank >= 4.** Results H1 now states that rank 8 on reversal (0.941 vs 1.000) misses the margin, so H1 is shown for rank 4 only.
6. **Minor, Table III caption / 1/2000.** "By construction" replaced by "empirically"; the 0.0005 residual is explained as one input whose reversal equals its ascending sort.
7. **Minor, compute.** Setup reports 241 runs, ~54 min wall clock, 68 min summed, median 16 s (6-27 s 5-95th pct), pretraining runs 50-60 s, and that this exceeds the planned 45 min.
8. **Minor, Fig. 1 / bolding.** Text notes Fig. 1 omits from-scratch; Table I caption says bold/underline does not imply significance (ties at 0.997).
9. **Minor, uncited phrase.** "Low-data advantage of a restricted update" removed; also toned down "leaves accuracy on the table".
10. **Minor, VERDICT/research.yaml.** research.yaml ablation names are kept as run names because `rh check` resolves them against runs; RESULTS.md now notes that the VERDICT ablation rows read "missing" for that reason and that the deltas are in the custom tables.
