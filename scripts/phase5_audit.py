"""Replay phase-5 native outcomes, acquisition weights and costs without overwrites."""
import argparse
import collections
import time
import numpy as np
import torch
import phase5_config as study


def audit(out, retrain):
    out=study.fresh(out);start=time.perf_counter();root=study.ROOT/'phase5'
    freeze=study.load(root/'freeze.json')
    for path,digest in freeze['files'].items():assert study.sha(study.ROOT/path)==digest,path
    dev=study.load(root/'runs/development/histories.json')
    attempts=study.load(root/'runs/development/attempts.json')
    fresh=study.load(root/'runs/confirmation/histories.json')
    assert fresh==study.extend_chains(study.histories(28092659,12,'transfer'))
    ep_dev={ep['id']:ep for h in dev for ep in h['episodes']}
    ep_fresh={ep['id']:ep for h in fresh for ep in h['episodes']}
    assert not set(ep_dev)&set(ep_fresh)
    dev_ids={r['id'] for ep in ep_dev.values() for r in ep['records']}
    later_ids={r['id'] for ep in ep_fresh.values() for r in ep['records']}
    assert not dev_ids&later_ids
    executions=0;checks=collections.Counter()
    def run(ep, records):
        nonlocal executions
        executions+=1
        return study.render(ep['request'],records)
    for ep in list(ep_dev.values())+list(ep_fresh.values()):
        rep=study.represent(ep['request'],ep['records'],'native_syntax')
        chosen=study.closure(rep)
        assert run(ep,rep['pool'])['value']==ep['expected']
        assert run(ep,study.selected(rep['pool'],chosen))['value']==ep['expected']
        for remove in chosen:
            subset=study.selected(rep['pool'],[i for i in chosen if i!=remove])
            assert not study.grade(ep,subset,run(ep,subset))
        checks['complete_pool_and_minimal_closure']+=1
    for row in attempts:
        ep=ep_dev[row['episode']];index={r['id']:r for r in ep['records']}
        records=[index[x] for x in row['ids']];answer=run(ep,records)
        assert study.grade(ep,records,answer)==row['complete']
        assert {k:v for k,v in answer.items() if k!='seconds'}=={k:v for k,v in row['answer'].items() if k!='seconds'}
        checks['eligible_executed_feedback']+=1
    paths=['development/explicit_only-outcomes.json','development/native_syntax-outcomes.json',
           'development/ordinary-outcomes.json','balanced/outcomes.json',
           'constraint-energy/outcomes.json','balanced-final/outcomes.json','confirmation/outcomes.json']
    ledger=[]
    for path in paths:
        rows=study.load(root/'runs'/path);cache={}
        for row in rows:
            ep=(ep_fresh if path.startswith('confirmation') else ep_dev)[row['episode']]
            index={r['id']:r for r in ep['records']}
            records=[index[x] for x in row['selected_ids']];answer=run(ep,records)
            assert study.grade(ep,records,answer)==row['first_complete']
            assert answer.get('value')==row['answer'].get('value')
            assert answer.get('error')==row['answer'].get('error')
            eligible={r['id'] for r in study.eligible(ep['request'],ep['records'])}
            assert set(row['selected_ids'])<=eligible
            key=(row['method'],row['history'],str(ep['request']))
            old=cache.get(key)
            hit=old is not None and set(old['ids'])<=eligible
            assert hit==row['cache_hit']
            assert (old is not None and not hit)==row['cache_invalidated']
            if hit:assert old['value']==answer['value'] and set(old['ids'])==set(row['selected_ids'])
            assert bool(row['repair'])==('error' in row['answer'])
            if row['repair']:
                records=[index[x] for x in row['repair']['ids']];answer=run(ep,records)
            assert study.grade(ep,records,answer)==row['final_complete']
            if 'value' in answer:cache[key]={'ids':[r['id'] for r in records],'value':answer['value']}
            checks['outcome_scope_cache_and_public_repair']+=1
        ledger.append(dict(path=path,episodes=len(rows),
            executions=sum(r['executions'] for r in rows),
            repairs=sum(r['repair'] is not None for r in rows),
            cache_hits=sum(r['cache_hit'] for r in rows),
            representation_seconds=sum(r['representation_seconds'] for r in rows),
            search_seconds=sum(r['work']['seconds'] for r in rows),
            discrete_evaluations=sum(r['work']['discrete_evaluations'] for r in rows),
            gradient_steps=sum(r['work']['gradient_steps'] for r in rows),
            parser_seconds=sum(r['answer']['seconds']+(r['repair']['answer']['seconds'] if r['repair'] else 0) for r in rows),
            repair_selection_seconds=sum(r['repair']['seconds'] if r['repair'] else 0 for r in rows),
            delivered_bytes=sum(r['delivery_bytes'] for r in rows)))
    model_specs=[('development/explicit_only-model.json','explicit_only',False,False),
                 ('development/native_syntax-model.json','native_syntax',False,False),
                 ('balanced/native_syntax-model.json','native_syntax',True,False),
                 ('constraint-energy/native_syntax-model.json','native_syntax',True,True),
                 ('balanced-final/native_syntax-model.json','native_syntax',True,False)]
    training=[];retrain_seconds=0.
    for path,grammar,balanced,constraint in model_specs:
        saved=study.load(root/'runs'/path)
        training.append(dict(path=path,**saved['train']))
        if retrain:
            rerun=study.fit(dev,attempts,grammar,balanced,constraint)
            np.testing.assert_array_equal(saved['weights'],rerun['weights'])
            retrain_seconds+=rerun['train']['seconds'];checks['bit_identical_weight_replay']+=1
    diag=study.load(root/'runs/optimizer-diagnosis/outcomes.json')
    for row in diag:
        ep=ep_fresh[row['episode']];index={r['id']:r for r in ep['records']}
        records=[index[x] for x in row['ids']]
        assert study.grade(ep,records,run(ep,records))==row['complete']
        checks['posthoc_optimizer_native_output']+=1
    diagnostic=dict(executions=len(diag),search_seconds=sum(x['work']['seconds'] for x in diag),
        gradient_steps=sum(x['work']['gradient_steps'] for x in diag),
        discrete_evaluations=sum(x['work']['discrete_evaluations'] for x in diag),
        parser_seconds=sum(x['answer']['seconds'] for x in diag))
    acquisition=study.load(root/'runs/development/acquisition-cost.json')
    cost=dict(acquisition=acquisition,training_runs=training,policy_evaluation_runs=ledger,
              optimizer_diagnosis=diagnostic,
              experiment_totals=dict(native_executions=acquisition['executions']+sum(x['executions'] for x in ledger)+len(diag),
                  fits=len(training),optimizer_steps=sum(x['optimizer_steps'] for x in training),
                  pair_presentations=sum(x['pair_presentations'] for x in training),
                  train_including_feature_pair_construction_seconds=sum(x['seconds'] for x in training),
                  gradient_steps=sum(x['gradient_steps'] for x in ledger)+diagnostic['gradient_steps'],
                  discrete_evaluations=sum(x['discrete_evaluations'] for x in ledger)+diagnostic['discrete_evaluations']),
              external_model_calls=0,embeddings_constructed=0,weight_downloads=0,
              unknown=['investigator tokens/dollars','human-equivalent authoring/label design work',
                       'machine joules','process startup/import/serialization time',
                       'native unit-test executions before final audit were not counted'],
              timing_caveat='Single-host small CPU runs, not isolated microbenchmarks. Nested inclusive times must not be added twice.')
    study.dump(out/'native-costs.json',cost)
    summary=study.load(root/'runs/confirmation/summary.json')
    rows=study.load(root/'runs/confirmation/outcomes.json')
    for method,values in summary.items():
        selected=[x for x in rows if x['method']==method]
        values['strata']={regime:dict(episodes=len([x for x in selected if x['transfer_regime']==regime]),
                           first_complete=sum(x['first_complete'] for x in selected if x['transfer_regime']==regime),
                           noncache_complete=sum(x['first_complete'] and not x['cache_hit'] for x in selected if x['transfer_regime']==regime),
                           noncache_n=sum(not x['cache_hit'] for x in selected if x['transfer_regime']==regime))
                          for regime in ['same_templates','two_extra_chain_sections']}
        values['noncache_complete']=sum(x['first_complete'] and not x['cache_hit'] for x in selected)
        values['noncache_n']=sum(not x['cache_hit'] for x in selected)
    study.dump(out/'confirmation-expanded-summary.json',summary)
    report=dict(checks=dict(checks),audit_native_executions=executions,
                audit_weight_replay_seconds=retrain_seconds,audit_wall_seconds=time.perf_counter()-start,
                frozen_files_verified=len(freeze['files']),current_script_sha256=study.sha(__file__),
                audit_replay_cost_separate_from_experiment=True,configparser_sha256=study.sha(study.configparser.__file__),
                development_histories=12,confirmation_histories=12,eligible_pool_reachability='all required sections present',
                primary_model_reading='not tested; native executable semantics only')
    study.dump(out/'audit.json',report)
    print(report);print(cost['experiment_totals'])


if __name__=='__main__':
    torch.set_num_threads(2)
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--retrain',action='store_true')
    args=parser.parse_args();audit(args.out,args.retrain)
