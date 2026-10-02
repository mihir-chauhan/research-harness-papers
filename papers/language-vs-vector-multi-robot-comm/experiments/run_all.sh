#!/bin/bash
# usage: run_all.sh main|sweeps ; every run goes through rh run
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
R="nice -n 10 $PY method/run.py"
name() { case $1 in none) echo "No communication";; continuous) echo "Continuous vector (DIAL-style, reimplemented)";; discrete) echo "Discrete tokens (Gumbel-softmax, reimplemented)";; language) echo "Templated language (proxy)";; esac; }
kind() { [ $1 = language ] && echo method || echo baseline; }
if [ "$1" = main ]; then
 for s in 0 1 2 3 4; do for sys in none continuous discrete language; do
  export RH_SYSTEM_NAME="$(name $sys)"
  rh run --kind $(kind $sys) --name "$(name $sys)" --group main --task rendezvous --seed $s --metrics-file results/raw/main_${sys}_$s.json -- $R --system $sys --seed $s --out results/raw/main_${sys}_$s.json
 done; done
 for s in 0 1 2 3 4; do for sys in none continuous discrete language; do
  rh run --kind $(kind $sys) --name "$(name $sys)" --group xplay --task rendezvous --seed $s --metrics-file results/raw/xplay_${sys}_$s.json -- $R --mode xplay --system $sys --seed $s --out results/raw/xplay_${sys}_$s.json
 done; done
else
 for s in 0 1 2 3 4; do
  for v in 2 3 4 6 8; do for sys in discrete language; do
   export RH_SYSTEM_NAME="$(name $sys)"
   [ -f results/raw/sv_${sys}_${v}_$s.json ] && continue
   rh run --kind ablation --name "$(name $sys)" --group sweep_vocab --task rendezvous --seed $s --config "{\"vocab\": $v}" --metrics-file results/raw/sv_${sys}_${v}_$s.json -- $R --system $sys --seed $s --vocab $v --out results/raw/sv_${sys}_${v}_$s.json
  done; done
  for n in 0.0 0.1 0.3 0.6 1.0; do
   export RH_SYSTEM_NAME="$(name continuous)"
   [ -f results/raw/sn_${n}_$s.json ] && continue
   rh run --kind ablation --name "$(name continuous)" --group sweep_noise --task rendezvous --seed $s --config "{\"noise\": $n}" --metrics-file results/raw/sn_${n}_$s.json -- $R --system continuous --seed $s --noise $n --out results/raw/sn_${n}_$s.json
  done
 done
fi
# --- audit-round additions: discrete temperature sweep and dense early evaluation ---
if [ "$1" = tau ]; then
 for s in 0 1 2 3 4; do for tau in 0.3 0.5 1.0 2.0; do
  export RH_SYSTEM_NAME="$(name discrete)"
  rh run --kind ablation --name "$(name discrete)" --group abl_tau --task rendezvous --seed $s --config "{\"tau\": $tau}" --metrics-file results/raw/tau_${tau}_$s.json -- $R --system discrete --seed $s --tau $tau --tag _tau$tau --out results/raw/tau_${tau}_$s.json
 done; done
fi
if [ "$1" = dense ]; then
 for s in 0 1 2 3 4; do for sys in continuous discrete language; do
  export RH_SYSTEM_NAME="$(name $sys)"
  rh run --kind ablation --name "$(name $sys)" --group dense_eval --task rendezvous --seed $s --config '{"eval_every": 10}' --metrics-file results/raw/dense_${sys}_$s.json -- $R --system $sys --seed $s --eval_every 10 --tag _dense --out results/raw/dense_${sys}_$s.json
 done; done
fi
