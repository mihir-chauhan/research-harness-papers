cd .
while [ $(ls results/raw/main_cnn_s*.json 2>/dev/null | wc -l) -lt 5 ]; do sleep 10; done
S="0 1 2"
bash experiments/run_main.sh fno "FNO no grid channel" 0.01 ablation abl_grid nogrid "$S" '{"lr":0.01,"modes":16,"grid":0,"epochs":100}' "--grid 0"
for n in 100 200; do
 bash experiments/run_main.sh fno "FNO n=$n" 0.01 ablation sweep_ntrain fno$n "$S" "{\"lr\":0.01,\"n_train\":$n,\"epochs\":100}" "--n_train $n"
 bash experiments/run_main.sh deeponet "DeepONet n=$n" 0.003 ablation sweep_ntrain don$n "$S" "{\"lr\":0.003,\"n_train\":$n,\"epochs\":100}" "--n_train $n"
done
for e in 500 2000; do
 bash experiments/run_main.sh deeponet "DeepONet ep=$e" 0.003 ablation sweep_epochs don$e "$S" "{\"lr\":0.003,\"epochs\":$e}" "--epochs $e"
 bash experiments/run_main.sh mlp "MLP ep=$e" 0.001 ablation sweep_epochs mlp$e "$S" "{\"lr\":0.001,\"epochs\":$e}" "--epochs $e"
done
