#!/bin/bash
# Step-matched control: no augmentation, 120 epochs (same number of gradient steps as augmentation with 60 epochs).
cd "$(dirname "$0")/.." || exit 1
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
W=$1; i=0
for s in 0 1 2 3 4; do for fr in 0.1 0.25 0.5 1.0; do
  i=$((i+1)); [ $((i % 2)) -eq "$W" ] || continue
  f=results/raw/abl_aug_steps_noaug120_${fr}_s${s}.json
  rh run --kind ablation --name "No augmentation, 120 epochs" --group abl_aug_steps --task hp16 --seed $s --config "{\"data_frac\": $fr, \"augment\": 0, \"epochs\": 120}" --metrics-file $f -- nice -n 10 $PY -W ignore method/run.py --seed $s --out $f --system ar --epochs 120 --tau 0.7 --kmax 100 --data_frac $fr --augment 0 --report_distinct 1 >/dev/null 2>&1
done; done
