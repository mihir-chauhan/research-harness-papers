#!/bin/bash
# re-run of the confusion read-out after the abscissa fix (trial boundaries T'), and its dependent collapse analyses
for s in 0 1 2 3 4 5 6 7 8 9; do
  sys="Confusion (MLP)"; f=Confusion__MLP_
  rh run --kind baseline --name "$sys" --group main --task ising --seed $s --metrics-file results/raw/main_${f}_s$s.json -- $PY method/run.py --system "$sys" --seed $s --out results/raw/main_${f}_s$s.json
done
sys="Confusion (MLP)"; f=Confusion__MLP_
for s in 0 1 2 3 4 5 6 7 8 9; do
  rh run --kind ablation --name "$sys" --group abl_nu_fixed --task ising --seed $s --config '{"nu": 1.0}' --metrics-file results/raw/nu1_${f}_s$s.json -- $PY method/analysis_nu1.py --system "$sys" --seed $s --out results/raw/nu1_${f}_s$s.json
  for w in 0.3 0.45; do
    rh run --kind ablation --name "$sys" --group abl_window_$w --task ising --seed $s --config "{\"window\": $w}" --metrics-file results/raw/win${w}_${f}_s$s.json -- $PY method/analysis_window.py --system "$sys" --seed $s --window $w --out results/raw/win${w}_${f}_s$s.json
  done
done
# nsamp sweep with epochs scaled so that nsamp x epochs equals the default 50 x 20 gradient-update budget
for s in 0 1 2 3 4; do
 for sys in MLP CNN; do
  g=$(echo "$sys" | tr -c 'A-Za-z0-9\n' '_')
  for n in 10 25; do
   ep=$((1000 / n))
   rh run --kind ablation --name "$sys" --group sweep_nsamp_ep --task ising --seed $s --config "{\"nsamp\": $n, \"epochs\": $ep}" --metrics-file results/raw/swe_${g}_${n}_s$s.json -- $PY method/run.py --system "$sys" --seed $s --nsamp $n --epochs $ep --out results/raw/swe_${g}_${n}_s$s.json
  done
 done
done
# analyses
rh run --kind sanity --name "Paired tests" --group analysis --task ising --seed 0 --metrics-file results/raw/analysis.json -- $PY method/analysis.py results/raw/analysis.json
rh run --kind sanity --name "Sweep summary" --group analysis --task ising --seed 0 --metrics-file results/raw/analysis_sweeps.json -- $PY method/analysis_sweeps.py results/raw/analysis_sweeps.json
