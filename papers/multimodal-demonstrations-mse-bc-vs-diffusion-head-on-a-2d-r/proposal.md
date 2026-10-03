# Proposal
Question: in a 2D point-mass reach with an obstacle bypassable on either side, 2,000 scripted bimodal demonstrations, when do GMM and 50-step DDPM heads beat an MSE MLP, and does DDPM beat a 2-component GMM?
Hypotheses (tests registered; see research.yaml): H1 MSE < GMM,DDPM on bimodal50; H2 DDPM does not beat GMM by >=0.05; H3 mode share fidelity on bimodal80; H4 MSE success rises with start jitter; H5 DDPM degrades with 1/5 steps.
Test: `rh compare` (as implemented by the platform) over 10 seeds, alpha 0.05. Refutation conditions listed per hypothesis.
Systems: MSE-MLP, GMM head (K=2), DDPM head (50 steps), all reimplemented, same MLP width 128, Adam 1e-3 cosine, 40 epochs, batch 256.
Tasks: bimodal50, bimodal80, unimodal (control). Metrics: success, collision, upper/lower mode share over 200 rollouts, upper_frac, mode_balance.
