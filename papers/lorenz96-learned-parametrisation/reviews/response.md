# Response to the audit (single fix round)

## Major

**1. Wrong-context citation of Rasp 2019 (introduction, related work, landscape).**
Fixed. I re-read the abstract of arXiv:1907.01351. The text now says that Rasp noted that online simulations with
offline-trained ML parametrisations *in Earth system models* were frequently plagued by instabilities and biases,
proposed coupled online learning, and illustrated the concept in Lorenz-96. The claim that the instability was
reported in Lorenz-96 is gone from `introduction.tex`, `related.tex` and `literature/landscape.md`. Two further
sentences that leaned on the same misreading were also changed: the H4 paragraph in `results.tex` ("unlike the
instabilities reported with other inputs and setups") now says that instabilities were reported for Earth system
models and that our stable runs say nothing about those models; `limitations.tex` no longer says the cited work
"shows" online training "to matter", only that it proposes it as a remedy.

## Minor

**2. N_ic = 90.** Fixed: the code uses 10 initial conditions on each of 10 test chains = 100. Changed in
`method.tex`, `proposal.md`, `method/DESIGN.md`, and stated in `experiments/PROTOCOL.md`.

**3. p-values without a committed `rh compare` output.** Fixed: ran
`rh compare --metric valid_time --ref 'Polynomial (deg 4)' --group main`; output committed as
`results/tables/compare_main_valid_time_ref_polynomial.csv` (Welch 2.9e-4, 8.1e-5, 0.36, 0.92; paired 0.051). Because
`rh compare` writes one file per metric, the no-closure comparison used for H1 is kept both as
`compare_main_valid_time.csv` and as `compare_main_valid_time_ref_noclosure.csv`. `results/RESULTS.md` names the files.

**4. Abstract stated a cause as fact.** Fixed: the abstract now says the AR(1) closure no longer had the lower
spectral and PDF error at F=18 and F=22, "possibly because its noise amplitude was fitted at F=20; not isolated by a
run". The conclusion was hedged the same way, and the ablation text now also gives the F=22 numbers behind the claim.

**5. Hardware and runtime paragraph.** Fixed. The text now says 24 rows are superseded (18 first loggings plus the six
AR(1) runs logged a second time under an interim name), and that the superseded rows equal the final rows in every
metric except runtime (I checked all 24 against the registry). It points to `results/runs.jsonl` and the logs for the
metrics and says the per-run JSON files and generated data are not committed. `experiments/run_all.sh` now uses the
final names ("..., deploy F=18/22") and the task label F20_c10 for the shift runs, and includes the pre-check; the
paper says it "lists the commands" of the pre-check and of the main, floor and ablation runs. I did not re-execute
the whole script (that would duplicate identical runs in the registry).

**6. Step-size pre-check had no logged run.** Fixed: added `experiments/precheck_dt.py` and logged it with `rh run`
as a sanity run ("Step-size pre-check", committed before it ran). 40 trajectories, 20-unit window after a 20-unit
spin-up, step 0.0025 against 0.00125 from the same initial states: the mean differs by 0.23% and the variance by
0.02%. The paper keeps the statement "less than 1%" and describes this run; the limitations note that it is a single
run comparing only the mean and variance.

**7. Lorenz (1996) not cited; "operational" for Shutts.** Fixed: added `lorenz2006predictability`
(DOI 10.1017/CBO9780511617652.004, the published version of the 1996 seminar paper) with `rh lit cite`; cited in the
introduction, related work and method. Shutts is now described as having "proposed a kinetic-energy backscatter
algorithm for use in ensemble prediction systems".

**8. Figure captions and the predictability inference.** Fixed. The trade-off figure now includes polynomial degrees
3, 5 and 6 (`experiments/analysis.py`), and its caption says "every configuration run at the training forcing F=20"
(the forcing-shift runs are scored against a different truth and are not on it). The Fig. 1 caption defines the error
bars (standard deviation over seeds, as drawn by `rh fig bars`). The sentence "so the truth's fast variables limit
predictability" was deleted.

**9. Toy-model limitation.** Fixed: the limitations section opens with the statement that two-scale Lorenz-96 is an
idealised toy system whose closure ranking may not transfer to real atmosphere or ocean models; the abstract and
conclusion say "idealised toy system" as well.

## Other changes from my own audit

- Related work: Brajard et al. was listed under "emulation of multiscale Lorenz-96"; their test case is the
  40-variable single-scale model. Heading and sentence corrected.
- Introduction: the sentence that temporally correlated noise "changes the simulated climate" [Wilks; Arnold] was
  replaced by a plain description of what the two papers study; Frezat et al. is described by what its abstract says
  (online training for non-differentiable solvers with a neural emulator).
- Results H2: "Where AR(1) wins on climate it loses on skill" was wrong for c=4 (no climate win there); it now says
  AR(1) has a shorter valid time in both regimes.
- Results H3: the explanation that a one-input function is a smooth curve a degree-4 polynomial already fits is now
  "may ... we did not isolate this".
- Ablations: "most of the climate benefit comes from adding any noise" restricted to what the means show; "no loss of
  skill" at half amplitude replaced by "a valid time close to that of the deterministic closure"; degree-3 value
  added to the degree paragraph; the MLP-input paragraph now states that width three did not raise valid time.
- Method: w1_pdf is computed on every seventh pooled sample (as in the code); now stated.
- Abstract/conclusion: "indistinguishable" replaced by "not distinguished by the registered tests".
- `experiments/PROTOCOL.md` said every run took under 3 minutes; corrected (two MLP runs took 394 s and 552 s).

## State
`rh paper build` OK (6 pages), `rh lit verify` CITATIONS VERIFIED (11 references), `rh check` READY. The only
remaining warning is the advisory verdict tier (the AR(1) closure is not best on valid time), which is the reported
result. No main, floor or ablation run was re-executed; all result tables are unchanged.
