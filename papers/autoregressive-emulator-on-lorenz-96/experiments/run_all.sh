#!/bin/bash
# usage: run_all.sh <stream>   (A: K=8 runs; B: baselines, K=1, K=4; C: K=2 sweep and noise ablation)
source seed/env.sh
cd .
export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
r(){ # kind name group tag seed config -- args
  kind=$1; name=$2; group=$3; tag=$4; seed=$5; cfg=$6; shift 6
  f=results/raw/${group}_${tag}_s${seed}.json
  nice -n 10 rh run --kind $kind --name "$name" --group $group --task l96 --seed $seed --config "$cfg" --metrics-file $f -- \
    $PY method/run.py --task l96 --seed $seed --out $f --curve results/raw/curve_${group}_${tag}_s${seed}.csv "$@" | tail -1 | cut -c1-60
}
case $1 in
A) for s in 0 1 2 3 4; do r method "CNN K=8" main K8 $s '{"K": 8}' --system cnn --rollout 8; done ;;
B) for s in 0 1 2 3 4; do
     r baseline "Persistence" main persistence $s '{}' --system persistence
     r baseline "Climatology" main climatology $s '{}' --system climatology
     r baseline "Linear stencil (ridge)" main linear $s '{}' --system linear
     r baseline "CNN K=1" main K1 $s '{"K": 1}' --system cnn --rollout 1
     r method "CNN K=4" main K4 $s '{"K": 4}' --system cnn --rollout 4
   done ;;
C) for s in 0 1 2 3 4; do
     r ablation "CNN K=2" sweep_K K2 $s '{"K": 2}' --system cnn --rollout 2
     r ablation "CNN K=1 noise=0.03" abl_noise K1n03 $s '{"K": 1, "noise": 0.03}' --system cnn --rollout 1 --noise 0.03
     r ablation "CNN K=1 noise=0.1" abl_noise K1n10 $s '{"K": 1, "noise": 0.1}' --system cnn --rollout 1 --noise 0.1
   done ;;
D) for s in 0 1 2 3 4; do
     r ablation "CNN K=1 ntrain=4" sweep_ntrain K1n4 $s '{"K": 1, "ntrain": 4}' --system cnn --rollout 1 --ntrain 4
     r ablation "CNN K=4 ntrain=4" sweep_ntrain K4n4 $s '{"K": 4, "ntrain": 4}' --system cnn --rollout 4 --ntrain 4
   done ;;
esac
