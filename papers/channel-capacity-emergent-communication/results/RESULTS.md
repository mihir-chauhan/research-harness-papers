# Results (3 seeds, 6000 steps; tables: results/tables/main_core.md, sweep_vocab.md, sweep_length.md)
- H1 partly supported: <8 bits -> near-zero accuracy, but 10 bits is also near-zero at this budget (optimisation-limited).
- H2 refuted/untestable: V16_L8 generalises better (held-out 0.436 Gumbel, 0.500 REINFORCE) than V4_L4 (0.013); tight channel not trained.
- H3 supported: topsim 0.10-0.36 learned vs 1.000 oracle; oracle reaches 0.846 held-out at V16_L8 (reference listener imperfect).
- H4 not supported: Gumbel vs REINFORCE within noise (V16_L8 Welch p=0.72).

## Addendum (audit round): tight-channel training dynamics
Group abl_longtrain (V4_L4, 20000 steps, 3 seeds, curves in results/raw/curve_*.csv, summary in results/tables/curve_summary.tex).
- Gumbel-softmax at V4_L4 is unstable, not under-trained: train accuracy peaks at 0.239-0.291 (steps 600-1400) then collapses; at 20000 steps train 0.01 +- 0.01, 1-2 distinct messages.
- REINFORCE keeps improving to 20000 steps (train 0.50 +- 0.12) but held-out stays 0.00 (memorises).
- H2 stays refuted/untestable as stated; H4 not supported (no Gumbel advantage; H4 within noise on held-out). Earlier "not trained to convergence" wording for Gumbel is withdrawn. Within-noise differences (REINFORCE train at V8_L4, topsim at V4_L4/V8_L4, V6_L6 vs V6_L8 held-out) are not claimed as directional.
