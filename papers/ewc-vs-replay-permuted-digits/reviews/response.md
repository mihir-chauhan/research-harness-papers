# Response to the audit (fix round)

One entry per finding of the second audit. The response to the first audit is in the git history of this file.

1. **(major) Table I overflowed the page.** Fixed. The main table is now built with
   `rh table --group main --metrics average_accuracy,forgetting,backward_transfer,last_task_accuracy`, i.e. only the
   four test metrics used in the text (the validation columns are dropped), and is set in a two-column `table*`
   float at natural size. `paper/main.log` has no overfull box; every column, including the seed count, is visible in
   the rendered PDF (checked on the page image).

2. **(minor) EWC vs fine-tuning p-value not in a saved compare output; compare CSV overwritten.** Fixed.
   `experiments/make_stats.sh` saves one `rh compare` output per scenario and per reference system (ER M=100 and
   Fine-tuning): `results/tables/compare_main_average_accuracy_<task>_ref-<ref>.{txt,csv}`. The EWC vs fine-tuning
   pair on split_cil (paired p = 0.2195) is in `..._split_cil_ref-Finetuning.txt`. The 95% intervals, which
   `rh compare` does not print, come from `experiments/paired_stats.py` (`results/tables/paired_main_average_accuracy.txt`)
   and are shown in the paper as a table of paired differences; the text now says which number comes from where.

3. **(minor) Sweep logs shared between rows.** Fixed by re-running. The 225 original sweep rows are retired with
   `rh supersede` (still visible with `rh runs --all`) and all 225 sweep runs were executed again through `rh run`
   with a driver that serialises jobs sharing a log stem (`experiments/drive.py`). The first attempt at the re-run was
   interrupted after 98 rows; the remaining 127 were run with `experiments/jobs.py sweeps --resume`, and the two
   partial logs of the interrupted jobs (no registry row) were deleted. `experiments/check_logs.py` reports one clean
   log per active row, and the re-run metrics are identical to the retired rows for all 225 runs, so no number in the
   paper changed. The limitations section describes this instead of the old disclosure.

4. **(minor) Job lists missing.** Fixed. `experiments/jobs.py` holds the job lists of the tune_lr, sweep and main
   groups (`--dry-run` prints the `rh run` commands). The generated commands were compared with
   `provenance.command` of the registry rows: sweeps and main are identical; the tune_lr rows were produced by an
   earlier driver version whose metrics-file names did not contain the learning rate, otherwise identical. This is
   stated in `experiments/PROTOCOL.md`. The introduction no longer says the lists "produced" the runs, only that the
   job lists of every group are in the repository.

5. **(minor) "20 per task at the end" in the abstract.** Fixed: the abstract now says "25 stored examples per earlier
   task while the last task is learned".

6. **(minor) Table I formatting.** Fixed in `experiments/make_tables.py`, which changes only the presentation of the
   `rh table` output (every number is the string `rh table` printed): the bold row label is removed, headers are
   readable names, every cell tied for best is bold and a runner-up is underlined only when the best is unique. The
   caption explains the marks.

7. **(minor) Published venues.** Partly fixed. The four references that have a Crossref DOI were re-added with
   `rh lit cite <DOI>`: Kirkpatrick et al. (PNAS), Rebuffi et al. (CVPR), Li and Hoiem (TPAMI), Liu et al. (ICPR).
   The other seven remain arXiv records: their published versions (ICML, NeurIPS and ICLR proceedings) have no DOI
   that `rh lit cite` can resolve, "Three scenarios for continual learning" and "On Tiny Episodic Memories" are
   arXiv-only under those titles, and BibTeX entries are not to be typed by hand. `rh lit verify` ends with
   CITATIONS VERIFIED.

## Changes from the self-audit
- The abstract and ablation text said that EWC's low forgetting at large lambda "comes with low accuracy on the last
  task" / "stability is bought with plasticity" without a table of last-task accuracy for the sweeps. Added that
  table (last-task accuracy per lambda and for four buffer sizes, from the registry) and replaced the phrase by the
  numbers. The table also shows an extreme value, last-task accuracy exactly 0 in all five seeds for lambda >= 1e4
  on split_cil, which the text now states and relates to the failure case of the main runs.
- Added the learning-rate selection table that the setup text quotes (0.930 against 0.911, rates within 0.001).
- "the peak is real" (split_cil, lambda sweep) reworded to a statement about seed standard deviations.
- The sentence that the M-versus-lambda comparison "is not biased towards replay by tuning" was replaced by the
  facts: the EWC value is the best of seven on those seeds, the buffer sizes were not tuned.
- Sweep figure enlarged to two-column width so its tick labels are readable.
- The EWC gain on the sweep seeds was quoted as a difference (0.143) that appears in no table; the abstract, results
  and conclusion now quote the two table values (0.340 against 0.196) instead.
- A negative number in a bold cell of the main table was typeset with a hyphen; fixed in `experiments/make_tables.py`.
