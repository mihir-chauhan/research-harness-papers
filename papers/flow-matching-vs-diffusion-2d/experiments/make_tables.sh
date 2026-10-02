#!/bin/sh
# Regenerates every table and figure of the paper from results/runs.jsonl (no experiment is run).
# Usage (after sourcing env.sh, from the project root): sh experiments/make_tables.sh
set -e
SW=sw_k1,sw_k2,sw_k4,sw_k8,sw_k16,sw_k100
ORD="DDIM,DDPM ancestral,Flow Matching (Euler),Flow Matching (Heun),Reflow-1 (Euler),Real data (floor)"
rh table --group main --metrics $SW --prec 3 --order "$ORD" && cp results/tables/main.tex results/tables/main_sw.tex && cp results/tables/main.md results/tables/main_sw.md
rh table --group main --metrics mmd_k1,mmd_k4,mmd_k16,mmd_k100,straight --prec 4 --order "$ORD" && cp results/tables/main.tex results/tables/main_mmd.tex && cp results/tables/main.md results/tables/main_mmd.md
rh table --group abl_schedule --metrics sw_k1,sw_k4,sw_k16,sw_k100,mmd_k100 --prec 3
rh table --group abl_reflow --metrics sw_k1,sw_k4,sw_k16,sw_k100,straight --prec 3
$PY method/postprocess_tables.py          # headers, labels, best/second marks (values untouched)
$PY experiments/analyze.py > /dev/null    # figures; by-product test tables go to results/analysis/ (not used by the paper)
# rh compare: the paired tests and ratios the paper prints with \rhval{cmp/...} (one CSV per metric; the reference is the first system of each difference)
for m in sw_k1 sw_k100 mmd_k1 straight; do rh compare --group main --metric $m --ref "Flow Matching (Euler)" > /dev/null; done
for m in sw_k4 mmd_k4; do rh compare --group main --metric $m --ref "DDIM" > /dev/null; done
