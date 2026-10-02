#!/bin/bash
# Audit-round runs: (a) augmentation ablation at data fractions where reversal adds new pairs, (b) extended SA tuning grid on DEV.
cd "$(dirname "$0")/.." || exit 1
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
W=$1
if [ "$W" -eq 0 ]; then
for s in 0 1 2 3 4; do for fr in 0.1 0.25 0.5; do
  f=results/raw/abl_aug_frac_aug1_${fr}_s${s}.json
  rh run --kind ablation --name "Conditional AR designer" --group abl_aug_frac --task hp16 --seed $s --config "{\"data_frac\": $fr, \"augment\": 1}" --metrics-file $f -- nice -n 10 $PY -W ignore method/run.py --seed $s --out $f --system ar --epochs 60 --tau 0.7 --kmax 100 --data_frac $fr --augment 1 --report_distinct 1 >/dev/null 2>&1
done; done
else
for s in 0 1 2 3 4; do for fr in 0.1 0.25 0.5; do
  f=results/raw/abl_aug_frac_aug0_${fr}_s${s}.json
  rh run --kind ablation --name "No reversal augmentation" --group abl_aug_frac --task hp16 --seed $s --config "{\"data_frac\": $fr, \"augment\": 0}" --metrics-file $f -- nice -n 10 $PY -W ignore method/run.py --seed $s --out $f --system ar --epochs 60 --tau 0.7 --kmax 100 --data_frac $fr --augment 0 --report_distinct 1 >/dev/null 2>&1
done; done
for obj in bin log; do g=tune2_sa; [ $obj = log ] && g=tune2_sa_log
for cfg in "0.1 0.05" "0.1 0.1" "0.25 0.05" "0.25 0.1" "0.25 0.2" "0.35 0.1"; do set -- $cfg
  f=results/raw/${g}_$1_$2.json
  rh run --kind ablation --name "Simulated annealing" --group $g --task hp16 --seed 100 --config "{\"T0\": $1, \"T1\": $2}" --metrics-file $f -- nice -n 10 $PY -W ignore method/run.py --system sa --obj $obj --mode tune --seed 100 --T0 $1 --T1 $2 --out $f >/dev/null 2>&1
done; done
fi
