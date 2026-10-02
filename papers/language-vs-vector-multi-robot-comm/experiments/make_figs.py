"""Fig. curves (mean +- std over seeds, from results/raw/curve_*.csv) and cross-play bars (from results/runs.jsonl)."""
import glob, json, collections, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 10})
SY = [("none", "No comm."), ("continuous", "Continuous"), ("discrete", "Discrete"), ("language", "Language (proxy)")]
col = dict(zip([s for s, _ in SY], ["#888888", "#1f77b4", "#d95f02", "#2ca02c"]))
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
for a, suffix, title in ((ax[0], "n0.1", "main (eval every 6400 episodes)"), (ax[1], "n0.1_dense", "dense (every 640 episodes)")):
    for s, lab in SY:
        fs = glob.glob(f"results/raw/curve_{s}_V4_{suffix}_s*.csv")
        if not fs: continue
        df = pd.concat([pd.read_csv(f) for f in fs]).groupby("step").value.agg(["mean", "std"])
        if suffix.endswith("dense"): df = df[df.index <= 40000]
        a.plot(df.index, df["mean"], color=col[s], label=lab); a.fill_between(df.index, df["mean"] - df["std"], df["mean"] + df["std"], color=col[s], alpha=.2)
    a.set_xlabel("training episodes"); a.set_ylabel("validation success"); a.set_title(title, fontsize=9)
ax[0].legend(fontsize=7); plt.tight_layout(); plt.savefig("results/figures/curves_main.pdf")
rows = [json.loads(l) for l in open("results/runs.jsonl")]
d = collections.defaultdict(list)
for r in rows:
    if r["group"] == "xplay" and r["status"] == "ok": d[r["name"].split(" (")[0]].append(r["metrics"]["xplay_success"])
fig, a = plt.subplots(figsize=(3.4, 2.6))
names = ["No communication", "Continuous vector", "Discrete tokens", "Templated language"]
a.bar(range(4), [np.mean(d[n]) for n in names], yerr=[np.std(d[n], ddof=1) for n in names], color=[col[s] for s, _ in SY])
a.set_xticks(range(4)); a.set_xticklabels(["None", "Cont.", "Discr.", "Lang."]); a.set_ylabel("cross-play success"); a.set_ylim(0, 1)
plt.tight_layout(); plt.savefig("results/figures/bars_xplay_xplay_success.pdf")
