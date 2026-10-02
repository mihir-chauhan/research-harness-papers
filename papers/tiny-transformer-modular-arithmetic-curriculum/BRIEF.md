# Can a small transformer learn modular addition faster with a curriculum

## Seed
Can a small transformer learn modular addition faster with a curriculum? Train a one- or two-layer transformer (torch, CPU, small modulus such as 23 or 31 so that runs finish in minutes) on modular addition with (a) uniform sampling, (b) a curriculum over operand size, (c) an anti-curriculum. Measure steps to reach 95 percent held-out accuracy, and how weight decay and training-set fraction interact with the curriculum. Keep within the CPU budget and say so if delayed generalisation (grokking) is not reached.

## Research question
Can a small transformer learn modular addition faster with a curriculum? Train a one- or two-layer transformer (torch, CPU, small modulus such as 23 or 31 so that runs finish in minutes) on modular addition with (a) uniform sampling, (b) a curriculum over operand size, (c) an anti-curriculum. Measure steps to reach 95 percent held-out accuracy, and how weight decay and training-set fraction interact with the curriculum. Keep within the CPU budget and say so if delayed generalisation (grokking) is not reached.

Field: nlp-llm
Scale: quick study, cpu, about 30 minutes of experiments.


## Author decisions (seed corpus)
- Task: (a+b) mod 23, 1-layer transformer (d=64, 4 heads), tokens [a,b,=]; held-out set = all pairs not in train.
- Systems: uniform, operand-size curriculum (key max(a,b), pool grows from 15% to 100% of the train set over 1000 steps), anti-curriculum (reverse order).
- Primary metric steps_to_95 (censored at 4000). Main cell wd=1, frac=0.5, 5 seeds; grid wd{0,1,3} x frac{0.4,0.5,0.7}, 3 seeds; sweeps on T_c and a shuffled-order control.
- Hypotheses H1-H4 and tests in proposal.md / research.yaml. Out of scope: other moduli, deeper models, mechanistic analysis.
- lr 3e-3 and the main cell were chosen from a 10-run pilot on uniform sampling with seed 100 (not used in any reported run; exploratory, outputs not kept, not in the registry, so the pilot claims are not verifiable).
