# Proposal

## Direction
Continual learning on permuted-pixel and split-class tasks built from scikit-learn digits: fine-tuning vs EWC vs a small replay buffer vs joint training; average accuracy and forgetting; replay buffer size vs EWC strength.

## Landscape
See literature/landscape.md. EWC [kirkpatrick2017overcoming], tiny-memory replay [chaudhry2019tiny], the three-scenario taxonomy [ven2019three]. None of this is new; the study is a controlled, small replication with a head-to-head "memory vs regularisation strength" sweep.

## Gap
Published comparisons use MNIST-scale or larger data and tune each method differently. Here every system shares one network, optimiser, step budget, gradient clip, evaluation and data split, on tiny 8x8 digits, so that the only difference is the anti-forgetting mechanism, and we sweep both knobs (buffer size M, EWC lambda) on the same axis of final average accuracy.

## Contribution (modest)
A reproducible CPU comparison on 3 scenarios (domain-incremental permuted digits, class-incremental split digits, task-incremental split digits), with sensitivity sweeps of lambda and M. No new algorithm.

## Hypotheses (tests registered before runs; all paired over 5 seeds, `rh compare`, alpha=0.05)
| ID | Hypothesis | Group | Metric | Refuted if |
|---|---|---|---|---|
| H1 | On perm_dil, ER with M=100 beats lambda*-EWC in final average accuracy | main | average_accuracy | EWC >= ER or difference not significant |
| H2 | On split_cil, EWC (val-chosen lambda) is no better than fine-tuning by more than 0.05 absolute, while ER M=100 is better than fine-tuning by more than 0.2 | main | average_accuracy | EWC gains >0.05, or ER gains <0.2 |
| H3 | On split_til, fine-tuning is already within 0.10 of joint training (task identity removes most interference), so the methods differ little | main | average_accuracy | fine-tune more than 0.10 below joint |
| H4 | Replay average accuracy increases with M (M=500 > M=20 > M=0) in every scenario; EWC accuracy vs lambda is inverted-U (an interior lambda beats both lambda=0 and lambda=1e5) on perm_dil and split_cil | sweep_buffer, sweep_lambda | average_accuracy | monotonicity or interior optimum fails in a scenario |
| H5 | Joint training upper-bounds all continual systems (average accuracy) in every scenario | main | average_accuracy | any continual system exceeds joint |

## Baselines
Fine-tuning (lower bound), EWC (reimplemented, diagonal Fisher with model-sampled labels, one penalty per task), Experience Replay (reimplemented, equal per-task share of M slots), joint training (retrain on union; upper bound). Out of scope: SI, LwF, A-GEM, DER++, iCaRL, pretrained backbones, larger data.

## Protocol decisions
Seeds 0-4 for the main table; seeds 10-14 for sweeps (separate data splits/permutations, selecting lambda* from validation accuracy, never test); seeds 100-101 for lr selection on validation.
