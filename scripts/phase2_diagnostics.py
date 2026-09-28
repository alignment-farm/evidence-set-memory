"""Acquisition and inference audit using development/training only."""
import json
from pathlib import Path
import time
import numpy as np
import torch
from phase2_energy import load,load_model,Energy,search,metrics,make_attempts,scores,sha
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'phase2/runs/acquisition-audit.json'
if out.exists(): raise RuntimeError('Existing audit')
torch.manual_seed(23);initial=Energy(True)
learned=load_model(ROOT/'phase2/runs/pairwise-seed23/checkpoint.json')
rows=[];cost={};start=time.perf_counter()
for split in ['train','development']:
    examples,labels,x,p,rep=load(split);cost[split]=rep
    for name,model in [('initial',initial),('learned',learned)]:
        with torch.no_grad():u,v=model(torch.from_numpy(x),torch.from_numpy(p))
        complete=0;recall=0
        for example,label,uu,vv in zip(examples,labels,u.numpy(),v.numpy()):
            selected,_=search(uu,vv,'exact')
            m=metrics(selected,label['supports']);complete+=m['complete'];recall+=m['recall']
        record=dict(split=split,model=name,n=len(examples),complete=complete,mean_recall=recall/len(examples))
        if split=='train':
            zp,zn=make_attempts(labels,x,p)
            with torch.no_grad():diff=scores(u,v,torch.from_numpy(zp))-scores(u,v,torch.from_numpy(zn))
            record['pair_order_accuracy']=float((diff>0).float().mean())
            record['margin_satisfied']=float((diff>1).float().mean())
        rows.append(record)
dump(out,dict(rows=rows,cost=cost,wall_seconds=time.perf_counter()-start,
               diagnostics='same acquisition pairs plus development; not fresh evaluation',
               script_sha256=sha(Path(__file__))))
print(out.read_text())
