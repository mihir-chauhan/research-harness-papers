# Proposal
See BRIEF.md for the question. Hypotheses and registered tests:
- H1: sw_k4, FM-Euler vs DDIM, paired t-test over 5 seeds per task, alpha 0.05 uncorrected. Refuted if DDIM is not worse on >=2 tasks.
- H2: ratio of seed-mean SW (DDIM / FM-Euler) per task at K=4 vs K=100. Refuted if the K=100 ratio is farther from 1 on >=2 tasks.
- H3: paired t-test, Reflow-1 vs FM-Euler, sw_k1 (expect lower) and sw_k100 (expect no improvement), per task.
- H4: paired t-test on `straight` (chord/arc length of 100-step ODE paths), FM vs DDIM and Reflow-1 vs FM, per task.
Baselines: DDIM and DDPM-ancestral (Ho et al.; Song et al.), FM-Heun, all reimplemented. Metrics: SW1, MMD, straightness. Refutation: see each test.
Exploratory (not registered as pass/fail): FM-Heun at K vs FM-Euler at 2K (equal NFE), diffusion schedule, reflow teacher steps, second reflow round.
