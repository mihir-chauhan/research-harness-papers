#!/bin/bash
# usage: run_main.sh <system> <model> <task> <seed>   (logs one run in group main)
sys=$1; mod=$2; task=$3; seed=$4
case $sys in none) sn="no correction";; reweight) sn="reweight";; ros) sn="ROS";; smote) sn="SMOTE";; threshold) sn="threshold";; esac
M=$(echo $mod | tr a-z A-Z)
if [ "$sys" = none ] && [ "$mod" = lr ]; then kind=method; else kind=baseline; fi
rh run --kind $kind --name "$M + $sn" --group main --task $task --seed $seed \
  --metrics-file results/raw/main_${sys}_${mod}_${task}_${seed}.json -- \
  $PY method/run.py --system $sys --model $mod --task $task --seed $seed --out results/raw/main_${sys}_${mod}_${task}_${seed}.json > /dev/null
