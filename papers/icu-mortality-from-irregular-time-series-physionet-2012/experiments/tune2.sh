#!/bin/bash
# stage 2 of tuning: regularisation (NNs) / learning rate and depth (GBDT) around the stage-1 optimum
cd "$(dirname "$0")/.."; mkdir -p results/raw; export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
job() {
  sys=$1; nm=$2; tag=$3; kv=$4; seed=$5
  cfg=$(python3 -c "import json,sys; print(json.dumps({k:float(v) if '.' in v else int(v) for k,v in (a.split('=') for a in sys.argv[1].split(','))}))" "$kv")
  rh run --kind sanity --name "tune $nm" --group tune2 --task physionet2012_mortality --tag ${tag}_s${seed} --seed $seed --config "$cfg" \
    --metrics-file results/raw/tune2_${sys}_${tag}_s${seed}.json -- nice -n 10 $PY method/run.py --system $sys --tune 1 --seed $seed --config "$cfg" --out results/raw/tune2_${sys}_${tag}_s${seed}.json
}
export -f job
{
for s in 100 101; do
 for lg in 0.02 0.1; do echo "gbdt GBDT lg$lg leaves=16,l2=10,lr_gb=$lg $s"; done
 echo "gbdt GBDT lv32 leaves=32,l2=10 $s"
 for p in "0.5 0.0001" "0.2 0.01" "0.5 0.01"; do set -- $p
  echo "gru_ffill gru_ffill d$1_w$2 hidden=32,lr=0.003,drop=$1,wd=$2 $s"
  echo "gru_md gru_md d$1_w$2 hidden=32,lr=0.001,drop=$1,wd=$2 $s"
  echo "grud grud d$1_w$2 hidden=32,lr=0.001,drop=$1,wd=$2 $s"
 done
done
} | xargs -P 2 -L 1 bash -c 'job "$0" "$1" "$2" "$3" "$4"'
