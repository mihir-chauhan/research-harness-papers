# Dyna-Q planning under model error

## Question
In tabular Dyna-style agents on small gridworlds, how does the number of planning steps n trade sample
efficiency (early cumulative reward) against damage from a stale model (dynamics changed mid-training)
or a wrong model (stochastic transitions, where the model stores the last observed outcome)?
Compared: Q-learning (n=0), Dyna-Q, Dyna-Q+ (bonus kappa*sqrt(tau) for stale transitions), prioritized sweeping (PS).

## Hypotheses (falsifiable)
- H1 (efficiency): on a static deterministic maze, more planning steps raise cumulative reward at 500 steps; Dyna-Q n=10 beats Q-learning.
- H2 (staleness): on the blocking maze (path closes at step 1000), Dyna-Q with larger n recovers worse (post-change reward falls with n); Dyna-Q+ recovers better than Dyna-Q at the same n.
- H3 (shortcut): on the shortcut maze (new shorter path opens at step 3000), Dyna-Q+ gains more post-change reward than Dyna-Q; plain Dyna-Q rarely finds it.
- H4 (stochastic): with slip probability 0.3 the last-outcome model is wrong; the benefit of planning shrinks or reverses relative to Q-learning at large n.
- H5 (PS): PS matches/exceeds Dyna-Q at equal n on static tasks but shares its staleness failure on blocking.
Each is refuted if the corresponding table rows (mean over 20 seeds, paired-seed comparison) go the other way or differ within noise.

## Method / systems (all reimplemented, numpy-free tabular python in method/run.py)
Epsilon-greedy (0.1), alpha 0.5, gamma 0.95, deterministic last-outcome model; Dyna-Q uniform planning;
Dyna-Q+ with kappa=1e-3 and untried-action initialisation as in Sutton & Barto; PS with threshold 1e-4 and predecessor queue.
Method under study ("Dyna-Q") is the display name for the method rows; other systems are baselines.

## Tasks
6x9 mazes (Sutton & Barto): blocking (T=3000, change at 1000), shortcut (T=6000, change at 3000), static (T=3000),
stochastic (slip 0.3, T=3000), stoch_blocking (slip 0.3 + blocking change).

## Metrics
cum_reward (total goals), post_reward (goals after change; second half for unchanged tasks), early_reward (goals in first 500 steps), late_reward (last 500 steps), runtime_s.

## Experiments
main (n=10, 20 seeds), sweep_n (n in 1,5,20,50,100; 10 seeds; Dyna-Q, Dyna-Q+, PS), abl_dynaq_plus (bonus off / untried-init off), sweep_kappa.
Hyperparameters are fixed a priori, no tuning on any split (there is no test split: tasks are fixed environments, results are over seeds).

## Out of scope
Function approximation, learned stochastic/ensemble models, deep MBRL, other grid sizes, hyperparameter tuning per method.
