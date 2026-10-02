# Results (3 seeds, win rule: >=5% lower seed-mean MSE and lower in all seeds; numbers from results/runs.jsonl via experiments/analyze.py)
Verdicts are given per training budget. 400 steps is the registered plan; 1000 and 2000 steps are a post hoc budget sweep added after the audit.
Tables: results/tables/rel.tex (400 steps), budget.tex (400/1000/2000), sw_dwell.tex, sw_dwell2000.tex, sw_noise.tex, abl_design_full.tex.

- H1 supported where tested: no nonlinear win on seas1, trend, multiseas, noisy at 400 steps (all horizons) or at 2000 steps (H=96).
  Small differences are sign-consistent across seeds but below 5%, and their sign changes with the budget (GRU multiseas +9.6% -> -1.2%).
- H2 not supported as registered at any budget; partly supported from 1000 steps. 400 steps: no win (PatchTST -4.97% H24, -4.82% H96, +1.41% H192).
  1000/2000 steps on regime: PatchTST wins at H24 (-9.8%, -9.2%), GRU wins at H24 (-13.2%, -17.1%) and H96 (-7.4%, -10.6%); nobody wins at H192
  (GRU -2.3%, -1.5%, 2/3 seeds). Dwell sweep at 2000 steps: GRU -5.7% (win), -8.9% (2/3), -10.6% (win), -3.6%, +12.0% for dwell 100..4000: wins only
  for dwell <= 500, margin not monotone in switching rate.
- H3 mixed (400 steps only): PatchTST's above-threshold margin (-9.3% at noise 0.1) vanishes with noise but a small 3/3-seed edge stays;
  the GRU gap moves the other way (+8.4% at 0.1 to -2.1% at 3.0).
- H4 supported at all three budgets: on ETTh1 no nonlinear win; at H96/192 DLinear better in all seeds (2000 steps: PatchTST +7.6%/+9.3%, GRU +2.9%/+6.8%);
  all learned models beat seasonal naive.
- H5 supported (400 steps): no-decomposition -0.2% (trend), +0.2% (regime), +1.9% (etth1).
- DLinear is converged at 400 steps (MSE changes by <= 0.004 on regime/etth1 up to 2000 steps); the GRU is not.
- Exploratory (400 steps): removing instance norm lowers MSE on regime for all models; on trend the mean increases are driven by seed 1
  (median per-seed change +8.8% DLinear, +134% PatchTST, +805% GRU).
