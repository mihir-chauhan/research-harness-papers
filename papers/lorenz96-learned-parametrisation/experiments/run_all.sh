#!/bin/bash
# usage: run_all.sh laneA|laneB   (each lane is sequential; two lanes run at once)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
R() {
  kind=$1; name=$2; group=$3; task=$4; seed=$5; cfg=$6; shift 7
  f=results/raw/${group}_$(echo "$name$task" | tr -c 'A-Za-z0-9' _)_s$seed.json
  nice -n 10 rh run --kind $kind --name "$name" --group $group --task "$task" --seed $seed --config "$cfg" --metrics-file $f -- $PY method/run.py "$@" --seed $seed --out $f > /dev/null
}
if [ "$1" = laneA ]; then
 for s in 0 1 2 3 4; do for t in F20_c10 F20_c4; do
  R baseline "No closure" main $t $s '{}' -- --system noclosure --task $t
  R baseline "Polynomial (deg 4)" main $t $s '{"deg":4}' -- --system poly --task $t
  R baseline "MLP (32x2)" main $t $s '{"hidden":32}' -- --system mlp --task $t
  R method "AR(1) stochastic" main $t $s '{"deg":4}' -- --system ar1 --task $t
 done; done
else
 f=results/raw/sanity_precheck_dt.json
 nice -n 10 rh run --kind sanity --name "Step-size pre-check" --group sanity --task F20_c10 --seed 0 --metrics-file $f -- $PY experiments/precheck_dt.py --task F20_c10 --seed 0 --out $f > /dev/null
 for s in 0 1 2 3 4; do for t in F20_c10 F20_c4; do R baseline "Truth (indep. run)" floor $t $s '{}' -- --system truth --task $t; done; done
 for s in 0 1 2; do
  for d in 1 2 3 5 6; do R ablation "Polynomial deg $d" abl_deg F20_c10 $s "{\"deg\":$d}" -- --system poly --task F20_c10 --deg $d; done
  for w in 1 3; do R ablation "MLP stencil $w" abl_mlpin F20_c10 $s "{\"stencil\":$w}" -- --system mlp --task F20_c10 --stencil $w; done
  for g in 0.5 1.5; do R ablation "AR(1) sigma x$g" abl_ar1 F20_c10 $s "{\"sigma_scale\":$g}" -- --system ar1 --task F20_c10 --sigma_scale $g; done
  R ablation "AR(1) white (phi=0)" abl_ar1 F20_c10 $s '{"phi":0}' -- --system ar1 --task F20_c10 --phi 0
  # forcing shift: task stays F20_c10 (training regime); the deployment forcing is in the name and config
  for F in 18 22; do
   R ablation "Polynomial deg 4, deploy F=$F" abl_shift F20_c10 $s "{\"F_test\":$F}" -- --system poly --task F20_c10 --F_test $F
   R ablation "MLP 32x2, deploy F=$F" abl_shift F20_c10 $s "{\"F_test\":$F}" -- --system mlp --task F20_c10 --F_test $F
   R ablation "AR(1) stochastic, deploy F=$F" abl_shift F20_c10 $s "{\"F_test\":$F}" -- --system ar1 --task F20_c10 --F_test $F
  done
 done
fi
