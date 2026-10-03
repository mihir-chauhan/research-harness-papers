| Method | auroc | auprc | brier | auroc_fold_sd | auroc_icu1 | auroc_icu2 | auroc_icu3 | auroc_icu4 | auroc_pooled | mean_epochs_or_trees | mean_pred | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU-D w/o input decay | **0.8310 ± 0.0016** | _0.4913 ± 0.0057_ | _0.0943 ± 0.0011_ | 0.0161 ± 0.0066 | 0.8277 ± 0.0058 | _0.8542 ± 0.0099_ | 0.7852 ± 0.0051 | **0.8281 ± 0.0044** | **0.8288 ± 0.0023** | **14.1600 ± 0.9529** | **0.1381 ± 0.0027** | 5 |
| GRU-D w/o any decay | _0.8307 ± 0.0024_ | **0.4914 ± 0.0053** | **0.0943 ± 0.0008** | **0.0145 ± 0.0071** | _0.8287 ± 0.0104_ | **0.8570 ± 0.0094** | **0.7855 ± 0.0046** | 0.8269 ± 0.0028 | _0.8284 ± 0.0029_ | _15.2000 ± 1.0198_ | 0.1413 ± 0.0031 | 5 |
| GRU-D w/o hidden decay | 0.8305 ± 0.0030 | 0.4892 ± 0.0074 | 0.0943 ± 0.0008 | _0.0155 ± 0.0070_ | **0.8290 ± 0.0094** | 0.8501 ± 0.0152 | _0.7852 ± 0.0039_ | _0.8270 ± 0.0063_ | 0.8276 ± 0.0045 | 15.6000 ± 1.2570 | _0.1403 ± 0.0019_ | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: auroc ↑, auprc ↑, brier ↓, auroc_fold_sd ↓, auroc_icu1 ↑, auroc_icu2 ↑, auroc_icu3 ↑, auroc_icu4 ↑, auroc_pooled ↑, mean_epochs_or_trees ↓, mean_pred ↓.
