#!/bin/zsh
# Rebuilds every table and figure of the paper from results/runs.jsonl. Run from the project root after sourcing seed/env.sh.
# (analysis/list_copies.py made the comparison groups used below; it only needs to run once.)
set -e
M=vpt,vpt_min,clim_w1,clim_ok,blowup,fit_seconds
rh table --group main --metrics $M --prec 3 --order "True system,MLP delay,GRU,ESN" > /dev/null
cp results/tables/main.tex results/tables/main_systems_raw.tex
rh table --group main --metrics vpt,clim_ok,blowup --prec 2 --order "ESN,ESN without squared features,GRU,GRU without input noise" > /dev/null
cp results/tables/main.tex results/tables/main_ablation_raw.tex
rh table --group main --metrics $M --prec 3 > /dev/null            # final main.tex / main.md: all rows of the group
# Paired tests, differences and ratios: `rh compare` only (analysis/make.py computes none). The groups abl_gru, nt<N> and
# st_<system><steps> hold copies (`rh log --from-run`) of the runs to be compared, so that each comparison is one rh compare call.
for m in vpt clim_ok; do
  rh compare --group main --metric $m --ref ESN > /dev/null       # ESN vs MLP, GRU, ESN without squares
  rh compare --group abl_gru --metric $m --ref GRU > /dev/null    # GRU vs GRU without input noise
done
for n in 500 2000 5000 10000; do rh compare --group nt$n --metric vpt --ref ESN > /dev/null; done                       # ESN vs MLP per training length
for g in mlp4000 mlp8000 mlp16000 mlp32000 gru3000 gru6000 gru12000; do rh compare --group st_$g --metric vpt --ref ESN > /dev/null; done   # ESN vs baseline per optimiser budget
$PY analysis/make.py
