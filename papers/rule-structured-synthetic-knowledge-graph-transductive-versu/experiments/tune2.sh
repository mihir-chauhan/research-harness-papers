#!/bin/bash
# second tuning round for TransE (best margin was at the edge of the first grid); validation split only
cd "$(dirname "$0")/.." ; mkdir -p results/raw
for s in 100 101; do
 for cfg in "6 1 64 200" "8 1 64 200" "4 1 64 400" "4 1 128 200"; do
  set -- $cfg; m=$1; p=$2; dim=$3; ep=$4
  n=tune2_transe_m${m}_p${p}_d${dim}_e${ep}_s$s
  nice -n 10 rh run --kind ablation --name "TransE (reimplemented)" --group tune_transe --task transductive --seed $s --config "{\"margin\": $m, \"p\": $p, \"dim\": $dim, \"epochs\": $ep}" --metrics-file results/raw/$n.json -- $PY method/run.py --system transe --task transductive --seed $s --eval_split val --margin $m --p $p --dim $dim --epochs $ep --out results/raw/$n.json >/dev/null
 done
done
