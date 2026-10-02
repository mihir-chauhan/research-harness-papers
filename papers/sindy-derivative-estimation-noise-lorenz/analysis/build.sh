#!/bin/sh
# Rebuild every table and figure of the paper from results/runs.jsonl. Run from the project root after sourcing env.sh.
set -e
rh table --group main > /dev/null
rh table --group abl_libstate > /dev/null
rh table --group abl_p > /dev/null
rh table --group sweep_width > /dev/null
# Welch tests. H2 uses FD as the reference; rh compare always writes compare_main_<metric>.csv, so that file is
# renamed before the comparison against the method (the default reference) overwrites it.
rh compare --metric coef_err --ref "FD-STLSQ" > /dev/null
mv results/tables/compare_main_coef_err.csv results/tables/h2_fd_ref_coef_err.csv
rh compare --metric coef_err > /dev/null
rh compare --metric support_exact > /dev/null
$PY analysis/make_report.py
