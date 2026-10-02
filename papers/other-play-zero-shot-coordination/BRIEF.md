# Zero-shot coordination in small symmetric games

## Question
Do independently trained self-play (SP) agents fail to coordinate with each other in small symmetric cooperative games, and do other-play (OP, training against symmetry-relabelled partners) and population-based training (reimplemented FCP-style: best response to a frozen population of SP agents) fix this, measured by cross-play between independently trained agents?

## Hypotheses (falsifiable; see proposal.md)
H1 SP: self-play ~ perfect, cross-play far lower. H2 OP cross-play > SP on every task. H3 Population cross-play > SP, grows with population size K, and (we expect) stays below OP. H4 OP needs the correct symmetry group (over-symmetrised OP loses the benefit in the lever game).

## Method and baselines (all reimplemented in method/run.py)
Tabular softmax policies, REINFORCE with batch-mean baseline and Adam. SP: partner = copy of own policy. OP: partner = copy relabelled by a uniformly random symmetry. Population (named "Population (FCP-style)"): K SP agents, then a best response to a randomly sampled member. Ablation OP-full: symmetrise over all actions.

## Tasks
lever (10 levers: 9 pay 1.0 on match, one pays 0.9), safe (4 symmetric levers pay 1 on match, a safe action gives 0.5 if either player picks it), signal (sender sees card with prior .4/.3/.2/.1, sends one of 4 symbols, receiver guesses; symmetry = relabelling symbols).

## Metrics
self_play, cross_play (exact expected payoff averaged over all ordered pairs of distinct independently trained agents; for the signal game both sender/receiver seatings), cross_play_min, gap, entropy, frac_special / frac_safe. 20 independent agents (or populations) per run, 5 seeds.

## Ablations
Symmetry group (OP vs OP-full), population size K sweep, initialisation scale sweep (for SP and OP), training steps for OP.

## Decisions recorded (rh decide)
Second game = safe-option matrix game plus a signalling game (both small). Evaluation is exact, no sampling. Hyperparameters fixed a priori (1500 steps, batch 64, lr 0.05, init sd 1.0), not tuned on cross-play; a smoke test on a separate seed (99) of OP on the lever game was used to pick the init-scale/steps sweep range, reported as a sensitivity study.

## Out of scope
Hanabi/Overcooked-scale deep RL, human partners, OBL/SAD/MEP (cited only), learned symmetry discovery.
