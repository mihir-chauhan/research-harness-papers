#!/bin/bash
# usage: run_all.sh <group> <kind> <system> <lr> <seed> [extra args]
source seed/env.sh
cd .
export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
g=$1; k=$2; s=$3; lr=$4; seed=$5; w=${6:--1}; tag=${7:-}
case $s in constant) n="Constant";; cosine) n="Warmup+Cosine";; step) n="Step decay";; schedulefree) n="Schedule-free AdamW";; esac
if [ "$w" != "-1" ]; then n="$n (warmup=$w)"; fi
f=results/raw/${g}_${s}_${lr}_w${w}_s${seed}.json
[ -f $f ] && exit 0
nice -n 10 rh run --kind $k --name "$n" --group $g --task lr$lr --seed $seed --config "{\"lr\": $lr, \"warmup\": $w}" --metrics-file $f -- $PY method/run.py --system $s --lr $lr --seed $seed --warmup $w --out $f >/dev/null 2>&1
