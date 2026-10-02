#!/bin/zsh
# usage: experiments/main.sh <seed> ; runs all systems x tasks for one seed (group main)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
s=$1
r() { # name kind task extra-args...
  n=$1; k=$2; t=$3; shift 3; f=results/raw/main_${n// /_}_${t}_s$s.json; f=${f//=/}
  rh run --kind $k --name "$n" --group main --task $t --seed $s --metrics-file $f -- nice -n 10 $PY method/run.py --task $t --seed $s --out $f "$@"
}
for t in sort_desc reverse; do
  r "No adaptation" sanity $t --system pretrained
done
for t in sort_desc reverse; do
  r "Full fine-tuning" baseline $t --system full
  r "From scratch" baseline $t --system scratch
  r "Last block" baseline $t --system lastblock
  r "Head only" baseline $t --system head
  for k in 1 2 4 8; do r "LoRA r=$k" method $t --system lora --rank $k; done
done
