#!/bin/bash
# usage: run_main.sh system h mu seed
sys=$1; h=$2; mu=$3; seed=$4
case $sys in mlp) name="MLP"; kind=baseline;; gcn) name="GCN (reimplemented)"; kind=method;;
 h2gcn) name="H2GCN-style (reimplemented)"; kind=baseline;; lp) name="Label propagation (reimplemented)"; kind=baseline;; esac
f=results/raw/main_${sys}_h${h}_mu${mu}_s${seed}.json
nice -n 10 rh run --kind $kind --name "$name" --group main --task h${h}_mu${mu} --seed $seed --config "{\"h\": $h, \"mu\": $mu}" --metrics-file $f -- $PY method/run.py --system $sys --h $h --mu $mu --seed $seed --out $f > /dev/null 2>&1 || echo FAIL $sys $h $mu $seed
