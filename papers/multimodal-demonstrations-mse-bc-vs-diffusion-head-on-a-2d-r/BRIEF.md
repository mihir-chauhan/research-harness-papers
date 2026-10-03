# Brief
Question: when do GMM and DDPM action heads beat MSE regression on a bimodal 2D obstacle-bypass reach, and does DDPM beat a 2-component GMM? Hypotheses H1-H5, systems, tasks, metrics, ablations: see proposal.md and research.yaml; protocol in experiments/PROTOCOL.md.
Decisions: the seed leaves start-state distribution open. I chose start jitter 0.01 (pilot seed 99: MSE neither 0 nor ~1) and sweep it, since at jitter 0 MSE fails entirely and at 0.03 largely succeeds in the pilot. Out of scope: images, real robots, IBC/BeT baselines, long horizons, tuning per method.
