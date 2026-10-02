# Results (CSBM, K=3, n=900, d=10; 5 seeds per cell; 660 main runs + 30 ablation + 45 degree sweep)
Tables: results/tables/{cells,main_mu1,winners,gcn_mlp_gap,h2_viol,abl_h2gcn_custom,sweep_deg_custom}.tex; tests: results/tables/paired_tests.csv, `rh compare`.
- H1 (GCN < MLP at mu=1, h in {0.3,0.4,0.5}; paired t, alpha .05): PARTLY SUPPORTED. h=0.3: -9.1 pts, p=0.007; h=0.4: -3.3 pts, p=0.142 (n.s.); h=0.5: GCN above MLP (+9.9, p=0.014). Dip is larger at h=0.2 (-9.5, p=0.001) and deepens with mu.
- H2 (H2GCN >= max(MLP,GCN)-0.02 everywhere): REFUTED, 6/33 violations (largest -0.078 at mu=0.5,h=0.6).
- H3 (LP best only at h>=0.8, mu=0.5; below MLP for h<=0.5): REFUTED (LP also best at mu=1 h>=0.9 and mu=2 h=1).
- H4 (crossover lower for weak features): SUPPORTED on the h>=1/3 branch (0.4/0.5/0.6 for mu=0.5/1/2); literal wording trivially false since GCN>MLP at h=0. Post-hoc clarification.
- H5 (tied weights hurt at h=0.1, 0.4): SUPPORTED at h=0.1 (0.724->0.356), NOT at h=0.4 (p=0.55).
