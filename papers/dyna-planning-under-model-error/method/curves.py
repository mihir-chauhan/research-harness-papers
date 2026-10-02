"""Cumulative-reward curves (mean +/- s.e. over seeds) from results/raw/curve_*.csv."""
import glob, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
for task, change in [("blocking", 1000), ("shortcut", 3000)]:
    df = pd.concat([pd.read_csv(f) for f in glob.glob(f"results/raw/curve_{task}__*.csv")])
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    for name, c in zip(["Q-learning", "Dyna-Q", "Dyna-Q+", "PS"], ["k", "#1b6ca8", "#d95f02", "#4d9a3c"]):
        g = df[df.name == name].groupby("step")["value"]
        m, s = g.mean(), g.std(ddof=1) / np.sqrt(g.count())
        ax.plot(m.index, m, color=c, lw=1, label=name); ax.fill_between(m.index, m - s, m + s, color=c, alpha=0.2, lw=0)
    ax.axvline(change, color="gray", ls=":", lw=0.8)
    ax.set_xlabel("real steps", fontsize=7); ax.set_ylabel("cumulative reward", fontsize=7); ax.tick_params(labelsize=6); ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(f"results/figures/curves_{task}.pdf"); plt.close(fig)
