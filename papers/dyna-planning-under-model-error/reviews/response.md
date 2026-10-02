# Response to audit

1. **Major, H4 "below Q-learning"**: accepted. Added `method/tests_stochastic.py` -> `results/tables/tests_stochastic_n.csv` (paired tests). Abstract, H4, failure paragraph, conclusion and limitations now say the advantage of planning shrinks (n=1 vs 100 p=0.0016) and that at n>=50 Dyna-Q is not distinguishable from Q-learning (p=0.44, 0.14). The H4 verdict is restricted to "shrinks"; harm is not claimed. Did not add seeds.
2. **Ablation tests**: ran `rh compare` on abl_dynaq_plus (ref Dyna-Q+ and ref Dyna-Q, CSVs in results/tables). Text now reports p-values; the blocking bonus effect (p=0.069) and w/o-untried gaps on blocking/shortcut/stoch-blocking are called trends.
3. **Early-reward p**: generated `compare_main_early_reward.csv`; RESULTS.md made consistent.
4. **PS claim**: scoped to cumulative and post-change reward; early-reward advantage (p=0.014) now reported in abstract, H5 and conclusion.
5. **Mechanism statements**: marked as conjectures (Dyna-Q+ at n=1, PS queue, noise-driven re-exploration); count-based-model claim softened and the missing correct-model control stated; Fig. 2 wording changed to "rises more steeply".
6. **Citations**: added Sutton 1990 (`sutton1990integrated`, via DOI) for Dyna-Q+ and the mazes; textbook is no longer named as a source (no verifiable record to cite).
7. **Provenance**: noted in README (overwritten raw files, empty logs, registry authoritative). Not regenerated: re-running would create duplicate registry rows; registry values were already confirmed by exact re-execution.
8. **Presentation**: caption says "underlined"; column renamed "seeds"; curve figures regenerated (`method/curves.py`) with y-axis "cumulative reward" and the s.e. band defined; Table I widened to full text width.
