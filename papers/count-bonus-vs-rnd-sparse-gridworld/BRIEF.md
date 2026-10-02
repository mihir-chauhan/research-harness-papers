# Exploration bonuses in sparse-reward gridworlds

## Seed
Exploration bonuses in sparse-reward gridworlds: epsilon-greedy Q-learning versus count-based bonuses versus a random-network-distillation style novelty bonus (small numpy networks), on chain and multi-room gridworlds of increasing size. Measure steps to first reward and final return, and test the known failure case of novelty bonuses under a 'noisy TV' state.

## Question
In tabular gridworlds with one sparse goal reward, how do epsilon-greedy, count-based bonuses and an RND-style bonus compare in steps to first reward and final return as the task grows, and does a noisy-TV cell (emitting a fresh random token from K values) distract each bonus?

## Hypotheses (falsifiable)
- H1: noise-free, both bonuses find the first reward faster than epsilon-greedy on the larger tasks (chain_40, room_6); refuted if epsilon-greedy is not slower.
- H2: noise-free, exact state counts are at least as fast as RND.
- H3: with a TV cell, RND (and observation-count) spend more time on the TV and reach reward later than on the noise-free twin; state-id counts are unaffected.
- H4: TV distraction depends on token cardinality K (sweep K in {1,4,16,64}).

## Method
Tabular Q-learning (alpha 0.5, gamma 0.99, eps 0.1) with r + beta*bonus. Systems (all reimplemented): egreedy (beta=0); count_state (1/sqrt(N(s))); count_obs (1/sqrt(N(s,token))); rnd (numpy MLP predictor vs fixed random target on one-hot [state, token], error normalised by running std); rnd_nonorm.
Tasks: chain_{10,20,40}, room_{2,4,6} (rooms of 5x5 joined by doors, goal in far corner), chain_20_tv, room_4_tv.
Metrics: steps_to_first_reward (censored at the budget), final_return, greedy_success, found_reward, tv_time_frac, coverage. Seeds: 5 per cell.
Ablations: rnd_nonorm; beta sweep; K sweep. (Extended in the audit rounds, see below.)
Out of scope: deep RL, pixels, hyperparameter search beyond one fixed setting, other novelty methods (ICM, pseudo-counts).
No tuning on a separate split: hyperparameters are fixed a priori and identical across tasks (recorded in method/DESIGN.md).

## Audit-round revisions (decisions recorded with `rh decide`)
The hypotheses and their tests are unchanged. Two audits changed the systems and controls:
- Round 1: the bonus systems carry a constant offset (target r + beta*(b - 1)) that epsilon-greedy lacks. Controls added to `main`: "Step penalty only (optimistic init)" (b = 0 with the offset) and "Count bonus (state), no offset".
- Round 2: the RND normaliser e/(sigma + 1e-8) divided by a zero running std when the first errors coincided, giving a bonus of 1e6-1e7 in the first steps and Q-values that did not wash out; every failed RND run had this spike. The method is now the guarded normaliser: b = 1 for the first 64 errors, then min(e/(sigma + 1e-8), 5). W = 64 and c = 5 were fixed a priori. The old normaliser is kept as the ablation "RND, unguarded normaliser (v1)" together with "RND, warm-up only", "RND, clip only" and "no bonus normalisation (rnd_nonorm)" (all eight tasks), and a clip sweep (c in 2, 5, 20, none).
- Round 2: all runs were repeated from one commit that contains the code (earlier rows are superseded in the registry); every run logs bonus diagnostics; the seed-100 pilot is logged (group `pilot`).
- Still out of scope: a forward-model (curiosity) bonus, which is the bonus the noisy-TV argument is about; RND is designed to be robust to it. H3 is therefore a test whether our RND-style bonus shows that robustness, and the paper says so.
