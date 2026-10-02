# Templated language vs learned vectors for multi-robot coordination (brief)

## Seed
Natural-language-like versus learned-vector communication for multi-robot coordination, at CPU scale: no communication, learned continuous vector, learned discrete tokens, and a fixed human-readable templated language (a proxy for natural language; no LLM). Measure task success, sample efficiency, cross-play.

## Precise question
In a hidden-target two-robot rendezvous with partial observability, how do the four channels compare on (i) final task success, (ii) sample efficiency, (iii) cross-play with a partner trained separately?

## Decisions (see `rh decide`)
- Task: 2 point robots start at the origin; target uniform in [-1,1]^2 is seen only by robot 0 (speaker); robot 1 (listener) sees only its own position and time. T=10 steps, velocity control. Success = both robots within 0.3 of the target at the end. (Two robots only; three-robot variant out of scope.)
- Channels at matched capacity (16 messages): continuous d=4 tanh vector with Gaussian noise 0.1; discrete 2 slots x 4 tokens (Gumbel-softmax straight-through); templated language "target is <row word> <col word>" on a 4x4 grid (fixed speaker, learned listener).
- Learning: all systems use the same pathwise-gradient objective through the differentiable dynamics (sum of squared final distances), Adam, 2000 steps x 64 episodes. This is not RL; stated as a limitation.
- Speaker's own motion policy is learned for every system.

## Hypotheses
H1 comm > no comm. H2 language has higher success_auc than both learned channels. H3 continuous final success > language (grid-capped). H4 language cross-play = self-play; learned channels drop.

## Baselines
No communication; continuous vector (DIAL/CommNet-style, reimplemented); discrete tokens (Gumbel-softmax, reimplemented).

## Metrics
success_rate (4000 held-out targets), success_auc (mean validation success over the learning curve, sample efficiency), episodes_to_50, final_dist, xplay_success (listener of seed i with speakers of the other 4 seeds). 5 seeds.

## Ablations / sensitivity
Vocabulary size (tokens per slot / grid words per axis) for discrete and language; channel noise for continuous.

## Out of scope
Real natural language / LLMs, real robots, RL with sparse reward, more than two robots, bandwidth-in-bytes accounting, human evaluation of legibility.
