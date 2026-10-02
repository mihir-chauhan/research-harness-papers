#!/bin/bash
# usage: run_main.sh "<seeds>"   (main group, all systems x tasks)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
TASKS="rot0 rot10 rot20 rot30 rot45 rot60 noise0.25 noise0.5 noise0.75 noise1.0 rot30_noise0.5"
for s in $1; do for t in $TASKS; do
 for spec in "mlp|baseline|MLP" "ts|method|MLP + temperature scaling" "mcd|baseline|MC dropout" "ens|baseline|Deep ensemble (5)"; do
  IFS='|' read sys kind name <<< "$spec"
  f=results/raw/main_${sys}_${t}_s${s}.json
  rh run --kind $kind --name "$name" --group main --task $t --seed $s --metrics-file $f -- nice -n 10 $PY method/run.py --system $sys --task $t --seed $s --out $f > /dev/null || echo FAIL $sys $t $s
 done; done; done
