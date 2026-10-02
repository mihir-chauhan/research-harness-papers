# Protocol
Tasks h{0,0.1..1}_mu{0.5,1,2}; systems MLP, GCN, H2GCN-style, LP; seeds 0-4; group `main` (660 runs). Ablation group `abl_h2gcn` (tied weights / 2-hop; h in {0.1,0.4,0.9}, mu=1, seeds 0-4). Sensitivity `sweep_deg` (mean degree) for GCN/MLP/H2GCN at h=0.4, mu=1. Metric: test accuracy. Tuning: method/tune.py, validation only. Hardware: shared CPU laptop, 2 threads; each run ~1-2 s.
