#!/bin/bash
# usage: run_all.sh <part>  ; runs one part of the study through `rh run`
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
TASKS="blocking shortcut static stochastic stoch_blocking"
R="nice -n 10 rh run"
go() { # kind name group task seed config extra-args...
  local kind=$1 name=$2 group=$3 task=$4 seed=$5 cfg=$6; shift 6
  # resume support: skip runs already registered with the same group/name/task/seed/config
  $PY -c 'import sys,json
g,n,t,s,c=sys.argv[1:6]; c=json.loads(c)
for l in open("results/runs.jsonl"):
    r=json.loads(l)
    if (r["group"],r["name"],r["task"],r["seed"],r["config"])==(g,n,t,int(s),c) and r["status"]=="ok": sys.exit(0)
sys.exit(1)' "$group" "$name" "$task" "$seed" "$cfg" && return 0
  local f="results/raw/${group}__${name//[ +\/]/_}__${task}__${seed}__$(echo $cfg | tr -dc "0-9a-z.").json"
  $R --kind $kind --name "$name" --group $group --task $task --seed $seed --config "$cfg" --metrics-file $f -- \
     $PY method/run.py --task $task --seed $seed --out $f "$@" >/dev/null
}
case $1 in
main)
  for task in $TASKS; do for seed in $(seq 0 19); do
    c="results/raw/curve_${task}__NAME__s$seed.csv"
    go baseline "Q-learning" main $task $seed '{"n":0}' --system q --n 0 --curve ${c/NAME/Q-learning}
    go method "Dyna-Q" main $task $seed '{"n":10}' --system dynaq --n 10 --curve ${c/NAME/Dyna-Q}
    go baseline "Dyna-Q+" main $task $seed '{"n":10}' --system dynaq+ --n 10 --curve ${c/NAME/Dyna-Q+}
    go baseline "Prioritized sweeping" main $task $seed '{"n":10}' --system ps --n 10 --curve ${c/NAME/PS}
  done; done;;
sweep_n)
  for task in $TASKS; do for seed in $(seq 0 9); do for n in 1 5 20 50 100; do
    go method "Dyna-Q" sweep_n $task $seed "{\"n\":$n}" --system dynaq --n $n
    go baseline "Dyna-Q+" sweep_n $task $seed "{\"n\":$n}" --system dynaq+ --n $n
    go baseline "Prioritized sweeping" sweep_n $task $seed "{\"n\":$n}" --system ps --n $n
  done; done; done;;
abl)
  for task in $TASKS; do for seed in $(seq 0 19); do
    go method "Dyna-Q" abl_dynaq_plus $task $seed '{"n":10}' --system dynaq --n 10
    go baseline "Dyna-Q+" abl_dynaq_plus $task $seed '{"n":10}' --system dynaq+ --n 10
    go ablation "Dyna-Q+ w/o bonus" abl_dynaq_plus $task $seed '{"n":10,"kappa":0}' --system dynaq+ --n 10 --kappa 0
    go ablation "Dyna-Q+ w/o untried" abl_dynaq_plus $task $seed '{"n":10,"untried":0}' --system dynaq+ --n 10 --untried 0
    go ablation "Dyna-Q+ w/o both" abl_dynaq_plus $task $seed '{"n":10,"kappa":0,"untried":0}' --system dynaq+ --n 10 --kappa 0 --untried 0
  done; done;;
sweep_kappa)
  for task in $TASKS; do for seed in $(seq 0 9); do for k in 0.0001 0.001 0.01 0.03; do
    go baseline "Dyna-Q+" sweep_kappa $task $seed "{\"kappa\":$k}" --system dynaq+ --n 10 --kappa $k
  done; done; done;;
esac
