#!/bin/bash
# usage: run_main.sh "<seeds>"   (env: RH_PROJECT, PY set by env.sh)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
cd "$RH_PROJECT"
r() { # kind name group task seed system config tag
  local f=results/raw/$3_$8_$4_$5.json
  rh run --kind $1 --name "$2" --group $3 --task $4 --seed $5 ${7:+--config "$7"} --metrics-file $f -- nice -n 10 $PY method/run.py --system $6 --task $4 --seed $5 ${7:+--config "$7"} --out $f >/dev/null 2>&1
}
for s in $1; do
 for t in val_3_10 test_11_20 test_21_40 test_41_70; do
  r baseline "BFS" main $t $s bfs "" bfs
  r baseline "Hand heuristic" main $t $s heuristic "" heur
  r baseline "Feature-MLP policy" main $t $s mlp "" mlp
  r method "Transformer policy" main $t $s transformer "" tf
 done
done
