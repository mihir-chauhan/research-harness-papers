#!/bin/bash
# systems other than the heuristic on the tuning bin (the heuristic's rows on this bin are in group tune_heur)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
cd "$RH_PROJECT"
r() { local f=results/raw/main_$7_$3_$4.json
  rh run --kind $1 --name "$2" --group main --task $3 --seed $4 --metrics-file $f -- nice -n 10 $PY method/run.py --system $5 --task $3 --seed $4 --out $f >/dev/null 2>&1; }
for s in 0 1 2 3 4; do
  r baseline "BFS" tune_21_35 $s bfs x bfs
  r baseline "Feature-MLP policy" tune_21_35 $s mlp x mlp
  r method "Transformer policy" tune_21_35 $s transformer x tf
done
