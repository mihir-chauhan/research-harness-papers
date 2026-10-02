H3 lorenz63: rho [0.1, 0.4, 0.7, 1.0, 1.4, 2.0] vpt means [9.7, 9.6, 9.419, 8.297, 4.056, 2.323] ratio best/worst 4.18; clim_ok [0.83, 0.85, 0.78, 0.8, 0.87, 0.78]
   lorenz63 rho 0.1 vs 0.4 vpt: 9.700 vs 9.600, paired p=0.861 (n=3)
   lorenz63 rho 0.1 vs 0.4 clim_ok: 0.833 vs 0.850, paired p=0.667 (n=3)
H3 lorenz96: rho [0.1, 0.4, 0.7, 1.0, 1.4, 2.0] vpt means [2.304, 2.041, 1.38, 0.639, 0.279, 0.21] ratio best/worst 10.95; clim_ok [1.0, 1.0, 0.88, 0.0, 0.0, 0.0]
   lorenz96 rho 0.1 vs 0.4 vpt: 2.304 vs 2.041, paired p=0.328 (n=3)
   lorenz96 rho 0.1 vs 0.4 clim_ok: 1.000 vs 1.000, paired p=n/a (n=3)
H4 lorenz63: size [100, 250, 500, 1000, 2000] vpt means [6.803, 8.776, 9.6, 9.441, 9.926]; clim_ok [0.9, 0.85, 0.85, 0.87, 0.87]
   lorenz63 N=1000 vs N=100 vpt: 9.441 vs 6.803, paired p=0.015 (n=3)
H4 lorenz96: size [100, 250, 500, 1000, 2000] vpt means [0.344, 1.423, 2.041, 2.618, 3.279]; clim_ok [0.0, 1.0, 1.0, 1.0, 1.0]
   lorenz96 N=1000 vs N=100 vpt: 2.618 vs 0.344, paired p=0.007 (n=3)
ntrain lorenz63 n=500: ESN 5.917 vs MLP 5.198 delta +0.719 paired p=0.228 (n=3)
ntrain lorenz96 n=500: ESN 0.671 vs MLP 0.582 delta +0.089 paired p=0.372 (n=3)
ntrain lorenz63 n=2000: ESN 9.040 vs MLP 5.842 delta +3.198 paired p=0.004 (n=3)
ntrain lorenz96 n=2000: ESN 1.784 vs MLP 1.982 delta -0.198 paired p=0.119 (n=3)
ntrain lorenz63 n=5000: ESN 9.600 vs MLP 5.554 delta +4.046 paired p=2.8e-04 (n=3)
ntrain lorenz96 n=5000: ESN 2.041 vs MLP 2.721 delta -0.680 paired p=0.163 (n=3)
ntrain lorenz63 n=10000: ESN 9.845 vs MLP 5.654 delta +4.190 paired p=0.004 (n=3)
ntrain lorenz96 n=10000: ESN 2.198 vs MLP 3.192 delta -0.994 paired p=0.016 (n=3)
H5 lorenz63 ESN: n [500, 2000, 5000, 10000] vpt [5.92, 9.04, 9.6, 9.84] clim_ok [0.9, 0.82, 0.85, 0.85] n80=2000
H5 lorenz63 MLP delay: n [500, 2000, 5000, 10000] vpt [5.2, 5.84, 5.55, 5.65] clim_ok [0.87, 0.88, 0.78, 0.82] n80=500
H5 lorenz63 GRU: n [500, 2000, 5000, 10000] vpt [2.53, 3.68, 3.6, 3.58] clim_ok [0.57, 0.85, 0.85, 0.87] n80=2000
H5 lorenz96 ESN: n [500, 2000, 5000, 10000] vpt [0.67, 1.78, 2.04, 2.2] clim_ok [0.33, 1.0, 1.0, 1.0] n80=2000
H5 lorenz96 MLP delay: n [500, 2000, 5000, 10000] vpt [0.58, 1.98, 2.72, 3.19] clim_ok [0.47, 1.0, 1.0, 1.0] n80=5000
H5 lorenz96 GRU: n [500, 2000, 5000, 10000] vpt [0.05, 0.42, 1.2, 1.74] clim_ok [0.0, 0.83, 1.0, 1.0] n80=10000
steps lorenz63 MLP delay steps=4000 (tuned 16000): vpt 3.508 p vs tuned 0.015; ESN(seeds 0-2) 9.600 ratio ESN/sys 2.74 (paired p ESN vs sys 0.002); fit_s 6.0
steps lorenz96 MLP delay steps=4000 (tuned 8000): vpt 2.382 p vs tuned 0.023; ESN(seeds 0-2) 2.041 ratio ESN/sys 0.86 (paired p ESN vs sys 0.367); fit_s 6.5
steps lorenz63 MLP delay steps=8000 (tuned 16000): vpt 5.031 p vs tuned 0.348; ESN(seeds 0-2) 9.600 ratio ESN/sys 1.91 (paired p ESN vs sys 0.010); fit_s 14.1
steps lorenz96 MLP delay steps=8000 (tuned 8000): vpt 2.721 p vs tuned tuned; ESN(seeds 0-2) 2.041 ratio ESN/sys 0.75 (paired p ESN vs sys 0.163); fit_s 15.9
steps lorenz63 MLP delay steps=16000 (tuned 16000): vpt 5.554 p vs tuned tuned; ESN(seeds 0-2) 9.600 ratio ESN/sys 1.73 (paired p ESN vs sys 2.8e-04); fit_s 28.5
steps lorenz96 MLP delay steps=16000 (tuned 8000): vpt 3.127 p vs tuned 0.108; ESN(seeds 0-2) 2.041 ratio ESN/sys 0.65 (paired p ESN vs sys 0.026); fit_s 20.3
steps lorenz63 MLP delay steps=32000 (tuned 16000): vpt 5.682 p vs tuned 0.177; ESN(seeds 0-2) 9.600 ratio ESN/sys 1.69 (paired p ESN vs sys 0.001); fit_s 55.7
steps lorenz96 MLP delay steps=32000 (tuned 8000): vpt 3.487 p vs tuned 0.100; ESN(seeds 0-2) 2.041 ratio ESN/sys 0.59 (paired p ESN vs sys 0.001); fit_s 53.5
steps lorenz63 GRU steps=3000 (tuned 6000): vpt 2.879 p vs tuned 0.130; ESN(seeds 0-2) 9.600 ratio ESN/sys 3.34 (paired p ESN vs sys 0.001); fit_s 20.9
steps lorenz96 GRU steps=3000 (tuned 6000): vpt 1.028 p vs tuned 0.282; ESN(seeds 0-2) 2.041 ratio ESN/sys 1.99 (paired p ESN vs sys 0.052); fit_s 21.6
steps lorenz63 GRU steps=6000 (tuned 6000): vpt 3.597 p vs tuned tuned; ESN(seeds 0-2) 9.600 ratio ESN/sys 2.67 (paired p ESN vs sys 0.005); fit_s 56.5
steps lorenz96 GRU steps=6000 (tuned 6000): vpt 1.203 p vs tuned tuned; ESN(seeds 0-2) 2.041 ratio ESN/sys 1.70 (paired p ESN vs sys 0.036); fit_s 62.5
steps lorenz63 GRU steps=12000 (tuned 6000): vpt 3.798 p vs tuned 0.777; ESN(seeds 0-2) 9.600 ratio ESN/sys 2.53 (paired p ESN vs sys 0.007); fit_s 107.4
steps lorenz96 GRU steps=12000 (tuned 6000): vpt 1.308 p vs tuned 0.193; ESN(seeds 0-2) 2.041 ratio ESN/sys 1.56 (paired p ESN vs sys 0.025); fit_s 112.4
main lorenz63: vpt order {'ESN': 9.546, 'MLP delay': 5.578, 'GRU': 3.787}; clim_ok order {'GRU': 0.86, 'ESN': 0.85, 'MLP delay': 0.81}
   ratios ESN/MLP 1.71 ESN/GRU 2.52 MLP/ESN 0.58
   fit_seconds {'ESN': 0.15, 'ESN without squared features': 0.15, 'GRU': 57.71, 'GRU without input noise': 55.7, 'MLP delay': 28.67, 'True system': 0.0}
   clim_w1_max over seeds {'ESN': 0.171, 'ESN without squared features': 0.169, 'GRU': 0.144, 'GRU without input noise': 1.0, 'MLP delay': 0.179, 'True system': 0.134}
main lorenz96: vpt order {'MLP delay': 2.882, 'ESN': 2.115, 'GRU': 1.33}; clim_ok order {'ESN': 1.0, 'MLP delay': 1.0, 'GRU': 1.0}
   ratios ESN/MLP 0.73 ESN/GRU 1.59 MLP/ESN 1.36
   fit_seconds {'ESN': 0.16, 'ESN without squared features': 0.15, 'GRU': 62.66, 'GRU without input noise': 62.44, 'MLP delay': 16.11, 'True system': 0.0}
   clim_w1_max over seeds {'ESN': 0.073, 'ESN without squared features': 1.0, 'GRU': 0.089, 'GRU without input noise': 1.0, 'MLP delay': 0.067, 'True system': 0.056}
compare lorenz63 vpt: ESN 9.546 vs MLP delay 5.578 delta +3.968 paired p=3.6e-06 welch p=2.1e-07 d=15.5
compare lorenz63 clim_ok: ESN 0.850 vs MLP delay 0.810 delta +0.040 paired p=0.654 welch p=0.664 d=0.3
compare lorenz63 vpt: ESN 9.546 vs GRU 3.787 delta +5.759 paired p=3.1e-05 welch p=1.5e-06 d=11.8
compare lorenz63 clim_ok: ESN 0.850 vs GRU 0.860 delta -0.010 paired p=0.704 welch p=0.903 d=-0.1
compare lorenz63 vpt: ESN 9.546 vs ESN without squared features 8.133 delta +1.414 paired p=0.008 welch p=0.010 d=2.5
compare lorenz63 clim_ok: ESN 0.850 vs ESN without squared features 0.840 delta +0.010 paired p=0.799 welch p=0.907 d=0.1
compare lorenz63 vpt: GRU 3.787 vs GRU without input noise 3.671 delta +0.116 paired p=0.657 welch p=0.759 d=0.2
compare lorenz63 clim_ok: GRU 0.860 vs GRU without input noise 0.630 delta +0.230 paired p=0.205 welch p=0.223 d=0.9
compare lorenz96 vpt: ESN 2.115 vs MLP delay 2.882 delta -0.767 paired p=0.018 welch p=0.005 d=-2.5
compare lorenz96 clim_ok: ESN 1.000 vs MLP delay 1.000 delta +0.000 paired p=n/a welch p=n/a d=n/a
compare lorenz96 vpt: ESN 2.115 vs GRU 1.330 delta +0.785 paired p=0.002 welch p=0.004 d=2.7
compare lorenz96 clim_ok: ESN 1.000 vs GRU 1.000 delta +0.000 paired p=n/a welch p=n/a d=n/a
compare lorenz96 vpt: ESN 2.115 vs ESN without squared features 0.961 delta +1.154 paired p=0.002 welch p=9.5e-04 d=4.5
compare lorenz96 clim_ok: ESN 1.000 vs ESN without squared features 0.000 delta +1.000 paired p=n/a welch p=n/a d=n/a
compare lorenz96 vpt: GRU 1.330 vs GRU without input noise 1.329 delta +0.001 paired p=0.995 welch p=0.997 d=0.0
compare lorenz96 clim_ok: GRU 1.000 vs GRU without input noise 0.010 delta +0.990 paired p=6.2e-08 welch p=6.2e-08 d=62.6
