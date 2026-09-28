"""Natural-text neural set energy and exact/relaxed inference, CPU only."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import re
import time
import numpy as np
import torch
from torch import nn
from phase2_assets import dump

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'.cache/phase2/partitions'
STOP = set('a an the of in on to for by and or is was were are be been it its this that which what who when where how did does do has have had from with at as into their his her they he she also after before'.split())
UNARY_NAMES = ['bm25','query_coverage','query_title_coverage','length','title_in_query','bridge_degree']
PAIR_NAMES = ['title_mention_max','title_mention_mean','title_overlap_max','title_overlap_mean',
              'token_jaccard','min_bm25','max_bm25','query_union_coverage']
COMBOS = np.array(list(itertools.combinations(range(20),4)), dtype=np.int64)
PAIR_POS = list(itertools.combinations(range(4),2))
torch.set_num_threads(2)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(text):
    return [s for s in re.findall(r'[a-z0-9]+',text.lower()) if s not in STOP]


def normalized(text):
    return ' '.join(re.findall(r'[a-z0-9]+',text.lower()))


def represent(example):
    """Visible fields only; no labels, decomposition, original retrieval rank/score."""
    paragraphs = example['paragraphs']
    assert len(paragraphs)==20
    q = set(tokens(example['question']))
    docs = [tokens(p['title']+' '+p['text']) for p in paragraphs]
    sets = list(map(set,docs))
    titles = [set(tokens(p['title'])) for p in paragraphs]
    df = Counter(t for d in sets for t in d)
    avglen = sum(map(len,docs))/20
    scores=[]
    for d in docs:
        tf = Counter(d)
        scores.append(sum(math.log(1+(20-df[t]+.5)/(df[t]+.5))*tf[t]*2.2/
                          (tf[t]+1.2*(.25+.75*len(d)/max(avglen,1))) for t in q if tf[t]))
    scores = np.array(scores,dtype=np.float32)/max(max(scores),1e-8)
    mention = np.zeros((20,20),dtype=np.float32)
    overlap = np.zeros_like(mention)
    for i in range(20):
        for j in range(20):
            if i!=j:
                title = normalized(paragraphs[i]['title']).split(' disambiguation')[0]
                mention[i,j] = len(title)>2 and title in normalized(paragraphs[j]['text'])
                overlap[i,j] = len(titles[i]&sets[j])/max(1,len(titles[i]))
    unary = np.array([[scores[i],len(q&s)/max(1,len(q)),len(q&titles[i])/max(1,len(q)),
                       min(math.log1p(len(docs[i]))/7,1),
                       float(normalized(paragraphs[i]['title']) in normalized(example['question'])),
                       float((mention[i].sum()+mention[:,i].sum())/38)] for i,s in enumerate(sets)],dtype=np.float32)
    pair = np.zeros((20,20,len(PAIR_NAMES)),dtype=np.float32)
    for i in range(20):
        for j in range(i+1,20):
            pair[i,j]=pair[j,i]=[max(mention[i,j],mention[j,i]),(mention[i,j]+mention[j,i])/2,
                                 max(overlap[i,j],overlap[j,i]),(overlap[i,j]+overlap[j,i])/2,
                                 len(sets[i]&sets[j])/max(1,len(sets[i]|sets[j])),
                                 min(scores[i],scores[j]),max(scores[i],scores[j]),
                                 len(q&(sets[i]|sets[j]))/max(1,len(q))]
    return unary,pair


def load(split,semantic=False):
    manifest=json.loads((ROOT/f'phase2/data/{split}-manifest.json').read_text())
    inp=DATA/f'{split}-inputs.json'
    lab=DATA/f'{split}-labels.json'
    assert sha(inp)==manifest['inputs_sha256'] and sha(lab)==manifest['labels_sha256']
    examples=json.loads(inp.read_text())
    labels=json.loads(lab.read_text())
    eligible=[i for i,e in enumerate(examples) if len(e['paragraphs'])==20]
    excluded=[e['id'] for e in examples if len(e['paragraphs'])!=20]
    examples=[examples[i] for i in eligible];labels=[labels[i] for i in eligible]
    t=time.perf_counter()
    features=[represent(e) for e in examples]
    cost=dict(seconds=time.perf_counter()-t,questions=len(examples),paragraphs=20*len(examples),
              input_bytes=inp.stat().st_size,unary_rows=20*len(examples),pair_rows=190*len(examples),
              excluded_non20_ids=excluded)
    x=np.stack([f[0] for f in features]);p=np.stack([f[1] for f in features])
    if semantic:
        semantic_start=time.perf_counter()
        encoding=json.loads((ROOT/f'phase2/runs/encoding-{split}.json').read_text())
        assert sha(ROOT/f'.cache/phase2/semantic/{split}.npz')==encoding['embeddings_sha256']
        cached=np.load(ROOT/f'.cache/phase2/semantic/{split}.npz')
        assert list(cached['ids'])==[e['id'] for e in examples]
        q,d,titles=cached['query'],cached['documents'],cached['titles']
        sim=np.einsum('bi,bni->bn',q,d);tsim=np.einsum('bi,bni->bn',q,titles)
        x=np.concatenate([x,sim[...,None],tsim[...,None]],axis=-1)
        p=np.concatenate([p,np.einsum('bni,bmi->bnm',d,d)[...,None]],axis=-1)
        cost['encoder_cost_ledger']=f'phase2/runs/encoding-{split}.json'
        cost['semantic_feature_seconds']=time.perf_counter()-semantic_start
    return examples,labels,x,p,cost


class Energy(nn.Module):
    def __init__(self,pairwise=True,semantic=False):
        super().__init__()
        self.pairwise=pairwise
        self.semantic=semantic
        self.unary=nn.Sequential(nn.Linear(8 if semantic else 6,32),nn.Tanh(),nn.Linear(32,1))
        self.pair=nn.Sequential(nn.Linear(9 if semantic else 8,32),nn.Tanh(),nn.Linear(32,1)) if pairwise else None

    def forward(self,x,p):
        u=self.unary(x).squeeze(-1)/4
        if self.pair is None:
            v=torch.zeros((*u.shape,u.shape[-1]),device=u.device)
        else:
            v=self.pair(p).squeeze(-1)/6
            v=v*(1-torch.eye(20,device=u.device))
        return u,v


def scores(u,v,z):
    return torch.einsum('bkn,bn->bk',z,u)+.5*torch.einsum('bki,bij,bkj->bk',z,v,z)


def ordinary(u,p,weight=0.):
    # Greedy query relevance plus title-supported complement, diminishing redundancy.
    selected=[]
    if u.shape[-1]>6:
        sim=u[:,6];sim=(sim-sim.min())/max(float(sim.max()-sim.min()),1e-8)
    else:sim=u[:,0]
    for _ in range(4):
        def score(i):
            link=max((p[i,j,0] for j in selected),default=0.)
            repeat=max((p[i,j,4] for j in selected),default=0.)
            return float(.5*u[i,0]+.5*sim[i]+.25*u[i,2]+weight*link-.15*repeat)
        selected.append(max((i for i in range(20) if i not in selected),key=lambda i:(score(i),-i)))
    return sorted(selected)


def make_attempts(labels,x,p,seed=22):
    rng=random.Random(seed)
    positives=[]; negatives=[]; pair_counts=[]
    for label,xx,pp in zip(labels,x,p):
        support=set(label['supports'])
        assert 1<=len(support)<=4
        neg=[]; pos=[]
        for k in range(32):
            gold=list(support)+rng.sample([i for i in range(20) if i not in support],4-len(support))
            if k<8:
                candidate=rng.sample(range(20),4)
            elif k<12:
                candidate=ordinary(xx,pp,[0,.25,.5,1][k-8])
            else:
                candidate=gold[:]
                candidate[candidate.index(rng.choice(sorted(support)))]=rng.choice([i for i in range(20) if i not in gold])
            # Complete sets aren't negative. Replace using known TRAINING annotations only.
            if support.issubset(candidate):
                candidate=gold[:]
                candidate[candidate.index(rng.choice(sorted(support)))]=rng.choice([i for i in range(20) if i not in gold])
            pos.append(np.eye(20,dtype=np.float32)[gold].sum(0))
            neg.append(np.eye(20,dtype=np.float32)[candidate].sum(0))
        positives.append(pos); negatives.append(neg)
    return np.array(positives),np.array(negatives)


def score_sets(u,v,sets):
    result=u[sets].sum(1)
    for i,j in PAIR_POS:
        result=result+v[sets[:,i],sets[:,j]]
    return result


def project(z,k=4):
    low=float(z.min()-1); high=float(z.max())
    for _ in range(35):
        mid=(low+high)/2
        if np.clip(z-mid,0,1).sum()>k: low=mid
        else: high=mid
    return np.clip(z-(low+high)/2,0,1)


def search(u,v,mode,seed=91):
    t=time.perf_counter(); count=0; gradients=0; accepted=0
    def score(ids):
        nonlocal count
        count+=len(ids)
        return score_sets(u,v,np.asarray(ids,dtype=int))
    if mode=='exact':
        values=score(COMBOS); best=COMBOS[int(values.argmax())]
    elif mode=='beam':
        beam=[()]
        for depth in range(4):
            expansions=sorted({tuple(sorted((*s,i))) for s in beam for i in range(20) if i not in s})
            values=[]
            for s in expansions:
                count+=1
                values.append(sum(u[i] for i in s)+sum(v[i,j] for i,j in itertools.combinations(s,2)))
            beam=[expansions[i] for i in np.argsort(-np.array(values),kind='stable')[:16]]
        best=np.array(beam[0])
    elif mode in ['relaxed','relaxed_swap']:
        rng=np.random.default_rng(seed)
        init=np.zeros(20); init[np.argsort(-u,kind='stable')[:4]]=1
        starts=[np.full(20,.2),init,project(rng.normal(size=20)),project(rng.normal(size=20))]
        candidates=[]
        for z in starts:
            candidates.append(np.sort(np.argsort(-z,kind='stable')[:4]))
            for step in range(80):
                # Analytic gradient of score, equivalent to autograd (tested separately).
                grad=u+v@z
                gradients+=1
                z=project(z+.3*grad)
            candidates.append(np.sort(np.argsort(-z,kind='stable')[:4]))
        vals=score(candidates); best=np.array(candidates[int(vals.argmax())])
        if mode=='relaxed_swap':
            value=float(vals.max())
            for _ in range(10):
                neighbors=sorted({tuple(sorted((set(best)-{int(a)})|{b})) for a in best for b in range(20) if b not in best})
                vals=score(neighbors); j=int(vals.argmax())
                if vals[j]<=value+1e-7: break
                best=np.array(neighbors[j]); value=float(vals[j]); accepted+=1
    else: raise ValueError(mode)
    return list(map(int,best)),dict(score_evaluations=count,selection_gradients=gradients,
                                    accepted_swaps=accepted,seconds=time.perf_counter()-t)


def metrics(selected,support):
    common=len(set(selected)&set(support))
    return dict(complete=int(set(support).issubset(selected)),recall=common/len(support),
                support_f1=2*common/(len(selected)+len(support)))


def train(out,pairwise=True,seed=11,epochs=60,semantic=False):
    if out.exists(): raise RuntimeError('Write-once run')
    out.mkdir(parents=True)
    torch.manual_seed(seed)
    ex,labels,x,p,rep=load('train',semantic)
    dev,dl,dx,dp,drep=load('development',semantic)
    zpos,zneg=make_attempts(labels,x,p)
    X,P,ZP,ZN=map(torch.from_numpy,[x,p,zpos,zneg])
    target=torch.tensor([[int(i in l['supports']) for i in range(20)] for l in labels],dtype=torch.float32)
    model=Energy(pairwise,semantic)
    optimizer=torch.optim.AdamW(model.parameters(),lr=.01,weight_decay=.001)
    best=-1.; history=[]; t=time.perf_counter(); cpu=time.process_time()
    for epoch in range(epochs):
        rng=np.random.default_rng(seed+epoch)
        order=rng.permutation(len(ex)); loss_sum=0.
        for offset in range(0,len(ex),16):
            ids=order[offset:offset+16]
            u,v=model(X[ids],P[ids])
            pos=scores(u,v,ZP[ids]); neg=scores(u,v,ZN[ids])
            ranking=torch.nn.functional.softplus(1-pos+neg).mean()
            bce=torch.nn.functional.binary_cross_entropy_with_logits(u*4,target[ids],pos_weight=torch.tensor(4.))
            loss=ranking+.25*bce
            optimizer.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),5)
            optimizer.step(); loss_sum+=float(loss.detach())
        if epoch in [0,4,9,19,39,59,epochs-1]:
            with torch.no_grad():
                uu,vv=model(torch.from_numpy(dx),torch.from_numpy(dp))
            uu,vv=uu.numpy(),vv.numpy()
            complete=[]; recalls=[]
            for a,b,l in zip(uu,vv,dl):
                selected,_=search(a,b,'exact')
                metric=metrics(selected,l['supports']); complete.append(metric['complete']); recalls.append(metric['recall'])
            record=dict(epoch=epoch+1,loss=loss_sum/math.ceil(len(ex)/16),development_complete=sum(complete),
                        development_n=len(dev),development_recall=float(np.mean(recalls)))
            history.append(record); print(json.dumps(record),flush=True)
            criterion=sum(complete)+float(np.mean(recalls))*.1
            if criterion>best:
                best=criterion
                dump(out/'checkpoint.json',dict(pairwise=pairwise,semantic=semantic,seed=seed,epoch=epoch+1,
                     state={k:v.detach().tolist() for k,v in model.state_dict().items()}))
        dump(out/'history.json',history)
    dump(out/'costs.json',dict(representation=rep,development_representation=drep,
         train_wall_seconds=time.perf_counter()-t,train_cpu_seconds=time.process_time()-cpu,
         epochs=epochs,optimizer_updates=epochs*math.ceil(len(ex)/16),
         training_questions=len(ex),set_contrasts=len(ex)*32,
         contrast_presentations=epochs*len(ex)*32,parameter_count=sum(v.numel() for v in model.parameters()),
         torch=torch.__version__,numpy=np.__version__,device='cpu',threads=2,seed=seed,
         code_sha256=sha(Path(__file__)),created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))


def load_model(path):
    cp=json.loads(path.read_text()); model=Energy(cp['pairwise'],cp.get('semantic',False))
    model.load_state_dict({k:torch.tensor(v) for k,v in cp['state'].items()})
    model.eval(); return model


def evaluate(split,out,checkpoint,unary_checkpoint,ordinary_weight=None):
    if split=='confirmation':
        frozen=json.loads((ROOT/'phase2/freeze.json').read_text())
        for file,checksum in frozen['files'].items():
            assert sha(ROOT/file)==checksum,file
    if out.exists(): raise RuntimeError('Write-once run')
    out.mkdir(parents=True)
    model=load_model(checkpoint); unary=load_model(unary_checkpoint)
    examples,labels,x,p,representation=load(split,model.semantic)
    forward_start=time.perf_counter()
    with torch.no_grad():us,vs=model(torch.from_numpy(x),torch.from_numpy(p))
    representation['pairwise_forward_seconds']=time.perf_counter()-forward_start
    forward_start=time.perf_counter()
    with torch.no_grad():pu,_=unary(torch.from_numpy(x),torch.from_numpy(p))
    representation['unary_forward_seconds']=time.perf_counter()-forward_start
    us,vs,pu=us.numpy(),vs.numpy(),pu.numpy()
    weights=[0.,.25,.5,1.] if ordinary_weight is None else [ordinary_weight]
    rows=[]
    for e,l,xx,pp,u,v,plain in zip(examples,labels,x,p,us,vs,pu):
        options={}
        for weight in weights:
            t=time.perf_counter(); selected=ordinary(xx,pp,weight)
            options[f'ordinary_{weight}']=(selected,dict(score_evaluations=74,selection_gradients=0,accepted_swaps=0,seconds=time.perf_counter()-t))
        options['learned_unary']=(list(map(int,np.argsort(-plain,kind='stable')[:4])),dict(score_evaluations=20,selection_gradients=0,accepted_swaps=0,seconds=0))
        for mode in ['exact','beam','relaxed','relaxed_swap']:
            options[mode]=search(u,v,mode)
        maximum=score_sets(u,v,np.array([options['exact'][0]]))[0]
        for arm,(selected,cost) in options.items():
            actual=score_sets(u,v,np.array([selected]))[0]
            rows.append(dict(id=e['id'],arm=arm,selected=selected,score=float(actual),
                 score_gap=float(maximum-actual),**metrics(selected,l['supports']),**cost))
    summary={}
    for arm in sorted({r['arm'] for r in rows}):
        group=[r for r in rows if r['arm']==arm]
        summary[arm]=dict(n=len(group),complete=sum(r['complete'] for r in group),
                         mean_recall=float(np.mean([r['recall'] for r in group])),
                         optimal_score=sum(r['score_gap']<1e-5 for r in group),
                         **{k:sum(r[k] for r in group) for k in ['score_evaluations','selection_gradients','accepted_swaps','seconds']})
    dump(out/'outcomes.json',rows);dump(out/'summary.json',summary)
    dump(out/'representation.json',representation)
    print(json.dumps(summary,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['train','evaluate'])
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--unary',action='store_true')
    parser.add_argument('--semantic',action='store_true')
    parser.add_argument('--seed',type=int,default=11)
    parser.add_argument('--epochs',type=int,default=60)
    parser.add_argument('--split',default='development',choices=['train','development','confirmation'])
    parser.add_argument('--checkpoint',type=Path)
    parser.add_argument('--unary-checkpoint',type=Path)
    parser.add_argument('--ordinary-weight',type=float)
    args=parser.parse_args()
    if args.command=='train': train(args.out,not args.unary,args.seed,args.epochs,args.semantic)
    else: evaluate(args.split,args.out,args.checkpoint,args.unary_checkpoint,args.ordinary_weight)


if __name__=='__main__': main()
