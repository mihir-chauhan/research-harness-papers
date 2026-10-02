#!/bin/zsh
# grid extension: the best lr was at the upper edge of the first grid for full, scratch, lora, lastblock
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
run() {
  f=results/raw/tune_$1_$3_$4.json
  rh run --kind sanity --name "$1" --group tune --task $4 --seed 100 --config "{\"lr\": $3, \"rank\": $5, \"split\": \"val\"}" --metrics-file $f -- nice -n 10 $PY method/run.py --system $2 --rank $5 --lr $3 --task $4 --seed 100 --eval_split val --out $f
}
for t in sort_desc reverse; do
 run full full 0.01 $t 4 & run scratch scratch 0.01 $t 4; wait
 run lora lora 0.03 $t 4 & run lastblock lastblock 0.03 $t 4; wait
 run head head 0.03 $t 4
done
