#!/bin/bash
# usage: run_abl.sh kind group name tag system h mu seed extra-args...   (tag: file/config label)
kind=$1; group=$2; name=${3//_/ }; tag=$4; sys=$5; h=$6; mu=$7; seed=$8; shift 8
f=results/raw/${group}_${tag}_h${h}_mu${mu}_s${seed}.json
nice -n 10 rh run --kind $kind --name "$name" --group $group --task h${h}_mu${mu} --seed $seed --config "{\"h\": $h, \"mu\": $mu, \"variant\": \"$tag\"}" --metrics-file $f -- $PY method/run.py --system $sys --h $h --mu $mu --seed $seed --out $f "$@" > /dev/null 2>&1 || echo FAIL $tag $h $mu $seed
