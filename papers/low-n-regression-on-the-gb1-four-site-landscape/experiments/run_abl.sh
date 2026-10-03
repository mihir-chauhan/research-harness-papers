#!/bin/bash
# usage: run_abl.sh gp|alpha|cnn
TASKS="rand_48 rand_96 rand_384 rand_2000 dbl_48 dbl_96 dbl_384 dbl_2000"
case $1 in
gp)
 for t in $TASKS; do for seed in 0 1 2 3 4; do f=results/raw/ablgp_${t}_$seed.json
  nice -n 10 rh run --kind ablation --name "GP fixed hyperparameters" --group abl_gp --task $t --seed $seed --config '{"gp_fixed":1}' --metrics-file $f -- $PY method/run.py --system gp --task $t --seed $seed --out $f --gp_fixed 1 | cut -c1-90; done; done;;
alpha)
 for sys in ridge pairwise; do
  if [ $sys = ridge ]; then nm="One-hot ridge fixed alpha"; else nm="One-hot + pairwise ridge fixed alpha"; fi
  for al in 0.001 0.01 0.1 1 10 100 1000; do for seed in 0 1 2 3 4; do f=results/raw/alpha_${sys}_${al}_$seed.json
  nice -n 10 rh run --kind ablation --name "$nm" --group sweep_alpha --task rand_384 --seed $seed --config "{\"alpha\":$al}" --metrics-file $f -- $PY method/run.py --system $sys --task rand_384 --seed $seed --out $f --alpha $al | cut -c1-90; done; done; done;;
cnn)
 for t in rand_48 rand_96 rand_384 rand_2000; do for seed in 0 1 2 3 4; do
  f=results/raw/ablcnn_ens_${t}_$seed.json
  nice -n 10 rh run --kind ablation --name "CNN ensemble of 5" --group abl_cnn --task $t --seed $seed --config '{"ensemble":5}' --metrics-file $f -- $PY method/run.py --system cnn --task $t --seed $seed --out $f --ensemble 5 | cut -c1-90
  f=results/raw/ablcnn_log_${t}_$seed.json
  nice -n 10 rh run --kind ablation --name "CNN log target" --group abl_cnn --task $t --seed $seed --config '{"log_target":1}' --metrics-file $f -- $PY method/run.py --system cnn --task $t --seed $seed --out $f --log_target 1 | cut -c1-90
 done; done;;
esac
