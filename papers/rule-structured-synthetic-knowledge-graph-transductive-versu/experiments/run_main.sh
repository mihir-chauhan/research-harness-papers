#!/bin/bash
# usage: run_main.sh <stream 1|2> ; two streams run in parallel
cd "$(dirname "$0")/.." ; mkdir -p results/raw
go() { # kind name group task seed config sysargs...
  local kind=$1 name=$2 group=$3 task=$4 seed=$5 cfg=$6; shift 6
  local f=results/raw/${group}_$(echo "$name" | tr -c 'A-Za-z0-9\n' _)_${task}_s${seed}_$(echo "$cfg" | tr -c 'A-Za-z0-9\n' _).json
  nice -n 10 rh run --kind $kind --name "$name" --group $group --task $task --seed $seed --config "$cfg" --metrics-file $f -- $PY method/run.py --task $task --seed $seed --out $f "$@" >/dev/null
}
if [ "$1" = 1 ]; then
 for s in 0 1 2 3 4; do for t in transductive inductive; do
  go method "Path-MP (2-hop)" main $t $s '{}' --system pathmp
  go baseline "TransE (reimplemented)" main $t $s '{}' --system transe
  go baseline "TransE+fold-in (reimplemented)" main $t $s '{}' --system transe_foldin
  go baseline "Rule oracle (hand-written)" main $t $s '{}' --system oracle
 done; done
 for s in 0 1 2 3 4; do go ablation "Path-MP (2-hop)" abl_nodrop inductive $s '{"drop_query_edge": 0}' --system pathmp --no_drop
   go ablation "Path-MP (2-hop)" abl_nodrop transductive $s '{"drop_query_edge": 0}' --system pathmp --no_drop; done
elif [ "$1" = 3 ]; then
 # re-run of the sweep_density baselines: in the first launch a variable clash in go() corrupted these 30 commands (logged as failed)
 for s in 0 1 2 3 4; do for f in 0.25 0.5 0.75; do
  go ablation "TransE+fold-in (reimplemented)" sweep_density inductive $s "{\"obs_frac\": $f}" --system transe_foldin --obs_frac $f
  go ablation "Rule oracle (hand-written)" sweep_density inductive $s "{\"obs_frac\": $f}" --system oracle --obs_frac $f
 done; done
else
 for s in 0 1 2 3 4; do for L in 1 3; do for t in transductive inductive; do
  go ablation "Path-MP (2-hop)" sweep_layers $t $s "{\"layers\": $L}" --system pathmp --layers $L
 done; done; done
 for s in 0 1 2 3 4; do for f in 0.25 0.5 0.75; do
  go ablation "Path-MP (2-hop)" sweep_density inductive $s "{\"obs_frac\": $f}" --system pathmp --obs_frac $f
  go ablation "TransE+fold-in (reimplemented)" sweep_density inductive $s "{\"obs_frac\": $f}" --system transe_foldin --obs_frac $f
  go ablation "Rule oracle (hand-written)" sweep_density inductive $s "{\"obs_frac\": $f}" --system oracle --obs_frac $f
 done; done
fi
