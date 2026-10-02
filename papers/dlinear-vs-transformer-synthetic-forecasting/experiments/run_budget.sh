#!/bin/bash
# Training-budget sweep (fix round). usage: run_budget.sh <part 0|1>   (two lanes run in parallel)
# Same code and settings as the main grid; only --steps changes (cosine schedule spans the new budget,
# validation checkpointing still every 100 steps). The 400-step cells are the main-grid / sweep_dwell rows.
cd "$(dirname "$0")/.." ; export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
run() { # name group task seed file config -- args
  local name=$1 group=$2 task=$3 seed=$4 f=$5 cfg=$6; shift 6
  [ -f results/raw/$f.json ] && return
  rh run --kind ablation --name "$name" --group $group --task $task --seed $seed --config "$cfg" --metrics-file results/raw/$f.json -- \
    nice -n 10 $PY method/run.py --task $task --seed $seed --out results/raw/$f.json "$@" >/dev/null 2>&1
}
NAMEOF() { case $1 in dlinear) echo DLinear;; patchtst) echo PatchTST;; gru) echo GRU;; esac; }
i=0
# (a) regime and etth1, all three horizons, 1000 and 2000 steps
for task in regime etth1; do for st in 2000 1000; do for seed in 0 1 2; do for sy in dlinear gru patchtst; do
  i=$((i+1)); [ $((i%2)) = $1 ] || continue
  run "$(NAMEOF $sy)" sweep_steps $task $seed st_${sy}_${task}_${st}_$seed "{\"steps\":$st}" --system $sy --steps $st
done; done; done; done
# (b) the four tasks without regime changes, H=96, 2000 steps
for task in multiseas seas1 trend noisy; do for seed in 0 1 2; do for sy in dlinear gru patchtst; do
  i=$((i+1)); [ $((i%2)) = $1 ] || continue
  run "$(NAMEOF $sy)" sweep_steps $task $seed st_${sy}_${task}_2000_$seed '{"steps":2000,"horizons":"96"}' --system $sy --steps 2000 --horizons 96
done; done; done
# (c) dwell sweep repeated at 2000 steps (regime task, H=96); dwell 500 is the 2000-step regime row of (a)
for d in 100 250 1000 4000; do for seed in 0 1 2; do for sy in dlinear gru patchtst; do
  i=$((i+1)); [ $((i%2)) = $1 ] || continue
  run "$(NAMEOF $sy)" sweep_dwell_2000 regime $seed sw_dwell2000_${sy}_${d}_$seed "{\"dwell\":$d,\"steps\":2000}" --system $sy --horizons 96 --dwell $d --steps 2000
done; done; done
