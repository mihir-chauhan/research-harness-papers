#!/bin/bash
# usage: run_all.sh A|B   (two disjoint streams; each trains its own networks)
source seed/env.sh
cd .
export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
# r <kind> <name> <group> <task> <seed> <tag> <extra args...>   (config JSON built from args)
r() { kind=$1; name=$2; group=$3; task=$4; seed=$5; tag=$6; cfg=$7; shift 7
  f=results/raw/${group}_${tag}_${task}_s${seed}.json
  nice -n 10 rh run --kind "$kind" --name "$name" --group "$group" --task "$task" --seed $seed --config "$cfg" \
     --metrics-file $f -- $PY method/run.py --task $task --seed $seed "$@" --out $f > /dev/null; }
S="0 1 2 3 4"
if [ "$1" = A ]; then
 for s in $S; do
  t=mix_overlap
  r baseline "Unguided conditional" main $t $s w0 '{"w":0,"tau":1}' --w 0 --tau 1
  r baseline "Low-temperature (tau=0.5)" main $t $s tau0.5 '{"w":0,"tau":0.5}' --w 0 --tau 0.5
  r method "CFG (w=3)" main $t $s w3 '{"w":3,"tau":1}' --w 3
  for w in 0.5 1 2 5 8; do r ablation "CFG w-sweep" sweep_w $t $s w$w "{\"w\":$w}" --w $w; done
  for tau in 0.8 0.7 0.4 0.3 0.2; do r ablation "Temperature sweep" sweep_tau $t $s tau$tau "{\"tau\":$tau}" --w 0 --tau $tau; done
  r ablation "Guidance on t/T in [0,0.5]" abl_interval $t $s lo0hi0.5 '{"w":3,"lo":0,"hi":0.5}' --w 3 --lo 0 --hi 0.5
  r ablation "Guidance on t/T in [0.5,1]" abl_interval $t $s lo0.5hi1 '{"w":3,"lo":0.5,"hi":1}' --w 3 --lo 0.5 --hi 1
  r ablation "Guidance on t/T in [0.2,0.6]" abl_interval $t $s lo0.2hi0.6 '{"w":3,"lo":0.2,"hi":0.6}' --w 3 --lo 0.2 --hi 0.6
 done
else
 for s in $S; do
  t=mix_sep
  r baseline "Unguided conditional" main $t $s w0 '{"w":0,"tau":1}' --w 0 --tau 1
  r baseline "Low-temperature (tau=0.5)" main $t $s tau0.5 '{"w":0,"tau":0.5}' --w 0 --tau 0.5
  r method "CFG (w=3)" main $t $s w3 '{"w":3,"tau":1}' --w 3
  r ablation "CFG w-sweep" sweep_w $t $s w8 '{"w":8}' --w 8
  for t in mix_overlap mix_sep; do r sanity "Real samples" ref $t $s real '{"real":1}' --real; done
 done
 for s in $S; do for p in 0.02 0.3; do
  r ablation "Label dropout p=$p" abl_dropout mix_overlap $s p$p "{\"w\":3,\"p_uncond\":$p}" --w 3 --p_uncond $p
 done; done
fi
