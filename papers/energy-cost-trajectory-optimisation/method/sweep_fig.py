"""Figures from the run registry: main-group control effort, and success / effort vs weight for the two swept costs.
Error bars are the sample std (ddof=1) over seeds, the same convention as the tables."""
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open('results/runs.jsonl')]
rows = [r for r in rows if r['status'] == 'ok']
TASKS = (('pendulum', 'pendulum'), ('cartpole', 'cart-pole'))
C = {'iLQR-Energy (ours)': '#d55e00', 'iLQR-Quad': '#0072b2', 'iLQR-Quad+Energy': '#009e73', 'EnergyShaping-LQR': '#7f7f7f'}

# main group: control effort per system and task
fig, axs = plt.subplots(1, 2, figsize=(3.5, 2.2))
names = ['iLQR-Quad', 'iLQR-Quad+Energy', 'iLQR-Energy (ours)', 'EnergyShaping-LQR']; short = ['Quad', 'Quad+E', 'Energy', 'E-shaping']
for ax, (t, tl) in zip(axs, TASKS):
    for i, n in enumerate(names):
        v = [r['metrics']['control_effort'] for r in rows if r['group'] == 'main' and r['task'] == t and r['name'] == n]
        assert len(v) == 5
        ax.bar(i, np.mean(v), yerr=np.std(v, ddof=1), color=C[n], capsize=2, width=0.7)
    ax.set_xticks(range(4)); ax.set_xticklabels(short, rotation=40, ha='right', fontsize=7); ax.set_title(tl, fontsize=8)
    ax.tick_params(axis='y', labelsize=7)
axs[0].set_ylabel('control effort', fontsize=8)
fig.tight_layout(); fig.savefig('results/figures/main_effort.pdf'); plt.close(fig)

# sweeps: both costs on one axis per task (x = w_E for the energy cost, q for the quadratic cost)
for metric, ylab, name in (('success_rate', 'success rate', 'sweep_success'), ('control_effort', 'control effort', 'sweep_effort')):
    fig, axs = plt.subplots(1, 2, figsize=(3.5, 2.2))
    for ax, (t, tl) in zip(axs, TASKS):
        for g, p, n, mk, lab in (('sweep_wE', 'wE', 'iLQR-Energy (ours)', 'o-', 'Energy ($w_E$)'), ('sweep_qscale', 'qscale', 'iLQR-Quad', 's--', 'Quad ($q$)')):
            ws = sorted({r['config'][p] for r in rows if r['group'] == g})
            m, s = [], []
            for w in ws:
                v = [r['metrics'][metric] for r in rows if r['group'] == g and r['task'] == t and r['config'][p] == w]
                assert len(v) == 3
                m.append(np.mean(v)); s.append(np.std(v, ddof=1))
            ax.errorbar(ws, m, yerr=s, fmt=mk, color=C[n], capsize=2, markersize=3, linewidth=1, label=lab)
        ax.set_xscale('log'); ax.set_xticks([0.01, 1, 100]); ax.set_title(tl, fontsize=8); ax.set_xlabel('weight', fontsize=8)
        ax.tick_params(labelsize=7)
        if metric == 'success_rate': ax.set_ylim(0.6, 1.03)
    axs[0].set_ylabel(ylab, fontsize=8); axs[1].legend(fontsize=6, loc='lower right' if metric == 'success_rate' else 'upper left')
    fig.tight_layout(); fig.savefig(f'results/figures/{name}.pdf'); plt.close(fig)
