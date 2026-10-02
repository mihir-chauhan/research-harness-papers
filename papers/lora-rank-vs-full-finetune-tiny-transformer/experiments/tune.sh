#!/bin/zsh
# learning-rate tuning on validation split, seed 100
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p results/raw
run() { # system sysargs-name lr task rank
  f=results/raw/tune_$1_$3_$4.json
  rh run --kind sanity --name "$1" --group tune --task $4 --seed 100 --config "{\"lr\": $3, \"rank\": $5, \"split\": \"val\"}" --metrics-file $f -- nice -n 10 $PY method/run.py --system $2 --rank $5 --lr $3 --task $4 --seed 100 --eval_split val --out $f
}
rh run --kind sanity --name pretrained --group tune --task reverse --seed 100 --config '{"split": "val"}' --metrics-file results/raw/tune_pre.json -- nice -n 10 $PY method/run.py --system pretrained --task reverse --seed 100 --eval_split val --out results/raw/tune_pre.json
for t in sort_desc reverse; do
 for lr in 0.0003 0.001 0.003; do run full full $lr $t 4 & run scratch scratch $lr $t 4; wait; done
 for lr in 0.001 0.003 0.01; do run lora lora $lr $t 4 & run lastblock lastblock $lr $t 4; wait; run head head $lr $t 4; done
done
