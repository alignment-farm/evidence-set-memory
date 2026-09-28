"""Bounded fixed-reader diagnostic. Run only during an available serving window.

uv run --no-project python scripts/reader_check.py --out runs/reader
No evaluator answers are included in requests. Each actual request/response saved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from quote_study import current, closure, execute, correct, dump, digest

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'docker.io/ai/qwen3:8B-Q4_K_M'
RULES = '''Prepare the requested quote from these source records. Follow the item ref
to its contract and the contract ref to its tax record. Revisions are authoritative:
for any key use its highest available revision. subtotal_cents = quantity *
unit_cents; tax_cents = floor((subtotal_cents * bps + 5000)/10000);
total_cents = subtotal_cents + tax_cents. Return only a JSON object with item,
quantity, subtotal_cents, tax_cents, total_cents and citations (three record IDs).
If a dependency is missing return {"error":"missing dependency"}. Do not invent
records, values, or citations. /no_think'''


def parse(content):
    text = content.split('</think>')[-1].strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1].rsplit('```', 1)[0]
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return {'error': 'invalid JSON'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--endpoint', default='https://mac-studio-7hr7.taile71f88.ts.net/engines/v1/chat/completions')
    args = parser.parse_args()
    if args.out.exists():
        raise RuntimeError('Write-once directory already exists')
    frozen = json.loads((ROOT/'runs/freeze.json').read_text())
    assert frozen['files']['scripts/reader_check.py'] == digest(Path(__file__))
    args.out.mkdir(parents=True)
    episodes = json.loads((ROOT/'runs/confirmation/histories.json').read_text())[0]['stages']
    outcomes = json.loads((ROOT/'runs/confirmation/outcomes.json').read_text())
    requests, results = {}, []
    for episode in episodes:
        task = episode['request']
        by_id = {r['id']: r for r in episode['records']}
        selections = {arm: [by_id[i] for i in next(r for r in outcomes
                      if r['arm'] == arm and r['task_id'] == task['task_id'])['selected']]
                      for arm in ['ordinary', 'exact', 'energy_swap']}
        selections['all_current'] = list(current(episode['records']).values())
        selections['omit_tax'] = [r for r in closure(task, episode['records']) if r['kind'] != 'tax']
        if episode['stage'] in [2, 3]:
            previous = episodes[episode['stage']-1]
            selections['stale'] = closure(previous['request'], previous['records'])
        for arm, selected in selections.items():
            message = json.dumps(dict(request=task, records=sorted(selected, key=lambda r: r['id'])), sort_keys=True)
            payload = dict(model=MODEL, temperature=0, seed=761, max_tokens=512,
                           chat_template_kwargs=dict(enable_thinking=False),
                           messages=[dict(role='system', content=RULES), dict(role='user', content=message)])
            key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            cached = key in requests
            if not cached:
                if len(requests) >= 24:
                    raise RuntimeError('Bounded request cap reached')
                dump(args.out/f'{key}-request.json', payload)
                start = time.perf_counter()
                req = urllib.request.Request(args.endpoint, data=json.dumps(payload).encode(),
                          headers={'Content-Type':'application/json', 'User-Agent':'evidence-set-memory-reader/1.0'})
                try:
                    with urllib.request.urlopen(req, timeout=180) as response:
                        raw = response.read()
                    obj = json.loads(raw)
                    answer = parse(obj['choices'][0]['message']['content'])
                    error = None
                except Exception as exc:
                    obj, answer, error = {}, {'error':'request failed'}, repr(exc)
                requests[key] = dict(response=obj, answer=answer, error=error,
                                     wall_seconds=time.perf_counter()-start)
                dump(args.out/f'{key}-response.json', requests[key])
                print(json.dumps(dict(stage=episode['stage'], arm=arm, request=len(requests),
                      seconds=requests[key]['wall_seconds'], error=error)), flush=True)
            answer = requests[key]['answer']
            primary_complete = correct(answer, episode['expected'])
            # Public fallback verification performs full ordinary work on EVERY call.
            # Charge it rather than presenting an evaluator-gated free repair.
            validation = execute(task, closure(task, episode['records']))
            needs_repair = not correct(answer, validation)
            repaired = validation if needs_repair else answer
            results.append(dict(task_id=task['task_id'], stage=episode['stage'], arm=arm,
                  request_hash=key, duplicate_context_reused=cached, primary_complete=primary_complete,
                  sufficient=set(episode['expected']['citations']).issubset({r['id'] for r in selected}),
                  controller_validation_source_records=len(episode['records']), controller_tool_calls=1,
                  repair=needs_repair, repaired_complete=correct(repaired, episode['expected']),
                  context_bytes=len(message.encode())))
            dump(args.out/'outcomes.json', results)
    usage = [r['response'].get('usage', {}) for r in requests.values()]
    dump(args.out/'summary.json', dict(unique_requests=len(requests), mapped_outcomes=len(results),
         usage_missing=sum(not u for u in usage),
         reported_prompt_tokens=sum(u.get('prompt_tokens', 0) for u in usage),
         reported_completion_tokens=sum(u.get('completion_tokens', 0) for u in usage),
         total_request_seconds=sum(r['wall_seconds'] for r in requests.values()),
         arms={arm:dict(n=sum(r['arm']==arm for r in results),
                       complete=sum(r['primary_complete'] for r in results if r['arm']==arm),
                       repairs=sum(r['repair'] for r in results if r['arm']==arm))
               for arm in sorted({r['arm'] for r in results})}))
    dump(args.out/'execution.json', dict(model=MODEL, endpoint=args.endpoint,
         temperature=0, requested_seed=761, requested_max_tokens=512, requested_thinking=False,
         server_setting_compliance='not independently verified',
         script_sha256=digest(Path(__file__)), provider='Docker Model Runner',
         finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    print((args.out/'summary.json').read_text())


if __name__ == '__main__':
    main()
