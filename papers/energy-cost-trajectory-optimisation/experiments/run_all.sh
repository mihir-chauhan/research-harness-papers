#!/bin/bash
# usage: run_all.sh <part>   part in main|sweeps_wE|sweeps_q|tuned|diag
source seed/env.sh
export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p results/raw
dn() { if [ "$1" = iLQR-Energy ]; then echo "iLQR-Energy (ours)"; else echo "$1"; fi; }  # bash 3.2: no assoc arrays
run() { # kind name group task seed system extra-flags config
  f=results/raw/$3_$1_${6}_$4_$5${8:+_$(echo "$8" | tr -dc "0-9.")}.json
  nice -n 10 rh run --kind $1 --name "$2" --group $3 --task $4 --seed $5 ${8:+--config "$8"} --metrics-file "$f" -- $PY method/run.py --system $6 --task $4 --seed $5 $7 --out "$f" >/dev/null
}
case $1 in
main) for s in 0 1 2 3 4; do for t in pendulum cartpole; do for sy in iLQR-Energy iLQR-Quad iLQR-Quad+Energy EnergyShaping-LQR; do
  k=baseline; [ $sy = iLQR-Energy ] && k=method
  run $k "$(dn $sy)" main $t $s $sy "" ; done; done; done;;
sweeps_wE) for s in 0 1 2; do for t in pendulum cartpole; do for w in 0.01 0.1 1 10 100; do
  run ablation "iLQR-Energy (ours)" sweep_wE $t $s iLQR-Energy "--wE $w" "{\"wE\": $w}"; done; done; done;;
sweeps_q) for s in 0 1 2; do for t in pendulum cartpole; do for q in 0.01 0.1 1 10 100; do
  run ablation "iLQR-Quad" sweep_qscale $t $s iLQR-Quad "--qscale $q" "{\"qscale\": $q}"; done; done; done;;
# tuned: weight picked per cost and task on sweep seeds 0-2 (highest success, ties by lowest effort), run on held-out seeds 3-4.
# iLQR-Energy on the cart-pole picks wE=1, whose seeds 3-4 are already in group main and are not re-logged.
tuned) for s in 3 4; do
  run ablation "iLQR-Energy (ours)" tuned pendulum $s iLQR-Energy "--wE 100" "{\"wE\": 100}"
  run ablation "iLQR-Quad" tuned pendulum $s iLQR-Quad "--qscale 100" "{\"qscale\": 100}"
  run ablation "iLQR-Quad" tuned cartpole $s iLQR-Quad "--qscale 0.1" "{\"qscale\": 0.1}"; done;;
# diag: closed-loop size of the energy and quadratic state-cost terms under the combined cost (default weights)
diag) for s in 0 1 2; do for t in pendulum cartpole; do
  run ablation "iLQR-Quad+Energy" diag_terms $t $s iLQR-Quad+Energy "--diag" "{\"diag\": 1}"; done; done;;
esac
