# Protocol
Groups (all: 64x64 synthetic shapes, 500-image clean test set, final checkpoint, 2 threads per run, 600 steps, batch 16, AdamW lr 1e-2 OneCycle):
- main: N=500; systems CE, GCE, SCE, Band-ignore CE; tasks none, boundary_p0.3, flip_p0.3; seeds 0-3.
- size: CE; N=100 and 2000 x tasks none, boundary_p0.3, flip_p0.3, seeds 0-3; N=250 and 1000 x tasks none, flip_p0.3, seeds 0-2 (N=500 = CE rows of main).
- sweep_noise: CE, N=500, flip_p0.1 and flip_p0.2, seeds 0-2.
- sweep_gce_q: GCE q in 0.3,0.9, flip_p0.3, N=500, seeds 0-2 (q=0.7 is in main).
- sweep_steps: CE, steps 200/1200, N=100, flip_p0.3, seeds 0-2 (600 steps is in size).
Tuning: GCE/SCE use the published defaults; q is swept in sweep_gce_q and reported but not used to pick the main-table setting.
History (disclosed): a first pilot (300 steps, lr 5e-3; 3 rows in group main) and a second pilot (450 steps, lr 5e-3; 36 rows in main) left several seeds with a collapsed triangle/square class even on clean labels; all those rows are superseded and the final budget (600 steps, lr 1e-2) was chosen from these pilots and two single-seed clean-label runs evaluated on the test split (a small leak, stated in the limitations).
Hardware: shared CPU machine (Apple silicon, heavily loaded), two runs at a time.
