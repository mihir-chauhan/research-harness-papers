# Proposal

## Direction
What does classifier-free guidance trade away? Small conditional diffusion model on a 2D multi-modal class-conditional mixture; sweep guidance scale; measure class precision, within-class mode coverage, variance collapse; compare with unguided and low-temperature sampling.

## Landscape
See literature/landscape.md. CFG [ho2022classifier]; classifier guidance [dhariwal2021diffusion]; GLIDE [nichol2021glide]; limited interval [kynknniemi2024applying]; Gibbs-like CFG [moufad2025conditional]; train/sample discrepancy [patel2023bridging]; P/R metrics [kynknniemi2019improved, sajjadi2018assessing].

## Gap and contribution
Image evaluations cannot see modes or variance. On a mixture with known centres, weights and posterior, each cost of guidance is directly measurable. Contribution: a small controlled accounting, versus unguided and low-temperature sampling. Not a new method.

## Hypotheses -> experiments
| ID | Hypothesis | Group | Metric | Decides if |
|---|---|---|---|---|
| H1 | CFG w=3 raises class accuracy vs unguided (mix_overlap) | main | class_acc | paired t-test, 5 seeds, p<0.05, positive difference; refuted if not |
| H2 | CFG w=3 raises mode_tv and lowers std_ratio vs unguided | main | mode_tv, std_ratio | paired t-tests p<0.05 each; refuted if either is not significant in that direction |
| H3 | tau=0.5 raises class_acc less than CFG w=3 | main | class_acc | paired t-test CFG vs tau=0.5 p<0.05 |
| H4 | mode_tv increase (w=3 minus w=0) smaller on mix_sep than mix_overlap | main | mode_tv | Welch t-test on per-seed differences, p<0.05 |
| H5 | w=8 raises off_support vs w=0 | main + sweep_w | off_support | paired t-test p<0.05 |

Exploratory (not tested, descriptive): trade-off frontier of CFG vs temperature at matched std_ratio; guidance interval and label dropout ablations.

## Baselines
Unguided conditional (w=0) and low-temperature sampling (tau=0.5, plus tau sweep), reimplemented on the same trained network.

## Refutation
Each hypothesis is refuted when its registered test fails to give a significant difference in the stated direction.
