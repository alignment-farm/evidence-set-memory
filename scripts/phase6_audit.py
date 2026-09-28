"""Reexecute final participant patches and reconcile native costs, no LLM calls."""
import argparse
from collections import Counter
import json
from pathlib import Path
import time
import phase6_edit as study


def totals(run):
    results=study.load(run/'results.json')
    responses=[study.load(p) for p in sorted((run/'calls').glob('*-response.json'))]
    tests=[]
    for r in results:
        tests.extend([r['baseline'],r['heldout']])
        tests.extend(e['public_test'] for e in r['events'] if 'public_test' in e)
    groups={}
    for policy in sorted({r['policy'] for r in results}):
        rows=[r for r in results if r['policy']==policy]
        groups[policy]=dict(n=len(rows),complete=sum(r['complete'] for r in rows),
            initial_noops=sum(r['initial_noop'] for r in rows),
            first_patch_public_pass=sum(r['first_patch_public_pass'] is True for r in rows),
            logical_requests=sum(len(r['events']) for r in rows),
            public_patch_submissions=sum(len(r['patches']) for r in rows),
            source_reads=sum('read' in e.get('action',{}) for r in rows for e in r['events']),
            prompt_tokens=sum(r['logical_prompt_tokens'] for r in rows),
            completion_tokens=sum(r['logical_completion_tokens'] for r in rows),
            initial_source_bytes=sum(r['selection']['bytes'] for r in rows),
            additional_source_bytes=sum(e.get('read_bytes',0) for r in rows for e in r['events']),
            representation_seconds=sum(r['representation']['seconds'] for r in rows),
            selection_seconds=sum(r['selection'].get('proposal_and_selection_seconds',r['selection']['seconds']) for r in rows),
            chosen_proposals=[r['selection'].get('chosen_proposal',r['policy']) for r in rows])
    return dict(run=str(run.relative_to(study.ROOT)),attempts=len(results),policies=groups,
        physical_requests=len(responses),endpoint_errors=sum(bool(x['error']) for x in responses),
        missing_usage=sum('usage' not in x['response'] for x in responses),
        prompt_tokens=sum(x['response'].get('usage',{}).get('prompt_tokens',0) for x in responses),
        completion_tokens=sum(x['response'].get('usage',{}).get('completion_tokens',0) for x in responses),
        server_cached_prompt_tokens=sum(x['response'].get('usage',{}).get('prompt_tokens_details',{}).get('cached_tokens',0) for x in responses),
        reader_seconds=sum(x['seconds'] for x in responses),pytest_invocations=len(tests),
        pytest_seconds=sum(t['seconds'] for t in tests),
        test_case_executions=sum(t.get('counts',{}).get('tests',0) for t in tests),
        reported_models=sorted({x['response'].get('model','unknown') for x in responses}))


def audit(out):
    out=study.fresh(out);start=time.perf_counter()
    roots=[study.PHASE/'runs'/name for name in ['development','packaging','transfer']]
    extra=study.PHASE/'runs/interface-validation'
    if extra.exists():roots.append(extra)
    old=study.load(study.PHASE/'development-tasks.json');later=study.load(study.PHASE/'runs/transfer/tasks.json')
    tasks={t['id']:t for t in old+later};by_request={t['request']:t for t in old+later}
    sources=[(study.ASSET,[])]+[(p.parent,study.load(p)) for parent in roots for p in parent.glob('states/*/lineage.json')]
    source_index={json.dumps({str(p.relative_to(s)):study.sha(p) for p in (s/'src').rglob('*.py')},sort_keys=True):(s,m) for s,m in sources}
    checks=Counter();replays=[]
    for run in roots:
        for row in study.load(run/'results.json'):
            task_id=row['task'].removeprefix('retention-');task=tasks[task_id]
            source,memory=source_index[json.dumps(row['source_base'],sort_keys=True)]
            identifier=study.hashlib.sha256((str(run)+row['task']+row['policy']).encode()).hexdigest()[:18]
            case=study.copy_case(source,study.ROOT/'.cache/phase6/audit-cases'/out.name/identifier)
            (case/'public_current.py').write_text(task['public_test']);(case/'heldout_current.py').write_text(task['hidden_test'])
            prior=[by_request[m['requirement']][field] for m in memory for field in ['public_test','hidden_test']]
            for i,text in enumerate(prior):(case/f'prior_{i}.py').write_text(text)
            for patch in row['patches']:study.apply_edits(case,patch)
            hashes={str(p.relative_to(case)):study.sha(p) for p in (case/'src').rglob('*.py')}
            assert hashes==row['source_result'];checks['patch_source_hash_replay']+=1
            public=study.test(case,['tests','public_current.py']+[f'prior_{i}.py' for i in range(len(prior))],'public')
            heldout=study.test(case,['heldout_current.py'],'heldout')
            assert (public['returncode']==0)==row['public_pass']
            assert (heldout['returncode']==0)==row['heldout_pass'];checks['native_complete_grade_replay']+=1
            for original in (study.ASSET/'tests').glob('*.py'):
                assert study.sha(original)==study.sha(case/'tests'/original.name)
            assert (case/'public_current.py').read_text()==task['public_test']
            assert (case/'heldout_current.py').read_text()==task['hidden_test'];checks['tests_not_modified']+=1
            for event in row['events']:
                key=event['request_hash'];req=study.load(run/f'calls/{key}-request.json')
                assert study.hashlib.sha256(json.dumps(req,sort_keys=True).encode()).hexdigest()==key
                text=json.dumps(req)
                # Private current test function names must not enter eligible model context.
                for function in study.re.findall(r'def (test_\w+)\(',task['hidden_test']):
                    assert function not in text,(row['task'],function)
                response=study.load(run/f'calls/{key}-response.json')
                assert 'f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef' in response['response']['model']
                checks['request_hash_reader_identity_private_test_boundary']+=1
            replays.append(dict(run=str(run.relative_to(study.ROOT)),task=row['task'],policy=row['policy'],
                                public=public,heldout=heldout))
    freeze=study.load(study.PHASE/'freeze.json')
    for path,digest in freeze['files'].items():assert study.sha(study.ROOT/path)==digest,path
    model=study.load(study.PHASE/'runs/acquisition/model.json')
    costs=[totals(run) for run in roots]
    preflights=[study.load(study.PHASE/f'assets/{v}-upstream-tests.json') for v in ['v1','v2','v3']]
    study.dump(out/'native-costs.json',dict(runs=costs,preflight_pytest_invocations=len(preflights),
        preflight_seconds=sum(t['seconds'] for t in preflights),
        acquisition=dict(parameters=6,main_steps=model['steps'],main_pairs=model['pairs'],
            main_seconds=model['seconds'],example_construction_seconds=model['example_construction_seconds'],
            leave_one_task_out_fits=len(model['leave_one_task_out']),
            leave_one_task_out_seconds=sum(x['fit']['seconds'] for x in model['leave_one_task_out'])),
        aggregate=dict(physical_reader_calls=sum(r['physical_requests'] for r in costs),
            prompt_tokens=sum(r['prompt_tokens'] for r in costs),completion_tokens=sum(r['completion_tokens'] for r in costs),
            reader_seconds=sum(r['reader_seconds'] for r in costs),pytest_invocations=sum(r['pytest_invocations'] for r in costs)+3),
        unknown=['investigator tokens/dollars','authored task/test labor','machine energy','Git/package network transfer',
                 'constructor/serialization/process startup overhead outside saved timers'],
        interpretation='Native token counts are not dollars or independent observations. Reported prompt-cache tokens are retained; wall times are not isolated.'))
    study.dump(out/'replayed-tests.json',replays)
    report=dict(checks=dict(checks),frozen_files=len(freeze['files']),seconds=time.perf_counter()-start,
                audit_pytest_invocations=2*len(replays),reader_calls=0,script_sha256=study.sha(__file__))
    study.dump(out/'audit.json',report);print(report)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    audit(parser.parse_args().out)
