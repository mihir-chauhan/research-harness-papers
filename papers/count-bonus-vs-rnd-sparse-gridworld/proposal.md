# Proposal
Question, hypotheses H1-H4, method, baselines, tasks and metrics: see BRIEF.md and research.yaml.
Refutation: H1 refuted if epsilon-greedy is not slower on chain_40/room_6; H2 refuted if RND is faster than counts; H3 refuted if RND's first-reward time on _tv tasks is not above its noise-free twin; H4 refuted if TV time and first-reward time do not vary with K.
Baselines: epsilon-greedy, count (state), count (obs). Ablations: rnd_nonorm, beta sweep, K sweep.
Audit round 2 (tests unchanged): the RND bonus now uses a guarded normaliser (warm-up 64, clip 5); added ablations: RND unguarded normaliser (v1), warm-up only, clip only (plus rnd_nonorm), and a clip sweep. See BRIEF.md.
