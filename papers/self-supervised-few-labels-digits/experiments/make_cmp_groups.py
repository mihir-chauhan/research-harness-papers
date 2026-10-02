"""Paired-comparison groups for Table "Additional paired comparisons" (run once, from the project root).

`rh compare` compares systems inside one group against one reference. This lists existing runs a second time
in four cmp_* groups with `rh log --from-run` (metrics and provenance are copied from the registry, nothing is
typed and nothing is run again), after which:
  rh compare --group cmp_aug      --metric test_acc --ref "SimCLR-style probe"
  rh compare --group cmp_supaug   --metric test_acc --ref "Supervised + aug"
  rh compare --group cmp_rotation --metric test_acc --ref "Rotation (reimplemented)"
  rh compare --group cmp_random   --metric test_acc --ref "Random CNN + probe"
"""
import json, subprocess, sys
rows=[json.loads(l) for l in open('results/runs.jsonl')]
ok=[r for r in rows if r['status']=='ok']
plan={'cmp_aug':[('abl_aug','SimCLR geom-only'),('abl_aug','SimCLR photo-only'),('main','SimCLR-style probe')],
      'cmp_supaug':[('abl_supaug','Supervised + aug'),('main','Supervised scratch'),('main','SimCLR-style probe')],
      'cmp_rotation':[('main','Rotation (reimplemented)'),('main','PCA + LR'),('main','Random CNN + probe')],
      'cmp_random':[('main','Random CNN + probe'),('main','PCA + LR'),('main','Pixels + LR')]}
have={(r['group'],r['name'],r['task'],r['seed']) for r in ok}
n=0
for g,srcs in plan.items():
    for sg,name in srcs:
        for r in sorted([r for r in ok if r['group']==sg and r['name']==name], key=lambda r:(r['task'],r['seed'])):
            if (g,name,r['task'],r['seed']) in have: continue
            subprocess.run(['rh','log','--from-run',r['run_id'],'--kind',r['kind'],'--name',name,'--group',g,'--task',r['task'],'--seed',str(r['seed'])],check=True,stdout=subprocess.DEVNULL)
            n+=1
print('copied',n)
