"""Paired tests for the stochastic-maze n-sweep (cum_reward), built from results/runs.jsonl. Writes results/tables/tests_stochastic_n.csv"""
import json, numpy as np, pandas as pd
from scipy import stats
rows=[json.loads(l) for l in open("results/runs.jsonl")]
rows=[r for r in rows if r["status"]=="ok" and r["task"]=="stochastic"]
def vec(group,name,n=None):
    d={r["seed"]:r["metrics"]["cum_reward"] for r in rows if r["group"]==group and r["name"]==name and (n is None or r["config"].get("n")==n) and r["seed"]<10}
    return np.array([d[s] for s in range(10)])
q=vec("main","Q-learning"); out=[]
for sysn in ["Dyna-Q","Dyna-Q+","Prioritized sweeping"]:
    base=vec("sweep_n",sysn,1)
    for n in [1,5,20,50,100]:
        x=vec("sweep_n",sysn,n)
        out.append(dict(system=sysn,n=n,mean=x.mean(),std=x.std(ddof=1),q_mean=q.mean(),q_std=q.std(ddof=1),
          p_vs_q=stats.ttest_rel(x,q).pvalue,p_vs_n1=stats.ttest_rel(x,base).pvalue if n>1 else np.nan,n_seeds=10))
pd.DataFrame(out).to_csv("results/tables/tests_stochastic_n.csv",index=False)
print(pd.DataFrame(out).round(4).to_string())
