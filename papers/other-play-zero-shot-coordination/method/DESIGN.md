# Design
`method/run.py` trains N=20 independent agents (or 20 independent populations) in parallel and evaluates them exactly.
Policies: tabular softmax. Matrix games: logits over actions. Signalling game: sender logits [card,msg], receiver logits [msg,guess].
Optimiser: REINFORCE, batch-mean baseline, Adam lr 0.05, batch 64, 1500 steps, init logits N(0, 1) (all fixed, not tuned).
SP: partner is a copy of the agent. OP: partner copy relabelled by a random symmetry sigma (lever: permutations of levers 0-8; safe: of levers 0-3; signal: of the 4 messages); the gradient flows through both copies of the shared policy. OP-full: lever/safe games symmetrise over all actions (wrong group).
Population (FCP-style, reimplemented): stage 1 trains K independent SP agents (K=8 default), stage 2 trains a best-response agent (same budget) against a uniformly sampled frozen member each sample; the stage-2 agent is the one evaluated. Evaluated agents of different independent populations form the cross-play pairs.
Metrics: self_play = mean of diagonal of the exact pair-payoff matrix; cross_play = mean off-diagonal (ordered pairs i!=j; signalling game averages both seatings); cross_play_min; gap; entropy; frac_special (lever: P(lever 9)>0.5), frac_safe.
