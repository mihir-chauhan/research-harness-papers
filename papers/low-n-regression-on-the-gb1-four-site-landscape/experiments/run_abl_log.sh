#!/bin/bash
 for sys in ridge pairwise gp; do
  case $sys in ridge) nm="One-hot ridge log target";; pairwise) nm="One-hot + pairwise ridge log target";; gp) nm="GP log target";; esac
  for t in rand_48 rand_96 rand_384 rand_2000 dbl_384 dbl_2000; do for seed in 0 1 2 3 4; do f=results/raw/abllog_${sys}_${t}_$seed.json
  nice -n 10 rh run --kind ablation --name "$nm" --group abl_logtarget --task $t --seed $seed --config '{"log_target":1}' --metrics-file $f -- $PY method/run.py --system $sys --task $t --seed $seed --out $f --log_target 1 | cut -c1-90; done; done; done
