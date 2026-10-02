# Protocol
Tasks: blocking (T=3000, wall opens left/closes right at step 1000), shortcut (T=6000, extra gap opens at 3000), static (T=3000), stochastic (slip 0.3), stoch_blocking (slip 0.3 + blocking change).
Seeds: 0-19 for `main` and `abl_dynaq_plus`; 0-9 for `sweep_n` (n in 1,5,20,50,100) and `sweep_kappa` (1e-4,1e-3 (from main, seeds 0-9),1e-2,3e-2). The seed fixes the agent's and environment's random stream.
Metrics: cum_reward (goals reached), early_reward (first 500 steps), post_reward (goals after the change; second half for unchanged tasks), late_reward (last 500 steps).
Tuning: none; all hyperparameters fixed a priori; no held-out split exists (fixed environments, results over seeds). Statistics: Welch and paired-seed t-tests via `rh compare` (uncorrected, 15 comparisons per metric).
Hardware: one CPU core of a shared Apple-silicon Mac; every run takes well under a second; the whole study well under 10 minutes.
Run: `bash experiments/run_all.sh {main|sweep_n|abl|sweep_kappa}`; `$PY method/analyze.py` builds sweep tables and figures.
