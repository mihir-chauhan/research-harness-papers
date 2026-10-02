#!/bin/sh
# Rebuild every table, figure and comparison from results/runs.jsonl. Run from the project root after sourcing env.sh.
set -e
rh table --group main --metrics steps_to_first_reward,found_reward,final_return --prec 2

# Welch / paired tests on steps to first reward against three references (rh compare writes one file; keep a copy of each)
for ref in "RND bonus" "Step penalty only (optimistic init)" "Epsilon-greedy Q-learning"; do
  rh compare --metric steps_to_first_reward --group main --ref "$ref" > /dev/null
  slug=$(echo "$ref" | tr 'A-Z ' 'a-z_' | tr -d '()-' | cut -c1-12)
  cp results/tables/compare_main_steps_to_first_reward.csv "results/tables/compare_steps_ref_${slug}.csv"
done
# the two compare files the paper's numbers are traced to: group main against the method, and group offset_control
# (copies of the main rows of penalty only and count (state), see run_all.py) against the penalty-only control
rh compare --metric steps_to_first_reward --group main --ref "RND bonus" > /dev/null
rh compare --metric steps_to_first_reward --group offset_control --ref "Step penalty only (optimistic init)" > /dev/null
$PY method/make_tables.py
rh verdict > /dev/null || true
printf '\nNote: the ablation deltas above pool all eight tasks (steps to first reward, lower is better; a negative delta means the variant is slower). Per-task numbers are in results/tables/main_compact.md. The "best baseline" column does not account for the offset confound: the penalty-only control explains the gain of the count bonus (results/RESULTS.md).\n' >> results/VERDICT.md
