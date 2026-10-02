# Results (second version, after the audit fix round)
All numbers: `results/tables/*.tex` (from `rh table`, `rh compare`, `analysis/make.py`; rebuild with `analysis/build.sh`) and `results/summary.md`.
Verdicts use the tests registered in `proposal.md`.

- **H1 (ESN longest VPT at 5000 samples, both tasks): refuted.** Lorenz-63: ESN 9.546 vs MLP 5.578 (ratio 1.71, paired p=3.6e-06) and GRU 3.787 (ratio 2.52, p=3.1e-05): supported on this task. Lorenz-96: ESN 2.115 < MLP 2.882 (delta -0.77, p=0.018); ESN > GRU 1.330 (p=0.002): refuted on this task. Rows: `main_systems.tex`, `tests.tex`.
- **H2 (clim_ok order differs from VPT order on at least one task): rule met formally, not treated as support.** Lorenz-63 clim_ok order GRU 0.860, ESN 0.850, MLP 0.810 vs VPT order ESN, MLP, GRU, so the registered rule is satisfied; but the clim_ok differences are within one seed std (paired p=0.654, 0.704) and Lorenz-96 is a three-way tie at 1.000. Read as: no measurable difference in the climate metric between the tuned systems.
- **H3 (best/worst seed-mean ESN VPT over rho > 2 on each task): supported.** 4.18 (Lorenz-63), 10.95 (Lorenz-96); `sweep_rho.tex`, seeds 0-2.
- **H4 (ESN VPT at N=1000 > N=100 on both tasks): supported.** 9.44 vs 6.80; 2.62 vs 0.34 (`sweep_size.tex`; paired p=0.015 and 0.007 in `summary.md`).
- **H5 (ESN longest mean VPT at 500 samples on both tasks): supported by the mean-ordering rule, weak.** Lorenz-63 5.92 vs MLP 5.20 (p=0.228), GRU 2.53; Lorenz-96 0.67 vs MLP 0.58 (p=0.372), GRU 0.05 (`sweep_ntrain.tex`, 3 seeds).
- Optimiser-step sweep (descriptive, no hypothesis; `sweep_steps.tex`): ESN/MLP ratio on Lorenz-63 2.74 at 4000 steps, 1.73 at the tuned 16000, 1.69 at 32000; on Lorenz-96 the MLP mean keeps rising to 3.49 at 32000 steps (tuned: 8000, 2.72), not significant with 3 seeds.
- Component ablations (`main_ablation.tex`, `tests.tex`): ESN without squared features loses VPT on both tasks (p=0.008, 0.002) and on Lorenz-96 all free runs leave the attractor region; GRU without input noise keeps VPT (p=0.657, 0.995) but on Lorenz-96 0.99 of its free runs leave the attractor region.
- `VERDICT.md` (advisory, from `rh verdict`) lists only the ESN ablation, because that command compares every ablation with the method row; the GRU ablation is compared with the GRU in `tests.tex`. Its ablation delta is pooled over both tasks.

Caveats: 3-5 seeds; small, unequal tuning grids with optima on grid edges; one small model per family; the first version of all groups is superseded in the registry (see `experiments/PROTOCOL.md`).
