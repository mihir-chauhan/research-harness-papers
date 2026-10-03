#!/bin/bash
# sensitivity sweeps (seeds 0-4); default margin 0.3 / nsamp 50 are the main-group rows
for s in "$@"; do
 for sys in MLP CNN; do
  f=$(echo "$sys" | tr -c 'A-Za-z0-9\n' '_')
  for m in 0.15 0.45 0.6; do
   rh run --kind ablation --name "$sys" --group sweep_margin --task ising --seed $s --config "{\"margin\": $m}" --metrics-file results/raw/swm_${f}_${m}_s$s.json -- $PY method/run.py --system "$sys" --seed $s --margin $m --out results/raw/swm_${f}_${m}_s$s.json
  done
  for n in 10 25; do
   rh run --kind ablation --name "$sys" --group sweep_nsamp --task ising --seed $s --config "{\"nsamp\": $n}" --metrics-file results/raw/swn_${f}_${n}_s$s.json -- $PY method/run.py --system "$sys" --seed $s --nsamp $n --out results/raw/swn_${f}_${n}_s$s.json
  done
 done
done
