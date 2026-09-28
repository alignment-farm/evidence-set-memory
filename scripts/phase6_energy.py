"""Small experience-fitted set energy over six public evidence proposals.

This is a cost-preference mechanism if complete outcomes are invariant; no
renaming of a score or gradient search over evidence is claimed as an EBM effect.
"""
import argparse
import itertools
import math
import time
import phase6_edit as study
from phase6_packaging import files_selection

POLICIES=['ordinary_files','all_files','ordinary','all','pointwise','root_only']
FEATURES=['source_bytes_20k','request_symbol_coverage','test_token_coverage',
          'unresolved_source_edges_20','resolved_source_edges_20','intact_file_delivery']


def feature(task,rows,chosen,policy):
    ids={r['id'] for r in chosen};whole={r['path'] for r in chosen if r['id'].endswith('::whole_file')}
    definitions=[r for r in rows if r['kind']=='definition']
    included=[r for r in definitions if r['id'] in ids or r['path'] in whole]
    present={r['symbol'] for r in included};all_symbols={r['symbol'] for r in definitions}
    requested={s for s in all_symbols if s.lower() in study.tokens(task['request'])}
    resolved=unresolved=0
    for row in included:
        refs=set(row['names'])&all_symbols-{row['symbol']}
        resolved+=len(refs&present);unresolved+=len(refs-present)
    test_words=study.tokens(task['public_test'])
    evidence_words=study.tokens('\n'.join(r['text'] for r in chosen))
    return [sum(len(r['text'].encode()) for r in chosen)/20000,
            len(requested&present)/max(1,len(requested)),
            len(test_words&evidence_words)/max(1,len(test_words)),
            unresolved/20,resolved/20,float(policy.endswith('_files'))]


def proposals(task,source):
    rows,_,_=study.records(source);result=[]
    for policy in POLICIES:
        chosen,work=files_selection(task,source,policy) if policy.endswith('_files') else study.select(task,rows,policy)
        result.append(dict(policy=policy,chosen=chosen,work=work,features=feature(task,rows,chosen,policy)))
    return result


def fit(rows,epochs=800):
    import numpy as np
    import torch
    torch.set_num_threads(2)
    start=time.perf_counter();pairs=[];quality_pairs=0
    for task in sorted({r['task'] for r in rows}):
        group=[r for r in rows if r['task']==task]
        for a,b in itertools.combinations(group,2):
            # Lexicographic realized complete quality, then total native token count.
            key=lambda r:(r['complete'],-r['tokens'])
            if key(a)==key(b):continue
            good,bad=(a,b) if key(a)>key(b) else (b,a)
            quality_pairs+=good['complete']!=bad['complete']
            pairs.append(np.array(good['features'])-np.array(bad['features']))
    if not pairs:raise RuntimeError('No eligible experience contrast')
    x=torch.tensor(np.array(pairs),dtype=torch.float64)
    w=torch.zeros(len(FEATURES),dtype=torch.float64,requires_grad=True)
    optimizer=torch.optim.Adam([w],lr=.03);trace=[]
    for step in range(epochs):
        optimizer.zero_grad();loss=torch.nn.functional.softplus(.5+x@w).mean()+.005*w.square().sum()
        loss.backward();optimizer.step()
        if step in [0,99,399,799]:trace.append(dict(step=step+1,loss=float(loss.detach())))
    coefficients=w.detach().tolist()
    return dict(weights=coefficients,features=FEATURES,steps=epochs,pairs=len(pairs),
                quality_pairs=quality_pairs,cost_only_pairs=len(pairs)-quality_pairs,
                pair_ranking_accuracy=float(((x@w)<0).double().mean()),
                seconds=time.perf_counter()-start,trace=trace)


def train(out):
    out=study.fresh(out);construction_start=time.perf_counter()
    tasks=study.load(study.PHASE/'development-tasks.json');examples=[];source=study.ASSET
    for task in tasks:
        candidates=proposals(task,source)
        for candidate in candidates:
            folder='packaging' if candidate['policy'].endswith('_files') else 'development'
            path=study.PHASE/f'runs/{folder}/{task["id"]}/{candidate["policy"]}/result.json'
            row=study.load(path)
            assert [r['id'] for r in candidate['chosen']]==row['selected']
            examples.append(dict(task=task['id'],policy=candidate['policy'],features=candidate['features'],
                complete=row['complete'],tokens=row['logical_prompt_tokens']+row['logical_completion_tokens'],
                source_result=str(path.relative_to(study.ROOT)),result_sha256=study.sha(path)))
        source=study.PHASE/f'runs/development/states/{task["id"]}'
    construction_seconds=time.perf_counter()-construction_start
    model=fit(examples)
    # Serious ordinary experience reuse: one cheapest successful proposal policy,
    # selected globally from completed tasks, without learning a feature model.
    policy_key=lambda policy:(sum(r['complete'] for r in examples if r['policy']==policy),
                               -sum(r['tokens'] for r in examples if r['policy']==policy))
    model['ordinary_experience_policy']=max(POLICIES,key=policy_key)
    model['ordinary_baseline_policy']=max(['ordinary','ordinary_files'],key=policy_key)
    model['broad_baseline_policy']=max(['all','all_files'],key=policy_key)
    model['seen_task_choices']={task['id']:min([r for r in examples if r['task']==task['id']],
        key=lambda r:sum(a*b for a,b in zip(r['features'],model['weights'])))['policy'] for task in tasks}
    model['leave_one_task_out']=[]
    for task in tasks:
        partial=fit([r for r in examples if r['task']!=task['id']])
        chosen=min([r for r in examples if r['task']==task['id']],key=lambda r:sum(a*b for a,b in zip(r['features'],partial['weights'])))
        model['leave_one_task_out'].append(dict(held_task=task['id'],chosen_policy=chosen['policy'],tokens=chosen['tokens'],fit=partial))
    model.update(timestamp=study.stamp(),script_sha256=study.sha(__file__),torch_threads=2,
                 example_construction_seconds=construction_seconds,development_tasks=len(tasks),
                 main_trainable_parameters=len(FEATURES),initial_weights=[0.]*len(FEATURES),
                 inference='Enumerate six public candidate sets and minimize linear energy; no selection-variable gradients')
    study.dump(out/'examples.json',examples);study.dump(out/'model.json',model)
    print(model)


def choose(task,source,model):
    start=time.perf_counter();candidates=proposals(task,source)
    winner=min(candidates,key=lambda r:sum(a*b for a,b in zip(r['features'],model['weights'])))
    work=dict(winner['work'],energy=sum(a*b for a,b in zip(winner['features'],model['weights'])),
              chosen_proposal=winner['policy'],proposal_evaluations=len(candidates),
              proposal_and_selection_seconds=time.perf_counter()-start,
              proposal_energies={r['policy']:sum(a*b for a,b in zip(r['features'],model['weights'])) for r in candidates})
    return winner['chosen'],work


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    train(parser.parse_args().out)
