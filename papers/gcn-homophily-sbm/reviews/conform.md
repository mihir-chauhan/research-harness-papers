# Conformance report: numbers traced, constants declared

No claim, verdict or experiment changed. No new training run was logged. One line per change.

## Constants declared (`rh const add`; setup facts, none is a result)
- `900` (abstract, introduction, method, limitations): declared `n_nodes` (`method/run.py --n` default).
- `300` (method, training): declared `max_epochs` (`method/run.py --epochs` default).
- `102` and `100` (setup, "seeds 100--102"): declared `tuning_seed_last`, `tuning_seed_first` (`method/tune.py`).
- `100` (method, patience): declared `early_stopping_patience` (`method/run.py --patience` default).
- `0.02` (abstract, setup, results, conclusion; the H2 tolerance): declared `h2_tolerance` (registered in `proposal.md`); it previously traced only by coincidence to an unrelated std.

## Derived numbers replaced by `\rhval{<key>}` (values from `rh compare`)
- results, H1: `p=0.007`, `0.142`, `0.014`, `0.001` (GCN vs MLP, mu=1, h=0.3/0.4/0.5/0.2) -> `cmp/main/mlp/<task>/accuracy/paired_p`.
- results, H1: `-9.5`, `-9.1`, `-3.2`, `-22.7`, `-25.3`, `-3.2`, `-1.9`, `+17.0` points -> `cmp/main/mlp/<task>/accuracy/delta` (now printed as accuracy fractions, not percentage points).
- results, H2: "trails GCN by `0.078`" (mu=0.5, h=0.6) -> `cmp/main/h2gcn-style-reimplemented/h0.6_mu0.5/accuracy/delta`.
- results, H4: "gap is `+1.0` points" (mu=0.5, h=0.4) -> `cmp/main/mlp/h0.4_mu0.5/accuracy/delta`.
- ablations, H5: `p<10^{-5}` (tied vs full, h=0.1) and `p=0.550` (h=0.4) -> `cmp/abl_h2gcn/h2gcn-tied-weights/<task>/accuracy/paired_p`.
- ablations, degree sweep: "by `0.059`, `0.084`, `0.033`, `0.048`" -> `cmp/sweep_deg_d{2,5,20}/mlp-deg{d}/h0.4_mu1.0/accuracy/delta` and `cmp/main/mlp/h0.4_mu1.0/accuracy/delta` (signed GCN-MLP). `0.084` was the flagged untraced number.
- abstract, setup: `660` -> `count/main/runs`; setup: `45` -> `count/sweep_deg/runs`; setup: "30 runs" -> "`count/abl_h2gcn/h2gcn-tied-weights/runs` runs per variant" (15 per variant, same fact).

## Hand-written tables (produced by `experiments/analyze.py`, `analyze2.py`; scripts edited, means/stds unchanged)
- Table I (`main_mu1.tex`): the 11 typed p-values in the last column -> `cmp/main/mlp/<task>/accuracy/paired_p`.
- Table III (`gcn_mlp_gap.tex`): all 33 typed GCN-MLP gaps -> `cmp/main/mlp/<task>/accuracy/delta`; caption changed from "percentage points" to "fraction".
- Table IV (`h2_viol.tex`): the typed `H2GCN-best` column deleted (no registry key for the H2GCN-vs-MLP row); the three mean columns stay.
- Table V (`abl_h2gcn_custom.tex`): typed Delta and p for tied and 2-hop -> `cmp/abl_h2gcn/<variant>/<task>/accuracy/{delta,paired_p}`; Delta is now "full minus variant" (sign flipped, caption says so) and 2-hop Delta has its own column.
- Table VI (`sweep_deg_custom.tex`): typed `GCN-MLP` and `p (paired)` rows -> the degree-sweep and main-grid `cmp` keys above.

## Derived numbers deleted (no registry key exists)
- method: "deviates from h by at most `0.016` in any graph (mean `0.004`)" -> "deviates slightly from h (logged per run as `realized_h`)".
- results, H2: "trails the MLP by `0.027`" (mu=2, h=0.3) -> the two cell means "(0.804 vs 0.830)".
- results, failure summary: "win is by `0.4` points over H2GCN-style" -> the two cell means "(0.539 vs 0.535)".

## Registry (rule 2)
- No hand-logged rows were found: all 736 rows have an `rh run` command, so nothing had to be re-run or dropped.
- Added 45 copies with `rh log --from-run` (original command and provenance kept, `copied_from` set; no metric typed, nothing re-trained), so `rh compare` has its reference in the same group: 15 full H2GCN-style rows (h=0.1/0.4/0.9, mu=1, seeds 0-4) into `abl_h2gcn`; MLP and GCN rows of each degree into new groups `sweep_deg_d2`, `sweep_deg_d5`, `sweep_deg_d20` (10 rows each). Registry is now 781 rows; `main` and `sweep_deg` are unchanged.
- New compare files: `results/tables/compare_abl_h2gcn_accuracy.csv`, `compare_sweep_deg_d{2,5,20}_accuracy.csv`.

## Reproducible metrics (rule 3)
- `research.yaml`: added metric `seconds` with `nondeterministic: true` (wall clock). No result metric is marked.
- Re-ran four logged runs (GCN main, tied-weights ablation, LP main, MLP deg20): `accuracy`, `val_accuracy`, `realized_h`, `lp_alpha` matched the registry to the last digit; only `seconds` differed. No unseeded randomness found.

## Text versus registry
- No disagreement found: every p-value and difference replaced above agrees with `rh compare` at the precision the text used.
- One scope note: the deleted "at most 0.016 (mean 0.004)" holds for the 660 main-grid graphs (0.0155, 0.0039); over the degree-sweep graphs the maximum is 0.025. The sentence did not say which graphs it covered.

## Other
- `paper/sections/author.tex`: not edited by me (platform rewrite left as is).
- `paper/main.tex`: `rh paper build` added the `\input{generated/values}` line.
- Table IV no longer stretched to column width (it has one column fewer).
- Wording: no "state of the art" or "novel" in the paper. Length: 6 pages.

## Final checks
- `rh paper build`: BUILD OK. `rh lit verify`: CITATIONS VERIFIED (11/11). `rh numbers`: 437 checked, 0 untraced. `rh check`: READY (one warning, pre-existing: verdict tier 0 < target 2, GCN is not best on h0.4_mu1.0, which is the paper's reported finding).
