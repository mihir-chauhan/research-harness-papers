# Protocol
Tasks: perm_dil, split_cil, split_til (5 tasks each). Seeds: lr selection 100,101 (val); sweeps 10-14; main 0-4. Each seed changes split, permutations/class order and initialisation.
Tuning: lr in {0.01,0.05,0.1} for Fine-tuning and Joint (val average accuracy, 2 seeds), one lr for everything: 0.1 (best val average accuracy for Joint on all tasks and for Fine-tuning on perm_dil; tied on split_cil; 0.01 was better for Fine-tuning on split_til by 0.02). EWC lambda in {0,1,10,100,1e3,1e4,1e5} and M in {0,5,10,20,50,100,200,500} swept on seeds 10-14; lambda* per task = argmax mean val_average_accuracy. ER in main uses fixed M=20 and M=100 (not tuned). Test split never used for selection.
Hardware: CPU, 2 threads, ~5-10 s per run. Driver: experiments/drive.py (helper) and experiments/jobs.py (job lists).

## Reproducing the run groups
    $PY experiments/jobs.py tune_lr    # 36 runs, group tune_lr
    $PY experiments/jobs.py sweeps     # 225 runs, groups sweep_buffer and sweep_lambda
    $PY experiments/jobs.py main       # 75 runs, group main (lambda* hard-coded from the sweep's validation accuracy)
    rh table --group main --metrics average_accuracy,forgetting,backward_transfer,last_task_accuracy --prec 3 \
       --order "Fine-tuning,EWC,Experience replay (M=20),Experience replay (M=100),Joint training"
    $PY experiments/make_tables.py     # main_paper.tex (presentation of main.tex), tune_lr_paper.tex, sweep_lasttask.tex
    $PY experiments/make_figs.py       # figures and sweep_both.tex
    sh experiments/make_stats.sh       # rh compare per scenario and reference; paired intervals
`--dry-run` prints the `rh run` commands. The generated commands were checked against provenance.command of all 336
original registry rows (tune_lr rows were produced by the first driver version, whose metrics-file names lacked the
config value; everything else is identical).

## Sweep re-run
The first execution of the sweeps (commit 2576ebf) let two workers start jobs with the same group/name/task/seed in the
same second; `rh run` names logs without the config value, so 24 log files were shared by 48 rows. Those 225 rows are
superseded in the registry (`rh supersede`, still listed by `rh runs --all`) and the sweeps were re-run from
experiments/jobs.py with a driver that serialises jobs sharing a log stem. The re-run was interrupted once after 98 rows and finished with `jobs.py sweeps --resume` (skips jobs that already have an active row); the two partial logs of the interrupted jobs were deleted. All 225 re-run rows have metrics identical to the superseded rows. experiments/check_logs.py verifies one log
per active row.
