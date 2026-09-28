"""Public length-stop repair; collect all responses before opening evaluator labels."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from phase2_assets import dump
from phase2_reader import parse,grade

ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads(path.read_text())
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise RuntimeError('Write-once run')
    source=ROOT/'phase2/runs/confirmation-reader'
    prior=read(source/'costs.json')  # Require completed frozen run.
    responses={path.name.removesuffix('-response.json'):read(path) for path in source.glob('*-response.json')}
    eligible=sorted(key for key,value in responses.items() if value['response'].get('choices',[{}])[0].get('finish_reason')=='length')
    earlier=sum(read(ROOT/f'phase2/runs/{name}/costs.json')['requests'] for name in ['development-reader','semantic-development-reader'])
    assert len(eligible)<=24 and earlier+prior['requests']+len(eligible)<=300
    a.out.mkdir(parents=True)
    dump(a.out/'eligibility.json',dict(requests=eligible,rule='Public finish_reason == length; no correctness trigger',
        source_costs_sha256=hashlib.sha256((source/'costs.json').read_bytes()).hexdigest()))
    start=time.perf_counter();repairs={};errors=0
    for index,key in enumerate(eligible):
        payload=read(source/f'{key}-request.json');payload['max_tokens']=4096
        newkey=digest(payload);dump(a.out/f'{newkey}-request.json',payload)
        request=urllib.request.Request('https://mac-studio-7hr7.taile71f88.ts.net/engines/v1/chat/completions',
            data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'evidence-set-memory-budget-diagnostic/1.0'})
        t=time.perf_counter()
        try:
            with urllib.request.urlopen(request,timeout=600) as response:result=json.loads(response.read())
            error=None
        except Exception as exc:result={};error=repr(exc);errors+=1
        repairs[key]=dict(response=result,answer=parse(result),error=error,wall_seconds=time.perf_counter()-t,new_request_hash=newkey)
        dump(a.out/f'{newkey}-response.json',repairs[key])
        print(json.dumps(dict(repair=index+1,total=len(eligible),seconds=repairs[key]['wall_seconds'],error=error)),flush=True)
        if errors>=2:
            dump(a.out/'failure.json',dict(errors=errors,reason='Endpoint errors; no substitution'))
            raise RuntimeError('Two endpoint errors')
    # Evaluation begins only after acquisition of all public-triggered responses.
    labels={r['id']:r for r in read(ROOT/'.cache/phase2/partitions/confirmation-labels.json')}
    original=read(source/'outcomes.json');effective={**responses,**repairs};rows=[]
    for row in original:
        key=row['request_hash'];answer=parse(effective[key]['response'])
        full=next(r for r in original if r['id']==row['id'] and r['arm']=='all')
        fallback=not answer['answer'].strip() or not set(answer['citations']).issubset(row['selected']) or bool(answer.get('parse_error'))
        final=parse(effective[full['request_hash']]['response']) if fallback else answer
        rows.append(dict(id=row['id'],arm=row['arm'],selected=row['selected'],request_hash=key,
            repaired=key in repairs,answer=answer,fallback=fallback and row['arm']!='all',
            **grade(answer,labels[row['id']],row['selected']),
            after_fallback=grade(final,labels[row['id']],full['selected'] if fallback else row['selected'])))
    def usage(key,field):
        return responses[key]['response'].get('usage',{}).get(field,0)+(repairs[key]['response'].get('usage',{}).get(field,0) if key in repairs else 0)
    summary={}
    for arm in sorted({r['arm'] for r in rows}):
        group=[r for r in rows if r['arm']==arm]
        summary[arm]=dict(n=len(group),answer_em=sum(r['answer_em'] for r in group),
            answer_f1=sum(r['answer_f1'] for r in group)/len(group),complete=sum(r['complete'] for r in group),
            repaired_calls=sum(r['repaired'] for r in group),fallback_calls=sum(r['fallback'] for r in group),
            after_fallback_complete=sum(r['after_fallback']['complete'] for r in group),
            after_fallback_answer_em=sum(r['after_fallback']['answer_em'] for r in group))
        for field in ['prompt_tokens','completion_tokens']:
            summary[arm][field]=sum(usage(r['request_hash'],field) for r in group)
            summary[arm]['fallback_'+field]=sum(usage(next(f['request_hash'] for f in rows if f['id']==r['id'] and f['arm']=='all'),field) for r in group if r['fallback'])
    dump(a.out/'outcomes.json',rows);dump(a.out/'summary.json',summary)
    dump(a.out/'costs.json',dict(requests=len(repairs),errors=errors,
        prompt_tokens=sum(r['response'].get('usage',{}).get('prompt_tokens',0) for r in repairs.values()),
        completion_tokens=sum(r['response'].get('usage',{}).get('completion_tokens',0) for r in repairs.values()),
        request_seconds=sum(r['wall_seconds'] for r in repairs.values()),wall_seconds=time.perf_counter()-start,
        usage_missing=sum('usage' not in r['response'] for r in repairs.values()),
        remaining_length_stops=sum(r['response'].get('choices',[{}])[0].get('finish_reason')=='length' for r in repairs.values()),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        protocol_sha256=hashlib.sha256((ROOT/'phase2/READER_BUDGET_DIAGNOSTIC.md').read_bytes()).hexdigest(),
        note='Additional physical calls only. Per-policy summary already includes original calls plus retries. Post-freeze diagnosis, not fresh confirmation.'))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
