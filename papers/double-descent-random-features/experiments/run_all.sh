#!/bin/bash
# usage: run_all.sh main|abl|sweep  (run from the workspace, after sourcing env)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
TASKS="synth_n0 synth_n0.25 synth_n0.5 synth_n1 digits_n0 digits_n0.15 digits_n0.3 digits_n0.6"
go() { # kind name group task seed sysargs...
  kind=$1; name=$2; group=$3; task=$4; seed=$5; shift 5
  tag=$(echo "${group}_${name}_${task}_s${seed}" | tr -c 'A-Za-z0-9_.\n' '_')
  rh run --kind $kind --name "$name" --group $group --task $task --seed $seed --config "{\"args\": \"$*\"}" \
    --metrics-file results/raw/$tag.json -- nice -n 10 $PY method/run.py --task $task --seed $seed "$@" --out results/raw/$tag.json --curve results/raw/curve_$tag.csv | tail -0
}
case $1 in
main) for t in $TASKS; do for s in 0 1 2 3 4; do
  go baseline MinNorm main $t $s --system minnorm
  go baseline FixedRidge main $t $s --system fixed --lam 0.01
  go baseline GlobalRidge main $t $s --system global
  go method TunedRidge main $t $s --system tuned
done; done;;
abl) for t in $TASKS; do for s in 0 1 2 3 4; do
  go ablation TunedRidge-LOO abl_tuning $t $s --system loo
  go ablation TunedRidge-val50 abl_tuning $t $s --system tuned --val-size 50
done; done;;
sweep) for t in $TASKS; do for s in 0 1 2 3 4; do for l in 1e-6 1e-4 1e-3 1e-1 1 10; do
  tag=$(echo "sweep_lambda_$t_s$s_$l")
  rh run --kind ablation --name FixedRidge-sweep --group sweep_lambda --task $t --seed $s --config "{\"lam\": $l}" \
    --metrics-file results/raw/sweep_${t}_s${s}_l$l.json -- nice -n 10 $PY method/run.py --task $t --seed $s --system fixed --lam $l --out results/raw/sweep_${t}_s${s}_l$l.json --curve results/raw/curve_sweep_${t}_s${s}_l$l.csv | tail -0
done; done; done;;
esac
