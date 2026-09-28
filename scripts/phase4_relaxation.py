"""Binary-equivalent energy extensions, on development only."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch
from phase2_energy import load,load_model,project,score_sets,metrics,sha
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
LAMBDAS=[-4.,-1.,-.25,0.,.25,1.,4.]


def optimize(u,v,lam):
    rng=np.random.default_rng(91);init=np.zeros(20);init[np.argsort(-u,kind='stable')[:4]]=1
    starts=[np.full(20,.2),init,project(rng.normal(size=20)),project(rng.normal(size=20))]
    candidates=[];fractionality=[];t=time.perf_counter()
    for z in starts:
        candidates.append(np.sort(np.argsort(-z,kind='stable')[:4]))
        for _ in range(80):z=project(z+.3*(u+v@z-lam*(1-2*z)))
        fractionality.append(float(np.sum(z*(1-z))))
        candidates.append(np.sort(np.argsort(-z,kind='stable')[:4]))
    vals=score_sets(u,v,np.array(candidates));chosen=candidates[int(vals.argmax())]
    rounded=dict(selected=list(map(int,chosen)),score=float(vals.max()),discrete_scores=8,
                 selection_gradients=320,seconds=time.perf_counter()-t,
                 mean_fractionality=float(np.mean(fractionality)))
    t=time.perf_counter();value=float(vals.max());evaluations=0;moves=0
    for _ in range(10):
        neighbors=sorted({tuple(sorted((set(chosen)-{int(a)})|{b})) for a in chosen for b in range(20) if b not in chosen})
        vals=score_sets(u,v,np.array(neighbors));evaluations+=len(neighbors);i=int(vals.argmax())
        if vals[i]<=value+1e-7:break
        chosen=neighbors[i];value=float(vals[i]);moves+=1
    refined=dict(selected=list(map(int,chosen)),score=value,discrete_scores=8+evaluations,
                 selection_gradients=320,seconds=rounded['seconds']+time.perf_counter()-t,
                 mean_fractionality=rounded['mean_fractionality'],swaps=moves)
    return rounded,refined


def checks():
    rng=np.random.default_rng(55)
    binary=np.zeros(20);binary[[1,4,8,15]]=1
    assert sum(binary*(1-binary))==0
    z=torch.tensor(project(rng.normal(size=20)),requires_grad=True)
    lam=4.
    penalty=lam*torch.sum(z*(1-z))
    grad=torch.autograd.grad(penalty,z)[0].detach().numpy()
    np.testing.assert_allclose(grad,lam*(1-2*z.detach().numpy()),atol=1e-12)
    return dict(binary_energy_invariance=True,gradient_matches_autograd=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,default=ROOT/'phase4/runs/extension')
    args=parser.parse_args();out=args.out
    if out.exists():raise RuntimeError('Existing results')
    out.mkdir(parents=True)
    verified=checks()
    examples,labels,x,p,cost=load('development',True)
    model=load_model(ROOT/'phase2/runs/semantic-pairwise/checkpoint.json')
    with torch.no_grad():us,vs=model(torch.from_numpy(x),torch.from_numpy(p))
    original=json.loads((ROOT/'phase2/runs/semantic-development/outcomes.json').read_text())
    rows=[]
    for e,label,u,v in zip(examples,labels,us.numpy(),vs.numpy()):
        global_score=next(r['score'] for r in original if r['id']==e['id'] and r['arm']=='exact')
        base=next(r['selected'] for r in original if r['id']==e['id'] and r['arm']=='relaxed')
        base_refined=next(r['selected'] for r in original if r['id']==e['id'] and r['arm']=='relaxed_swap')
        for lam in LAMBDAS:
            rounded,refined=optimize(u,v,lam)
            for name,result,reference in [('rounded',rounded,base),('refined',refined,base_refined)]:
                if lam==0:assert sorted(result['selected'])==sorted(reference)
                rows.append(dict(id=e['id'],lam=lam,method=name,**result,
                     global_score_gap=global_score-result['score'],
                     changed_from_zero=sorted(result['selected'])!=sorted(reference),
                     **metrics(result['selected'],label['supports'])))
    summary={}
    for lam in LAMBDAS:
        summary[str(lam)]={}
        for method in ['rounded','refined']:
            group=[r for r in rows if r['lam']==lam and r['method']==method]
            summary[str(lam)][method]=dict(n=len(group),complete=sum(r['complete'] for r in group),
                   global_optima=sum(r['global_score_gap']<1e-5 for r in group),
                   changed_sets=sum(r['changed_from_zero'] for r in group),
                   mean_fractionality=float(np.mean([r['mean_fractionality'] for r in group])),
                   **{key:sum(r[key] for r in group) for key in ['discrete_scores','selection_gradients','seconds']})
    dump(out/'outcomes.json',rows);dump(out/'summary.json',summary)
    dump(out/'provenance.json',dict(script_sha256=sha(Path(__file__)),protocol_sha256=sha(ROOT/'phase4/PROTOCOL.md'),
           checkpoint_sha256=sha(ROOT/'phase2/runs/semantic-pairwise/checkpoint.json'),checks=verified,
           zero_extension_matches_phase2=True,representation=cost,
           actual_selection_gradients=len(examples)*len(LAMBDAS)*320,
           note='Refined counts include their rounded predecessor; do not double-count shared work.',
           source='Seen development, no new weights or encoder calls or reader calls',
           created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
