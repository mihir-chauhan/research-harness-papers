"""Hypothesis-test table from the `rh compare` CSVs (reference system: MPNN-max + steps)."""
import pandas as pd
# (hypothesis, compared system, short label, metric, registered in proposal.md / research.yaml before the runs?)
spec = [("H1", "MPNN-sum + steps", "sum+steps", "mae_sparse_n64", True), ("H1", "MPNN-sum + steps", "sum+steps", "mae_sparse_n16", False),
        ("H2", "MPNN-max", "max", "mae_sparse_n64", True), ("H2", "MPNN-max", "max", "mae_sparse_n16", False),
        ("H3", "MLP (flat adjacency)", "MLP", "mae_sparse_n16", True), ("H3", "MLP (flat adjacency)", "MLP", "mae_sparse_n64", True)]
def g(x): return "nan" if x != x else (f"{x:.1e}" if abs(x) >= 100 or (0 < abs(x) < 0.001) else f"{x:.3f}")
out = []
for h, other, short, m, reg in spec:
    d = pd.read_csv(f"results/tables/compare_main_{m}.csv"); r = d[d["name"] == other].iloc[0]
    cell = m.replace("mae_sparse_n", "S") + ("" if reg else "$^\\ast$")
    out.append(f"{h} & {short} & {cell} & {g(r.ref_mean)} & {g(r['mean'])} & {g(r.welch_p)} & {g(r.paired_p)} \\\\")
open("results/tables/hyp_table.tex", "w").write("\\begin{tabular}{lllcccc}\\toprule\n & System & Cell & Ref. & Other & Welch $p$ & paired $p$ \\\\\\midrule\n" + "\n".join(out) + "\n\\bottomrule\\end{tabular}\n")
print(open("results/tables/hyp_table.tex").read())
