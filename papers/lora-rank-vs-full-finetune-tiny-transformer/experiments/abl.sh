#!/bin/zsh
# usage: experiments/abl.sh <part>; ablation / sensitivity groups
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
part=$1
if [ $part = targets ]; then   # LoRA on q,v only vs all linear layers (all-linear rows live in group main)
  for s in 0 1 2 3 4; do for t in sort_desc reverse; do for k in 1 4; do
    f=results/raw/abl_targets_qv_r${k}_${t}_s$s.json
    rh run --kind ablation --name "LoRA r=$k (q,v only)" --group abl_targets --task $t --seed $s --config "{\"rank\": $k, \"targets\": \"q,v\"}" --metrics-file $f -- nice -n 10 $PY method/run.py --system lora --rank $k --targets q,v --task $t --seed $s --out $f
  done; done; done
fi
if [ $part = ntrain ]; then   # fewer adaptation examples, 3 seeds, same tuned lrs
  for s in 0 1 2; do for n in 100 300; do
    for sys in "Full fine-tuning|full|4" "From scratch|scratch|4" "Last block|lastblock|4" "LoRA r=1|lora|1" "LoRA r=4|lora|4" "LoRA r=8|lora|8"; do
      IFS='|' read name sy k <<< "$sys"
      f=results/raw/sweep_ntrain_${sy}${k}_n${n}_s$s.json
      rh run --kind ablation --name "$name" --group sweep_ntrain --task sort_desc --seed $s --config "{\"n_train\": $n}" --metrics-file $f -- nice -n 10 $PY method/run.py --system $sy --rank $k --n_train $n --task sort_desc --seed $s --out $f
    done; done; done
fi
if [ $part = lr ]; then   # lr sweep, lora r4 and full (default lr rows come from group main)
  for s in 0 1 2; do for t in sort_desc reverse; do
    for lr in 0.0003 0.001 0.003 0.01; do
      f=results/raw/sweep_lr_lora_${lr}_${t}_s$s.json
      rh run --kind ablation --name "LoRA r=4" --group sweep_lr --task $t --seed $s --config "{\"lr\": $lr}" --metrics-file $f -- nice -n 10 $PY method/run.py --system lora --rank 4 --lr $lr --task $t --seed $s --out $f
    done
    for lr in 0.0003 0.001 0.003; do
      f=results/raw/sweep_lr_full_${lr}_${t}_s$s.json
      rh run --kind ablation --name "Full fine-tuning" --group sweep_lr --task $t --seed $s --config "{\"lr\": $lr}" --metrics-file $f -- nice -n 10 $PY method/run.py --system full --lr $lr --task $t --seed $s --out $f
    done
  done; done
fi
if [ $part = curves ]; then   # forgetting / adaptation curves, reverse and sort_desc
  for s in 0 1 2; do for sy in "full|4" "lora|1" "lora|4" "lastblock|4"; do
    IFS='|' read sy k <<< "$sy"
    f=results/raw/curve_${sy}${k}_s$s.json
    rh run --kind ablation --name "curve-$sy-r$k" --group curves --task sort_desc --seed $s --config "{\"rank\": $k}" --metrics-file $f -- nice -n 10 $PY method/run.py --system $sy --rank $k --task sort_desc --seed $s --curve_csv results/raw/curve_${sy}${k}_s$s.csv --out $f
  done; done
fi
