#!/bin/bash
# usage: tune.sh  -- runs the tuning grids (2 jobs at a time); each cell is logged via rh run (group tune)
cd "$(dirname "$0")/.."; mkdir -p results/raw; export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
job() { # system name cfgtag cfg seed
  sys=$1; nm=$2; tag=$3; kv=$4; seed=$5
  cfg=$(python3 -c "import json,sys; print(json.dumps({k:float(v) if '.' in v else int(v) for k,v in (a.split('=') for a in sys.argv[1].split(','))}))" "$kv")
  rh run --kind sanity --name "tune $nm" --group tune --task physionet2012_mortality --tag ${tag}_s${seed} --seed $seed --config "$cfg" \
    --metrics-file results/raw/tune_${sys}_${tag}_s${seed}.json -- nice -n 10 $PY method/run.py --system $sys --tune 1 --seed $seed --config "$cfg" --out results/raw/tune_${sys}_${tag}_s${seed}.json
}
export -f job
{
for s in 100 101; do
 for C in 0.003 0.01 0.03 0.1 0.3; do echo "lr LR C$C C=$C $s"; done
 for lv in 4 8 16; do for l2 in 1 10; do echo "gbdt GBDT l${lv}_${l2} leaves=$lv,l2=$l2 $s"; done; done
 for sys in gru_ffill gru_md grud; do for h in 32 64 128; do for lr in 0.001 0.003; do echo "$sys $sys h${h}_lr$lr hidden=$h,lr=$lr $s"; done; done; done
done
} | xargs -P 2 -L 1 bash -c 'job "$0" "$1" "$2" "$3" "$4"'
