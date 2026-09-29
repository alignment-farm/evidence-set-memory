"""Bounded source editing with optional model-authored pytest self-checks."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
import phase6_edit as old
import phase6_energy as energy
from phase6_prompt import canonical_output

ROOT=old.ROOT; PHASE=ROOT/'phase7'; PYTHON=PHASE/'.venv/bin/python'
dump=old.dump; load=old.load; sha=old.sha; fresh=old.fresh
ASSETS={
 'dotenv':dict(root=str(old.ASSET),package='src/dotenv',pythonpath='src',tests=['tests'],
               extras=['setup.cfg','README.md'],entry=('dotenv','dotenv.cli')),
 'slugify':dict(root=str(ROOT/'.cache/phase7/python-slugify'),package='slugify',pythonpath='.',
                tests=['test.py'],extras=['README.md'],entry=('slugify','slugify.__main__'))}
RULES='''You are a code-edit participant. Implement the current requirement while preserving prior requirements and upstream behavior. All public source/tests are available through reads. Return exactly one JSON action:
{"read":["relative/path.py"]} to read up to 3 inventory files;
{"edits":[{"path":"production/path.py","old":"unique exact existing text","new":"replacement"}]} to edit existing production files only;
{"finish":true} when implementation is complete.
Do not modify evaluator tests, dependencies or scope rules. Public tests are examples, not the entire requirement. After public success, review each requirement clause and boundary cases before finishing. The harness reports test results after edits. You may continue to read and repair. Keep responses JSON, without explanations. /no_think'''
CHECK_RULE='''
You may also use {"check":"Python pytest test source"} to create and execute your own checks. Use pytest fixtures such as tmp_path/monkeypatch. Derive tests from the stated requirement and public source, including edge cases; no private tests are accessible. Check code is limited to 12000 characters and runs for at most 60 seconds. It cannot modify production/test files or access the network/study archives. Own checks remain and rerun after each edit. Fix incorrect own expectations if needed by submitting a new check; earlier checks are retained as observations, not authoritative requirements.'''


def source_hashes(source,asset):
    return {str(p.relative_to(source)):sha(p) for p in sorted((source/asset['package']).glob('*.py'))}


def copy_case(source,asset,dest):
    dest=fresh(dest); origin=Path(asset['root'])
    shutil.copytree(source/asset['package'],dest/asset['package'])
    for name in asset['tests']+asset['extras']:
        p=origin/name
        if p.is_dir():shutil.copytree(p,dest/name)
        else:shutil.copy2(p,dest/name)
    (dest/'tmp').mkdir();(dest/'bin').mkdir()
    if not (dest/'setup.cfg').exists():(dest/'pytest.ini').write_text('[pytest]\n')
    entry,module=asset['entry']; wrapper=dest/'bin'/entry
    wrapper.write_text(f'#!{PYTHON}\nfrom {module} import '+('cli' if entry=='dotenv' else 'main')+'\n'+('cli' if entry=='dotenv' else 'main')+'()\n')
    wrapper.chmod(0o755)
    return dest


def execute(case,asset,targets,label):
    start=time.perf_counter();case=case.resolve(); report=case/'tmp'/f'{label}.xml'
    profile=f'''(version 1) (allow default) (deny network*)
    (deny file-write* (require-all (require-not (subpath "{case}/tmp")) (require-not (literal "/dev/null")) (require-not (literal "/dev/ptmx")) (require-not (regex #"^/dev/ttys[0-9]+$"))))
    (deny file-read-data (require-all (subpath "{ROOT}") (require-not (subpath "{case}")) (require-not (subpath "{PHASE}/.venv"))))
    (deny file-read* (subpath "/Users/macos-user/.codex") (subpath "/Users/macos-user/.ssh"))'''
    env={'PATH':f'{case}/bin:{PYTHON.parent}:/usr/bin:/bin','PYTHONPATH':str(case/asset['pythonpath']),
         'PYTHONDONTWRITEBYTECODE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','TMPDIR':str(case/'tmp'),'LANG':'en_US.UTF-8'}
    config='setup.cfg' if (case/'setup.cfg').exists() else 'pytest.ini'
    command=['/usr/bin/sandbox-exec','-p',profile,str(PYTHON),'-m','pytest','-q','-p','no:cacheprovider',
             '-c',config,'--rootdir',str(case),'--confcutdir',str(case),
             '--basetemp',str(case/'tmp'/label),'--junitxml',str(report),*targets]
    try:
        result=subprocess.run(command,cwd=case,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
        output=result.stdout;code=result.returncode
    except subprocess.TimeoutExpired as exc:output=str(exc.stdout);code=124
    counts={}
    if report.exists():
        suites=ET.parse(report).getroot()
        counts={k:sum(int(s.get(k,0)) for s in suites.iter('testsuite')) for k in ['tests','failures','errors','skipped']}
    return dict(command=command,returncode=code,output=output,counts=counts,seconds=time.perf_counter()-start)


def records(source,asset):
    start=time.perf_counter();rows=[];inventory=[]
    for path in sorted((source/asset['package']).glob('*.py')):
        relative=str(path.relative_to(source));text=path.read_text();lines=text.splitlines(keepends=True)
        nodes=[n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
        occupied=set()
        for node in nodes:
            begin=min([node.lineno]+[d.lineno for d in node.decorator_list])-1;end=node.end_lineno
            occupied.update(range(begin,end));content=''.join(lines[begin:end])
            rows.append(dict(id=relative+'::'+node.name,path=relative,symbol=node.name,text=content,
                names=sorted({n.id for n in ast.walk(node) if isinstance(n,ast.Name)}),line=begin+1,
                kind='definition',sha256=hashlib.sha256(content.encode()).hexdigest()))
        content=''.join(line for i,line in enumerate(lines) if i not in occupied)
        rows.append(dict(id=relative+'::module',path=relative,symbol='module',text=content,names=[],line=1,
                        kind='module',sha256=hashlib.sha256(content.encode()).hexdigest()))
        inventory.append(dict(path=relative,bytes=len(text.encode()),symbols=[n.name for n in nodes]))
    for name in asset['tests']+asset['extras']:
        path=Path(asset['root'])/name
        paths=path.rglob('*.py') if path.is_dir() else [path]
        inventory.extend(dict(path=str(p.relative_to(Path(asset['root']))),bytes=p.stat().st_size) for p in paths)
    return rows,inventory,dict(seconds=time.perf_counter()-start,source_files=len(list((source/asset['package']).glob('*.py'))),
        source_bytes=sum(len(r['text'].encode()) for r in rows),records=len(rows))


def proposal(task,source,rows,policy):
    chosen,_=old.select(task,rows,policy.replace('_files',''))
    if policy.endswith('_files'):
        chosen=[dict(id=p+'::whole_file',path=p,line=1,text=(source/p).read_text(),sha256=sha(source/p))
                for p in sorted({r['path'] for r in chosen})]
    return chosen


def selection(task,source,rows,policy):
    start=time.perf_counter();model=load(ROOT/'phase6/runs/acquisition/model.json');energies={}
    actual={'ordinary_access':'ordinary','full_context':'all','empirical_reuse':model['ordinary_experience_policy']}.get(policy,policy)
    if policy=='learned_energy':
        choices={p:proposal(task,source,rows,p) for p in energy.POLICIES}
        energies={p:sum(a*b for a,b in zip(energy.feature(task,rows,chosen,p),model['weights'])) for p,chosen in choices.items()}
        actual=min(energy.POLICIES,key=lambda p:energies[p]);chosen=choices[actual]
    else:chosen=proposal(task,source,rows,actual)
    return chosen,dict(chosen_proposal=actual,energies=energies,seconds=time.perf_counter()-start,
                       bytes=sum(len(r['text'].encode()) for r in chosen),records=len(chosen))


def apply_edits(case,asset,obj):
    changed={}; allowed=set(source_hashes(case,asset))
    if len(obj['edits'])>12:raise ValueError('At most twelve replacements')
    for edit in obj['edits']:
        path=edit['path']
        if path not in allowed or (case/path).is_symlink():raise ValueError('Only existing production files')
        current=changed.get(path,(case/path).read_text());before=edit['old'];after=edit['new']
        if not isinstance(before,str) or not before or not isinstance(after,str):raise ValueError('Nonempty exact old text required')
        if current.count(before)!=1:raise ValueError(f'Expected unique old text in {path}; found {current.count(before)}')
        changed[path]=current.replace(before,after,1)
    for path,text in changed.items():ast.parse(text,filename=path)
    for path,text in changed.items():(case/path).write_text(text)
    return list(changed)


def parse(response):
    obj=json.loads(response['choices'][0]['message'].get('content') or '')
    if not isinstance(obj,dict) or len(obj)!=1:raise ValueError('Exactly one JSON action required')
    key=next(iter(obj))
    if key in ['read','edits'] and isinstance(obj[key],list):return obj
    if key=='check' and isinstance(obj[key],str) and 0<len(obj[key])<=12000:return obj
    if key=='finish' and obj[key] is True:return obj
    raise ValueError('Unknown or malformed action')


def public_output(result,case):
    return canonical_output(result['output'][-14000:].replace(str(case),'<CASE>'))


def attempt(task,source,asset_name,policy,checks,out,calls,prior=None,memory=None,cap=8):
    wall=time.perf_counter();out=fresh(out);asset=ASSETS[asset_name]
    case=copy_case(source,asset,ROOT/'.cache/phase7/work'/hashlib.sha256(str(out).encode()).hexdigest()[:18])
    (case/'public_current.py').write_text(task['public_test']); prior=prior or []
    for i,content in enumerate(prior):(case/f'prior_{i}.py').write_text(content)
    targets=asset['tests']+['public_current.py']+[f'prior_{i}.py' for i in range(len(prior))]
    protected={str(p.relative_to(case)):sha(p) for p in case.rglob('*.py') if str(p.relative_to(case)) not in source_hashes(case,asset)}
    rows,inventory,representation=records(source,asset)
    inventory += [dict(path=p,bytes=(case/p).stat().st_size) for p in targets if p.endswith('.py') and p not in {x['path'] for x in inventory}]
    chosen,work=selection(task,source,rows,policy);baseline=execute(case,asset,targets,'baseline');test_runs=[baseline]
    initial=dict(requirement=task['request'],public_acceptance_test=task['public_test'],inventory=inventory,
        evidence=[{k:r[k] for k in ['id','path','line','text','sha256']} for r in chosen],
        prior_completed_changes=memory or [],baseline_test_output=public_output(baseline,case),max_calls=cap)
    messages=[dict(role='system',content=RULES+(CHECK_RULE if checks else '\nScratch execution is unavailable in this control.')),
              dict(role='user',content=json.dumps(initial,sort_keys=True))]
    events=[];patches=[];scratch=[];finished=False;public=baseline
    for turn in range(cap):
        payload=dict(model=old.MODEL,messages=messages,temperature=0,seed=761,max_tokens=4096,
                     response_format={'type':'json_object'},chat_template_kwargs={'enable_thinking':False})
        key,response,reused=old.request(payload,calls);event=dict(turn=turn,request_hash=key,reused=reused)
        if response['error']:event['error']=response['error'];events.append(event);break
        messages.append(dict(role='assistant',content=response['response']['choices'][0]['message'].get('content') or ''))
        try:
            action=parse(response['response']);event['action']=action
            if 'read' in action:
                if not 1<=len(action['read'])<=3:raise ValueError('Read one to three files')
                allowed={r['path'] for r in inventory};parts=[]
                for path in action['read']:
                    if path not in allowed:raise ValueError('Not in public inventory')
                    parts.append(dict(path=path,text=(case/path).read_text()))
                event['read_bytes']=sum(len(p['text'].encode()) for p in parts);feedback=dict(requested_source=parts)
            elif 'check' in action:
                if not checks:raise ValueError('Scratch checks unavailable in control')
                ast.parse(action['check']);name=f'scratch_{len(scratch)}.py';(case/name).write_text(action['check']);scratch.append(name)
                report=execute(case,asset,[name],f'check_{turn}');test_runs.append(report);event['check_test']=report
                feedback=dict(own_check_output=public_output(report,case),own_check_path=name)
            elif 'edits' in action:
                event['changed']=apply_edits(case,asset,action);patches.append(action)
                public=execute(case,asset,targets,f'public_{turn}');test_runs.append(public);event['public_test']=public
                feedback=dict(public_test_output=public_output(public,case),public_pass=public['returncode']==0,
                              instruction='Review full requirement, self-check if useful, then finish or continue.')
                if scratch:
                    report=execute(case,asset,scratch,f'scratch_{turn}');test_runs.append(report);event['scratch_retest']=report
                    feedback['own_check_output']=public_output(report,case)
            else:finished=True;events.append(event);break
            messages.append(dict(role='user',content=json.dumps(feedback,sort_keys=True)))
        except (ValueError,KeyError,TypeError,SyntaxError) as exc:
            event['interface_error']=str(exc);messages.append(dict(role='user',content=json.dumps({'interface_error':str(exc)})))
        for path,digest in protected.items():assert sha(case/path)==digest,path
        events.append(event);dump(out/'events.json',events)
    # Private test file is absent during all eligible reader/scratch actions.
    assert not (case/'heldout_current.py').exists()
    (case/'heldout_current.py').write_text(task['hidden_test'])
    final_public=execute(case,asset,targets,'final_public');heldout=execute(case,asset,['heldout_current.py'],'heldout')
    test_runs.extend([final_public,heldout])
    for path,digest in protected.items():assert sha(case/path)==digest,path
    result=dict(task=task['id'],asset=asset_name,policy=policy,checks_enabled=checks,call_cap=cap,
        complete=final_public['returncode']==0 and heldout['returncode']==0,finished=finished,
        public_pass=final_public['returncode']==0,heldout_pass=heldout['returncode']==0,
        representation=representation,selection=work,selected=[r['id'] for r in chosen],events=events,patches=patches,
        baseline=baseline,final_public=final_public,heldout=heldout,test_runs=test_runs,
        scratch=[dict(path=p,content=(case/p).read_text()) for p in scratch],
        source_base=source_hashes(source,asset),source_result=source_hashes(case,asset),
        protected_hashes=protected,prior_tests=prior,prior_memory=memory or [],source=str(source.relative_to(ROOT)),
        logical_prompt_tokens=sum(load(calls/f'{e["request_hash"]}-response.json')['response'].get('usage',{}).get('prompt_tokens',0) for e in events),
        logical_completion_tokens=sum(load(calls/f'{e["request_hash"]}-response.json')['response'].get('usage',{}).get('completion_tokens',0) for e in events),
        wall_seconds=time.perf_counter()-wall)
    dump(out/'result.json',result);print(json.dumps({k:result[k] for k in ['task','policy','checks_enabled','complete','logical_prompt_tokens','logical_completion_tokens']}),flush=True)
    return result,case


def develop(out):
    out=fresh(out);calls=out/'calls';calls.mkdir();results=[]
    task=load(ROOT/'phase6/runs/transfer/tasks.json')[1]
    prior_tasks=load(ROOT/'phase6/development-tasks.json')+[load(ROOT/'phase6/runs/transfer/tasks.json')[0]]
    source=ROOT/'phase6/runs/transfer/states/transfer-get-key-literal'
    prior=[t[k] for t in prior_tasks for k in ['public_test','hidden_test']];memory=load(source/'lineage.json')
    dump(out/'task.json',task)
    for checks in [False,True]:
        for policy in ['ordinary_access','empirical_reuse']:
            row,_=attempt(task,source,'dotenv',policy,checks,out/f'{policy}-{checks}',calls,prior,memory)
            results.append(row);dump(out/'results.json',results)
    dump(out/'execution.json',dict(timestamp=old.stamp(),script_sha256=sha(__file__)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args();develop(args.out)
