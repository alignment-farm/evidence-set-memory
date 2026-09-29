"""Freeze the self-check comparison, then execute separately authored tasks."""
import argparse
from pathlib import Path
import shutil
import phase7_edit as s


def freeze():
    assert (s.PHASE/'runs/development/execution.json').exists()
    assert not (s.PHASE/'transfer-tasks.json').exists(),'Later tasks must be authored after freeze'
    assert not (s.PHASE/'freeze.json').exists()
    paths=list((s.ROOT/'scripts').glob('phase7_*.py'))+[s.ROOT/'scripts/test_phase7_edit.py']
    paths += [s.ROOT/p for p in ['scripts/phase6_edit.py','scripts/phase6_energy.py','scripts/phase6_prompt.py',
        'phase6/runs/acquisition/model.json','phase6/runs/acquisition/examples.json','phase7/PROTOCOL.md',
        'phase7/CLAIM.md','phase7/pyproject.toml','phase7/uv.lock','uv.lock']]
    paths += list((s.PHASE/'assets-v2').glob('*'))
    paths += [s.PHASE/'runs/development/results.json',s.PHASE/'runs/development/execution.json']
    s.dump(s.PHASE/'freeze.json',dict(timestamp=s.old.stamp(),future_task_file_absent=True,
        files={str(p.relative_to(s.ROOT)):s.sha(p) for p in paths},call_cap=8,
        new_parameter_updates=False,reader_digest='f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef'))


def transfer(out):
    frozen=s.load(s.PHASE/'freeze.json')
    for path,digest in frozen['files'].items():assert s.sha(s.ROOT/path)==digest,path
    out=s.fresh(out);calls=out/'calls';calls.mkdir();tasks=s.load(s.PHASE/'transfer-tasks.json')
    s.dump(out/'tasks.json',tasks);asset=s.ASSETS['slugify'];source=Path(asset['root'])
    prior=[];memory=[];results=[];accepted=[]
    for task in tasks:
        candidates={}
        for policy in ['ordinary_access','full_context','empirical_reuse','learned_energy']:
            row,case=s.attempt(task,source,'slugify',policy,True,out/task['id']/policy,calls,prior,memory)
            results.append(row);candidates[policy]=(row,case);s.dump(out/'results.json',results)
        passed=[p for p,(row,_) in candidates.items() if row['complete']]
        if not passed:
            s.dump(out/'rejected-history.json',dict(task=task['id'],reason='No accepted complete revision'))
            break
        policy=passed[0];row,case=candidates[policy];state=s.fresh(out/'states'/task['id'])
        shutil.copytree(case/asset['package'],state/asset['package']);source=state
        memory.append(dict(requirement=task['request'],accepted_policy=policy,patches=row['patches'],source_hashes=row['source_result']))
        s.dump(state/'lineage.json',memory);prior.extend([task['public_test'],task['hidden_test']]);accepted.append(task)
    # A single native all-obligations retention run, not another model success.
    case=s.copy_case(source,asset,s.ROOT/'.cache/phase7/retention'/out.name)
    for i,text in enumerate(prior):(case/f'prior_{i}.py').write_text(text)
    report=s.execute(case,asset,asset['tests']+[f'prior_{i}.py' for i in range(len(prior))],'retention')
    s.dump(out/'retention.json',dict(accepted_tasks=[t['id'] for t in accepted],test=report,reader_calls=0,source_hashes=s.source_hashes(source,asset)))
    s.dump(out/'execution.json',dict(timestamp=s.old.stamp(),script_sha256=s.sha(__file__),freeze_sha256=s.sha(s.PHASE/'freeze.json')))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','transfer']);p.add_argument('--out');a=p.parse_args()
    if a.command=='freeze':freeze()
    else:transfer(a.out)
