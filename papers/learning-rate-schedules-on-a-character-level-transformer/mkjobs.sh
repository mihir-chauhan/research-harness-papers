k(){ if [ $1 = cosine ]; then echo method; else echo baseline; fi; }
for seed in 0 1 2; do for lr in 3e-3 1e-3 1e-2; do for s in constant cosine step schedulefree; do echo "main $(k $s) $s $lr $seed"; done; done; done
for seed in 0 1 2; do for lr in 3e-4 3e-2; do for s in constant cosine step schedulefree; do echo "main $(k $s) $s $lr $seed"; done; done; done
for seed in 0 1 2; do for w in 0 50 300; do echo "abl_warmup ablation cosine 1e-2 $seed $w"; done; for w in 100 300; do echo "abl_warmup ablation constant 1e-2 $seed $w"; done; done
