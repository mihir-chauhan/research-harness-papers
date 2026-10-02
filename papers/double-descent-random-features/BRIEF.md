# Double descent in random-features regression (brief)

## Question
How do label noise and ridge regularisation change the height and position of the test-error peak of random-ReLU-features regression as the number of features N sweeps through the interpolation threshold N=n, on a synthetic single-index task and on sklearn digits (one-hot regression), and does optimally tuned ridge remove the peak?

## Decisions (open choices)
- n=200 training points; widths N/n in a 25-point grid 0.05..25 (N<=5000), nested random features per seed; features relu(Wx/sqrt d)/sqrt N so the ridge is comparable across N.
- Label noise: Gaussian noise added to training and validation labels only; test MSE is measured against clean targets. Synthetic noise sd {0,0.25,0.5,1}; digits one-hot noise sd {0,0.15,0.3,0.6}.
- "Method": ridge tuned per width on a 200-point validation set (grid 15 values 1e-6..10). Baselines (reimplemented): min-norm interpolation, fixed ridge 1e-2, one global tuned ridge. 5 seeds.
- Peak "bump" statistic defined in proposal.md; thresholds fixed before running.

## Hypotheses and tests: see proposal.md (H1-H5). Ablations: abl_tuning (LOO; 50-point validation), sweep_lambda (fixed lambda sweep). 
## Out of scope: deep networks, SGD training, other activations, other n/d, theory.

## Decisions made during the study
- Peak statistics use the window 0.4<=N/n<=4 (after smoke runs; see proposal.md and the paper). Hump statistic bump_rel over the full grid.
- Outcomes: H1, H2 supported; H3 refuted as registered; H4 partly supported (threshold met, registered paired test vs MinNorm not significant); H5 mixed. See results/RESULTS.md.
