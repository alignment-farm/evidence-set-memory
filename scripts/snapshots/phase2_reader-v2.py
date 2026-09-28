"""Fixed QA reader with actual source citations, visible fallback, and raw traces."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.request
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
SCRIPT_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'.cache/reconnaissance/MuSiQue'))
from metrics.answer import compute_exact,compute_f1

RULES='''Answer the question using the supplied source paragraphs. Return only JSON:
{"answer":"short answer", "citations":[integer paragraph IDs supporting the reasoning]}.
Cite the evidence needed to connect the question to the answer, including intermediate
facts. If evidence is insufficient, return {"answer":"", "citations":[]}.
Do not invent evidence or cite paragraphs not supplied. /no_think'''


def parse(response):
    try:
        text=response['choices'][0]['message']['content'].split('</think>')[-1].strip()
        if text.startswith('```'): text=text.split('\n',1)[1].rsplit('```',1)[0]
        result=json.loads(text)
        assert isinstance(result['answer'],str) and isinstance(result['citations'],list)
        assert all(type(i)==int for i in result['citations'])
        return result
    except (KeyError,ValueError,TypeError,IndexError,AssertionError):
        return dict(answer='',citations=[],parse_error=True)


def grade(answer,label,selected):
    aliases=[label['answer'],*label['aliases']]
    em=max(compute_exact(a,answer['answer']) for a in aliases)
    f1=max(compute_f1(a,answer['answer']) for a in aliases)
    cites=set(answer['citations']);gold=set(label['supports'])
    citation_valid=cites.issubset(selected)
    return dict(answer_em=em,answer_f1=f1,citations_complete=gold.issubset(cites),
                citations_valid=citation_valid,complete=int(em and gold.issubset(cites) and citation_valid),
                retrieved_complete=gold.issubset(selected))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--split',choices=['development','confirmation'],default='development')
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--limit',type=int,default=6)
    parser.add_argument('--ordinary-arm',required=True)
    parser.add_argument('--model',default='docker.io/ai/qwen3.8:27b-q4_K_M')
    args=parser.parse_args()
    if args.out.exists(): raise RuntimeError('Use a new output path')
    if args.split=='confirmation':
        freeze=json.loads((ROOT/'phase2/freeze.json').read_text())
        for name,digest in freeze['files'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        assert args.model==freeze['reader_model']
    args.out.mkdir(parents=True)
    cache=ROOT/'.cache/phase2/partitions'
    examples=json.loads((cache/f'{args.split}-inputs.json').read_text())
    labels={l['id']:l for l in json.loads((cache/f'{args.split}-labels.json').read_text())}
    selected_rows=json.loads(args.selection.read_text())
    available={r['id'] for r in selected_rows}
    examples=[e for e in examples if e['id'] in available][:args.limit]
    rows=[];calls={};errors=0
    started=time.perf_counter()
    for index,e in enumerate(examples):
        label=labels[e['id']]
        by_id={p['idx']:p for p in e['paragraphs']}
        arms={arm:next(r['selected'] for r in selected_rows if r['id']==e['id'] and r['arm']==arm)
              for arm in [args.ordinary_arm,'learned_unary','exact','relaxed_swap']}
        arms.update(all=list(by_id),no_context=[],oracle_support=label['supports'],
                    support_removed=label['supports'][:-1])
        outputs={}
        # All-evidence first so fallback never requires a hidden quality trigger.
        for arm in ['all',*sorted(set(arms)-{'all'})]:
            ids=sorted(arms[arm]);paragraphs=[by_id[i] for i in ids]
            user=json.dumps(dict(question=e['question'],paragraphs=paragraphs),sort_keys=True)
            rules=RULES if arm!='no_context' else 'Answer from your existing knowledge. No sources are supplied. Return only JSON with a short answer and citations: []. If unknown use an empty answer. /no_think'
            payload=dict(model=args.model,messages=[dict(role='system',content=rules),dict(role='user',content=user)],
                         temperature=0,seed=761,max_tokens=512,response_format=dict(type='json_object'),
                         chat_template_kwargs=dict(enable_thinking=False))
            key=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
            reused=key in calls
            if not reused:
                if len(calls)>=240: raise RuntimeError('Request cap')
                dump(args.out/f'{key}-request.json',payload)
                start=time.perf_counter()
                req=urllib.request.Request('https://mac-studio-7hr7.taile71f88.ts.net/engines/v1/chat/completions',
                     data=json.dumps(payload).encode(),headers={'Content-Type':'application/json',
                     'User-Agent':'evidence-set-memory-phase2-reader/1.0'})
                try:
                    with urllib.request.urlopen(req,timeout=180) as response: result=json.loads(response.read())
                    answer=parse(result);error=None
                except Exception as exc:
                    result={};answer=dict(answer='',citations=[],request_error=True);error=repr(exc);errors+=1
                calls[key]=dict(response=result,answer=answer,error=error,wall_seconds=time.perf_counter()-start)
                dump(args.out/f'{key}-response.json',calls[key])
                print(json.dumps(dict(case=index+1,arm=arm,requests=len(calls),seconds=calls[key]['wall_seconds'],error=error)),flush=True)
                if errors>=2:
                    dump(args.out/'failure.json',dict(errors=errors,reason='Two endpoint failures; no automatic substitution'))
                    raise RuntimeError('Endpoint failures')
            answer=calls[key]['answer'];outputs[arm]=answer
            fallback=not answer['answer'].strip() or not set(answer['citations']).issubset(ids) or bool(answer.get('parse_error'))
            # Public inability/format trigger; wrong confident answers are not oracle-repaired.
            final=outputs['all'] if fallback else answer
            row=dict(id=e['id'],arm=arm,selected=ids,answer=answer,request_hash=key,reused=reused,
                     source_chars=sum(len(p['text'])+len(p['title']) for p in paragraphs),
                     fallback=fallback and arm!='all',**grade(answer,label,ids),
                     after_fallback=grade(final,label,list(by_id) if fallback else ids))
            rows.append(row);dump(args.out/'outcomes.json',rows)
    summary={}
    for arm in arms:
        group=[r for r in rows if r['arm']==arm]
        summary[arm]=dict(n=len(group),complete=sum(r['complete'] for r in group),
                         answer_em=sum(r['answer_em'] for r in group),
                         answer_f1=sum(r['answer_f1'] for r in group)/len(group),
                         retrieval_complete=sum(r['retrieved_complete'] for r in group),
                         fallback_calls=sum(r['fallback'] for r in group),
                         after_fallback_complete=sum(r['after_fallback']['complete'] for r in group),
                         after_fallback_answer_em=sum(r['after_fallback']['answer_em'] for r in group),
                         source_chars=sum(r['source_chars'] for r in group),
                         # Per-policy tokens include repeated use, unlike physical dedup total below.
                         prompt_tokens=sum(calls[r['request_hash']]['response'].get('usage',{}).get('prompt_tokens',0) for r in group),
                         completion_tokens=sum(calls[r['request_hash']]['response'].get('usage',{}).get('completion_tokens',0) for r in group))
        for field in ['prompt_tokens','completion_tokens']:
            summary[arm]['fallback_'+field]=sum(calls[next(a['request_hash'] for a in rows if a['id']==r['id'] and a['arm']=='all')]['response'].get('usage',{}).get(field,0) for r in group if r['fallback'])
    dump(args.out/'summary.json',summary)
    dump(args.out/'costs.json',dict(model=args.model,requests=len(calls),mapped_outcomes=len(rows),
             prompt_tokens=sum(c['response'].get('usage',{}).get('prompt_tokens',0) for c in calls.values()),
             completion_tokens=sum(c['response'].get('usage',{}).get('completion_tokens',0) for c in calls.values()),
             request_seconds=sum(c['wall_seconds'] for c in calls.values()),wall_seconds=time.perf_counter()-started,
             errors=errors,usage_missing=sum('usage' not in c['response'] for c in calls.values()),
             script_sha256=SCRIPT_SHA,
             timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
