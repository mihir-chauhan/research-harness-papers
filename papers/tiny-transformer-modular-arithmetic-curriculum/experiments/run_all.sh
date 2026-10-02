#!/bin/bash
# usage: experiments/run_all.sh <stream 0|1>   (two streams run in parallel; jobs are split by index parity)
# Every run: rh run ... -- $PY method/run.py ; metrics to results/raw/<id>.json
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
S=$1; i=0
job() { # kind group name task seed system extra-args(json config) -- extra cli args...
  local kind=$1 group=$2 name=$3 task=$4 seed=$5 sys=$6 cfg=$7; shift 7
  i=$((i+1)); [ $((i%2)) -eq $S ] || return 0
  local id="${group}_${task}_${sys}_$(echo "$cfg" | tr -dc 'a-z0-9._')_s${seed}"
  nice -n 10 rh run --kind $kind --name "$name" --group $group --task $task --seed $seed --config "$cfg" \
    --metrics-file results/raw/$id.json -- $PY method/run.py --system $sys --task $task --seed $seed "$@" --out results/raw/$id.json > results/logs/$id.log 2>&1
}
nm() { case $1 in uniform) echo "Uniform sampling";; curriculum) echo "Operand-size curriculum";; anticurriculum) echo "Anti-curriculum";; esac; }
# main
for seed in 0 1 2 3 4; do for sys in uniform curriculum anticurriculum; do
  kind=baseline; [ $sys = curriculum ] && kind=method
  job $kind main "$(nm $sys)" wd1_f0.5 $seed $sys '{"wd":1,"frac":0.5}' --wd 1 --frac 0.5
done; done
# sensitivity to curriculum length and shuffled-order control (main cell, 5 seeds)
for seed in 0 1 2 3 4; do
  for w in 250 500 2000 4000; do
    job ablation sweep_warm "Operand-size curriculum" wd1_f0.5 $seed curriculum "{\"warm\":$w}" --wd 1 --frac 0.5 --warm $w
  done
  job ablation abl_shuffled "Shuffled-order pool growth" wd1_f0.5 $seed curriculum '{"order":"random"}' --wd 1 --frac 0.5 --order random
done
# weight decay x training fraction grid (3 seeds), main cell excluded (it is in group main)
for wd in 0 1 3; do for f in 0.4 0.5 0.7; do
  [ "$wd" = 1 ] && [ "$f" = 0.5 ] && continue
  for seed in 0 1 2; do for sys in uniform curriculum anticurriculum; do
    job ablation grid "$(nm $sys)" wd${wd}_f${f} $seed $sys "{\"wd\":$wd,\"frac\":$f}" --wd $wd --frac $f
  done; done
done; done
