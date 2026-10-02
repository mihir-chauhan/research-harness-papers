# Results (5 seeds; tables in results/tables/main.md, compare_main_*.csv, sensitivity.tex)
- H1 supported: CE mem_rate 1.000/1.000/0.995 at 20/40/60%; test_acc 0.991 (0%) -> 0.709 (40%), 0.436 (60%).
- H2 supported (and LS is below CE at 40%: 0.668 vs 0.709, paired p=0.0141 uncorrected); eps sweep 0.05-0.6 never lowers mem_rate.
- H3 supported at alpha=1 (acc +0.024/+0.053/+0.087 over CE; mem_rate 0.919/0.892/0.853) but mixup still memorises ~90%; larger alpha (sweep) keeps improving.
- H4 half supported: small-loss best at 20/40/60% (0.943/0.896/0.771) with oracle rate, only negative mem_gap; "worse than CE at 0%" untestable (identical to CE when rate=0).
- H5 partly supported: most gain lost at assumed rate 0.1 and 0.2 (0.733, 0.774) but not 0.3 (0.828); over-estimation (0.5, 0.6) not harmful (0.918, 0.921). No-warm-up variant 0.924 > main 0.896 (paired over same seeds, p=0.003; test split).
Primary caveats: tiny dataset, oracle rate, untuned baselines, final-epoch evaluation. Discarded launcher-bug runs are in results/discarded_launcher_bug (see rh decide).

## Audit-round notes
- CNN has 40,618 parameters (earlier text said ~30k; corrected).
- Logged 5-epoch curves (results/tables/curves.tex, analysis/make_curves.py): rankings are specific to final-epoch evaluation (best logged checkpoint at 40%: CE 0.805, LS 0.854, mixup 0.891, small-loss 0.904; test-split selected, optimistic).
- No-warm-up vs main is paired over the same seeds: delta test_acc +0.028 (p=0.0030), mem_rate -0.133 (test split, uncorrected).
- H5 is partly supported: most of the gain is lost at assumed rates 0.1 and 0.2, not at 0.3; over-estimation not harmful.
- Log-file collision: in the sweep groups, log filenames omit the config and two parallel streams shared paths, so 34 of 65 sweep rows share 17 log files; for 17 rows the surviving log lacks that row's metrics. Registry values and results/raw/*.json are correct (auditor re-ran affected rows bit-identically). Rows were not re-logged to avoid duplicate registry entries.
- VERDICT.md ablation row reads 'missing' because the advisory verdict pairs an ablation with the method inside one group, while the full-method rows live in group main; the paired comparison is in Table warm (analysis/make_curves.py). Sweeps are sensitivity studies and are not listed as ablations.

## Conformance notes (number tracing)
- Differences to CE and p-values in the paper now come from `rh compare --group main --metric test_acc|mem_rate --ref CE` (results/tables/compare_main_*.csv, `\rhval{cmp/...}`), whose sign is CE minus system. results/tables/paired.tex is removed.
- The logged-curve table (curves.tex) and the paired no-warm-up table (warmup_paired.tex) are removed from the paper and from results/tables: their values are computed by analysis/make_curves.py from run logs / across run groups and are not registry statistics. The numbers quoted for them above in this file are that script's output, not registry values. The paper keeps the ordering claim in words only.
- runtime_s is declared `nondeterministic: true` in research.yaml; all other logged metrics reproduce exactly from the seed (checked on Mixup/digits_noise40/seed 3 and Small-loss/digits_noise60/seed 1).
