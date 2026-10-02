#!/bin/bash
# Fix round (after audit): re-runs every KRR system with the wide hyperparameter grid, plus the grid-sensitivity,
# linear-ridge and mean-predictor runs. usage: run_fix.sh <lane 0|1>. MLP runs are not repeated (their code is unchanged).
lane=$1; i=0
job() { # kind name group sys seed n grid tag
  i=$((i+1)); [ $((i%2)) -eq $lane ] || return 0
  f=results/raw/$3_$4_n$6_$7_s$5.json
  nice -n 10 rh run --kind $1 --name "$2" --group $3 --task lj_clusters --seed $5 \
    --config "{\"n_train\": $6, \"krr_grid\": \"$7\"}" --metrics-file $f -- $PY method/run.py --system $4 --seed $5 --n_train $6 --krr_grid $7 --out $f > results/raw/log_$3_$4_n$6_$7_s$5.txt 2>&1
}
declare -a KRR=("raw_krr|Raw coords KRR|baseline" "sorted_krr|Sorted dist KRR|baseline" "sf_krr|SymFn-sum KRR|method")
for s in 0 1 2 3 4; do for e in "${KRR[@]}"; do IFS='|' read k nm kind <<< "$e"; job $kind "$nm" main $k $s 500 wide; done; done
for n in 50 150 1500; do for s in 0 1 2; do for e in "${KRR[@]}"; do IFS='|' read k nm kind <<< "$e"; job $kind "$nm" sweep_ntrain $k $s $n wide; done; done; done
for s in 0 1 2 3 4; do
 job ablation "SymFn-sum KRR radial-only" abl_sf sfrad_krr $s 500 wide
 job ablation "SymFn-sum linear ridge" abl_linear sf_lin $s 500 wide
 job ablation "SymFn-sum linear ridge radial-only" abl_linear sfrad_lin $s 500 wide
 job ablation "Sorted dist linear ridge" abl_linear sorted_lin $s 500 wide
 for g in narrow mid; do
  job ablation "SymFn-sum KRR ($g grid)" sweep_krrgrid sf_krr $s 500 $g
  job ablation "Sorted dist KRR ($g grid)" sweep_krrgrid sorted_krr $s 500 $g
 done
done
# mean-predictor reference at the other training sizes (no hyperparameters)
for n in 50 150 1500; do for s in 0 1 2; do
 i=$((i+1)); [ $((i%2)) -eq $lane ] || continue
 f=results/raw/sweep_ntrain_const_n${n}_s$s.json
 nice -n 10 rh run --kind baseline --name "Mean predictor" --group sweep_ntrain --task lj_clusters --seed $s --config "{\"n_train\": $n}" \
   --metrics-file $f -- $PY method/run.py --system const --seed $s --n_train $n --out $f > results/raw/log_sweep_ntrain_const_n${n}_s$s.txt 2>&1
done; done
# untruncated-energy tail (documents why E <= 50 truncation is used)
if [ "$lane" = 0 ]; then
 f=results/raw/sanity_energy_tail_s0.json
 nice -n 10 rh run --kind sanity --name "Energy tail (untruncated)" --group sanity --task lj_clusters --seed 0 --config '{"m": 4000}' \
   --metrics-file $f -- $PY method/energy_tail.py --seed 0 --m 4000 --out $f > results/raw/log_sanity_energy_tail_s0.txt 2>&1
fi
