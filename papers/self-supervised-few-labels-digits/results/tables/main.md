| Method | Task | test_acc | n |
|---|---|---|---|
| Pixels + LR | n50 | 0.831 ± 0.040 | 5 |
| Random CNN + probe | n50 | 0.856 ± 0.022 | 5 |
| Supervised scratch | n50 | _0.918 ± 0.017_ | 5 |
| Rotation (reimplemented) | n50 | 0.772 ± 0.037 | 5 |
| PCA + LR | n50 | 0.820 ± 0.031 | 5 |
| SimCLR-style probe | n50 | **0.955 ± 0.012** | 5 |
| Pixels + LR | n10 | 0.564 ± 0.061 | 5 |
| Random CNN + probe | n10 | 0.546 ± 0.118 | 5 |
| Supervised scratch | n10 | _0.662 ± 0.043_ | 5 |
| Rotation (reimplemented) | n10 | 0.441 ± 0.033 | 5 |
| PCA + LR | n10 | 0.505 ± 0.063 | 5 |
| SimCLR-style probe | n10 | **0.826 ± 0.037** | 5 |
| Pixels + LR | n200 | 0.932 ± 0.013 | 5 |
| Random CNN + probe | n200 | 0.944 ± 0.015 | 5 |
| Supervised scratch | n200 | _0.976 ± 0.010_ | 5 |
| Rotation (reimplemented) | n200 | 0.908 ± 0.010 | 5 |
| PCA + LR | n200 | 0.914 ± 0.010 | 5 |
| SimCLR-style probe | n200 | **0.979 ± 0.010** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: test_acc ↑.
