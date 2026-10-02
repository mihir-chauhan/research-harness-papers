#!/bin/bash
# usage: run_all.sh <phase>; runs every registered configuration through `rh run`
set -u
cd "$RH_PROJECT"
r() { # kind name group task seed tag system [extra args] [config json]
  local kind=$1 name=$2 group=$3 task=$4 seed=$5 tag=$6 sys=$7 cfg=$8; shift 8
  [ -f results/raw/${group}_${tag}_${task}_s${seed}.json ] && return 0  # resume: skip finished runs
  nice -n 10 rh run --kind $kind --name "$name" --group $group --task $task --seed $seed --config "$cfg" \
    --metrics-file results/raw/${group}_${tag}_${task}_s${seed}.json -- \
    $PY method/run.py --system $sys --task $task --seed $seed "$@" --out results/raw/${group}_${tag}_${task}_s${seed}.json | tail -1 | cut -c1-120
}
case $1 in
main)
 for t in lever safe signal; do for s in 0 1 2 3 4; do
  r baseline "Self-play" main $t $s sp SP '{}'
  r method "Other-play" main $t $s op OP '{}'
  r baseline "Population (FCP-style)" main $t $s pbt PBT '{"pop_size": 8}'
 done; done;;
abl)
 for t in lever safe; do for s in 0 1 2 3 4; do
  r ablation "Other-play" abl_symmetry $t $s op OP '{}'
  r ablation "OP-full (wrong group)" abl_symmetry $t $s opfull OP-full '{}'
  r ablation "Self-play" abl_symmetry $t $s sp SP '{}'
 done; done
 for t in signal; do for s in 0 1 2 3 4; do
  r ablation "Other-play" abl_symmetry $t $s op OP '{}'
  r ablation "Self-play" abl_symmetry $t $s sp SP '{}'
 done; done;;
pop)
 for t in lever safe signal; do for K in 1 2 4 16 32; do for s in 0 1 2 3 4; do
  r ablation "Population (FCP-style)" sweep_popsize $t $s K$K PBT "{\"pop_size\": $K}" --pop_size $K
 done; done; done;;
init)
 for sd in 0.25 0.5 2 4; do for s in 0 1 2 3 4; do
  r ablation "Self-play" sweep_init lever $s sp_sd$sd SP "{\"init_std\": $sd}" --init_std $sd
  r ablation "Other-play" sweep_init lever $s op_sd$sd OP "{\"init_std\": $sd}" --init_std $sd
 done; done;;
steps)
 for st in 500 5000 15000; do for s in 0 1 2 3 4; do
  r ablation "Other-play" sweep_steps lever $s op_st$st OP "{\"steps\": $st}" --steps $st
 done; done;;
esac
