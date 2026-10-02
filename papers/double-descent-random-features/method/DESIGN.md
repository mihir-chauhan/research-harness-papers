# Design
`method/run.py`: one run = one (system, task, seed) full width sweep.
- Data: synthetic y=tanh(2 w.x), x~N(0,I_50), |w|=1, n=200 train, 200 val, 2000 test; digits: 200 train / 200 val / 1397 test random split per seed, pixels/16 then standardised by train statistics (constant pixels dropped), 10 one-hot targets. Gaussian label noise (sd sigma) on train and val labels only; test MSE vs clean targets, averaged over targets.
- Features phi(x)=relu(W^T x/sqrt(d))/sqrt(N), W~N(0,1) fixed per seed with N_max=5000 columns; width N uses the first N columns (nested). 24 widths N/n in {0.05..25}. No intercept.
- Ridge: a = argmin (1/n)|y-Phi a|^2 + lam |a|^2 (via SVD). lam=0: pseudo-inverse, singular values below 1e-10*s_max dropped.
- Systems: minnorm (lam=0); fixed (lam=1e-2 default, --lam); global (one lam for all widths minimising mean validation MSE over widths); tuned (lam per width minimising validation MSE; grid 10^-6..10^1 step 0.5 dex, 15 values); loo (per-width lam minimising closed-form leave-one-out MSE on the training set, no validation data). --val-size shortens the validation set.
- Metrics: see proposal.md. bump = max_p min(m_p - min_{j<p} m_j, m_p - min_{j>p} m_j) over the full width grid, bump_rel=bump/min m.
