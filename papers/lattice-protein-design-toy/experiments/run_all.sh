#!/bin/bash
# Main + ablation runs. Usage: run_all.sh <worker 0|1>; two workers split the job list.
cd "$(dirname "$0")/.." || exit 1
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
W=$1; i=0
job(){ # kind name group seed config-json extra-args...
  local kind=$1 name=$2 group=$3 seed=$4 cfg=$5; shift 5
  if [[ " $* " == *" ar "* ]]; then i=$((i+1)); [ $((i % 2)) -eq "$W" ] || return 0; else [ "$W" -eq 0 ] || return 0; fi
  # skip jobs already logged (same name/group/seed/config)
  $PY - "$name" "$group" "$seed" "$cfg" <<'PY' && return 0
import json,sys
n,g,s,c=sys.argv[1:]
for l in open("results/runs.jsonl"):
    r=json.loads(l)
    if r.get("name")==n and r.get("group")==g and str(r.get("seed"))==s and r.get("config")==json.loads(c): sys.exit(0)
sys.exit(1)
PY
  local f=results/raw/${group}_$(echo "$name" | tr -c 'A-Za-z0-9\n' _)_${cfg//[^A-Za-z0-9.]/}_s${seed}.json
  rh run --kind "$kind" --name "$name" --group "$group" --task hp16 --seed "$seed" --config "$cfg" --metrics-file "$f" -- \
     nice -n 10 $PY -W ignore method/run.py --seed "$seed" --out "$f" "$@" >/dev/null 2>&1
}
for s in 0 1 2 3 4; do
  job baseline "Random search" main $s '{}' --system random
  job baseline "Simulated annealing" main $s '{"T0": 0.5, "T1": 0.2}' --system sa --T0 0.5 --T1 0.2
  job baseline "Contact heuristic" main $s '{}' --system heuristic
  job method "Conditional AR designer" main $s '{"epochs": 60, "tau": 0.7}' --system ar --epochs 60 --tau 0.7
done
for s in 0 1 2 3 4; do
  job ablation "Conditional AR designer" abl_components $s '{"epochs": 60, "tau": 0.7, "variant": "full"}' --system ar --epochs 60 --tau 0.7 --kmax 100
  job ablation "Unconditional AR" abl_components $s '{"epochs": 60, "tau": 0.7, "variant": "uncond"}' --system ar --epochs 60 --tau 0.7 --kmax 100 --conditional 0
  job ablation "No reversal augmentation" abl_components $s '{"epochs": 60, "tau": 0.7, "variant": "noaug"}' --system ar --epochs 60 --tau 0.7 --kmax 100 --augment 0
  for fr in 0.1 0.25 0.5; do
    job ablation "Conditional AR designer" sweep_data_frac $s "{\"data_frac\": $fr}" --system ar --epochs 60 --tau 0.7 --kmax 100 --data_frac $fr
  done
done
