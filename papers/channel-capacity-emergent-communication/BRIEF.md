# Emergent communication in a referential (Lewis signalling) game with a discrete channel

## Seed
Emergent communication in a referential (Lewis signalling) game with a discrete channel: how do vocabulary size and message length affect accuracy, and does the emerging protocol become compositional? Small torch speaker and listener trained with Gumbel-softmax or REINFORCE on attribute-value objects. Measure accuracy on held-out attribute combinations and topographic similarity, and compare against a channel that is larger than needed.

## Research question
Emergent communication in a referential (Lewis signalling) game with a discrete channel: how do vocabulary size and message length affect accuracy, and does the emerging protocol become compositional? Small torch speaker and listener trained with Gumbel-softmax or REINFORCE on attribute-value objects. Measure accuracy on held-out attribute combinations and topographic similarity, and compare against a channel that is larger than needed.

Field: multi-agent emergent-communication
Scale: quick study, cpu, about 30 minutes of experiments.

## Study design (decided by the author agent)
Hypotheses H1-H4 and the systems, tasks (main: V4_L4, V8_L4, V16_L8; sweeps: V in {2,3,4,8,16} at L=5, L in {2,3,4,6,8} at V=6),
metrics (heldout_acc, topsim, train_acc, gen_gap), 3 seeds, 6000 training steps for every system, are specified in proposal.md and
experiments/PROTOCOL.md. Out of scope: images, populations, iterated learning, large scale.
