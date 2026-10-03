"""Expands <<A key prec>> and <<V group|name metric stat prec>> shorthands in paper/drafts/*.txt into \\rhval calls (paper/sections/*.tex)."""
import re, sys, glob, os
T = "physionet2012_mortality"; slug = lambda s: re.sub(r"[^a-z0-9+]+", "-", s.lower()).strip("-")
def rep(m):
    a = m.group(1).split()
    if a[0] == "A": return "\\rhval{analysis/paired-analysis-v2/%s/%s/mean:%s}" % (T, a[1], a[2])
    g, n = m.group(1)[2:].split(" ")[0].split("|"); rest = m.group(1)[2:].split(" ")
    return None
def conv(s):
    def f(m):
        body = m.group(1).strip()
        if body.startswith("A "):
            _, k, p = body.split(); return "\\rhval{analysis/paired-analysis-v2/%s/%s/mean:%s}" % (T, k, p)
        if body.startswith("V "):
            head, tail = body[2:].split(" ", 1); mm = tail.split()
            g, n = head.split("|"); n = n.replace("_", " ")
            return "\\rhval{%s/%s/%s/%s/%s:%s}" % (g, slug(n), T, mm[0], mm[1], mm[2])
        raise ValueError(body)
    return re.sub(r"<<(.*?)>>", f, s)
for p in glob.glob("paper/drafts/*.txt"):
    open("paper/sections/" + os.path.basename(p)[:-4] + ".tex", "w").write(conv(open(p).read()))
