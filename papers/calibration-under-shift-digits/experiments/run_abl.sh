#!/bin/bash
# ablation + sweeps; usage: run_abl.sh oracle|members|dropout
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
case $1 in
oracle)
 for s in 0 1 2 3 4; do for t in rot0 rot10 rot20 rot30 rot45 rot60 noise0.25 noise0.5 noise0.75 noise1.0 rot30_noise0.5; do
  f=results/raw/abl_oracle_${t}_s${s}.json
  rh run --kind ablation --name "TS oracle (shifted val)" --group abl_oracle --task $t --seed $s --metrics-file $f -- nice -n 10 $PY method/run.py --system ts_oracle --task $t --seed $s --out $f >/dev/null || echo FAIL $t $s
 done; done;;
members)
 for s in 0 1 2; do for t in rot0 rot30 noise0.5; do for m in 1 2 3 5 10; do
  f=results/raw/sw_members${m}_${t}_s${s}.json
  rh run --kind ablation --name "Deep ensemble" --group sweep_members --task $t --seed $s --config "{\"members\": $m}" --metrics-file $f -- nice -n 10 $PY method/run.py --system ens --members $m --task $t --seed $s --out $f >/dev/null || echo FAIL
 done; done; done;;
dropout)
 for s in 0 1 2; do for t in rot0 rot30 noise0.5; do for p in 0.1 0.2 0.3 0.5; do
  f=results/raw/sw_p${p}_${t}_s${s}.json
  rh run --kind ablation --name "MC dropout" --group sweep_dropout --task $t --seed $s --config "{\"p\": $p}" --metrics-file $f -- nice -n 10 $PY method/run.py --system mcd --p $p --task $t --seed $s --out $f >/dev/null || echo FAIL
 done; done; done;;
dropdet)
 for s in 0 1 2 3 4; do for t in rot0 rot10 rot20 rot30 rot45 rot60 noise0.25 noise0.5 noise0.75 noise1.0 rot30_noise0.5; do
  f=results/raw/abl_dropdet_${t}_s${s}.json
  rh run --kind ablation --name "Dropout-trained MLP, deterministic" --group abl_dropdet --task $t --seed $s --metrics-file $f -- nice -n 10 $PY method/run.py --system mcd_det --task $t --seed $s --out $f >/dev/null || echo FAIL $t $s
 done; done;;
esac
