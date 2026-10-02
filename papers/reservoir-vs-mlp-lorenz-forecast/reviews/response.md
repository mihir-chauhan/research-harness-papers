# Response to the audit

All experiments were rerun after the audit with corrected code (commit `848bbd1`; the first-version rows are kept in
`results/runs.jsonl`, marked superseded). Every number in the paper now comes from the rerun, through
`analysis/build.sh` (`rh table`, `rh compare`, `analysis/make.py`).

## Major

1. **MLP baseline under-trained; unequal tuning.** Fixed by re-tuning and rerunning. `method/tune.py` now has a second
   stage for the MLP and GRU that tunes optimiser steps and learning rate on the validation seed (MLP: steps
   {4000, 8000, 16000} x lr {1, 2, 5}e-3; GRU: steps {3000, 6000} x lr {1, 3, 10}e-3; GRU noise grid extended to 0.3).
   Selected: MLP 16000 steps / lr 1e-3 (Lorenz-63), 8000 / 2e-3 (Lorenz-96); GRU 6000 steps. All main and
   `sweep_ntrain` rows were rerun with these settings. The paper now states the Lorenz-63 ratio as 1.71 (MLP) and 2.52
   (GRU) and the Lorenz-96 result as MLP ahead (2.882 vs 2.115, paired p=0.018). A new group `sweep_steps` measures the
   MLP and GRU at other optimiser budgets on test seeds 0-2 (Table V, Fig. 2), and the text says that the ESN/MLP ratio on
   Lorenz-63 moves from 2.74 (4000 steps) to 1.69 (32000) and that the MLP's Lorenz-96 mean keeps rising beyond the
   tuned budget. Tuning grids remain unequal in cells (27 / 18 / 11); this is stated in the setup and limitations.
2. **ESN not deterministic; rho=0.1 dissociation claim.** `ESN.__init__` now uses a dense eigensolver
   (`numpy.linalg.eigvals`), all ESN rows were rerun, and the climate metric uses 20 free runs of 10000 steps per seed
   (was 5), with a "True system" row as sampling floor. Five main runs were repeated in this round (group `repro`); all
   metrics are bit-identical to the registered ones, and the setup says so. The rho=0.1 claim is removed: the rerun gives
   clim_ok 0.83 vs 0.85 on Lorenz-63, and the text now says clim_ok shows no trend with rho there.
3. **Table III caption sign.** The table was rebuilt with explicit columns "A", "B", "A - B" and the caption says
   "Differences are A - B (positive: A is higher)".
4. **haluszczynski2019good mischaracterised.** Related work now reports what the abstract says (short- and long-term
   quality vary strongly among realisations and topologies; realisations with better short-term prediction also tend to
   reproduce the climate better) and relates H2 to it.

## Minor

5. **Lyapunov exponents.** `lib.LYAP` now holds the values the committed `method/lyap.py` gives (0.905, 1.158); the
   method section states the settings. The two logged runs had been made from an uncommitted tree, so in this round they
   were superseded and rerun at a commit containing the script (identical values, group `lyapunov`).
6. **H5 wording.** Replaced by the paired tests (p=0.228 on Lorenz-63, 0.372 on Lorenz-96; Table IV).
7. **"Keeps rising", "still improving", "ahead from 2000".** Rewritten: the ESN's change between 5000 and 10000 samples
   is described as within one seed std; the MLP's lead on Lorenz-96 is described as a mean ordering from 2000 samples
   with the paired test reaching 0.05 only at 10000 (p=0.016, 3 seeds).
8. **"Ratio above 3.71 on both tasks".** The conclusion now gives both ratios (4.18 and 10.95 after the rerun).
9. **Table II marks and bold font.** The best/second marks are removed from the paper tables (ties made them
   misleading) and the caption says so. Bold and italic now render: the build loads Times New Roman through fontspec,
   with Latin Modern as fallback.
10. **"Every free run diverges".** Replaced by "leaves the attractor region", defined in the method section as
    non-finite or exceeding three times the largest reference magnitude, with the note that such a run need not be
    numerically unbounded.
11. **Ablation tests and VERDICT.md.** The component ablations are logged in group `main` and tested with
    `rh compare` against their own full system (Table III: ESN vs ESN without squares, GRU vs GRU without noise).
    `VERDICT.md` now lists the ESN ablation as "matters: yes". The GRU ablation is not listed there because `rh verdict`
    compares every ablation with the method (ESN) row, which would be the wrong reference; `results/RESULTS.md` says so.
12. **Citations.** The reservoir-versus-RNN comparison is attributed to vlachas2020backpropagation only;
    vlachas2018data is described as LSTMs compared with Gaussian processes. Citations were added for Lorenz-96
    (lorenz1998optimal), Benettin's method (benettin1980lyapunov), echo state networks (jaeger2004harnessing), GRU
    (cho2014learning) and Adam (kingma2014adam). The unsourced claim that "the reservoir wins" depends on tuning was
    replaced by a pointer to this paper's own optimiser-step sweep.

## Found in the self-audit and changed

- H2: with the rerun data the registered rule is met on Lorenz-63 (clim_ok order GRU, ESN, MLP vs VPT order ESN, MLP,
  GRU), but by differences of 0.01-0.05 with paired p of 0.65-0.70. The paper reports "met formally, not evidence of a
  dissociation" instead of claiming support.
- The setup said three tuned optima lie on a grid edge; more do (learning rates, ridge, input scale). It now says
  "several ... among them".
- The claim that the main ESN row is sub-optimal on Lorenz-96 was weakened: rho=0.1 vs 0.4 is within the seed std.
- A limitations item about an empty registry `config` field was removed; the rerun rows carry their config.
- Compute: the live runs add up to about 100 minutes of process time, above the planned 30 minutes of wall-clock; the
  setup section states this.
- To stay at 6 pages, the bar chart, the spectral-radius figure and the climate-versus-training-length table are not in
  the paper; no claim in the text depends on them (the spectral-radius and size numbers are in Table VII).
- The first-version tuning rows (group `tuning`) were superseded so that the registry's live rows are only those the
  paper uses.
