| Method | train_acc | heldout_acc | topsim | n_unique_messages | n |
|---|---|---|---|---|---|
| Gumbel-softmax sender-receiver | _0.01 ± 0.01_ | **0.01 ± 0.02** | _0.00 ± 0.00_ | **1.67 ± 0.58** | 3 |
| REINFORCE sender (reimplemented) | **0.50 ± 0.12** | _0.00 ± 0.00_ | **0.31 ± 0.02** | _117.00 ± 27.73_ | 3 |

Mean ± std over seeds; bold = best, underline = second. Directions: train_acc ↑, heldout_acc ↑, topsim ↑, n_unique_messages ↓.
