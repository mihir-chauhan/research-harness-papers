# Protocol
Tasks: 2D Ising, J=k_B=1, periodic, L=16,24,32, 40 temperatures linspace(1.5,3.5), 200 samples/T (4 chains x 50). Seeds 0-9 (data and models regenerated per seed; data seed 1000*seed+L).
Split: chains 0-2 train/fit, chain 3 held out; classifiers see only T<=1.97 and T>=2.57; all curves evaluated on chain 3.
Metrics: tc_error = |Tc_est-Tc_exact| per L (read-out per system, see DESIGN.md) and after FSS collapse; nu_error=|nu-1|; acc_far.
Tuning: none on test quantities; hyperparameters fixed a priori (DESIGN.md); pilot on seed 100 only for timing.
Groups: main (10 seeds x 7 systems), sweep_margin (MLP, CNN; margin 0.15, 0.45, 0.6; seeds 0-4), sweep_nsamp (MLP, CNN; 10 and 25 samples per chain; seeds 0-4), sweep_nsamp_ep (same, epochs scaled so samples x epochs = 1000, i.e. constant number of gradient updates; seeds 0-4), sanity (sampler check), analysis (paired tests). The learning-by-confusion rows were re-run after fixing the abscissa of its curves (trial boundary T' instead of the grid point below it); superseded rows are archived in results/superseded_runs.jsonl.
Hardware: CPU, 2 threads per process, at most two processes at a time.
