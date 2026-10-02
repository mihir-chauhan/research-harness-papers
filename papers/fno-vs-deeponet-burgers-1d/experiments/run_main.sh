# usage: run_main.sh <system> <display name> <lr> [group] [extra args as config json fragment is built by caller]
source seed/env.sh && cd . && export RH_PROJECT=$PWD OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
sys=$1; name=$2; lr=$3; kind=$4; group=$5; tag=$6; seeds=$7; shift 7
# remaining args: "<json config>" "<extra cli flags>"
cfg=$1; flags=$2
for s in $seeds; do
 f=results/raw/${group}_${tag}_s${s}.json
 nice -n 10 rh run --kind $kind --name "$name" --group $group --task burgers_nu0.01 --seed $s --config "$cfg" --metrics-file $f -- $PY method/run.py --system $sys --seed $s --lr $lr --epochs 100 $flags --out $f > /tmp/bx/${group}_${tag}_$s.log 2>&1
done
