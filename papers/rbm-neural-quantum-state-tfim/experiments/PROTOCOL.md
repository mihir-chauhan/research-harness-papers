# Protocol (final; v3 rate selection, two starts)

**Tasks.** Periodic TFIM, J=1. N=10 with Gamma in {0.25, 0.5, 0.75, 1, 1.25, 1.5, 2}; N=8 and N=12 with Gamma in {0.5, 1, 1.5}: 13 tasks.

**Systems.** {mean-field, Jastrow, RBM alpha=1, 2, 4} x {SGD, SR}: 10 systems, all in `method/run.py`. Method of record: RBM alpha=2 SR.

**Budget, identical for every system.** 300 iterations, 256 persistent Metropolis chains (one sample per chain per iteration), 10N burn-in steps, N Metropolis steps between iterations, SR shift 1e-2, parameters initialised N(0, 0.01^2). No momentum, schedule or clipping.

**Starts.** Every (system, task, seed) is optimised twice with the same rate and budget:
- start S (group `main`): symmetric, a_i ~ N(0, 0.01^2);
- start B (group `main_b`): symmetry-broken, a_i = 0.5 + N(0, 0.01^2) (`--field-init 0.5`).
The reported state is the start with the lower variational energy (equivalently lower relative energy error, E0 being a constant per task); a diverged start loses to a finite one; a seed is "diverged" only if both starts diverged. Per-start results are reported in the paper's start table. Start B was added in the audit fix round, after the hypotheses were registered.

**Registry group `selected`.** `experiments/list_selected.py` lists the selected run of every (system, task, seed) again in group `selected` with `rh log --from-run` (metrics, config and provenance copied from the registry; no new run, no typed number). The paper's ratios and paired tests on the selected states are `rh compare --group selected --metric rel_energy_error --ref "RBM alpha=2 SR"`. `experiments/make_tables.py` skips these copies when it counts runs and run time.

**Seeds.** Main runs: 0-4. Tuning: 100, 101, 102 (disjoint from the main seeds).

**Learning-rate selection (v3).** Per (ansatz, optimiser). Grid {0.003, 0.01, 0.03, 0.1} for SGD (36 tuning runs per system) and {0.02, 0.05, 0.1} for SR (27 runs per system); 3 tuning tasks (tfim_N10_g0.25, tfim_N10_g1.00, tfim_N12_g0.50) x 3 tuning seeds, start S only; lowest mean relative energy error, a diverged run counting as infinite. Registry group `tune_lr3`; selection by `experiments/select_lr.py`; selected rates in `experiments/lr.json`. Five of ten selected rates are on a grid edge (mean-field SGD/SR and RBM alpha=2/4 SR at the top, Jastrow SR at the bottom; see the paper's limitations). Rates were not re-tuned for start B.

**History.** v1 (`tune_lr`: 3-point grid, 1 task, 1 seed) and v2 (`tune_lr2`: 3 tasks, 1 seed) selected rates that diverged in the main runs; their main runs are superseded rows in the registry. The Jastrow ansatz was first stored as an N x N block of which only the upper triangle was used; it now has one parameter per pair, and all Jastrow tuning, main and curve runs were re-run (earlier rows superseded; the Jastrow SGD rate changed from 0.003 to 0.03 under the same rule).

**Metrics.** Evaluated by exact enumeration of all 2^N configurations of the trained state: relative energy error (primary), |Mz| error, <sigma^x> error, infidelity to the ED ground state (scipy eigsh). The Monte Carlo energy (mean of the last 20 iterations) is logged as a consistency check.

**Sampling-free reference (group `exact_opt`).** L-BFGS (at most 1000 iterations) on the exactly enumerated energy with the exact gradient, both starts, seed 0, for mean-field, Jastrow and RBM alpha=2 on all 13 tasks; the lower-energy start is reported. Diagnostic only (needs all 2^N configurations).

**Ablations (RBM alpha=2 SR, N=10, Gamma=1, seeds 0-4, start S only).** SR shift {1e-4, 1e-3, 1e-2, 1e-1, 1}; samples per iteration {32, 64, 128, 256, 512}. Training curves: all systems, 3 seeds, start S. Start ablation: the per-start table over all systems and tasks.

**Hardware.** Shared CPU, 2 threads, numpy; at most two runs at a time. Run counts and run times: paper Table "checks and cost" (`results/tables/t_check.tex`).

**Known logging limitation.** In the tuning groups run before the fix round (`tune_lr`, `tune_lr2`, `tune_lr3` except Jastrow) and in two `sweep_samples` rows, runs that differ only in the rate started within the same second and share a log file name, so the earlier log was overwritten. Registry metrics come from the per-run metrics files and are unaffected; the driver now orders tuning runs so that this cannot happen.

**Known reproducibility limitation.** The ED reference (`scipy.sparse.linalg.eigsh` in `tfim_exact`) is called without a start vector, so ARPACK draws one that the run seed does not control. The variational state, its energy and `n_params` repeat exactly; every metric that uses the reference (`rel_energy_error`, `mc_energy_error`, `mz_error`, `mx_error`, `infidelity`) repeats only up to the accuracy of the reference. Measured by re-running logged commands (conform round): differences below 4e-10 absolute in all tasks except tfim_N10_g0.25, where the two lowest levels are nearly degenerate and the infidelity of a partly symmetry-broken state moved by up to 7e-8 (2 of the 100 main runs of that task changed by about 2e-6 relative). `runtime_s` is wall-clock time and is marked `nondeterministic` in research.yaml.
