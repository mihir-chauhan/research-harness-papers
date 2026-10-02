#!/bin/sh
# Saves every significance output quoted in the paper, one file per scenario and reference system.
# Run from the project root after sourcing the environment: sh experiments/make_stats.sh
set -e
T=results/tables
rm -f $T/compare_main_*
for task in perm_dil split_cil split_til; do
  for ref in "Experience replay (M=100)" "Fine-tuning"; do
    tag=$(echo "$ref" | tr -cd 'A-Za-z0-9')
    rh compare --metric average_accuracy --group main --task $task --ref "$ref" | grep -v '^wrote' > $T/compare_main_average_accuracy_${task}_ref-${tag}.txt
    mv $T/compare_main_average_accuracy.csv $T/compare_main_average_accuracy_${task}_ref-${tag}.csv
  done
done
$PY experiments/paired_stats.py average_accuracy > $T/paired_main_average_accuracy.txt
