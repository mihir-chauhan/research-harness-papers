# Results (rendezvous, 5 seeds; tables in results/tables/)
- H1 supported: all channels > none (success 0.071); discrete lowest at 0.678 (main.md).
- H2 not supported vs continuous / supported vs discrete / speed language-vs-continuous inconclusive: main success_auc (0.887 vs 0.951) mostly tracks final success; dense eval (dense_eval.tex): episodes_to_50 language 1024+-351, continuous 896+-351, discrete 9984+-3282.
- Discrete baseline untuned: tau sweep (abl_tau.tex) best 0.721 (tau=0.5) vs 0.678 at tau=1, within noise, below language 0.931; uses ~11 of 16 messages.
- H3 supported: continuous 1.000 > language 0.931 (grid cap at V=4; language reaches 1.000 at V>=6, sweeps_summary.tex).
- H4 supported with caveat: xplay learned channels 0.066 (~ none 0.071), language 0.931 = self-play; true by construction (fixed speaker).
- Sweeps: both symbolic channels improve with V; continuous degrades with noise (1.000 at 0.0 -> 0.301 at 1.0).
