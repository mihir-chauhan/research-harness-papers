#!/bin/bash
# usage: run_all.sh <lane: main|abl> <part 0|1>   (two lanes run in parallel)
cd "$(dirname "$0")/.." ; export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
run() { # kind name group task seed file config -- args
  local kind=$1 name=$2 group=$3 task=$4 seed=$5 f=$6 cfg=$7; shift 7
  [ -f results/raw/$f.json ] && return
  rh run --kind $kind --name "$name" --group $group --task $task --seed $seed --config "$cfg" --metrics-file results/raw/$f.json -- \
    nice -n 10 $PY method/run.py --task $task --seed $seed --out results/raw/$f.json "$@" >/dev/null 2>&1
}
# (bash 3.2 on macOS has no associative arrays: use a function)
NAMEOF() { case $1 in snaive) echo "Seasonal naive";; dlinear) echo DLinear;; patchtst) echo PatchTST;; gru) echo GRU;; esac; }
KIND() { [ $1 = dlinear ] && echo method || echo baseline; }
i=0
if [ $1 = main ]; then
  for task in regime etth1 trend multiseas noisy seas1; do for seed in 0 1 2; do for sy in snaive dlinear patchtst gru; do
    i=$((i+1)); [ $((i%2)) = $2 ] || continue
    run $(KIND $sy) "$(NAMEOF $sy)" main $task $seed main_${sy}_${task}_$seed '{}' --system $sy
  done; done; done
else
  for seed in 0 1 2; do
    for task in trend regime etth1; do for sy in linear dlinear patchtst gru; do
      i=$((i+1)); [ $((i%2)) = $2 ] || continue
      [ $sy = linear ] && run ablation "Linear (no decomp)" abl_design $task $seed abl_linear_${task}_$seed '{"variant":"no_decomp"}' --system linear --horizons 96
      [ $sy != linear ] && run ablation "$(NAMEOF $sy) no norm" abl_design $task $seed abl_nonorm_${sy}_${task}_$seed '{"variant":"no_norm"}' --system $sy --horizons 96 --no_norm
    done; done
    for d in 100 250 1000 4000; do for sy in dlinear patchtst gru; do
      i=$((i+1)); [ $((i%2)) = $2 ] || continue
      run ablation "$(NAMEOF $sy)" sweep_dwell regime $seed sw_dwell_${sy}_${d}_$seed "{\"dwell\":$d}" --system $sy --horizons 96 --dwell $d
    done; done
    for nz in 0.1 0.6 1.5 3.0; do for sy in dlinear patchtst gru; do
      i=$((i+1)); [ $((i%2)) = $2 ] || continue
      run ablation "$(NAMEOF $sy)" sweep_noise regime $seed sw_noise_${sy}_${nz}_$seed "{\"noise\":$nz}" --system $sy --horizons 96 --noise $nz
    done; done
  done
fi
