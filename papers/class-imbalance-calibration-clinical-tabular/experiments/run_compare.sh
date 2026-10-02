#!/bin/bash
# Paired tests with `rh compare` for every metric x task x reference arm used in the paper.
# Each call overwrites results/tables/compare_main_<metric>.csv, so the output is moved to results/tables/compare/.
mkdir -p results/tables/compare
cp results/tables/compare_main_brier.csv /tmp/cic_compare_main_brier.csv
for met in auroc auprc brier cal_slope cal_citl slope_dev citl_abs sens spec bal_acc; do
  for task in bc_natural bc_1to5 bc_1to20 bc_1to50; do
    for ref in "LR + no correction" "GB + no correction" "LR + threshold" "GB + threshold"; do
      case $ref in *threshold) case $met in sens|spec|bal_acc) ;; *) continue;; esac;; esac
      tag=$(echo "$ref" | tr -d ' +' )
      rh compare --metric $met --group main --task $task --ref "$ref" > /dev/null || echo "FAILED $met $task $ref"
      mv results/tables/compare_main_${met}.csv results/tables/compare/${met}_${task}_${tag}.csv
    done
  done
done
# keep the registered primary comparison (Brier at 1:20 against the reference arm) where rh wrote it
cp /tmp/cic_compare_main_brier.csv results/tables/compare_main_brier.csv
ls results/tables/compare | wc -l
