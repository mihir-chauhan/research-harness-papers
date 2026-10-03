"""Figures from the curves saved by the main runs (results/raw) and the metrics in results/runs.jsonl."""
import json, re, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TC = 2 / np.log(1 + np.sqrt(2))
SEEDS = range(10)
rows = [json.loads(l) for l in open("results/runs.jsonl")]
main = {(r["name"], r["seed"]): r["metrics"] for r in rows if r["group"] == "main" and r["status"] == "ok"}


def load(name, seed):
    return np.load(f"results/raw/main_{re.sub('[^A-Za-z0-9]', '_', name)}_s{seed}_curves.npz")


plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
col = {16: "#1f77b4", 24: "#ff7f0e", 32: "#2ca02c"}

# Figure 1: ordered-phase probability curves, mean +- std over seeds
names = ["LogReg (raw)", "LogReg (Z2-fixed)", "MLP", "CNN"]
fig, ax = plt.subplots(1, 4, figsize=(7.2, 1.9), sharey=True)
for a, n in zip(ax, names):
    for L in (16, 24, 32):
        C = np.array([load(n, s)[f"L{L}"] for s in SEEDS]); T = load(n, 0)["T"]
        a.plot(T, C.mean(0), color=col[L], label=f"L={L}")
        a.fill_between(T, C.mean(0) - C.std(0), C.mean(0) + C.std(0), color=col[L], alpha=0.15, lw=0)
    a.axvline(TC, color="k", ls=":", lw=0.8); a.axhline(0.5, color="gray", lw=0.5)
    a.set_title(n); a.set_xlabel("T")
ax[0].set_ylabel("mean P(ordered)"); ax[0].legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig("results/figures/fig_curves.pdf"); plt.close(fig)

# Figure 2: collapse of CNN / MLP / Binder with the exponent and Tc found for seed 0
fig, ax = plt.subplots(1, 4, figsize=(7.2, 1.9))
for a, n, lab in zip(ax, ["MLP", "CNN", "Binder/chi (reference)", "PCA"], ["MLP", "CNN", "Binder U4", "PCA |PC1|"]):
    m = main[(n, 0)]; tc = m["tc_bias_fss"] + TC; nu = m["nu_fss"]; z = load(n, 0)
    for L in (16, 24, 32):
        a.plot((z["T"] - tc) * L ** (1 / nu), z[f"L{L}"], ".-", ms=2, lw=0.6, color=col[L], label=f"L={L}")
    a.set_xlim(-12, 12) if n != "PCA" else None
    a.set_title(f"{lab} (seed 0)", fontsize=7); a.set_xlabel(r"$(T-T_c)L^{1/\nu}$")
ax[0].legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig("results/figures/fig_collapse.pdf"); plt.close(fig)

# Figure 3: learning by confusion W curves and PCA susceptibility proxy
fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.9))
for L in (16, 24, 32):
    C = np.array([load("Confusion (MLP)", s)[f"L{L}"] for s in SEEDS]); T = load("Confusion (MLP)", 0)["T"]
    ax[0].plot(T, C.mean(0), color=col[L], label=f"L={L}")
    Q = np.array([load("PCA", s)[f"L{L}"] for s in SEEDS]); ax[1].plot(load("PCA", 0)["T"], Q.mean(0), color=col[L])
for a in ax: a.axvline(TC, color="k", ls=":", lw=0.8); a.set_xlabel("T")
ax[0].set_ylabel("held-out accuracy"); ax[0].set_title("confusion W", fontsize=7); ax[0].legend(frameon=False, fontsize=6)
ax[1].set_ylabel(r"mean$|z_1|$ / max"); ax[1].set_title("PCA", fontsize=7)
fig.tight_layout(); fig.savefig("results/figures/fig_confusion_pca.pdf"); plt.close(fig)

# Figure 4: sensitivity sweeps (main rows are the default setting)
def collect(group, sysn, key, val, metric):
    out = {}
    for r in rows:
        if r["group"] == group and r["name"] == sysn and r["status"] == "ok":
            out.setdefault(r["config"][key], []).append(r["metrics"][metric])
    return out
fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.9), sharey=True)
for a, (grp, key, default, xl) in zip(ax, [("sweep_margin", "margin", 0.3, "margin"), ("sweep_nsamp", "nsamp", 50, "samples/chain")]):
    for n, c in (("MLP", "#d62728"), ("CNN", "#1f77b4")):
        d = collect(grp, n, key, None, "tc_error_l32")
        d[default] = [main[(n, s)]["tc_error_l32"] for s in range(5)]  # same seeds 0-4 as the sweeps
        xs = sorted(d); a.errorbar(xs, [np.mean(d[x]) for x in xs], [np.std(d[x]) for x in xs], color=c, marker="o", ms=3, lw=0.8, capsize=2, label=n)
        if key == "nsamp":  # same sweep with epochs scaled to a constant number of updates (dashed)
            d2 = collect("sweep_nsamp_ep", n, key, None, "tc_error_l32"); d2[default] = d[default]
            xs = sorted(d2); a.errorbar(xs, [np.mean(d2[x]) for x in xs], [np.std(d2[x]) for x in xs], color=c, marker="s", ms=2.5, lw=0.8, ls="--", capsize=2)
    a.set_xlabel(xl)
ax[0].set_ylabel("$|T_c$ error$|$, L=32"); ax[0].legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig("results/figures/fig_sweeps.pdf"); plt.close(fig)
print("ok")
