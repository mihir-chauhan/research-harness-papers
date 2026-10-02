"""Cosmetic post-processing of rh-generated tables: readable headers and labels, best/second
marks computed without the real-data floor row (main tables) and removed from the two-row
ablation blocks, where they carry no information. Values are never changed."""
import re, sys, pathlib
T = pathlib.Path(__file__).resolve().parent.parent / "results" / "tables"
def hdr(s):
    s = re.sub(r"sw\\_k(\d+)", r"SW@\1", s)
    s = re.sub(r"mmd\\_k(\d+)", r"MMD@\1", s)
    s = s.replace("start at ab>=4e-5", "start at $\\bar\\alpha\\ge4\\times10^{-5}$").replace("& checkerboard &", "& Checkerboard &")
    return s.replace("eight\\_gaussians", "8 Gaussians").replace("two\\_moons", "Two moons")
def cellval(c):
    c = re.sub(r"\\(textbf|underline)\{(.*)\}", r"\2", c.strip())
    m = re.match(r"(-?[\d.]+) \$\\pm\$", c)
    return (float(m.group(1)), c) if m else (None, c)
for f in ["main_sw", "main_mmd", "abl_schedule", "abl_reflow"]:
    MARK = f.startswith("main")
    p = T / (f + ".tex"); lines = p.read_text().split("\n"); out = []
    block = []
    def flush():
        if not block: return
        rows = [[c for c in re.split(r" & ", l.rstrip(" \\"))] for l in block]
        ncol = len(rows[0]); cells = [[cellval(c) for c in r] for r in rows]
        for j in range(2, ncol - 1):
            cand = [(cells[i][j][0], i) for i in range(len(rows)) if cells[i][j][0] is not None and "floor" not in rows[i][0]]
            if len(cand) < 2: continue
            if not MARK:  # ablation tables: strip rh's marks
                for i in range(len(rows)): cells[i][j] = (None, cells[i][j][1])
                continue
            hi = "straight" in hdr_cols[j] if False else (j == straight_col)
            cand.sort(reverse=hi); b, s = cand[0][1], cand[1][1]
            for i in range(len(rows)):
                v = cells[i][j][1]
                cells[i][j] = (None, v)
            cells[b][j] = (None, "\\textbf{%s}" % cells[b][j][1]); cells[s][j] = (None, "\\underline{%s}" % cells[s][j][1])
        for r, cs in zip(rows, cells):
            out.append(" & ".join(r[:2] + [c[1] for c in cs[2:]]) + " \\\\")
        block.clear()
    hdr_cols = []; straight_col = -1
    for l in lines:
        if l.startswith("Method &"):
            l = hdr(l); hdr_cols = l.split(" & ")
            straight_col = next((i for i, c in enumerate(hdr_cols) if "straight" in c), -1)
            out.append(l); continue
        if re.search(r"\\\\\s*$", l) and " & " in l and not l.startswith("Method"):
            block.append(l); continue
        flush(); out.append(l)
    flush()
    p.write_text(hdr("\n".join(out)))
