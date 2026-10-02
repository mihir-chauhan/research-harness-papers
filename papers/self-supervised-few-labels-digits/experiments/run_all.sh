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
for s in $SEEDS; do for t in n50 n10 n200; do
  run baseline "Pixels + LR" main $t $s pix '{}' --system pixels_lr
  run baseline "PCA + LR" main $t $s pca '{}' --system pca_lr
  run baseline "Random CNN + probe" main $t $s rand '{}' --system random_cnn
  run baseline "Supervised scratch" main $t $s sup '{}' --system supervised
  run baseline "Rotation (reimplemented)" main $t $s rot '{}' --system rotation
  run method "SimCLR-style probe" main $t $s simclr '{}' --system simclr
done; done
echo MAIN_DONE_$1
