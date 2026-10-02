# Proposal
See BRIEF.md and research.yaml. Question: cross-play of independently trained agents under SP, OP and population training in three small symmetric games.
Hypotheses H1-H4 as in research.yaml. Refutation: H1 refuted if SP cross-play is within 0.1 of self-play on any task; H2 refuted on a task where OP cross-play is not above SP; H3 refuted if PBT <= SP or does not increase with K; H4 refuted if OP-full matches OP on the lever game.
Method: tabular REINFORCE; baselines reimplemented; metrics exact expected payoffs. Tasks: lever, safe, signal.
