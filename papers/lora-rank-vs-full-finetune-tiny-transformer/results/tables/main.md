| Method | Task | adapt_acc | adapt_tok_acc | pretask_acc | n |
|---|---|---|---|---|---|
| Head only | sort_desc | 0.012 ± 0.007 | 0.615 ± 0.015 | 0.000 ± 0.000 | 5 |
| Last block | sort_desc | 0.965 ± 0.007 | 0.995 ± 0.001 | 0.000 ± 0.000 | 5 |
| From scratch | sort_desc | 0.997 ± 0.001 | 1.000 ± 0.000 | 0.000 ± 0.000 | 5 |
| Full fine-tuning | sort_desc | 0.996 ± 0.003 | 1.000 ± 0.000 | _0.000 ± 0.000_ | 5 |
| LoRA r=4 | sort_desc | _0.997 ± 0.001_ | _1.000 ± 0.000_ | 0.000 ± 0.000 | 5 |
| LoRA r=8 | sort_desc | **0.997 ± 0.001** | **1.000 ± 0.000** | 0.000 ± 0.000 | 5 |
| LoRA r=1 | sort_desc | 0.978 ± 0.007 | 0.997 ± 0.001 | 0.000 ± 0.000 | 5 |
| LoRA r=2 | sort_desc | 0.994 ± 0.002 | 0.999 ± 0.000 | 0.000 ± 0.000 | 5 |
| No adaptation | sort_desc | 0.000 ± 0.000 | 0.093 ± 0.015 | **0.999 ± 0.001** | 5 |
| Head only | reverse | 0.000 ± 0.000 | 0.248 ± 0.009 | _0.004 ± 0.004_ | 5 |
| Last block | reverse | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.001 ± 0.000 | 5 |
| From scratch | reverse | _1.000 ± 0.000_ | _1.000 ± 0.000_ | 0.001 ± 0.000 | 5 |
| Full fine-tuning | reverse | **1.000 ± 0.000** | **1.000 ± 0.000** | 0.001 ± 0.000 | 5 |
| LoRA r=4 | reverse | 0.999 ± 0.002 | 1.000 ± 0.000 | 0.001 ± 0.000 | 5 |
| LoRA r=8 | reverse | 0.941 ± 0.080 | 0.992 ± 0.011 | 0.001 ± 0.000 | 5 |
| LoRA r=1 | reverse | 0.799 ± 0.447 | 0.821 ± 0.400 | 0.000 ± 0.000 | 5 |
| LoRA r=2 | reverse | 0.800 ± 0.447 | 0.883 ± 0.261 | 0.000 ± 0.000 | 5 |
| No adaptation | reverse | 0.001 ± 0.000 | 0.193 ± 0.005 | **0.999 ± 0.001** | 5 |

Mean ± std over seeds; bold = best, underline = second. Directions: adapt_acc ↑, adapt_tok_acc ↑, pretask_acc ↑.
