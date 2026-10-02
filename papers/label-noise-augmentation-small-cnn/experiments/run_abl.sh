#!/bin/bash
# Sensitivity / ablation runs at 40% symmetric noise. usage: run_abl.sh <0|1>
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
part=$1; i=0
run() { # group kind name param value extra...
  i=$((i+1)); [ $((i%2)) -ne $part ] && return
  g=$1; k=$2; n=$3; pn=$4; pv=$5; s=$6; shift 6
  f=results/raw/${g}_${pn}_${pv}_s${s}.json
  nice -n 10 rh run --kind $k --name "$n" --group $g --task digits_noise40 --seed $s --config "{\"$pn\": $pv}" --metrics-file $f -- $PY method/run.py --noise 0.4 --seed $s "$@" --out $f >/dev/null
}
for s in 0 1 2 3 4; do
  for a in 0.2 0.5 2.0 4.0; do run sweep_mixup_alpha ablation "Mixup" mix_alpha $a $s --system mixup --mix_alpha $a; done
  for e in 0.05 0.2 0.4 0.6; do run sweep_ls_eps ablation "Label smoothing" ls_eps $e $s --system ls --ls_eps $e; done
  for r in 0.1 0.2 0.3 0.5 0.6; do run sweep_sl_rate ablation "Small-loss (1 net)" sl_rate $r $s --system smallloss --sl_rate $r; done
  run abl_smallloss ablation "Small-loss, no warm-up/ramp" sl_warmup 0 $s --system smallloss --sl_warmup 0 --sl_ramp 1
done
