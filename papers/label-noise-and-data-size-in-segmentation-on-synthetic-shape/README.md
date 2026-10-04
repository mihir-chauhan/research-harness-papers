# Label noise and data size in segmentation on synthetic shapes

An autonomous study of the Stemma seed corpus (byline Tern-81A), produced by the Stemma autonomous AI research pipeline. The topic was chosen to cover the field.

- `BRIEF.md`: the approved research brief
- `proposal.md`, `literature/`: the question, hypotheses and related work
- `method/`: the implementation (method and reimplemented baselines)
- `experiments/PROTOCOL.md`: the evaluation protocol
- `results/runs.jsonl`: every run (append-only registry), `results/tables/`, `results/figures/`
- `paper/`: the paper in IEEE conference format (`paper/main.pdf`), `paper/citations.json`: the reference check

Every number in the paper comes from `results/runs.jsonl`. Reproduce a run with the command recorded in its `provenance.command` field. Code: MIT. Paper text and figures: CC BY 4.0.
