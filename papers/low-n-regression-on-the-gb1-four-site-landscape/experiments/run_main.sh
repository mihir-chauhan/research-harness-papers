#!/bin/bash
# usage: run_main.sh "<systems>"   (runs the main group for the given systems)
name_of() { case $1 in ridge) echo "One-hot ridge (reimplemented)";; pairwise) echo "One-hot + pairwise ridge";; gp) echo "GP Hamming kernel (reimplemented)";; cnn) echo "CNN (reimplemented)";; esac; }
for s in $1; do
 if [ $s = pairwise ]; then kind=method; else kind=baseline; fi
 for t in rand_48 rand_96 rand_384 rand_2000 dbl_48 dbl_96 dbl_384 dbl_2000; do
  for seed in 0 1 2 3 4; do
   f=results/raw/main_${s}_${t}_$seed.json
   nice -n 10 rh run --kind $kind --name "$(name_of $s)" --group main --task $t --seed $seed --metrics-file $f -- $PY method/run.py --system $s --task $t --seed $seed --out $f | cut -c1-90
  done
 done
done
