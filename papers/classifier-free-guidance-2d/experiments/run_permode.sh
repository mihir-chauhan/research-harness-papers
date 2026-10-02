#!/bin/bash
source seed/env.sh
cd .
export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
for s in 0 1 2 3 4; do for cfg in "0 1" "3 1" "8 1" "0 0.5"; do set -- $cfg; f=results/raw/permode_w$1_tau$2_s$s.json
nice -n 10 rh run --kind ablation --name "Per-mode mass (w=$1, tau=$2)" --group abl_permode --task mix_overlap --seed $s --config "{\"w\":$1,\"tau\":$2}" --metrics-file $f -- $PY method/permode.py --seed $s --w $1 --tau $2 --out $f >/dev/null; done; done
