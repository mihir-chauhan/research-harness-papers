#!/bin/bash
# usage: run_all.sh <stream 0|1>   ; streams split seeds so SSL pretraining caches are not shared across streams
source seed/env.sh
cd .
export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
run() { # kind name group task seed tag extra-args-json extra-cli...
  kind=$1; name=$2; group=$3; task=$4; seed=$5; tag=$6; cfg=$7; shift 7
  f=results/raw/${group}_${tag}_${task}_s${seed}.json
  [ -f $f ] && return
  nice -n 10 rh run --kind $kind --name "$name" --group $group --task $task --seed $seed --config "$cfg" --metrics-file $f -- $PY method/run.py --task $task --seed $seed --out $f "$@" > /dev/null 2>results/raw/err_${group}_${tag}_${task}_s${seed}.txt || echo FAIL $f
}
if [ "$1" = 0 ]; then SEEDS="0 1 2"; else SEEDS="3 4"; fi
for s in $SEEDS; do
 for t in n50 n10 n200; do
  run ablation "SimCLR geom-only" abl_aug $t $s geom '{"aug":"geom"}' --system simclr --aug geom
  run ablation "SimCLR photo-only" abl_aug $t $s photo '{"aug":"photo"}' --system simclr --aug photo
  run ablation "Supervised + aug" abl_supaug $t $s supaug '{"sup_aug":"full"}' --system supervised --sup_aug full
 done
 for tau in 0.1 0.2 1.0; do run ablation "SimCLR tau=$tau" sweep_tau n50 $s tau$tau "{\"tau\":$tau}" --system simclr --tau $tau; done
 for ep in 10 30; do run ablation "SimCLR ep=$ep" sweep_epochs n50 $s ep$ep "{\"epochs\":$ep}" --system simclr --epochs $ep; done
done
echo ABL_DONE_$1
