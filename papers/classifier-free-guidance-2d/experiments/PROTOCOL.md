# Protocol
Tasks mix_overlap (sigma 0.6), mix_sep (sigma 0.35); training data streamed fresh from the generator (no fixed split); evaluation on 4x1500 generated samples per run, true reference samples drawn fresh for swd. Seeds 0-4 (label-dropout ablation: also seeds 0-4). Hyperparameters fixed a priori (no tuning, no tuning budget; w, tau grids chosen before runs). Hardware: CPU, 2 threads; ~50 s training per network, ~5-10 s per sampling run.
Groups: ref (real-sample reference), main (3 systems x 2 tasks x 5 seeds), sweep_w, sweep_tau, abl_interval, abl_dropout (mix_overlap).
