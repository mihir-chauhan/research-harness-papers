# Response to audit

1. **Parameter count (major)** – fixed. "about 30k" replaced by "about 41k" (40,618 exactly) in setup, results, limitations, conclusion and method/DESIGN.md.
2. **Sweep log collisions (minor)** – not re-run (would add duplicate registry rows). Registry values and results/raw/*.json are correct; the collision is documented in results/RESULTS.md.
3. **Early-epoch curves (minor)** – fixed. New analysis/make_curves.py reads the logged 5-epoch curves (checked against the registry final accuracy) and writes Table "curves"; results, limitations, abstract and conclusion now say the ranking is specific to final-epoch evaluation, with LS above CE and mixup near small-loss before memorisation (best checkpoint flagged as test-split optimistic).
4. **H3 mechanism / 20% claim (minor)** – mechanism marked as an untested conjecture; the 20% result described as suggestive.
5. **H5 wording (minor)** – H5 quoted as in BRIEF.md; verdict now "partly supported" (most gain lost at 0.1, 0.2, not at 0.3).
6. **ceil vs round (minor)** – method formula changed to max{1, round(.)}, matching the code.
7. **Warm-up pairing (minor)** – now described as paired over the same seeds with a small table (+0.028, p=0.0030; mem_rate -0.133), test-split caveat kept.
8. **Related-work/uncited claims (minor)** – H2 now contrasts with Lukasik et al.; the "published comparisons" sentence and the "easiest for small-loss" claim were softened/reworded rather than cited.
9. **PROTOCOL/VERDICT/ties (minor)** – PROTOCOL run count corrected (70). Tie markup removed in the 0% memorisation columns of Table I. VERDICT.md still shows "missing" for the ablation row: the advisory verdict only pairs rows within one group while the full-method rows are in group main; research.yaml now lists only the real ablation and the explanation is in RESULTS.md.
