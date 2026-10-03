"""Propositional sequent calculus (G3cp-style, set contexts), tactics, random provable sequents, optimal-proof DP."""
import random
import sys

sys.setrecursionlimit(10000)
NVARS = 5
FULL = (1 << (1 << NVARS)) - 1
VARMASK = [sum(1 << r for r in range(1 << NVARS) if (r >> i) & 1) for i in range(NVARS)]


def key(f):
    return repr(f)


def size(f):  # number of connectives
    return 0 if f[0] == 'v' else 1 + sum(size(g) for g in f[1:])


def depth(f):
    return 0 if f[0] == 'v' else 1 + max(depth(g) for g in f[1:])


def atoms(f, acc=None):
    acc = set() if acc is None else acc
    if f[0] == 'v':
        acc.add(f[1])
    else:
        for g in f[1:]:
            atoms(g, acc)
    return acc


def tt(f):
    t = f[0]
    if t == 'v':
        return VARMASK[f[1]]
    if t == 'not':
        return FULL ^ tt(f[1])
    a, b = tt(f[1]), tt(f[2])
    if t == 'and':
        return a & b
    if t == 'or':
        return a | b
    return (FULL ^ a) | b


def valid(goal):
    L, R = goal
    lhs = FULL
    for f in L:
        lhs &= tt(f)
    rhs = 0
    for f in R:
        rhs |= tt(f)
    return (lhs & ~rhs & FULL) == 0


def mk(L, R):
    return (tuple(sorted(set(L), key=key)), tuple(sorted(set(R), key=key)))


def is_axiom(goal):
    L, R = goal
    la = {f[1] for f in L if f[0] == 'v'}
    return any(f[0] == 'v' and f[1] in la for f in R)


def candidates(goal):
    """Tactics = (side, index) of compound formulas; side 0 = left, 1 = right."""
    L, R = goal
    return [(0, i) for i, f in enumerate(L) if f[0] != 'v'] + [(1, i) for i, f in enumerate(R) if f[0] != 'v']


BRANCHING = {(0, 'or'), (0, 'imp'), (1, 'and')}


def branches(tac, goal):
    side, i = tac
    return (side, goal[side][i][0]) in BRANCHING


def apply(goal, tac):
    """Return list of subgoals (axioms already closed are NOT removed here)."""
    L, R = goal
    side, i = tac
    if side == 0:
        f = L[i]
        rest = L[:i] + L[i + 1:]
        if f[0] == 'not':
            return [mk(rest, R + (f[1],))]
        if f[0] == 'and':
            return [mk(rest + (f[1], f[2]), R)]
        if f[0] == 'or':
            return [mk(rest + (f[1],), R), mk(rest + (f[2],), R)]
        return [mk(rest, R + (f[1],)), mk(rest + (f[2],), R)]  # imp
    f = R[i]
    rest = R[:i] + R[i + 1:]
    if f[0] == 'not':
        return [mk(L + (f[1],), rest)]
    if f[0] == 'and':
        return [mk(L, rest + (f[1],)), mk(L, rest + (f[2],))]
    if f[0] == 'or':
        return [mk(L, rest + (f[1], f[2]))]
    return [mk(L + (f[1],), rest + (f[2],))]  # imp


def open_goals(goals):
    return [g for g in goals if not is_axiom(g)]


# ---------------- random generation ----------------
def rand_formula(rng, n):
    if n == 0:
        return ('v', rng.randrange(NVARS))
    op = rng.choice(['not', 'and', 'or', 'imp', 'and', 'or', 'imp'])
    if op == 'not':
        return ('not', rand_formula(rng, n - 1))
    k = rng.randint(0, n - 1)
    return (op, rand_formula(rng, k), rand_formula(rng, n - 1 - k))


def rand_sequent(rng, n):
    m = rng.randint(1, 3)
    n = max(n, m - 1 if False else 0)
    # split n connectives over m formulas
    cuts = sorted(rng.randint(0, n) for _ in range(m - 1))
    sizes = [b - a for a, b in zip([0] + cuts, cuts + [n])]
    fs = [rand_formula(rng, s) for s in sizes]
    sides = [rng.randint(0, 1) for _ in fs]
    if all(s == 0 for s in sides):
        sides[-1] = 1
    L = [f for f, s in zip(fs, sides) if s == 0]
    R = [f for f, s in zip(fs, sides) if s == 1]
    return mk(L, R)


def seq_size(g):
    return sum(size(f) for f in g[0] + g[1])


def subst(f, sub):
    if f[0] == 'v':
        return sub[f[1]]
    return (f[0],) + tuple(subst(g, sub) for g in f[1:])


def n_occ(g):
    cnt = {}
    def rec(f):
        if f[0] == 'v':
            cnt[f[1]] = cnt.get(f[1], 0) + 1
        else:
            for h in f[1:]:
                rec(h)
    for f in g[0] + g[1]:
        rec(f)
    return cnt


def rewrites(f):
    """All formulas equivalent to f obtained by one top-level equivalence rewrite."""
    t = f[0]
    out = []
    if t in ('and', 'or'):
        a, b = f[1], f[2]
        o = 'or' if t == 'and' else 'and'
        out.append((t, b, a))
        if b[0] == t:
            out.append((t, (t, a, b[1]), b[2]))
        if b[0] == o:
            out.append((o, (t, a, b[1]), (t, a, b[2])))
        if a[0] == o:
            out.append((o, (t, a[1], b), (t, a[2], b)))
        out.append(('not', (o, ('not', a), ('not', b))))
    if t == 'not':
        g = f[1]
        if g[0] == 'not':
            out.append(g[1])
        if g[0] in ('and', 'or'):
            o = 'or' if g[0] == 'and' else 'and'
            out.append((o, ('not', g[1]), ('not', g[2])))
        if g[0] == 'imp':
            out.append(('and', g[1], ('not', g[2])))
    if t == 'imp':
        a, b = f[1], f[2]
        out.append(('or', ('not', a), b))
        out.append(('imp', ('not', b), ('not', a)))
        if b[0] == 'and':
            out.append(('and', ('imp', a, b[1]), ('imp', a, b[2])))
        if a[0] == 'or':
            out.append(('and', ('imp', a[1], b), ('imp', a[2], b)))
    out.append(('not', ('not', f)))
    return out


def rewrite_at(rng, f):
    nodes = []
    def walk(g, path):
        nodes.append(path)
        for i, h in enumerate(g[1:], 1):
            if g[0] != 'v':
                walk(h, path + (i,))
    walk(f, ())
    path = rng.choice(nodes)
    def rec(g, p):
        if not p:
            return rng.choice(rewrites(g))
        i = p[0]
        return g[:i] + (rec(g[i], p[1:]),) + g[i + 1:]
    return rec(f, path)


def gen_one(rng, nmin, nmax, kind):
    """kind 0: rejection-sampled random valid sequent; 1: substitution instance of a small valid core;
    2: substitution instance plus 1-2 random distractor formulas (weakening)."""
    while True:
        if kind == 0:
            g = rand_sequent(rng, rng.randint(nmin, nmax))
            if not valid(g):
                continue
        elif kind == 3:
            f = rand_formula(rng, rng.randint(max(nmin // 3, 1), max(nmax // 2, 2)))
            h = f
            for _ in range(rng.randint(1, 4)):
                h = rewrite_at(rng, h)
            g = mk([f], [h])
            assert valid(g)
        else:
            while True:
                core = rand_sequent(rng, rng.randint(0, 4))
                if valid(core) and max(atoms_seq(core), default=-1) < 3:
                    break
            occ = n_occ(core)
            csz = seq_size(core)
            target = rng.randint(nmin, nmax)
            budget = max(target - csz - (3 if kind == 2 else 0), 0)
            vs = sorted(occ)
            sub = {}
            for v in vs:
                per = max(budget // max(sum(occ.values()), 1), 0)
                sub[v] = rand_formula(rng, rng.randint(0, max(2 * per, 0)))
            L = [subst(f, sub) for f in core[0]]
            R = [subst(f, sub) for f in core[1]]
            if kind == 2:
                for _ in range(rng.randint(1, 2)):
                    d = rand_formula(rng, rng.randint(1, 4))
                    (L if rng.random() < 0.5 else R).append(d)
            g = mk(L, R)
            assert valid(g)
        if is_axiom(g) or not (nmin <= seq_size(g) <= nmax):
            continue
        return g


def atoms_seq(g):
    a = set()
    for f in g[0] + g[1]:
        atoms(f, a)
    return a


def gen_provable(rng, nmin, nmax, count, exclude=()):
    out, seen = [], set(exclude)
    while len(out) < count:
        g = gen_one(rng, nmin, nmax, rng.randrange(4))
        if g in seen:
            continue
        seen.add(g)
        out.append(g)
    return out


# ---------------- optimal proof size DP ----------------
class Oracle:
    def __init__(self, cap=200000):
        self.memo = {}
        self.cap = cap

    def best(self, goal):
        """(min number of tactic applications, [optimal tactics]). inf if unprovable / cap hit."""
        if is_axiom(goal):
            return 0, []
        r = self.memo.get(goal)
        if r is not None:
            return r
        if len(self.memo) > self.cap:
            raise MemoryError
        cands = candidates(goal)
        costs = []
        for t in cands:
            c = 1
            for sg in apply(goal, t):
                c += self.best(sg)[0]
            costs.append(c)
        if not costs:
            r = (float('inf'), [])
        else:
            m = min(costs)
            r = (m, [t for t, c in zip(cands, costs) if c == m])
        self.memo[goal] = r
        return r


def collect_states(goal, oracle, rng, p_opt=0.5, maxstates=40):
    """Walk the proof tree; follow an optimal tactic w.p. p_opt, else a random one. Returns [(goal, optimal_tactics)]."""
    out, stack = [], [goal]
    while stack and len(out) < maxstates:
        g = stack.pop()
        if is_axiom(g):
            continue
        _, opt = oracle.best(g)
        if not opt:
            continue
        out.append((g, opt))
        t = rng.choice(opt) if rng.random() < p_opt else rng.choice(candidates(g))
        stack.extend(apply(g, t))
    return out
