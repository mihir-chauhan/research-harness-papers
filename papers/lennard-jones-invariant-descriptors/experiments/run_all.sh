#!/bin/bash
# usage: run_all.sh <lane 0|1>; runs half of the job list. Needs env from seed/env.sh and RH_PROJECT.
lane=$1; i=0
job() { # kind name group sys seed n
  i=$((i+1)); [ $((i%2)) -eq $lane ] || return 0
  f=results/raw/$3_$4_n$6_s$5.json
  nice -n 10 rh run --kind $1 --name "$2" --group $3 --task lj_clusters --seed $5 \
    --config "{\"n_train\": $6}" --metrics-file $f -- $PY method/run.py --system $4 --seed $5 --n_train $6 --out $f > results/raw/log_$3_$4_n$6_s$5.txt 2>&1
}
declare -a SYS=("raw_krr|Raw coords KRR|baseline" "raw_mlp|Raw coords MLP|baseline" "sorted_krr|Sorted dist KRR|baseline" "sorted_mlp|Sorted dist MLP|baseline" "sf_krr|SymFn-sum KRR|method" "sf_mlp|SymFn-sum MLP|baseline" "sf_atomwise|SymFn atomwise MLP (BP-style)|baseline")
for s in 0 1 2 3 4; do for e in "${SYS[@]}"; do IFS='|' read k nm kind <<< "$e"; job $kind "$nm" main $k $s 500; done; done
for n in 50 150 1500; do for s in 0 1 2; do for e in "${SYS[@]}"; do IFS='|' read k nm kind <<< "$e"; job $kind "$nm" sweep_ntrain $k $s $n; done; done; done
for s in 0 1 2; do
 job ablation "SymFn-sum KRR radial-only" abl_sf sfrad_krr $s 500
 job ablation "SymFn-sum MLP radial-only" abl_sf sfrad_mlp $s 500
 job ablation "Raw coords MLP + rot/perm aug" abl_aug raw_mlp_aug $s 500
done
