#!/bin/bash
lane=$1; i=0
job() { i=$((i+1)); [ $((i%2)) -eq $lane ] || return 0
  f=results/raw/$3_$4_n500_st$6_s$5.json
  nice -n 10 rh run --kind $1 --name "$2" --group $3 --task lj_clusters --seed $5 --config "{\"n_train\": 500, \"steps\": $6}" \
    --metrics-file $f -- $PY method/run.py --system $4 --seed $5 --n_train 500 --steps $6 --out $f > results/raw/log_$3_$4_st$6_s$5.txt 2>&1; }
[ "$lane" = 0 ] && for s in 0 1 2 3 4; do
 nice -n 10 rh run --kind baseline --name "Mean predictor" --group main --task lj_clusters --seed $s --config '{"n_train": 500}' --metrics-file results/raw/main_const_n500_s$s.json -- $PY method/run.py --system const --seed $s --n_train 500 --out results/raw/main_const_n500_s$s.json > results/raw/log_main_const_s$s.txt 2>&1 || true
done 2>&1 | grep -c ok
for s in 0 1 2; do for st in 1000 12000; do
 job ablation "Sorted dist MLP" sweep_steps sorted_mlp $s $st
 job ablation "SymFn-sum MLP" sweep_steps sf_mlp $s $st
done; done
