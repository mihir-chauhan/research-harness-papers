#!/bin/bash
# ablation (tied weights, 2-hop) and degree sweep; two workers
cd "$(dirname "$0")/.."
{
for h in 0.1 0.4 0.9; do for s in 0 1 2 3 4; do
 echo ablation abl_h2gcn H2GCN_tied_weights tied h2gcn $h 1.0 $s --sep 0
 echo ablation abl_h2gcn H2GCN_+_2-hop twohop h2gcn $h 1.0 $s --twohop 1
done; done
for d in 2 5 20; do for s in 0 1 2 3 4; do
 echo ablation sweep_deg MLP_deg$d mlp$d mlp 0.4 1.0 $s --deg $d
 echo ablation sweep_deg GCN_deg$d gcn$d gcn 0.4 1.0 $s --deg $d
 echo ablation sweep_deg H2GCN_deg$d h2gcn$d h2gcn 0.4 1.0 $s --deg $d
done; done
} > /tmp/jobs_extra.txt
xargs -P2 -L1 experiments/run_abl.sh < /tmp/jobs_extra.txt
