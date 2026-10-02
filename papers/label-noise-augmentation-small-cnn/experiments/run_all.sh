#!/bin/bash
# usage: run_all.sh <part 0|1>  (two parallel streams over the same grid)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
part=$1; i=0
nm() { case $1 in ce) echo "CE";; ls) echo "Label smoothing";; mixup) echo "Mixup";; smallloss) echo "Small-loss (1 net)";; esac; }
run() { # group kind name task seed config extra...
  i=$((i+1)); [ $((i%2)) -ne $part ] && return
  g=$1; k=$2; n=$3; t=$4; s=$5; c=$6; shift 6
  f=results/raw/${g}_$(echo "$n" | tr -c 'A-Za-z0-9\n' _)_${t}_s${s}.json
  nice -n 10 rh run --kind $k --name "$n" --group $g --task $t --seed $s --config "$c" --metrics-file $f -- $PY method/run.py --noise $(python3 -c "print(${t#digits_noise}/100)") "$@" --seed $s --out $f >/dev/null
}
for nz in 0 20 40 60; do for s in 0 1 2 3 4; do for sys in ce ls mixup smallloss; do
  k=baseline; [ $sys = smallloss ] && k=method
  run main $k "$(nm $sys)" digits_noise$nz $s '{}' --system $sys
done; done; done
