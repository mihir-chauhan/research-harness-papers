cd .
while [ $(ls results/raw/main_{fno,deeponet,mlp}_s*.json 2>/dev/null | wc -l) -lt 15 ]; do sleep 10; done
S="0 1 2"
for m in 4 8 32; do
 bash experiments/run_main.sh fno "FNO modes=$m" 0.01 ablation sweep_modes m$m "$S" "{\"lr\":0.01,\"modes\":$m,\"epochs\":100}" "--modes $m"
done
