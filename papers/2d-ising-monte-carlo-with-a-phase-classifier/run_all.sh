#!/bin/bash
# usage: run_all.sh <seed list...> ; runs main group for each seed
for s in "$@"; do
  for sys in "Binder/chi (reference)" "PCA" "LogReg (raw)" "LogReg (Z2-fixed)" "MLP" "Confusion (MLP)" "CNN"; do
    kind=baseline; [ "$sys" = "CNN" ] && kind=method
    f=$(echo "$sys" | tr -c 'A-Za-z0-9\n' '_')
    rh run --kind $kind --name "$sys" --group main --task ising --seed $s --metrics-file results/raw/main_${f}_s$s.json -- $PY method/run.py --system "$sys" --seed $s --out results/raw/main_${f}_s$s.json
  done
done
