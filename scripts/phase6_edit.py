"""Bounded fixed-reader code edits against pinned python-dotenv source.

No evaluation test text enters source selection or reader payloads. The public
tests do; model edits are restricted to production source in isolated copies.
"""
import argparse
import ast
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PHASE=ROOT/'phase6'
ASSET=ROOT/'.cache/phase6/python-dotenv'
PYTHON=PHASE/'.venv/bin/python'
MODEL='docker.io/ai/qwen3.8:27b-q4_K_M'
ENDPOINT='https://mac-studio-7hr7.taile71f88.ts.net/engines/v1/chat/completions'
COMMIT='d6c0b9638349a7dd605d60ee555ff60421c1a594'
RULES='''You are a code-edit participant. Implement only the current requirement in the supplied repository revision. Current and prior requirements and unchanged upstream regression tests must pass. You have ordinary access to any source/test file in the inventory; request missing source rather than inventing unseen code. Return ONLY one JSON object, either {"read":["relative/path.py"]} to read up to 3 files, or {"edits":[{"path":"src/dotenv/file.py","old":"exact existing text","new":"replacement text"}]} to submit a patch. Each old string must occur exactly once. Edits apply in listed order. Empty edits means no change needed. Only existing src/dotenv/*.py production files may be changed; never change tests, dependencies or scope rules. Preserve public API compatibility except where the requirement explicitly changes it. The harness will run tests and can return public failure output for repair. Do not return shell commands, full rewritten files, or Markdown. Keep explanations out of the JSON. /no_think'''


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def load(path):return json.loads(Path(path).read_text())
def fresh(path):
    path=Path(path).resolve()
    if path.exists():raise FileExistsError(path)
    path.mkdir(parents=True);return path
def stamp():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())


def file_manifest(base):
    return {str(p.relative_to(base)):dict(sha256=sha(p),bytes=p.stat().st_size)
            for p in sorted(base.rglob('*')) if p.is_file() and '.git' not in p.parts
            and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts}


def copy_case(source,dest):
    dest=fresh(dest)
    shutil.copytree(source/'src',dest/'src');shutil.copytree(ASSET/'tests',dest/'tests')
    shutil.copy2(ASSET/'setup.cfg',dest/'setup.cfg')
    (dest/'tmp').mkdir();(dest/'bin').mkdir()
    entry=dest/'bin/dotenv'
    entry.write_text(f'#!{PYTHON}\nfrom dotenv.cli import cli\ncli()\n');entry.chmod(0o755)
    return dest


def test(case,targets,label):
    """Network denied; writes confined to the owned case, not other study/state."""
    start=time.perf_counter();case=case.resolve()
    profile=f'''(version 1) (allow default) (deny network*)
    (deny file-write* (require-all (require-not (subpath "{case}")) (require-not (literal "/dev/null")) (require-not (literal "/dev/ptmx")) (require-not (regex #"^/dev/ttys[0-9]+$"))))
    (deny file-read* (subpath "/Users/macos-user/.codex") (subpath "/Users/macos-user/.ssh"))'''
    env={'PATH':f'{case}/bin:{PYTHON.parent}:/usr/bin:/bin',
         'PYTHONPATH':str(case/'src'),'PYTHONDONTWRITEBYTECODE':'1',
         'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','TMPDIR':str(case/'tmp'),'LANG':'en_US.UTF-8'}
    report=case/f'{label}.xml'
    cmd=['/usr/bin/sandbox-exec','-p',profile,str(PYTHON),'-m','pytest','-q',
         '-p','no:cacheprovider','--basetemp',str(case/f'tmp/{label}'),
         '--junitxml',str(report),*targets]
    try:
        result=subprocess.run(cmd,cwd=case,env=env,text=True,stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,timeout=60)
        output=result.stdout;code=result.returncode
    except subprocess.TimeoutExpired as error:
        output=str(error.stdout);code=124
    summary={}
    if report.exists():
        suites=ET.parse(report).getroot()
        for key in ['tests','failures','errors','skipped']:
            summary[key]=sum(int(s.get(key,0)) for s in suites.iter('testsuite'))
    return dict(command=cmd,returncode=code,output=output,counts=summary,
                seconds=time.perf_counter()-start,source_sha256={str(p.relative_to(case)):sha(p) for p in (case/'src').rglob('*.py')})


def records(source):
    start=time.perf_counter();rows=[];inventory=[]
    for path in sorted((source/'src/dotenv').glob('*.py')):
        relative=str(path.relative_to(source));text=path.read_text();lines=text.splitlines(keepends=True)
        tree=ast.parse(text);nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
        occupied=set()
        for node in nodes:
            begin=min([node.lineno]+[d.lineno for d in node.decorator_list])-1;end=node.end_lineno
            occupied.update(range(begin,end));content=''.join(lines[begin:end])
            names={n.id for n in ast.walk(node) if isinstance(n,ast.Name)}
            rows.append(dict(id=relative+'::'+node.name,path=relative,symbol=node.name,text=content,
                             names=sorted(names),line=begin+1,kind='definition',sha256=hashlib.sha256(content.encode()).hexdigest()))
        header=''.join(line for i,line in enumerate(lines) if i not in occupied)
        rows.append(dict(id=relative+'::module',path=relative,symbol='module',text=header,
                         names=[],line=1,kind='module',sha256=hashlib.sha256(header.encode()).hexdigest()))
        inventory.append(dict(path=relative,bytes=len(text.encode()),symbols=[n.name for n in nodes]))
    for p in sorted((ASSET/'tests').glob('*.py')):
        inventory.append(dict(path='tests/'+p.name,bytes=p.stat().st_size))
    inventory.append(dict(path='README.md',bytes=(ASSET/'README.md').stat().st_size))
    return rows,inventory,dict(seconds=time.perf_counter()-start,files_scanned=len(list((source/'src/dotenv').glob('*.py'))),
                                characters_scanned=sum(len(r['text']) for r in rows),records=len(rows))


def tokens(text):return set(re.findall(r'[a-z_][a-z_0-9]+',text.lower()))


def rank(task,rows):
    q=tokens(task['request']+'\n'+task['public_test'])
    definitions=[r for r in rows if r['kind']=='definition']
    score=lambda r: (8*(r['symbol'].lower() in q)+len(q&tokens(r['text']))/(len(tokens(r['text']))**.5),r['id'])
    return sorted(definitions,key=score,reverse=True)


def with_headers(chosen,rows):
    ids={r['id'] for r in chosen};paths={r['path'] for r in chosen}
    ids|={r['id'] for r in rows if r['kind']=='module' and r['path'] in paths}
    return [r for r in rows if r['id'] in ids]


def select(task,rows,policy):
    begin=time.perf_counter();ordered=rank(task,rows)
    if policy=='all':chosen=rows
    elif policy=='root_only':chosen=with_headers(ordered[:1],rows)
    elif policy=='pointwise':chosen=with_headers(ordered[:3],rows)
    elif policy=='ordinary':
        q=tokens(task['request']);chosen=[r for r in ordered if r['symbol'].lower() in q][:4] or ordered[:1]
        # Two rounds of explicit referenced-symbol expansion, capped by native bytes.
        for _ in range(2):
            names=set().union(*(set(r['names']) for r in chosen))
            for row in ordered:
                if row not in chosen and row['symbol'] in names and sum(len(r['text']) for r in chosen)+len(row['text'])<=14000:
                    chosen.append(row)
        chosen=with_headers(chosen,rows)
    else:raise ValueError(policy)
    return chosen,dict(seconds=time.perf_counter()-begin,records=len(chosen),bytes=sum(len(r['text'].encode()) for r in chosen))


def parse_response(response):
    message=response['choices'][0]['message'];text=message.get('content') or ''
    decoder=json.JSONDecoder();found=[]
    for match in re.finditer(r'\{',text):
        try:
            obj,_=decoder.raw_decode(text[match.start():])
            if isinstance(obj,dict) and (isinstance(obj.get('edits'),list) or isinstance(obj.get('read'),list)):
                found.append(obj)
        except ValueError:pass
    if not found:raise ValueError('No schema-valid JSON read/edit object')
    return found[-1]


def apply_edits(case,obj):
    changed={}
    if len(obj['edits'])>12:raise ValueError('At most 12 exact replacements')
    for edit in obj['edits']:
        path=edit.get('path','')
        if not re.fullmatch(r'src/dotenv/[a-z_]+\.py',path):raise ValueError('Out-of-scope path')
        target=case/path
        if not target.is_file() or target.is_symlink():raise ValueError('Only existing source files')
        current=changed.get(path,target.read_text());old=edit['old'];new=edit['new']
        if not isinstance(old,str) or not old or not isinstance(new,str):raise ValueError('Nonempty exact old text required')
        if current.count(old)!=1:raise ValueError(f'Expected unique old text in {path}; found {current.count(old)}')
        changed[path]=current.replace(old,new,1)
    for path,text in changed.items():ast.parse(text,filename=path)
    for path,text in changed.items():(case/path).write_text(text)
    return list(changed)


def request(payload,calls):
    key=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    target=calls/f'{key}-response.json'
    if target.exists():return key,load(target),True
    dump(calls/f'{key}-request.json',payload);start=time.perf_counter()
    req=urllib.request.Request(ENDPOINT,json.dumps(payload).encode(),
         headers={'Content-Type':'application/json','User-Agent':'evidence-set-memory-phase6/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=360) as response:raw=json.loads(response.read())
        error=None
    except Exception as exc:raw={};error=repr(exc)
    result=dict(response=raw,error=error,seconds=time.perf_counter()-start,timestamp=stamp())
    dump(target,result)
    print(json.dumps(dict(request=key,seconds=result['seconds'],error=error,
                         usage=raw.get('usage'),finish=[c.get('finish_reason') for c in raw.get('choices',[])])),flush=True)
    return key,result,False


def attempt(task,source,out,policy,calls,prior_tests=None,prior_memory=None,selection_override=None):
    out=fresh(out)
    work_id=hashlib.sha256(str(out).encode()).hexdigest()[:20]
    case=copy_case(source,ROOT/'.cache/phase6/work'/work_id)
    (case/'public_current.py').write_text(task['public_test'])
    (case/'heldout_current.py').write_text(task['hidden_test'])
    for i,text in enumerate(prior_tests or []):(case/f'prior_{i}.py').write_text(text)
    public_targets=['tests','public_current.py']+[f'prior_{i}.py' for i in range(len(prior_tests or []))]
    baseline=test(case,public_targets,'baseline');dump(out/'baseline.json',baseline)
    rows,inventory,representation=records(source)
    chosen,selection=select(task,rows,policy) if selection_override is None else selection_override
    initial=dict(requirement=task['request'],public_acceptance_test=task['public_test'],inventory=inventory,
                 evidence=[{k:r[k] for k in ['id','path','line','text','sha256']} for r in chosen],
                 prior_completed_changes=prior_memory or [],
                 baseline_test_output=baseline['output'][-6000:].replace(str(case),'<CASE>'))
    messages=[dict(role='system',content=RULES),dict(role='user',content=json.dumps(initial,sort_keys=True))]
    events=[];patches=[];public=baseline;first_patch_success=None
    if baseline['returncode']!=0:
        for turn in range(4):
            payload=dict(model=MODEL,messages=messages,temperature=0,seed=761,max_tokens=4096,
                         response_format={'type':'json_object'},chat_template_kwargs={'enable_thinking':False})
            key,response,reused=request(payload,calls)
            event=dict(turn=turn,request_hash=key,reused=reused)
            if response['error']:
                event['error']=response['error'];events.append(event);break
            raw=response['response'];content=raw['choices'][0]['message'].get('content') or ''
            messages.append(dict(role='assistant',content=content))
            try:
                obj=parse_response(raw);event['action']=obj
                if 'read' in obj:
                    if not 1<=len(obj['read'])<=3:raise ValueError('Read 1 to 3 files')
                    available={r['path'] for r in inventory};parts=[]
                    for path in obj['read']:
                        if path not in available:raise ValueError('Path is not public source inventory')
                        target=case/path if path.startswith('src/') or path.startswith('tests/') else ASSET/path
                        parts.append(dict(path=path,text=target.read_text()))
                    event['read_bytes']=sum(len(p['text'].encode()) for p in parts)
                    messages.append(dict(role='user',content=json.dumps({'requested_source':parts})))
                else:
                    event['changed']=apply_edits(case,obj);patches.append(obj)
                    public=test(case,public_targets,f'public_{turn}');dump(out/f'public-{turn}.json',public)
                    event['public_test']=public
                    if first_patch_success is None:first_patch_success=public['returncode']==0
                    if public['returncode']==0:
                        events.append(event);break
                    messages.append(dict(role='user',content=json.dumps({'public_test_failure':public['output'][-14000:].replace(str(case),'<CASE>')})))
            except (ValueError,KeyError,TypeError,SyntaxError) as error:
                event['interface_error']=str(error)
                messages.append(dict(role='user',content=json.dumps({'interface_error':str(error),'instruction':'Correct the JSON exact-match edit or read missing source.'})))
            events.append(event);dump(out/'events.json',events)
    # Only after stopping: hidden failure cannot cause any further model request.
    heldout=test(case,['heldout_current.py'],'heldout');dump(out/'heldout.json',heldout)
    result=dict(task=task['id'],policy=policy,complete=public['returncode']==0 and heldout['returncode']==0,
                public_pass=public['returncode']==0,heldout_pass=heldout['returncode']==0,
                initial_noop=baseline['returncode']==0,first_patch_public_pass=first_patch_success,
                selected=[r['id'] for r in chosen],representation=representation,selection=selection,
                events=events,patches=patches,baseline=baseline,heldout=heldout,
                source_base={str(p.relative_to(source)):sha(p) for p in (source/'src').rglob('*.py')},
                source_result={str(p.relative_to(case)):sha(p) for p in (case/'src').rglob('*.py')},
                logical_prompt_tokens=sum(load(calls/f'{e["request_hash"]}-response.json')['response'].get('usage',{}).get('prompt_tokens',0) for e in events),
                logical_completion_tokens=sum(load(calls/f'{e["request_hash"]}-response.json')['response'].get('usage',{}).get('completion_tokens',0) for e in events))
    dump(out/'result.json',result);dump(out/'events.json',events)
    print(json.dumps(dict(task=task['id'],policy=policy,complete=result['complete'],calls=len(events),
                         tokens=result['logical_prompt_tokens']+result['logical_completion_tokens'])),flush=True)
    return result,case


def preflight(out):
    out=fresh(out)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ASSET,text=True).strip()==COMMIT
    case=copy_case(ASSET,out/'case');result=test(case,['tests'],'upstream')
    dump(out/'upstream-tests.json',result)
    dump(out/'source-manifest.json',file_manifest(ASSET))
    dump(out/'provenance.json',dict(timestamp=stamp(),source_commit=COMMIT,script_sha256=sha(__file__),
        python=subprocess.check_output([str(PYTHON),'--version'],text=True).strip(),
        dmr_inspect=json.loads(subprocess.check_output(['docker','model','inspect','qwen3.8:27b-q4_K_M'],text=True)),
        dmr_ps=subprocess.check_output(['docker','model','ps'],text=True)))
    print(json.dumps(result,indent=2))


def develop(out,only=None):
    out=fresh(out);calls=out/'calls';calls.mkdir();tasks=load(PHASE/'development-tasks.json')
    source=ASSET;prior_tests=[];memory=[];results=[]
    for task in tasks[:only]:
        candidates={}
        for policy in ['ordinary','all','pointwise','root_only']:
            result,case=attempt(task,source,out/f'{task["id"]}/{policy}',policy,calls,prior_tests,memory)
            results.append(result);candidates[policy]=(result,case)
        passing=[p for p in ['ordinary','all','pointwise','root_only'] if candidates[p][0]['complete']]
        if not passing:
            dump(out/'blocked.json',dict(task=task['id'],reason='No accepted complete source revision; diagnose before next task'))
            break
        chosen=passing[0];accepted,case=candidates[chosen]
        state=fresh(out/f'states/{task["id"]}');shutil.copytree(case/'src',state/'src');source=state
        prior_tests.extend([task['public_test'],task['hidden_test']])
        memory.append(dict(requirement=task['request'],accepted_policy=chosen,patches=accepted['patches'],source_hashes=accepted['source_result']))
        dump(out/f'states/{task["id"]}/lineage.json',memory)
    dump(out/'results.json',results)
    dump(out/'execution.json',dict(script_sha256=sha(__file__),timestamp=stamp(),calls=len(list(calls.glob('*-response.json')))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['preflight','develop']);parser.add_argument('--out',required=True)
    parser.add_argument('--only',type=int)
    args=parser.parse_args()
    if args.command=='preflight':preflight(args.out)
    else:develop(args.out,args.only)
