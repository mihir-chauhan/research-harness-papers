"""Best-first proof search over proof states (lists of open goals). One expansion = one popped state; its
children are the states reached by every tactic applicable to the state's first open goal. Goals closed by the
axiom rule are removed for free when a state is created."""
import heapq
import math
from logic import candidates, apply, open_goals, branches, size


def heuristic_costs(goal, variant):
    """Hand-written tactic ranking: non-branching rules first; ties by formula size (variant 'small') or
    by size descending ('large'); variant 'fifo' keeps formula order. Cost = rank of the tactic."""
    c = candidates(goal)
    if variant == 'small':
        k = lambda t: (branches(t, goal), size(goal[t[0]][t[1]]))
    elif variant == 'large':
        k = lambda t: (branches(t, goal), -size(goal[t[0]][t[1]]))
    elif variant == 'right':
        k = lambda t: (branches(t, goal), -t[0], size(goal[t[0]][t[1]]))
    else:
        raise ValueError(variant)
    order = sorted(c, key=k)
    return [(t, float(r)) for r, t in enumerate(order)]


def prove(goal, cost_fn, budget=100, mode='bestfirst'):
    """cost_fn(goal) -> list[(tactic, step_cost)] (step_cost >= 0, lower = tried earlier).
    mode 'bfs': ignore costs, FIFO by depth. mode 'bestfirst': priority = cumulative cost, ties -> deeper first.
    mode 'greedy': follow the single cheapest tactic (no backtracking; fails if budget runs out).
    Returns (solved, expansions)."""
    start = open_goals([goal])
    if not start:
        return True, 0
    counter = 0
    heap = [(0.0, 0, 0, start)]
    exp = 0
    while heap and exp < budget:
        pr, nd, _, goals = heapq.heappop(heap)
        exp += 1
        g = goals[0]
        tacs = cost_fn(g) if mode != 'bfs' else [(t, 0.0) for t in candidates(g)]
        if mode == 'greedy' and tacs:
            tacs = [min(tacs, key=lambda x: x[1])]
        for t, c in tacs:
            child = open_goals(apply(g, t)) + goals[1:]
            if not child:
                return True, exp
            counter += 1
            depth = -nd + 1
            if mode == 'bfs':
                p = float(depth)
            else:
                p = pr + c
            heapq.heappush(heap, (p, -depth, counter, child))
    return False, exp


def policy_cost_fn(score_fn, cost='nll'):
    """score_fn(goal) -> list of logits aligned with candidates(goal). Step cost = -log softmax."""
    cache = {}
    def f(goal):
        r = cache.get(goal)
        if r is None:
            c = candidates(goal)
            lg = score_fn(goal)
            m = max(lg)
            z = math.log(sum(math.exp(x - m) for x in lg)) + m
            if cost == 'nll':
                r = [(t, z - x) for t, x in zip(c, lg)]
            else:  # 'rank': rank of the tactic under the policy (same cost scale as the hand heuristic)
                order = sorted(range(len(c)), key=lambda i: -lg[i])
                rk = {i: r_ for r_, i in enumerate(order)}
                r = [(t, float(rk[i])) for i, t in enumerate(c)]
            cache[goal] = r
        return r
    return f
