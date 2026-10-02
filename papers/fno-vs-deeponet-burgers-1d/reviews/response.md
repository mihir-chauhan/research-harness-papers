# Response to the audit

New run in this round: one tuning run, `tune-cnn` at lr 1e-2 (seed 100, group `tune`, run id d98b2a85f8, 146 s), launched on a clean tree at commit b744b86. No other experiment was run; all other numbers come from the existing registry.

1. **major - "four runs per system" / CNN never run at 1e-2 (setup.tex, limitations.tex).**
   The finding is correct. Fixed at the cause: the CNN lr=1e-2 tuning point was run and logged through `rh run`. It diverges (validation rel. L2 = 1.0000, the network outputs approximately zero), as the auditor's own run did, so the selected rate (3e-3) and all main results are unchanged. The registry now has four successful tuning runs per system, and the paper has a new tuning table (Table I, `results/tables/tune.tex`, generated from the registry) with all 16 validation errors. The text now states the order of events: the grid was extended for the FNO, DeepONet and MLP before the main runs, and the CNN's point was added only in the revision. Limitations names the asymmetry and adds that the FNO's selected rate is still at the edge of the extended grid.

2. **minor - MLP "within 1e-4".** Text now says the two validation errors differ by less than 2e-4; both values (0.0940, 0.0941) are in the tuning table.

3. **minor - Eq. 2 vs code (activation after the last Fourier layer).** Method section now states that GELU is applied for l = 0, 1, 2 and that the last layer has no activation. While re-reading `method/run.py` against the text I also added: the branch/trunk layer sizes of DeepONet, that the CNN has no activation after its last convolution and a 49-point receptive field, that the lifting takes (a(x), x), and that the Fourier interpolation drops the 128-point Nyquist mode. `method/DESIGN.md` updated likewise. No code change.

4. **minor - CNN receptive field; "would also improve".** The receptive field (49 of 128 points) is now stated in the method, named in the H1 paragraph and in Limitations as an untested second candidate cause of the CNN's error. The speculation is removed: the text says the CNN was not run longer (500 epochs would exceed the per-run time limit) and that whether it would improve is unknown. The H2 sentence "the CNN fails because ..." is hedged to "a likely cause", with the statement that it was not isolated by a run.

5. **minor - DeepONet weaker than prior work suggests.** Abstract, related work, results (H1), limitations and conclusion now say that our plain DeepONet does not reproduce the comparable performance reported by Lu et al. for simple settings, that no published error value was used as a reference, and that the numbers are a lower bound on DeepONet quality. The ablation table now has a training-error column, and the text reports that between 500 and 2000 epochs DeepONet's test error barely moves (0.1314 to 0.1276) while its training error halves (0.0833 to 0.0417), i.e. it overfits.

6. **minor - PDEBench and Lu et al. in the introduction.** Reworded: Lu et al. are summarised as their abstract does (comparable in relatively simple settings, FNO deteriorating on complex geometries and noisy data); PDEBench is cited for larger-scale data including 1D Burgers with baselines, and related work says its baselines are FNO, U-Net and PINN with no DeepONet.

7. **minor - MLP at 2000 epochs; step-count confound.** The ablation table now has "change vs default" and Welch p columns. The MLP statement reads "within noise of its 100-epoch value (Welch p of 0.314 and 0.145)". The H4 paragraph, the abstract and Limitations state that the n_train sweep fixes epochs, so 100/200/400 pairs get 500/1000/2000 gradient steps, with no matched-step control. The mechanism claim "limited by optimisation as much as by data" is hedged to "may". The H3 claim now quotes the table (4 modes 36% worse, 8 vs 16 modes about 1%), and the grid-channel paragraph cites its p-value row.

8. **minor - Table headers, params format, VERDICT.md, BRIEF/PROTOCOL grid.**
   - The main table is now `results/tables/maintab.tex`, written by `experiments/make_figs.py` from the same registry rows as `rh table --group main` (which is still generated as `main.tex`/`main.md` for cross-checking): headers "test 128 / train 128 / test 256 / test 512 / rs256 / params / time (s)" match the caption, parameters are integers, time has one decimal. It is no longer shrunk with `\resizebox`.
   - `research.yaml` ablations now carry their group. `rh verdict` was re-run, but it still prints "missing" for every ablation: the tool looks for the FNO's rows inside each ablation group, and the reference FNO runs are in `main` (re-logging identical runs under another group is not allowed). I did not work around this. Instead a hand-written note at the end of `results/VERDICT.md` and in `results/RESULTS.md` explains both this and the paired-vs-Welch p-value, and points to `results/tables/ablsum.md`, which has the deltas and Welch p-values. Note that re-running `rh verdict` overwrites the hand-written note in VERDICT.md; the copy in RESULTS.md stays.
   - BRIEF.md, experiments/PROTOCOL.md and a dated amendment line in proposal.md now give the four-value grid, the order in which it was extended, and the selected rates. Hypotheses and registered tests are unchanged.

## Other changes from the self-audit
- Failure-case sentence about the FNO ("dominated by what it cannot gain from the grid") replaced by a plain statement of what the table shows.
- Abstract: "insensitive" replaced by "no measurable sensitivity on three seeds".
- Conclusion: added that the size of the FNO gap should not be generalised given under-fit baselines.

## Not done
- No longer CNN training and no CNN with a larger receptive field (a 500-epoch CNN run would take about 14 minutes, above the per-run limit). The paper says so.
- No matched-step control for the n_train sweep and no regularisation control for the MLP. Both are stated as limits.
