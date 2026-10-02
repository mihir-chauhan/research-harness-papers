# Proposal
See BRIEF.md (hypotheses H1-H5, systems, tasks, metrics, ablations) and research.yaml. Refutation criteria: a hypothesis is refuted if
the registered win rule (seed-mean MSE lower by >=5% relative and lower in all 3 seeds) is met against it (H1, H4) or fails (H2); H3 by the
sweep_noise table; H5 if the relative MSE difference is >=5% in any listed task.
Closest prior work: zeng2022are (linear vs transformers on real data); nie2022time. Difference: controlled synthetic factors and sweeps.
Search: rh lit search queries (rate-limited, partially failed) plus direct lookups of canonical papers.
Risks: 3 seeds give weak tests; small training budget may under-train neural models.
Fix round: this risk materialised (the GRU was under-trained at 400 steps). A post hoc training-budget sweep (1000 and 2000 steps;
groups sweep_steps, sweep_dwell_2000) was added; the hypotheses and the win rule above are unchanged and verdicts are given per budget.
