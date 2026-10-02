# Seed corpus of the research library

AI-generated research papers, one directory per paper, each a complete study: brief, proposal, literature notes, code, run registry (`results/runs.jsonl`), tables, figures, the paper in IEEE conference format (`paper/main.pdf`), the reference check (`paper/citations.json`) and the independent audit (`reviews/audit.json`).

These papers were written end to end by an AI research agent running the [research-harness](https://github.com/mihir-chauhan/research-harness) pipeline. The topics were chosen to cover many fields and no person reviewed the papers. They are small CPU-scale studies, they are not peer reviewed, and they should be read as first looks, not as established results. Absolute paths of the machine that ran the studies were replaced by relative ones in logs and run records; nothing else was edited.

What was enforced for every paper here:

- every number in the paper comes from a run recorded in `results/runs.jsonl`;
- every cited reference resolves on arXiv or Crossref with a matching title;
- a second AI agent that did not write the paper re-ran two experiments, compared the text against the tables, read the citations against the cited papers, and its findings were fixed or the paper was dropped.

Code: MIT. Text and figures: CC BY 4.0.

| Field | Paper | Directory |
|---|---|---|
| reinforcement-learning | How Many Planning Steps? Dyna-Q, Dyna-Q+ and Prioritized Sweeping Under Stale and Stochastic Tabular Models | [`papers/dyna-planning-under-model-error`](papers/dyna-planning-under-model-error) |
| robotics | How Wide Should Domain Randomisation Be? A Small-Scale CartPole Study of Range Width and a Success-Gated Curriculum | [`papers/domain-randomisation-range-robustness`](papers/domain-randomisation-range-robustness) |
| robotics | Templated Language versus Learned Vectors for Multi-Robot Rendezvous: A Small CPU Study of Success, Sample Efficiency and Cross-Play | [`papers/language-vs-vector-multi-robot-comm`](papers/language-vs-vector-multi-robot-comm) |
