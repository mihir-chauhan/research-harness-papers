# Protocol
Tasks: double_integrator, unicycle (3 circular obstacles, radii 0.5-0.8, start/goal randomised per seed; scenarios depend only on the seed, so all systems see identical episodes). Seeds 0-4, 100 episodes each. Default: alpha=2, dt=0.05 (always passed explicitly), braking threshold 1.0 (not tuned).
Systems (registry names): Nominal, CT-CBF, DT-CBF (method row), Braking. All reimplemented in method/run.py.
Groups (driver: experiments/run_all.py):
- main: 4 systems x 2 tasks x 5 seeds = 40 runs.
- grid_alpha_dt: CT-CBF, DT-CBF; alpha in 0.5,1,2,5,10 x dt in 0.01,0.02,0.05,0.1,0.2; both tasks = 500 runs. The one-factor alpha/dt sweeps are slices dt=0.05 / alpha=2.
- grid_dt005: CT-CBF, DT-CBF; dt=0.005 (= plant step); alpha in 2,5,10; both tasks = 60 runs.
- sweep_dth: Braking, dth in 0.25,0.5,1,2; both tasks = 40 runs.
- abl_select: nearest vs critical obstacle, double integrator, CT-CBF and DT-CBF = 20 runs.
660 runs in total. Metrics: see method/DESIGN.md; a violation is a clearance below -1e-9 m, the same for every system.
No tuning. Hardware: shared CPU laptop, 2 threads; each run takes under one second.
Tables and figures: `rh table --group main ...`, `python method/make_sweeps.py` (reads results/runs.jsonl).
