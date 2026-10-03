#!/bin/bash
# usage: run_abl.sh "<seeds>"
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
cd "$RH_PROJECT"
r() { # kind name group task seed system config tag
  local f=results/raw/$3_$8_$4_$5.json
  rh run --kind $1 --name "$2" --group $3 --task $4 --seed $5 ${7:+--config "$7"} --metrics-file $f -- nice -n 10 $PY method/run.py --system $6 --task $4 --seed $5 ${7:+--config "$7"} --out $f >/dev/null 2>&1
}
for s in $1; do
 for t in test_11_20 test_21_40 test_41_70; do
  r ablation "Transformer greedy" abl_search $t $s transformer '{"mode": "greedy"}' greedy
  r ablation "Transformer rank cost" abl_search $t $s transformer '{"cost": "rank"}' rank
  r ablation "MLP rank cost" abl_search $t $s mlp '{"cost": "rank"}' mlprank
  r ablation "Transformer learned pos" abl_pos $t $s transformer '{"pos": "learned"}' lp
 done
 for n in 1000 4000 10000; do
  for t in test_11_20 test_41_70; do
   r ablation "Transformer ntrain" sweep_ntrain $t $s transformer "{\"ntrain\": $n}" n$n
  done
 done
 for b in 25 50 200; do
  r ablation "Transformer budget" sweep_budget test_41_70 $s transformer "{\"budget\": $b}" tf$b
  r ablation "Hand heuristic budget" sweep_budget test_41_70 $s heuristic "{\"budget\": $b}" h$b
  r ablation "BFS budget" sweep_budget test_41_70 $s bfs "{\"budget\": $b}" b$b
 done
done
