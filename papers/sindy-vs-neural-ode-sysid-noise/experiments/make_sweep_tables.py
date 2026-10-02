"""Builds sweep tables (mean over 5 seeds, median in brackets for pred_nrmse) directly from results/runs.jsonl."""
import json, numpy as np, collections
rows = [json.loads(l) for l in open("results/runs.jsonl")]
def table(prefix, param, vals, metric, fname, systems):
    out = []
    for task in ["pendulum", "vdp"]:
        d = collections.defaultdict(list)
        for r in rows:
            if r["group"] == f"{prefix}_{task}" and r["status"] == "ok":
                d[("SINDy (STLSQ)" if param == "lam" else r["name"], r["config"][param])].append(r["metrics"][metric])
        for s in systems:
            cells = []
            for v in vals:
                x = np.array(d[(s, v)])
                cells.append(f"{x.mean():.3f} ({np.median(x):.3f})")
            out.append(f"{task} & {s} & " + " & ".join(cells) + r" \\")
    hdr = r"\begin{tabular}{llc" + "c" * (len(vals) - 1) + r"}\toprule" + "\nTask & Method & " + " & ".join(f"{param}={v}" for v in vals) + r" \\\midrule" + "\n"
    open(f"results/tables/{fname}.tex", "w").write(hdr + "\n".join(out) + "\n" + r"\bottomrule\end{tabular}" + "\n")
S = ["SINDy (STLSQ)", "Neural ODE (MLP)", "DMDc (linear LS)"]
table("sweep_ntrain", "ntrain", [200, 500, 1000, 2000, 5000], "pred_nrmse", "sweep_ntrain_pred", S)
table("sweep_ntrain", "ntrain", [200, 500, 1000, 2000, 5000], "lqr_cost", "sweep_ntrain_lqr", S)
table("sweep_lam", "lam", [0.01, 0.03, 0.1, 0.3, 1.0], "pred_nrmse", "sweep_lam_pred", ["SINDy (STLSQ)"])
table("sweep_lam", "lam", [0.01, 0.03, 0.1, 0.3, 1.0], "lqr_cost", "sweep_lam_lqr", ["SINDy (STLSQ)"])
