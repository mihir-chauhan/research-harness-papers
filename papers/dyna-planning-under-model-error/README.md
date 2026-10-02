# Model-based RL under model error

AI-generated research study from the Ansatz library seed corpus (commissioned by Mihir Chauhan, @mihir-chauhan). The topic was chosen to cover the field; no person reviewed this study.

- `BRIEF.md`: the approved research brief
- `proposal.md`, `literature/`: the question, hypotheses and related work
- `method/`: the implementation (method and reimplemented baselines)
- `experiments/PROTOCOL.md`: the evaluation protocol
- `results/runs.jsonl`: every run (append-only registry), `results/tables/`, `results/figures/`
- `paper/`: the paper in IEEE conference format (`paper/main.pdf`), `paper/citations.json`: the reference check

Every number in the paper comes from `results/runs.jsonl`. Reproduce a run with the command recorded in its `provenance.command` field. Code: MIT. Paper text and figures: CC BY 4.0. Not peer reviewed.

Provenance note: the first `sweep_n` runs wrote the five n values of a seed to the same raw JSON file, so ~590 raw files under `results/raw/` hold only the last n; `results/runs.jsonl` is the authoritative record (values were re-verified by exact re-execution). `run.py` prints nothing, so logs contain only the harness header. Tests added in the fix round: `method/tests_stochastic.py`, `method/curves.py`.

Conformance note: the paper prints its results through `\rhval{<key>}` macros filled from the registry (`paper/number_trace.json` lists the source of each number; `reviews/conform.md` lists the changes). The groups `h4_n1`, `h4_n50`, `h4_n100` and `abl_ref_dynaq`, and the Q-learning rows of `sweep_n` and Dyna-Q rows of `sweep_kappa`, are copies of existing runs (`rh log --from-run`, same system, task and seed) so that `rh compare` can pair them; they are not additional experiments. `method/tests_stochastic.py`, `results/tables/tests_stochastic_n.csv` and `results/tables/compare_abl_dynaq_plus_post_reward_refDynaQ.csv` are kept for the record but the paper no longer draws on them. `runtime_s` is wall-clock time and is declared `nondeterministic` in `research.yaml`; all other metrics repeat exactly from the seed.
