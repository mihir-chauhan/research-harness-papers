#!/bin/bash
# usage: run_abl.sh prior <system> <model> <task> <seed>   |   run_abl.sh ratio <model> <task> <seed> <ratio>
if [ "$1" = prior ]; then
  sys=$2; mod=$3; task=$4; seed=$5; M=$(echo $mod | tr a-z A-Z)
  case $sys in reweight) sn="reweight";; ros) sn="ROS";; smote) sn="SMOTE";; esac
  f=results/raw/abl_prior_${sys}_${mod}_${task}_${seed}.json
  rh run --kind ablation --name "$M + $sn + prior corr" --group abl_priorcorr --task $task --seed $seed --config '{"prior_corr": 1}' \
    --metrics-file $f -- $PY method/run.py --system $sys --model $mod --task $task --seed $seed --prior_corr 1 --out $f > /dev/null
else
  mod=$2; task=$3; seed=$4; r=$5; M=$(echo $mod | tr a-z A-Z)
  f=results/raw/sweep_smote_${mod}_${task}_${seed}_${r}.json
  rh run --kind ablation --name "$M + SMOTE" --group sweep_smote_ratio --task $task --seed $seed --config "{\"smote_ratio\": $r}" \
    --metrics-file $f -- $PY method/run.py --system smote --model $mod --task $task --seed $seed --smote_ratio $r --out $f > /dev/null
fi
