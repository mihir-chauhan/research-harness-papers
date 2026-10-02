# Protocol
Tasks: adapt sort_asc-pretrained model to sort_desc and reverse (8 digits, 0-9 uniform). Seeds 0-4 (main): seed s fixes pretrained model, adaptation set and init of adapters. Metrics: adapt_acc, adapt_tok_acc, trainable_params, pretask_acc, forgetting, zero_shot_acc.
Tuning: learning rate per system chosen on the validation split (seed 100, its own pretrained model, `--eval_split val`) from 3 values: full/scratch {3e-4,1e-3,3e-3}; lora(r=4)/lastblock/head {1e-3,3e-3,1e-2}; one run per value per task; pick best mean val adapt_acc over both tasks; LoRA rank 4's value used for all ranks. Group `tune`.
Groups: `main` (all systems x 2 tasks x 5 seeds), `abl_targets` (LoRA q,v only, r in {1,4}, 5 seeds), `sweep_lr` (LoRA r4 and full, lrs other than the default, 3 seeds), curves (seed 0..2, r1 and full and lastblock).
Hardware: Apple laptop CPU, 2 threads; each run 8-20 s except the one-off pretraining (~50 s per seed).
