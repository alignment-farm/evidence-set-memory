"""Rebuild archived edits and scratch checks; reconcile costs without inference."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import time
import phase7_edit as s


def costs(run):
    rows=s.load(run/'results.json');responses=[s.load(p) for p in (run/'calls').glob('*-response.json')]
    groups={}
    for policy,checks in sorted({(r['policy'],r['checks_enabled']) for r in rows}):
        part=[r for r in rows if (r['policy'],r['checks_enabled'])==(policy,checks)]
        groups[f'{policy}:checks={checks}']=dict(attempts=len(part),complete=sum(r['complete'] for r in part),
            public_pass=sum(r['public_pass'] for r in part),finished=sum(r['finished'] for r in part),
            logical_calls=sum(len(r['events']) for r in part),
            prompt_tokens=sum(r['logical_prompt_tokens'] for r in part),completion_tokens=sum(r['logical_completion_tokens'] for r in part),
            check_submissions=sum(len(r['scratch']) for r in part),
            read_calls=sum('read' in e.get('action',{}) for r in part for e in r['events']),
            read_bytes=sum(e.get('read_bytes',0) for r in part for e in r['events']),
            interface_errors=sum('interface_error' in e for r in part for e in r['events']),
            initial_source_bytes=sum(r['selection']['bytes'] for r in part),
            representation_seconds=sum(r['representation']['seconds'] for r in part),
            selection_seconds=sum(r['selection']['seconds'] for r in part),
            proposal_choices=[r['selection']['chosen_proposal'] for r in part],
            pytest_invocations=sum(len(r['test_runs']) for r in part),
            pytest_seconds=sum(t['seconds'] for r in part for t in r['test_runs']))
    return dict(run=str(run.relative_to(s.ROOT)),groups=groups,physical_calls=len(responses),
        request_seconds=sum(r['seconds'] for r in responses),errors=sum(bool(r['error']) for r in responses),
        prompt_tokens=sum(r['response'].get('usage',{}).get('prompt_tokens',0) for r in responses),
        completion_tokens=sum(r['response'].get('usage',{}).get('completion_tokens',0) for r in responses),
        cached_prompt_tokens=sum(r['response'].get('usage',{}).get('prompt_tokens_details',{}).get('cached_tokens',0) for r in responses))


def run(out):
    out=s.fresh(out);start=time.perf_counter();checks=Counter();replays=[]
    for name in ['development','transfer']:
        root=s.PHASE/'runs'/name
        tasks=[s.load(root/'task.json')] if name=='development' else s.load(root/'tasks.json')
        tasks={t['id']:t for t in tasks}
        for index,row in enumerate(s.load(root/'results.json')):
            task=tasks[row['task']];asset=s.ASSETS[row['asset']];source=s.ROOT/row['source']
            assert s.source_hashes(source,asset)==row['source_base']
            case=s.copy_case(source,asset,s.ROOT/'.cache/phase7/audit'/out.name/f'{name}-{index}')
            (case/'public_current.py').write_text(task['public_test'])
            for i,text in enumerate(row['prior_tests']):(case/f'prior_{i}.py').write_text(text)
            targets=asset['tests']+['public_current.py']+[f'prior_{i}.py' for i in range(len(row['prior_tests']))]
            tests=[];scratch=[]
            for event in row['events']:
                key=event['request_hash'];request=s.load(root/f'calls/{key}-request.json')
                assert hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()==key
                response=s.load(root/f'calls/{key}-response.json')
                if not response['error']:
                    assert 'f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef' in response['response']['model']
                for function in re.findall(r'def (test_\w+)\(',task['hidden_test']):
                    assert function not in json.dumps(request),function
                assert not (case/'heldout_current.py').exists();checks['request_identity_and_private_file_boundary']+=1
                if 'interface_error' in event:continue
                action=event.get('action',{})
                if 'check' in action:
                    path=f'scratch_{len(scratch)}.py';(case/path).write_text(action['check']);scratch.append(path)
                    report=s.execute(case,asset,[path],f'check_{event["turn"]}');tests.append(report)
                    assert report['returncode']==event['check_test']['returncode'];checks['scratch_grade_replay']+=1
                elif 'edits' in action:
                    s.apply_edits(case,asset,action)
                    report=s.execute(case,asset,targets,f'public_{event["turn"]}');tests.append(report)
                    assert report['returncode']==event['public_test']['returncode'];checks['public_repair_grade_replay']+=1
                    if scratch:
                        report=s.execute(case,asset,scratch,f'scratch_{event["turn"]}');tests.append(report)
                        assert report['returncode']==event['scratch_retest']['returncode'];checks['scratch_repair_replay']+=1
            assert s.source_hashes(case,asset)==row['source_result'];checks['source_hash_replay']+=1
            for path,digest in row['protected_hashes'].items():assert s.sha(case/path)==digest
            checks['protected_files_unchanged']+=1
            (case/'heldout_current.py').write_text(task['hidden_test'])
            public=s.execute(case,asset,targets,'final_public');hidden=s.execute(case,asset,['heldout_current.py'],'heldout');tests += [public,hidden]
            assert (public['returncode']==0)==row['public_pass'];assert (hidden['returncode']==0)==row['heldout_pass']
            checks['complete_grade_replay']+=1
            replays.append(dict(run=name,task=row['task'],policy=row['policy'],checks_enabled=row['checks_enabled'],tests=tests))
    frozen=s.load(s.PHASE/'freeze.json')
    for path,digest in frozen['files'].items():assert s.sha(s.ROOT/path)==digest,path
    ledger=[costs(s.PHASE/'runs'/name) for name in ['development','transfer']]
    s.dump(out/'replays.json',replays)
    preflights=[s.load(p) for folder in ['assets','assets-v2'] for p in (s.PHASE/folder).glob('*.json') if p.name.endswith('-upstream.json') or p.name=='scratch-security.json']
    s.dump(out/'native-costs.json',dict(runs=ledger,physical_calls=sum(r['physical_calls'] for r in ledger),
        prompt_tokens=sum(r['prompt_tokens'] for r in ledger),completion_tokens=sum(r['completion_tokens'] for r in ledger),
        reader_seconds=sum(r['request_seconds'] for r in ledger),
        preflight_tests=len(preflights),preflight_seconds=sum(p['seconds'] for p in preflights),
        retention=s.load(s.PHASE/'runs/transfer/retention.json'),new_training_fits=0,
        posthoc_check_diagnosis=s.load(s.PHASE/'runs/check-diagnosis/summary.json'),
        inherited_acquisition='phase6/runs/audit/native-costs.json',
        unknown=['investigator compute and labor','authored labels/workload labor','machine joules','package/Git network bytes',
                 'serving backend build and isolated latency','small untimed setup/serialization overhead']))
    s.dump(out/'audit.json',dict(checks=dict(checks),frozen_files=len(frozen['files']),
        pytest_invocations=sum(len(r['tests']) for r in replays),pytest_seconds=sum(t['seconds'] for r in replays for t in r['tests']),
        wall_seconds=time.perf_counter()-start,reader_calls=0,script_sha256=s.sha(__file__)))
    print(dict(checks))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
