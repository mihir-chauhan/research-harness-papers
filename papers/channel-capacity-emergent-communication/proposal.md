# Proposal

## Question
In a Lewis reconstruction game over 4 attributes x 4 values (256 objects, 8 bits), how do vocabulary size V and message length
L affect accuracy on held-out attribute combinations and topographic similarity, and is a channel much larger than needed
worse for generalisation/compositionality?

## Hypotheses
- H1 (capacity needed): channels with capacity L*log2 V below 8 bits cannot reach high accuracy; above it train accuracy rises.
  Refuted if accuracy at ~5 bits is as high as at >=10 bits.
- H2 (over-capacity hurts generalisation): a channel far larger than needed (V16_L8) has a larger train-held-out gap and lower
  topsim than a tight one (V4_L4) for the learned senders. Refuted if held-out accuracy and topsim are equal or higher.
- H3 (compositionality does not emerge by default): learned protocols have topsim well below the oracle compositional code, and
  held-out accuracy well below it. Refuted if topsim within noise of the oracle's.
- H4 (estimator): Gumbel-softmax outperforms REINFORCE on held-out accuracy at equal steps. Refuted if REINFORCE >= Gumbel.

## Method / systems
Gumbel-softmax GRU sender and receiver (ST hard samples); baselines (reimplemented): REINFORCE sender (Williams), random-code
sender (non-compositional reference), oracle-compositional sender (upper reference).
Metrics: heldout_acc (all 4 attributes correct, 10% held-out combinations), topsim (Spearman Hamming meanings vs messages),
gen_gap, train_acc. Ablations/sweeps: vocabulary sweep (L=5), length sweep (V=6) for the Gumbel system.
Out of scope: images, population/iterated-learning pressure, large scale.
