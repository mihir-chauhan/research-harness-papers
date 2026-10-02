# Response to the audit (fix round)

All numbers below are in the regenerated tables (`results/tables/t_*.tex`, built by `experiments/make_tables.py` from `results/runs.jsonl`). New runs: Jastrow tuning re-run (63), Jastrow main and curve re-runs (130 + 6), symmetry-broken-start main runs for all ten systems (650, group `main_b`), sampling-free reference (78, group `exact_opt`). Code was committed before each batch.

## Major

**1. Jastrow baseline stuck at a symmetric stationary point (H1 margins an initialisation artefact).** Accepted; fixed at the cause.
- `method/run.py` has a new `--field-init` option. Every system (not only Jastrow and mean-field) is now run from two starts with the same rate and budget: S (symmetric, as before, group `main`) and B (fields a_i = 0.5 + noise, group `main_b`). The reported state per (system, task, seed) is the lower-energy start. Giving all ten systems the same two starts keeps the restart budget equal.
- Result: Jastrow-SR is now 5.6e-5 / 7.4e-5 / 6.0e-5 at N10 g0.25 / N10 g0.5 / N12 g0.5 (was 4.2e-4 / 3.1e-3 / 2.8e-3). The RBM alpha=2 SR margin over Jastrow at Gamma<=0.5 is 1.47-2.37x on means (Table II), not 8-60x. The mean-field N12 g0.5 cell is now 1.0e-3 (the domain-wall value 2.3e-1 appears only in the start-S row of the start ablation).
- I also added a sampling-free reference (L-BFGS on the enumerated energy, exact gradient; group `exact_opt`) for mean-field, Jastrow and RBM alpha=2. It reproduces the auditor's Jastrow optima (2.5e-7, 3.0e-5, 1.7e-5) and shows that for Gamma<=0.5 the Jastrow optimum is below the RBM-SR Monte Carlo result in 3 of 4 tasks. The abstract, H1 text, conclusion, limitations and `results/RESULTS.md` now say that the small-field margin reflects optimisation, not the ansatz, and that the Jastrow baseline is still under-optimised there; the claim that the RBM's advantage is an ansatz effect is restricted to Gamma>=0.75, where Jastrow VMC is within about 30% of its optimum.
- The per-start medians are reported as the start ablation (Table VI, SR systems; all systems in `results/tables/main.md` and `main_b.md`).
- Side effect worth knowing: all 28 diverged runs come from start S; no start-B run diverged. The paper reports per-start divergence counts (Table VIII) rather than only the selected-state count.
- Caveats stated in the paper: the two-start selection is post-registration, uses the exactly evaluated energy, and rates were tuned from start S only.

**2. Jastrow parameter count 110 instead of 55.** Accepted. The ansatz is now stored with one parameter per pair (N + N(N-1)/2), so `n_params` is 55 at N=10 by construction. Because this changes the random stream, all Jastrow runs were repeated under the fixed code (tuning, main, curves) and the old rows superseded. Under the unchanged selection rule the Jastrow SGD rate moved from 0.003 to 0.03 (the three lowest rates are within noise of each other). The count is shown in the P10 column of Table I.

## Minor

- **Abstract, "more than two orders of magnitude at larger fields".** Replaced by the ratios of means from Table II: 2.07 at Gamma=0.25 and 68-496 for Gamma>=1 (results text adds 15-23 at Gamma=0.5 and 0.75).
- **"Tuning cost: 315 runs, the same for every system".** Corrected: 36 runs per SGD system, 27 per SR system (setup text, Table VIII).
- **"well under the 30-minute budget".** Removed. Table VIII gives summed run time (47 min for reported runs, 82 min for all runs including superseded ones), wall-clock with a run executing (47 min) and the longest run (115 s); the setup says the brief's target of about 30 minutes was exceeded. `research.yaml` (45 min) is also exceeded and is left as it was.
- **H3 diverged-seed counts and N=12 overlap.** The Gamma=1 cells now have no seed without a finite state (the diverged start-S runs are replaced by their start-B run; per-start counts are in Table VI). A new Table III gives mean, median, min and max over seeds, and the text states that the alpha=1 vs 2 ranges overlap at N=12 and the alpha=2 vs 4 ranges at N=10.
- **Mean-field domain-wall cell.** The start-S value (2.3e-1) and the start-B value (1.0e-3) are both in Table VI and named in the text; the main table uses the selected state. Table VIII counts runs with error above 0.1 per start (13 / 0) and among selected states (0).
- **Grid-edge selections.** Disclosed in the limitations: five of ten rates are on a grid edge (mean-field SGD and SR, RBM alpha=2 and 4 SR at the top; Jastrow SR at the bottom). After the Jastrow re-tune, Jastrow SGD is no longer on an edge. The grids were not extended (compute).
- **Abstract should say alpha=4 SR beats the method of record at the critical field.** Added, and repeated in H3 and the conclusion (0/5 paired wins at Gamma=1 for every N; 31/65 overall).
- **Related work: Pfeuty sentence and uncited "standard ansaetze" claim.** Reworded: the chain is exactly solvable by a free-fermion mapping, and ED is used because it gives the ground-state vector; the claim about common practice is removed.
- **PROTOCOL.md and BRIEF.md described the v1 protocol.** Both rewritten for the final protocol (v3 rates, two starts, reference runs, history). `method/DESIGN.md` and `proposal.md` (amendments section; hypotheses unchanged) updated as well.
- **Overwritten log files in tuning groups.** Not repairable for the existing rows without re-running 250+ runs; noted as a limitation in `experiments/PROTOCOL.md`. The driver now orders tuning runs so that two runs with the same name, task and seed cannot start in the same second (used for the Jastrow re-tune).
- **Fig. 1 panels and legend; "unclipped-and-tuned optimiser".** Fig. 1 is redrawn with labelled panels (a), (b) and the legend below the axes; the training-curve figure's legend is also moved below the plot. The conclusion sentence now reads "an adaptive optimiser, per-start tuning, symmetric ansaetze and larger systems".

## Other changes from my own audit of the paper
- The registered tests use per-task means and a paired comparison; the first version judged on medians only. Table II now reports ratios of means, paired wins and a paired t-test on the selected states (uncorrected, n=5, stated as indicative).
- New failure case reported: in the ordered phase the lower-energy start is often a symmetry-broken state with infidelity 0.5 (Table V), so energy is a poor selection criterion for the state there.
- The setup claimed that raw outputs are in the repository; `results/raw/` is git-ignored. The sentence now says code, logs and the registry are there, and the curve CSV files that the training-curve figure reads are now tracked.
- Tables were consolidated to stay within six pages: the two energy tables are one, the critical-point table is dropped (its parameter column moved to Table I, infidelity to Table V), the two sweep tables are one, the per-seed sweep figure is dropped, and <sigma^x> errors are logged but no longer tabulated. Obsolete generated table and figure files were removed.
- Not done: the reference optimisation for RBM alpha=1 and 4 (compute), a re-tune of rates for start B, and wider rate grids. All three are listed in the limitations.
