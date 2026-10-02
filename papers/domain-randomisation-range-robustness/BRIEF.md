# How wide should domain randomisation be?

## Question
Train a small policy with cross-entropy method (CEM) on CartPole under different domain-randomisation (DR) ranges of physical parameters (cart mass, pole mass, pole length, force magnitude). Evaluate on nominal, in-range and out-of-range dynamics. Is there a range beyond which nominal performance drops faster than robustness improves? Compare no DR, narrow DR, wide DR and a success-gated curriculum that widens the range.

## Decisions (open choices in the seed)
- Task: CartPole only (batched numpy copy of gymnasium CartPole-v1 dynamics, checked against gymnasium); Pendulum is out of scope for the quick study.
- Learner: CEM on a 4-8-1 tanh MLP. Range parameter: log-scale half-width w, each parameter scaled by exp(U(-w,w)).
- Curriculum: w starts at 0, +0.05 whenever the best CEM candidate succeeds (500 steps) on >=80% of sampled environments, capped at 1.0.
- Metrics: ret_nominal; ret_w50, ret_w100 (shifted dynamics); ret_robust = mean over shifts w in {0.25,0.5,0.75,1,1.5,2}; ret_ood = mean at w=1.5,2.0.

## Hypotheses
- H1: wide DR (w=1.0) beats no DR on ret_robust (refuted if not positive at alpha 0.05).
- H2: some training width exists beyond which nominal return falls >5% below no-DR nominal while robustness stops improving (refuted if nominal stays within 5% for all widths 0..3).
- H3: the success-gated curriculum matches wide DR on ret_robust and ret_ood.

## Baselines
No randomisation, uniform DR narrow (w=0.25), uniform DR wide (w=1.0) (all reimplemented; DR after Tobin et al., Peng et al.).

## Ablations
Curriculum gate threshold {none, 0.5, 0.95} (group abl_curriculum); uniform DR width sweep w in {0,.25,.5,1,1.5,2,3} (group sweep_width).

## Seeds / compute
5 seeds, CPU, a few seconds per run.

## Out of scope
Real hardware, other tasks, learned (adaptive) sampling distributions, policies with system identification/memory, tuning of CEM hyperparameters.
