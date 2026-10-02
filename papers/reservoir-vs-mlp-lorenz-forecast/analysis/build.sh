#!/bin/zsh
# Rebuilds every table and figure of the paper from results/runs.jsonl. Run from the project root after sourcing seed/env.sh.
set -e
M=vpt,vpt_min,clim_w1,clim_ok,blowup,fit_seconds
rh table --group main --metrics $M --prec 3 --order "True system,MLP delay,GRU,ESN" > /dev/null
cp results/tables/main.tex results/tables/main_systems_raw.tex
rh table --group main --metrics vpt,clim_ok,blowup --prec 2 --order "ESN,ESN without squared features,GRU,GRU without input noise" > /dev/null
cp results/tables/main.tex results/tables/main_ablation_raw.tex
rh table --group main --metrics $M --prec 3 > /dev/null            # final main.tex / main.md: all rows of the group
for m in vpt clim_ok; do
  rh compare --group main --metric $m --ref GRU > /dev/null; cp results/tables/compare_main_$m.csv results/tables/compare_main_${m}_refGRU.csv
  rh compare --group main --metric $m --ref ESN > /dev/null; cp results/tables/compare_main_$m.csv results/tables/compare_main_${m}_refESN.csv
done
$PY analysis/make.py
