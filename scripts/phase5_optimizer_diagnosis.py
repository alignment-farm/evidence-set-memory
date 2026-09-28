"""Post-freeze, unblinded mechanism diagnosis; never updates published confirmation."""
import argparse
import time
import numpy as np
import phase5_config as study


def relaxed(rep,weights,steps,starts):
    begin=time.perf_counter();n=len(rep['pool']);rng=np.random.default_rng(87)
    initial=[np.full(n,.5),np.zeros(n),np.ones(n),rng.random(n)]
    initial += [rng.random(n) for _ in range(starts-4)]
    candidates=[];terminals=[]
    for x in initial:
        z=x.copy();candidates.append((z>=.5).astype(float))
        for _ in range(steps):
            g=np.full(n,weights[1]);g[rep['root']]-=weights[0]
            for i,j in rep['edges']:
                g[i]+=weights[2]*(1-z[j])+weights[3]*z[j]
                g[j]+=(weights[3]-weights[2])*z[i]
            z=np.clip(z-.05*g,0,1)
        rounded=(z>=.5).astype(float);candidates.append(rounded)
        terminals.append(dict(fractionality=float(np.sum(z*(1-z))),
                              continuous_energy=float(study.feature(z,rep)@weights),
                              rounded_energy=float(study.feature(rounded,rep)@weights)))
    energies=study.feature(np.array(candidates),rep)@weights
    best=candidates[int(np.argmin(energies))]
    return np.flatnonzero(best).tolist(),dict(seconds=time.perf_counter()-begin,
        gradient_steps=steps*starts,discrete_evaluations=len(candidates),
        energy=float(energies.min()),terminals=terminals)


def run(out):
    out=study.fresh(out);root=study.ROOT/'phase5/runs/confirmation'
    data=study.load(root/'histories.json');published=study.load(root/'outcomes.json')
    ep_index={ep['id']:ep for h in data for ep in h['episodes']}
    exact={r['episode']:r for r in published if r['method']=='exact'}
    weights=np.array(study.load(study.ROOT/'phase5/runs/balanced-final/native_syntax-model.json')['weights'])
    rows=[]
    for original in [r for r in published if r['method']=='relax' and not r['cache_hit']]:
        ep=ep_index[original['episode']];rep=study.represent(ep['request'],ep['records'],'native_syntax')
        for label,steps,starts in [('original_replay',60,4),('more_steps',240,4),('more_starts',60,16),('one_flip',60,4)]:
            if label=='one_flip':
                chosen,work=study.search(rep,weights,'relax_flip')
            else:
                chosen,work=relaxed(rep,weights,steps,starts)
            records=study.selected(rep['pool'],chosen);ids=[r['id'] for r in records]
            if label=='original_replay':assert ids==original['selected_ids']
            answer=study.render(ep['request'],records)
            rows.append(dict(method=label,episode=ep['id'],transfer_regime=original['transfer_regime'],
                ids=ids,work=work,answer=answer,complete=study.grade(ep,records,answer),
                energy_gap=work['energy']-exact[ep['id']]['work']['energy']))
    summary={}
    for method in sorted({r['method'] for r in rows}):
        r=[x for x in rows if x['method']==method]
        summary[method]=dict(n=len(r),complete=sum(x['complete'] for x in r),
            global_energy=sum(abs(x['energy_gap'])<1e-9 for x in r),
            search_seconds=sum(x['work']['seconds'] for x in r),
            gradient_steps=sum(x['work']['gradient_steps'] for x in r),
            discrete_evaluations=sum(x['work']['discrete_evaluations'] for x in r),
            maximum_energy_gap=max(x['energy_gap'] for x in r))
    study.dump(out/'outcomes.json',rows);study.dump(out/'summary.json',summary)
    study.dump(out/'provenance.json',dict(study.provenance(),diagnostic_sha256=study.sha(__file__),
                                        fresh_confirmation=False,weights_updated=False))
    print(summary)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
