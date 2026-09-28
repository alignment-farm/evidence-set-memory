"""Frozen-energy scaling on augmented, already-seen natural-text development pools."""
import argparse
from collections import Counter
import itertools
import json
import math
from pathlib import Path
import time
import numpy as np
import torch
from phase2_energy import tokens,normalized,project,load_model,represent,sha,metrics
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]


def features(question,paragraphs,q,d,t):
    n=len(paragraphs);query=set(tokens(question))
    docs=[tokens(p['title']+' '+p['text']) for p in paragraphs]
    sets=list(map(set,docs));titles=[set(tokens(p['title'])) for p in paragraphs]
    df=Counter(w for s in sets for w in s);avg=sum(map(len,docs))/n
    relevance=[]
    for doc in docs:
        tf=Counter(doc)
        relevance.append(sum(math.log(1+(n-df[w]+.5)/(df[w]+.5))*tf[w]*2.2/
                         (tf[w]+1.2*(.25+.75*len(doc)/max(avg,1))) for w in query if tf[w]))
    relevance=np.array(relevance,dtype=np.float32)/max(max(relevance),1e-8)
    mention=np.zeros((n,n),dtype=np.float32);overlap=np.zeros_like(mention)
    bodies=[normalized(p['text']) for p in paragraphs]
    for i in range(n):
        title=normalized(paragraphs[i]['title']).split(' disambiguation')[0]
        for j in range(n):
            if i!=j:
                mention[i,j]=len(title)>2 and title in bodies[j]
                overlap[i,j]=len(titles[i]&sets[j])/max(1,len(titles[i]))
    x=np.array([[relevance[i],len(query&s)/max(1,len(query)),len(query&titles[i])/max(1,len(query)),
                 min(math.log1p(len(docs[i]))/7,1),
                 float(normalized(paragraphs[i]['title']) in normalized(question)),
                 float((mention[i].sum()+mention[:,i].sum())/(2*(n-1)))] for i,s in enumerate(sets)],dtype=np.float32)
    p=np.zeros((n,n,8),dtype=np.float32)
    for i in range(n):
        for j in range(i+1,n):
            p[i,j]=p[j,i]=[max(mention[i,j],mention[j,i]),(mention[i,j]+mention[j,i])/2,
                   max(overlap[i,j],overlap[j,i]),(overlap[i,j]+overlap[j,i])/2,
                   len(sets[i]&sets[j])/max(1,len(sets[i]|sets[j])),
                   min(relevance[i],relevance[j]),max(relevance[i],relevance[j]),
                   len(query&(sets[i]|sets[j]))/max(1,len(query))]
    return np.concatenate([x,(d@q)[:,None],(t@q)[:,None]],axis=-1),np.concatenate([p,(d@d.T)[...,None]],axis=-1)


def search(u,v,method):
    n=len(u);count=0;gradients=0;moves=0;started=time.perf_counter();cpu=time.process_time()
    def score(ss):
        nonlocal count
        arr=np.asarray(ss,dtype=int);count+=len(arr)
        values=u[arr].sum(1)
        for a,b in itertools.combinations(range(arr.shape[1]),2):values+=v[arr[:,a],arr[:,b]]
        return values
    if method=='exact':
        source=itertools.combinations(range(n),4);best=None;value=-np.inf
        while chunk:=list(itertools.islice(source,50000)):
            values=score(chunk);idx=int(values.argmax())
            if values[idx]>value:best=chunk[idx];value=float(values[idx])
    elif method=='beam':
        beam=[()]
        for depth in range(4):
            expanded=sorted({tuple(sorted((*s,i))) for s in beam for i in range(n) if i not in s})
            values=score(expanded)
            beam=[expanded[i] for i in np.argsort(-values,kind='stable')[:16]]
        best=beam[0];value=float(score([best])[0])
    elif method=='relaxed_swap':
        rng=np.random.default_rng(91)
        start=np.zeros(n);start[np.argsort(-u,kind='stable')[:4]]=1
        starts=[np.full(n,4/n),start,project(rng.normal(size=n)),project(rng.normal(size=n))]
        candidates=[]
        for z in starts:
            candidates.append(np.sort(np.argsort(-z,kind='stable')[:4]))
            for _ in range(80):z=project(z+.3*(u+v@z));gradients+=1
            candidates.append(np.sort(np.argsort(-z,kind='stable')[:4]))
        values=score(candidates);best=candidates[int(values.argmax())];value=float(values.max())
        for _ in range(10):
            neighbors=sorted({tuple(sorted((set(best)-{int(a)})|{b})) for a in best for b in range(n) if b not in best})
            values=score(neighbors);i=int(values.argmax())
            if values[i]<=value+1e-7:break
            best=neighbors[i];value=float(values[i]);moves+=1
    else:raise ValueError(method)
    return dict(selected=list(map(int,best)),score=value,score_evaluations=count,
                selection_gradients=gradients,swaps=moves,
                wall_seconds=time.perf_counter()-started,cpu_seconds=time.process_time()-cpu)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'phase3/runs/scaling')
    args=parser.parse_args();out=args.out
    if out.exists():raise RuntimeError('Write-once scaling run')
    out.mkdir(parents=True)
    examples=json.loads((ROOT/'.cache/phase2/partitions/development-inputs.json').read_text())
    labels=json.loads((ROOT/'.cache/phase2/partitions/development-labels.json').read_text())
    cached=np.load(ROOT/'.cache/phase2/semantic/development.npz')
    model=load_model(ROOT/'phase2/runs/semantic-pairwise/checkpoint.json')
    rng=np.random.default_rng(123)
    rows=[];pools=[]
    for index in range(12,16):
        e=examples[index]
        refs=[(index,j) for j in range(20)]
        seen={(p['title'],p['text']) for p in e['paragraphs']}
        extras=[(i,j) for i in range(len(examples)) if i!=index for j in range(20)]
        rng.shuffle(extras)
        for i,j in extras:
            p=examples[i]['paragraphs'][j];key=(p['title'],p['text'])
            if key in seen:continue
            seen.add(key);refs.append((i,j))
            if len(refs)==160:break
        for n in [20,40,80,160]:
            subset=refs[:n];pars=[examples[i]['paragraphs'][j] for i,j in subset]
            d=np.stack([cached['documents'][i,j] for i,j in subset]);t=np.stack([cached['titles'][i,j] for i,j in subset])
            before=time.perf_counter();x,p=features(e['question'],pars,cached['query'][index],d,t)
            feature_seconds=time.perf_counter()-before
            if n==20:
                original_x,original_p=represent(e)
                np.testing.assert_allclose(x[:,:6],original_x,rtol=1e-6,atol=1e-7)
                np.testing.assert_allclose(p[:,:,:8],original_p,rtol=1e-6,atol=1e-7)
            before=time.perf_counter()
            with torch.no_grad():
                u=model.unary(torch.from_numpy(x)).squeeze(-1).numpy()/4
                v=model.pair(torch.from_numpy(p)).squeeze(-1).numpy()/6
            np.fill_diagonal(v,0)
            forward_seconds=time.perf_counter()-before
            pools.append(dict(id=e['id'],n=n,records=[dict(question_id=examples[i]['id'],idx=j,
                         text_sha256=__import__('hashlib').sha256((examples[i]['paragraphs'][j]['title']+'\n'+examples[i]['paragraphs'][j]['text']).encode()).hexdigest()) for i,j in subset]))
            answers={method:search(u,v,method) for method in ['exact','beam','relaxed_swap']}
            for method,result in answers.items():
                rows.append(dict(id=e['id'],n=n,method=method,**result,
                       global_score_gap=answers['exact']['score']-result['score'],
                       feature_seconds=feature_seconds,coefficient_forward_seconds=forward_seconds,
                       **metrics(result['selected'],labels[index]['supports'])))
            dump(out/'outcomes.json',rows);dump(out/'pool-lineage.json',pools)
            print(json.dumps(dict(id=e['id'],n=n,results={k:{f:v[f] for f in ['wall_seconds','score_evaluations','score']} for k,v in answers.items()})),flush=True)
    summary={}
    for n in [20,40,80,160]:
        summary[str(n)]={}
        for method in ['exact','beam','relaxed_swap']:
            group=[r for r in rows if r['n']==n and r['method']==method]
            summary[str(n)][method]=dict(cases=len(group),global_optima=sum(r['global_score_gap']<1e-5 for r in group),
               complete=sum(r['complete'] for r in group),**{k:sum(r[k] for r in group) for k in
                 ['wall_seconds','cpu_seconds','score_evaluations','selection_gradients','swaps']})
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',dict(script_sha256=sha(Path(__file__)),
           protocol_sha256=sha(ROOT/'phase3/PROTOCOL.md'),checkpoint_sha256=sha(ROOT/'phase2/runs/semantic-pairwise/checkpoint.json'),
           new_encoder_calls=0,new_training_updates=0,reader_calls=0,source_split='seen development indices 12:16',
           concurrent_work='Phase-2 serial reader on same host; timing is illustrative, not isolated benchmark',
           created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
