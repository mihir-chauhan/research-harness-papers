# Design
method/run.py: one entrypoint, all agents operate on arrays Q[K,R,S,A] (K tables, R=1000 replicas).
- q: target r + g max_a Q(s',a).
- double (van Hasselt 2010): per step pick table u uniformly; a*=argmax Q_u(s',.); target r+g Q_{1-u}(s',a*); act on (Q0+Q1)/2.
- double_both: update both tables every step (ablation).
- wdq (Zhang et al. 2017): a*=argmax Q_u, a_L=argmin Q_u, beta=|Q_o(s',a*)-Q_o(s',a_L)|/(c+|.|), c=1, target r+g[beta Q_u(s',a*)+(1-beta)Q_o(s',a*)].
- maxmin (Lan et al. 2020, N=2): act and bootstrap on min over tables: target r+g max_a' min_i Q_i(s',a'); one randomly chosen table updated.
Terminal transitions bootstrap 0. Ties broken by 1e-9 noise. Flags: --init true warm-starts at Q*, --epsilon, --alpha, --sigma, --n_actions.
Estimated start value = max_a of acting values (Q for q; mean for double family; min for maxmin).
