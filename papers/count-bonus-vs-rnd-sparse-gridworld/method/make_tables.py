"""Tables and figures built from results/runs.jsonl (live rows only; superseded rows are skipped).

Run after `rh table --group main` and `rh compare` (see experiments/build_results.sh):
  - main_compact (from results/tables/main_agg.csv), tests (the `rh compare` values, as \rhval keys in the tex)
  - tv_frac, abl_norm, abl_diag, sweep_beta/K/clip tables (tex + md)
  - bars_main_steps, spike_vs_steps, sweepK_tv figures
"""
import json, collections, re
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

T, F = "results/tables/", "results/figures/"


def live_rows(path="results/runs.jsonl"):
    out = []
    for l in open(path):
        r = json.loads(l)
        if r.get("kind") == "control":
            if r.get("op") == "supersede":
                for p in out:
                    if p["group"] == r["group"] and p["name"] == r["name"] and p["status"] == "ok":
                        p["status"] = "superseded"
            continue
        out.append(r)
    return [r for r in out if r["status"] == "ok"]


rows = live_rows()
main = [r for r in rows if r["group"] == "main"]
EPS, PEN, CNO, CST, COB, RND = ("Epsilon-greedy Q-learning", "Step penalty only (optimistic init)",
                                "Count bonus (state), no offset", "Count bonus (state)", "Count bonus (obs)", "RND bonus")
NON, V1, WUP, CLP = ("no bonus normalisation (rnd_nonorm)", "RND, unguarded normaliser (v1)", "RND, warm-up only", "RND, clip only")
ORDER = [EPS, PEN, CNO, CST, COB, RND]
SHORT = {EPS: "eps-greedy", PEN: "penalty only", CNO: "count, no offset", CST: "count (state)", COB: "count (obs)", RND: "RND (guarded)",
         CLP: "RND, clip only", WUP: "RND, warm-up only", V1: "RND, unguarded (v1)", NON: "RND, no normalisation"}
TASKS = ["chain_10", "chain_20", "chain_40", "room_2", "room_4", "room_6", "chain_20_tv", "room_4_tv"]
tx = lambda s: s.replace("_", "\\_")
d = collections.defaultdict(list)
for r in main: d[(r["name"], r["task"])].append(r)
for k in d: d[k].sort(key=lambda r: r["seed"])
M = lambda n, t, m: np.array([r["metrics"][m] for r in d[(n, t)]])
pm = lambda x, p=2: f"{np.mean(x):.{p}f} $\\pm$ {np.std(x, ddof=1):.{p}f}"


def write(name, head, body, align=None):
    align = align or "l" + "r" * (len(head) - 1)
    tex = "\\begin{tabular}{" + align + "}\n\\hline\n" + " & ".join(head) + " \\\\\n\\hline\n"
    tex += "".join((" & ".join(c) + " \\\\\n") if c else "\\hline\n" for c in body) + "\\hline\n\\end{tabular}\n"
    open(T + name + ".tex", "w").write(tex)
    md = "| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n" + "".join("| " + " | ".join(c) + " |\n" for c in body if c)
    md = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", md)
    md = re.sub(r"\\multicolumn\{\d+\}\{l\}\{\\emph\{([^}]*)\}\}", r"*\1*", md)
    open(T + name + ".md", "w").write(md.replace("$\\pm$", "±").replace("\\_", "_").replace("\\quad ", "- ").replace("\\epsilon", "eps").replace("$", "").replace("\\", ""))


# ---- 1. main table, compact layout (systems x tasks) from the aggregate that `rh table --group main` writes
# (results/tables/main_agg.csv; results/tables/main.{md,tex} is the same data in long format for all ten systems).
# Bold (steps block): lowest mean of the column among the six rows shown at the printed precision, ties all bold.
import csv
agg = {(r["name"], r["task"], r["metric"]): (float(r["mean"]), float(r["std"])) for r in csv.DictReader(open(T + "main_agg.csv"))}
body = [["\\multicolumn{9}{l}{\\emph{Steps to first reward}}"]]
best = {t: round(min(agg[(n, t, "steps_to_first_reward")][0] for n in ORDER)) for t in TASKS}
for n in ORDER:
    c = [SHORT[n]]
    for t in TASKS:
        mu, sd = agg[(n, t, "steps_to_first_reward")]
        txt = f"{mu:.0f} $\\pm$ {sd:.0f}"
        c.append("\\textbf{" + txt + "}" if round(mu) == best[t] else txt)
    body.append(c)
body += [None, ["\\multicolumn{9}{l}{\\emph{Seeds that found the reward (of 5) / final return}}"]]
for n in ORDER:
    body.append([SHORT[n]] + [f"{round(agg[(n, t, 'found_reward')][0] * 5)} / {agg[(n, t, 'final_return')][0]:.2f} $\\pm$ {agg[(n, t, 'final_return')][1]:.2f}" for t in TASKS])
body += [None, ["\\multicolumn{9}{l}{\\emph{RND normaliser variants: mean steps to first reward (seeds that found the reward, of 5)}}"]]
for n in [CLP, WUP, V1, NON]:
    body.append([SHORT[n]] + [f"{agg[(n, t, 'steps_to_first_reward')][0]:.0f} ({round(agg[(n, t, 'found_reward')][0] * 5)})" for t in TASKS])
write("main_compact", ["System"] + [tx(t) for t in TASKS], body)

# ---- 2. TV tasks: TV time fraction, and steps to first reward against the noise-free twin
# (no test here: `rh compare` compares systems on one task, and the paper reports only statistics rh computes)
body, v1 = [], []
for t, twin in [("chain_20_tv", "chain_20"), ("room_4_tv", "room_4")]:
    body += [None, ["\\multicolumn{4}{l}{\\emph{" + tx(t) + " (twin: " + tx(twin) + ")}}"]]
    for n in [EPS, PEN, CST, COB, RND]:
        a_, b_ = M(n, twin, "steps_to_first_reward"), M(n, t, "steps_to_first_reward")
        body.append([SHORT[n], pm(M(n, t, "tv_time_frac"), 3), f"{a_.mean():.0f}", f"{b_.mean():.0f}"])
    f, x = M(V1, t, "found_reward"), M(V1, t, "tv_time_frac")  # unguarded variant: TV share by outcome
    v1.append([tx(t), pm(x, 3)] + [f"{np.mean(x[f == flag]):.3f} ($n$={int((f == flag).sum())})" for flag in (1.0, 0.0)])
write("tv_frac", ["System", "TV share", "twin", "TV"], body[1:])
write("tv_frac_unguarded", ["Task", "TV share, all seeds", "found seeds", "not-found seeds"], v1)

# ---- 2b. tests on steps to first reward: every cell is a value recorded by `rh compare`, printed through its \rhval key
# (group main, reference RND bonus; group offset_control, reference penalty only: copies of the main rows of the two
# systems, made with `rh log --from-run`, so that this second reference has its own compare file). The md shows the numbers.
def cmp_rows(path):
    return {(r["name"], r["task"]): r for r in csv.DictReader(open(T + path))}
c_rnd, c_pen = cmp_rows("compare_main_steps_to_first_reward.csv"), cmp_rows("compare_offset_control_steps_to_first_reward.csv")
assert all(r["ref"] == RND for r in c_rnd.values()) and all(r["ref"] == PEN for r in c_pen.values())
SLUG = {CST: "count-bonus-state", PEN: "step-penalty-only-optimistic-init", EPS: "epsilon-greedy-q-learning"}
CELLS = [("main", c_rnd, CST, "paired_p"), ("main", c_rnd, PEN, "welch_p"), ("offset_control", c_pen, CST, "welch_p"), ("main", c_rnd, EPS, "welch_p")]
head = ["Task", "cnt / RND", "pen / RND", "cnt / pen", "RND / $\\epsilon$-gr"]
write("tests", head, [[tx(t)] + [f"{float(c[(n, t)][col]):.4g}" for g, c, n, col in CELLS] for t in TASKS])
md = open(T + "tests.md").read()
write("tests", head, [[tx(t)] + ["\\rhval{cmp/%s/%s/%s/steps_to_first_reward/%s}" % (g, SLUG[n], t, col) for g, c, n, col in CELLS] for t in TASKS])
open(T + "tests.md", "w").write(md)

# ---- 3. normaliser ablation: mean steps to first reward (seeds that found the reward, of 5), all tasks
ABL = [RND, CLP, WUP, V1, NON, PEN]
body = [[SHORT[n]] + [f"{np.mean(M(n, t, 'steps_to_first_reward')):.0f} ({int(M(n, t, 'found_reward').sum())})" for t in TASKS] for n in ABL]
write("abl_norm", ["System"] + [tx(t) for t in TASKS], body)
body = [[SHORT[n], tx(t), pm(M(n, t, "steps_to_first_reward"), 0), f"{int(M(n, t, 'found_reward').sum())}/5",
         pm(M(n, t, "final_return"))] for t in TASKS for n in ABL]
write("abl_norm_long", ["System", "Task", "steps", "found", "return"], body)

# ---- 4. bonus diagnostics over the 40 runs of each variant (spike: bonus above 1e4 in the first 100 steps)
SPIKE = 1e4
DS = [RND, CLP, WUP, V1, NON]
DSLUG = {RND: "rnd-bonus", CLP: "rnd-clip-only", WUP: "rnd-warm-up-only", V1: "rnd-unguarded-normaliser-v1", NON: "no-bonus-normalisation-rnd_nonorm"}
col = {}
for n in DS:
    rs = [r["metrics"] for t in TASKS for r in d[(n, t)]]
    sp = [m for m in rs if m["bonus_max_early"] > SPIKE]; ns = [m for m in rs if m["bonus_max_early"] <= SPIKE]
    fo = lambda ms: f"{int(sum(m['found_reward'] for m in ms))}/{len(ms)}" if ms else "--"
    col[n] = [str(len(sp)), fo(sp), fo(ns)]
    # the four statistics below are per-task statistics that rh records (over the 5 seeds of a task); the table shows the
    # task with the largest one, as its \rhval key in the tex and as a number in the md
    for met, stat, fn in [("bonus_median", "median", np.median), ("bonus_max", "max", np.max), ("bonus_gt1_frac", "mean", np.mean), ("q_abs_max", "max", np.max)]:
        v, t = max((float(fn(M(n, t, met))), t) for t in TASKS)
        col[n].append((f"{v:.4g}", "\\rhval{main/%s/%s/%s/%s}" % (DSLUG[n], t, met, stat)))
labs = ["spike runs (of 40)", "found, spike runs", "found, other runs", "median $b$", "max $b$", "share $b>1$", "max $|Q|$"]
head = ["", "guarded", "clip only", "warm-up", "v1", "no norm."]
cell = lambda c, i: c if isinstance(c, str) else c[i]
write("abl_diag", head, [[lab] + [cell(col[n][i], 0) for n in DS] for i, lab in enumerate(labs)])
md = open(T + "abl_diag.md").read()
write("abl_diag", head, [[lab] + [cell(col[n][i], 1) for n in DS] for i, lab in enumerate(labs)])
open(T + "abl_diag.md", "w").write(md)
# per-run listing for the record (markdown only)
with open(T + "abl_diag_per_run.md", "w") as f:
    f.write("| system | task | seed | found | steps | bonus_max_early | bonus_max | q_abs_max |\n|---|---|---|---|---|---|---|---|\n")
    for n in [V1, RND, CLP, WUP]:
        for t in TASKS:
            for r in d[(n, t)]:
                m = r["metrics"]
                f.write(f"| {SHORT[n]} | {t} | {r['seed']} | {int(m['found_reward'])} | {int(m['steps_to_first_reward'])} | {m['bonus_max_early']:.4g} | {m['bonus_max']:.4g} | {m['q_abs_max']:.4g} |\n")

# ---- 5. sweeps (the default-value cell is the main run)
def cell_runs(group, name, task, param, v, default):
    if v == default: return d[(name, task)]
    return sorted([r for r in rows if r["group"] == group and r["name"] == name and r["task"] == task and r["config"].get(param) == v],
                  key=lambda r: r["seed"])


def sweep(group, param, vals, default, names, task, metrics, fname, head0):
    sh = {"steps_to_first_reward": "steps", "tv_time_frac": "TV", "final_return": "return", RND: "RND", COB: "Cnt", CST: "Cnt"}
    body = []
    for v in vals:
        c = [f"{v:g}"]
        for n in names:
            rs = cell_runs(group, n, task, param, v, default)
            assert len(rs) == 5, (group, n, v, len(rs))
            for m in metrics:
                x = [r["metrics"][m] for r in rs]
                c.append(pm(x, 0 if m.startswith("steps") else 3 if m.startswith("tv") else 2))
        body.append(c)
    write(fname, [head0] + [f"{sh[n]} {sh[m]}" for n in names for m in metrics], body)


sweep("sweep_beta", "beta", [0.03, 0.1, 0.3, 1.0], 0.1, [RND, CST], "room_4", ["steps_to_first_reward", "final_return"], "sweep_beta_perconfig", "$\\beta$")
sweep("sweep_K", "K", [1, 4, 16, 64], 16, [RND, COB], "room_4_tv", ["steps_to_first_reward", "tv_time_frac"], "sweep_K_perconfig", "$K$")
body = []
for lab, v in [("2", 2.0), ("5", 5.0), ("20", 20.0), ("none", None)]:
    c = [lab]
    for t in ["chain_20", "room_4"]:
        rs = d[(WUP, t)] if v is None else cell_runs("sweep_clip", RND, t, "clip", v, 5.0)
        assert len(rs) == 5
        assert sum(r["metrics"]["found_reward"] for r in rs) == 5  # every seed finds the reward (stated in the caption)
        c += [pm([r["metrics"]["steps_to_first_reward"] for r in rs], 0), f"{np.mean([r['metrics']['bonus_clip_frac'] for r in rs]):.3f}"]
    body.append(c)
write("sweep_clip_perconfig", ["$c$", "chain\\_20 steps", "clipped", "room\\_4 steps", "clipped"], body)

# ---- figures
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
COL = {EPS: "#8a8a8a", PEN: "#e69f00", CNO: "#cc79a7", CST: "#0072b2", COB: "#56b4e9", RND: "#d55e00"}
# steps to first reward, one column wide: bars are means, dots the five seeds, log axis; dotted lines mark the step budget
fig, ax = plt.subplots(figsize=(3.45, 2.25))
ts = [t for t in TASKS if t.startswith("chain")] + [t for t in TASKS if t.startswith("room")]
w = 0.14
for i, n in enumerate(ORDER):
    xs = np.arange(len(ts)) + (i - 2.5) * w
    ax.bar(xs, [np.mean(M(n, t, "steps_to_first_reward")) for t in ts], w, color=COL[n], label=SHORT[n])
    for x, t in zip(xs, ts):
        ax.scatter([x] * 5, M(n, t, "steps_to_first_reward"), s=1.5, color="k", zorder=3, linewidths=0)
ax.set_yscale("log"); ax.set_ylim(20, 2.5e5)
ax.plot([-0.5, 3.5], [30000] * 2, "k:", lw=.7); ax.plot([3.5, 7.5], [100000] * 2, "k:", lw=.7)
ax.text(-0.45, 36000, "budget", fontsize=6.5); ax.text(3.55, 120000, "budget", fontsize=6.5)
ax.set_xticks(range(len(ts))); ax.set_xticklabels([t.replace("_tv", "\nTV").replace("_", "\n", 1) for t in ts], fontsize=7)
ax.set_ylabel("steps to first reward"); ax.tick_params(axis="y", labelsize=7)
fig.legend(*ax.get_legend_handles_labels(), ncol=3, fontsize=7.5, loc="upper center", frameon=False, columnspacing=1.0, handlelength=1.0)
plt.tight_layout(rect=(0, 0, 1, 0.85)); plt.savefig(F + "bars_main_steps.pdf"); plt.close()

# unguarded normaliser: largest bonus in the first 100 steps against time to first reward, one point per run
fig, ax = plt.subplots(figsize=(3.45, 2.0))
for n, mk, c in [(V1, "o", "#d55e00"), (RND, "s", "#0072b2")]:
    for flag, fill in [(1.0, True), (0.0, False)]:
        xs, ys = [], []
        for t in TASKS:
            bud = 30000 if t.startswith("chain") else 100000
            for r in d[(n, t)]:
                if r["metrics"]["found_reward"] == flag:
                    xs.append(r["metrics"]["bonus_max_early"]); ys.append(r["metrics"]["steps_to_first_reward"] / bud)
        ax.scatter(xs, ys, marker=mk, s=18, facecolors=c if fill else "none", edgecolors=c, linewidths=0.8,
                   label=f"{'unguarded (v1)' if n == V1 else 'guarded'}, {'found' if fill else 'not found'}" if xs else None)
ax.set_xscale("log"); ax.axvline(SPIKE, color="k", lw=.5, ls=":")
ax.set_xlabel("largest bonus $b$ in the first 100 steps"); ax.set_ylabel("steps to first reward / budget")
ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.52, 0.93), frameon=False)
plt.tight_layout(); plt.savefig(F + "spike_vs_steps.pdf"); plt.close()

# TV time fraction against K
fig, ax = plt.subplots(figsize=(3.45, 2.2))
for n, c, mk in [(RND, "#d55e00", "s"), (COB, "#56b4e9", "o")]:
    Ks = [1, 4, 16, 64]
    xs = [[r["metrics"]["tv_time_frac"] for r in cell_runs("sweep_K", n, "room_4_tv", "K", K, 16)] for K in Ks]
    ax.errorbar(Ks, [np.mean(x) for x in xs], yerr=[np.std(x, ddof=1) for x in xs], color=c, marker=mk, ms=4, lw=1, capsize=2, label=SHORT[n])
ax.set_xscale("log", base=2); ax.set_xticks([1, 4, 16, 64]); ax.set_xticklabels(["1", "4", "16", "64"])
ax.set_xlabel("TV token cardinality $K$"); ax.set_ylabel("TV time fraction"); ax.set_ylim(bottom=0); ax.legend(fontsize=8, frameon=False)
plt.tight_layout(); plt.savefig(F + "sweepK_tv.pdf"); plt.close()
print("tables and figures written")
