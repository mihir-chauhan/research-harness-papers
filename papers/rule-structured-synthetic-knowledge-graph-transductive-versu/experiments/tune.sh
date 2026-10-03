#!/bin/bash
# tuning on validation split of fresh graphs (seeds 100,101), never the test split
cd "$(dirname "$0")/.." ; mkdir -p results/raw
for s in 100 101; do
 for m in 1 2 4; do for p in 1 2; do
  n=tune_transe_m${m}_p${p}_s$s
  nice -n 10 rh run --kind ablation --name "TransE (reimplemented)" --group tune_transe --task transductive --seed $s --config "{\"margin\": $m, \"p\": $p}" --metrics-file results/raw/$n.json -- $PY method/run.py --system transe --task transductive --seed $s --eval_split val --margin $m --p $p --out results/raw/$n.json >/dev/null
 done; done
 for e in 3 6; do for lr in 0.003 0.01; do
  n=tune_pm_e${e}_lr${lr}_s$s
  nice -n 10 rh run --kind ablation --name "Path-MP (2-hop)" --group tune_pathmp --task transductive --seed $s --config "{\"pm_epochs\": $e, \"pm_lr\": $lr}" --metrics-file results/raw/$n.json -- $PY method/run.py --system pathmp --task transductive --seed $s --eval_split val --pm_epochs $e --pm_lr $lr --out results/raw/$n.json >/dev/null
 done; done
done
