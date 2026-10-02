"""Reads results/runs.jsonl (run `rh compare --metric test_acc --group main` and `experiments/drive.py derived` first).
Writes results/figures/*.pdf and results/tables/{main,abl_sam,rho_sweep,wd_sweep,corr,cmp,sel}.tex.
No table cell is a typed number: every result cell is a \\rhval{<key>} macro that `rh paper build` fills from the
registry (correlations, Holm-adjusted p-values: rows of group `derived`, logged by experiments/derive.py).
The .csv/.md copies next to the tables are for reading only."""
import json, collections, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
R = [json.loads(l) for l in open("results/runs.jsonl")]
R = [r for r in R if r["group"] in ("main", "sweep_rho", "sweep_wd", "abl_sam")]
df = pd.DataFrame([dict(group=r["group"], name=r["name"], task=r["task"], seed=r["seed"],
                        rho=r["config"].get("rho", 0.0), wd=r["config"].get("wd", 0.0), **r["metrics"]) for r in R])
TASKS = ["digits_n0.0", "digits_n0.2", "digits_n0.4", "spirals_n0.2"]
def save(t, name, prec=3):
    t.to_csv(f"results/tables/{name}.csv")
    open(f"results/tables/{name}.md", "w").write(t.to_string())
# --- sweeps: SAM rows = main SAM + sweep_rho ; SGD+WD rows = main SGD+WD + sweep_wd
sam = df[(df.name == "SAM")]; wdd = df[(df.name == "SGD+WD")]
rs = sam.groupby(["task", "rho"]).test_acc.agg(["mean", "std", "count"]).reset_index()
wsw = wdd.groupby(["task", "wd"]).test_acc.agg(["mean", "std", "count"]).reset_index()
sgd = df[df.name == "SGD"].groupby("task").test_acc.agg(["mean", "std"])
piv = rs.pivot(index="task", columns="rho", values="mean").loc[TASKS]; piv.columns = [f"{c:g}" for c in piv.columns]
piv.insert(0, "SGD", sgd["mean"].loc[TASKS])
save(piv, "rho_sweep", 3); print(piv.round(3)); print(rs["count"].unique())
pw = wsw.pivot(index="task", columns="wd", values="mean").loc[TASKS]; pw.columns = [f"{c:g}" for c in pw.columns]
save(pw, "wd_sweep", 3); print(pw.round(3)); print(wsw["count"].unique())
# --- fig: rho sweep
fig, ax = plt.subplots(1, 4, figsize=(7.2, 2.0), sharey=False)
for a, t in zip(ax, TASKS):
    d = rs[rs.task == t]; a.errorbar(d.rho, d["mean"], d["std"], marker="o", ms=3, lw=1, capsize=2, color="C0", label="SAM")
    a.axhline(sgd["mean"][t], color="C3", ls="--", lw=1, label="SGD")
    w = wdd[(wdd.task == t) & (wdd.group == "main")].test_acc.mean(); a.axhline(w, color="C2", ls=":", lw=1, label="SGD+WD (sel.)")
    a.set_xscale("log"); a.set_title(t.replace("_n", " n"), fontsize=7); a.tick_params(labelsize=6); a.set_xlabel(r"$\rho$", fontsize=7)
ax[0].set_ylabel("test acc", fontsize=7); ax[0].legend(fontsize=5)
plt.tight_layout(); plt.savefig("results/figures/rho_sweep.pdf"); plt.close()
# --- correlations (all evaluation-seed runs)
rows = []
def corr(d, label):
    out = {"subset": label, "n": len(d)}
    for s in ["sharp_rand", "sharp_adv"]:
        for g in ["gap_acc", "gap_loss"]:
            out[f"{s[6:]}-{g[4:]}"] = spearmanr(d[s], d[g])[0]
    rows.append(out)
df["collapsed"] = np.where(df.task.str.startswith("digits"), df.test_acc < 0.15, df.test_acc < 0.55)
print("collapsed runs:", df[df.collapsed].groupby(["task", "name", "rho", "wd"]).size())
corr(df, "all tasks pooled")
corr(df[~df.collapsed], "pooled, collapsed runs removed")
for t in TASKS: corr(df[df.task == t], t)
for t in TASKS: corr(df[(df.task == t) & ~df.collapsed], t + " no collapsed")
corr(df[(df.name == "SAM") & (df.task != "spirals_n0.2")], "SAM-sweep digits pooled")
for t in TASKS[:3]: corr(df[(df.name == "SAM") & (df.task == t)], f"SAM only {t}")
ct = pd.DataFrame(rows).set_index("subset"); ct["n"] = ct["n"].astype(int)
save(ct, "corr", 2); print(ct.round(2))
# --- scatter
fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.5))
cols = dict(zip(TASKS, ["C0", "C1", "C3", "C2"])); mk = {"SGD": "o", "SGD+WD": "s", "SAM": "^", "SAM random direction": "v", "SAM+WD": "D"}
for a, s in zip(ax, ["sharp_adv", "sharp_rand"]):
    for (t, n), d in df.groupby(["task", "name"]):
        a.scatter(d[s], d.gap_acc, s=14, marker=mk[n], color=cols[t], alpha=.7, lw=0)
    a.set_xscale("log"); a.set_xlabel(s.replace("_", " ") + " (loss increase, norm 0.5)", fontsize=8); a.tick_params(labelsize=7)
ax[0].set_ylabel("gap_acc", fontsize=8)
from matplotlib.lines import Line2D
h = [Line2D([], [], marker="o", ls="", color=c, label=t.replace("_n", " n"), ms=4) for t, c in cols.items()] + \
    [Line2D([], [], marker=m, ls="", color="gray", label=n, ms=4) for n, m in mk.items()]
ax[1].legend(handles=h, fontsize=6, loc="center left", bbox_to_anchor=(1.02, 0.5), ncol=1)
plt.tight_layout(); plt.savefig("results/figures/sharp_gap.pdf"); plt.close()
# --- tables: every result cell is \rhval{<key>} (the keys of `rh values --list`), nothing is typed
import re
def slug(x): return re.sub(r"[^a-z0-9_.+-]+", "-", str(x).lower()).strip("-") or "x"
def rv(*parts, fmt="3"): return "\\rhval{" + "/".join(slug(q) if "@" not in str(q) else q for q in parts) + (":" + fmt if fmt else "") + "}"
def esc(x): return str(x).replace("_", "\\_")
def tabular(name, spec, head, body):
    open(f"results/tables/{name}.tex", "w").write("\n".join([f"\\begin{{tabular}}{{{spec}}}", "\\toprule", head + " \\\\", "\\midrule"] + body + ["\\bottomrule", "\\end{tabular}"]) + "\n")
sel = json.load(open("experiments/selected.json"))
RHOS = sorted(sam.rho.unique()); WDS = sorted(wdd.wd.unique())
def sweep_key(t, name, param, v):
    """mean test accuracy of `name` on task t at param=v: the selected value was run in group main, the others in the sweep group"""
    if v == sel[f"{t}|{name}"]: return rv("main", name, t, "test_acc", "mean")
    return rv(f"sweep_{param}", f"{slug(name)}@{param}={slug(json.loads(json.dumps(float(v))))}", t, "test_acc", "mean")
tabular("rho_sweep", "l" + "r" * (len(RHOS) + 1), "task & SGD & " + " & ".join(f"{v:g}" for v in RHOS),
        [f"{esc(t)} & " + rv("main", "SGD", t, "test_acc", "mean") + " & " + " & ".join(sweep_key(t, "SAM", "rho", v) for v in RHOS) + " \\\\" for t in TASKS])
tabular("wd_sweep", "l" + "r" * len(WDS), "task & " + " & ".join(f"{v:g}" for v in WDS),
        [f"{esc(t)} & " + " & ".join(sweep_key(t, "SGD+WD", "wd", v) for v in WDS) + " \\\\" for t in TASKS])
# correlations: rows of group `derived` (experiments/derive.py corr); pooled rows are filed under the primary task
PRIMARY = "digits_n0.4"
CORR = [("all tasks pooled", "corr pooled all", PRIMARY), ("pooled, collapsed runs removed", "corr pooled no-collapsed", PRIMARY)] + \
       [(esc(t), "corr all", t) for t in TASKS] + [(esc(t) + " no collapsed", "corr no-collapsed", t) for t in TASKS] + \
       [("SAM-sweep digits pooled", "corr pooled SAM digits", PRIMARY)] + [("SAM only " + esc(t), "corr SAM", t) for t in TASKS[:3]]
tabular("corr", "lrrrrr", "subset & n & rand-acc & rand-loss & adv-acc & adv-loss",
        [f"{lab} & " + rv("derived", nm, t, "n_runs", "mean", fmt="") + " & " +
         " & ".join(rv("derived", nm, t, m, "mean", fmt="2") for m in ["rand_acc", "rand_loss", "adv_acc", "adv_loss"]) + " \\\\" for lab, nm, t in CORR])
# paired comparison: statistics of `rh compare` (ref SAM), Holm-adjusted paired p from experiments/derive.py paired
c = pd.read_csv("results/tables/compare_main_test_acc.csv").set_index(["task", "name"])
dfmt = lambda x: "3" if abs(x) >= 0.01 else "4"
pfmt = lambda x: "3" if x >= 0.01 else "sci2"
holm = {(r["task"], r["name"]): r["metrics"]["holm_p"] for r in map(json.loads, open("results/runs.jsonl"))
        if r["group"] == "derived" and "holm_p" in r["metrics"] and r["status"] == "ok"}
body = []
for t in TASKS:
    for b in ["SGD", "SGD+WD"]:
        k = lambda st: ("cmp", "main", b, t, "test_acc", st)
        body.append(f"{esc(t)} & {b} & " + rv(*k("delta"), fmt=dfmt(c.loc[(t, b), "delta"])) + " & " + rv(*k("welch_p"), fmt=pfmt(c.loc[(t, b), "welch_p"]))
                    + " & " + rv(*k("paired_p"), fmt=pfmt(c.loc[(t, b), "paired_p"])) + " & "
                    + rv("derived", f"SAM minus {b}", t, "holm_p", "mean", fmt=pfmt(holm[(t, f"SAM minus {b}")])) + " \\\\")
tabular("cmp", "llrrrr", "task & vs & diff & Welch p & paired p & Holm p", body)
st = pd.DataFrame({t: {"SAM rho": sel[f"{t}|SAM"], "SGD+WD wd": sel[f"{t}|SGD+WD"]} for t in TASKS}).T
open("results/tables/sel.tex", "w").write(st.to_latex(float_format=lambda x: f"{x:g}", escape=True))
# --- main and ablation tables: mean +- std over seeds, sharp_rand in scientific notation (its values are of order 1e-3)
COLS = [("test_acc", "3", "3"), ("gap_acc", "3", "3"), ("memorised", "3", "3"), ("sharp_adv", "4", "4"), ("sharp_rand", "sci2", "sci1"), ("weight_norm", "2", "2")]
def typeset(group, order):
    body = []
    for t in TASKS:
        if body: body.append("\\midrule")
        for n in order:
            body.append(f"{n} & {esc(t)} & " + " & ".join(rv(group, n, t, k, "mean", fmt=fm) + " $\\pm$ " + rv(group, n, t, k, "std", fmt=fs) for k, fm, fs in COLS) + " \\\\")
    tabular(group, "ll" + "c" * len(COLS), "Method & Task & " + " & ".join(esc(k) for k, _, _ in COLS), body)
typeset("main", ["SGD", "SGD+WD", "SAM"])
typeset("abl_sam", ["SAM random direction", "SAM+WD"])
