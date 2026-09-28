"""Authored chronological configuration experiment; native CPython execution.

Write-once outputs. `develop`, `freeze`, `confirm`; no confirmation data generated
by development. No expected value or feedback is accepted by representation/search.
"""
import argparse
import configparser
import hashlib
import itertools
import json
import platform
import random
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['missing_request', 'set_size', 'unresolved_edges', 'resolved_edges']
TOKEN = re.compile(r'\$\$|\$\{([^}]+)\}')
NAIVE = re.compile(r'\$\{([^}:]+):[^}]+\}')
STAGES = ['initial', 'repeat', 'value_correction', 'dependency_revision',
          'revised_repeat', 'old_valid_obligation']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')


def load(path):
    return json.loads(Path(path).read_text())


def fresh(path):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f'Preserving existing output: {path}')
    path.mkdir(parents=True)
    return path


def histories(seed, count, prefix):
    """Independent expected strings are authored here, not computed by executor."""
    rng = random.Random(seed)
    result = []
    for h in range(count):
        tag = f'{prefix}-{h}-{rng.randrange(1000000)}'
        names = [f's_{rng.randrange(1000000000)}' for _ in range(8)]
        assert len(set(names)) == 8
        a, b, c, zone, local = [f'v{rng.randrange(1000000000)}' for _ in range(5)]
        mode = h % 3
        leaf = a if mode == 0 else '${zone}/' + a
        options = [{'value': f'${{{names[1]}:value}}/${{{names[3]}:value}}'},
                   {'value': f'${{{names[2]}:value}}'}, {'value': leaf},
                   {'value': b}, {'value': c},
                   {'value': f'old/${{{names[4]}:value}}'},
                   {'value': f'decoy/${{{names[7]}:value}}'}, {'value': 'unused'},
                   {'zone': zone}]
        if mode == 2:
            options[2]['zone'] = local
        sections = names + ['DEFAULT']
        archive = []
        def add(i, revision, opts, scope='production'):
            archive.append(dict(id=f'{tag}/{scope}/{sections[i]}@{revision}',
                                section=sections[i], revision=revision, scope=scope,
                                options=dict(opts)))
        for i, opts in enumerate(options):
            add(i, 1, opts)
        # Same section names in another environment test mandatory scope filtering.
        for i in [0, 2, 3]:
            add(i, 7, {'value': 'staging-only'}, 'staging')
        stages = []
        val = a if mode == 0 else (zone if mode == 1 else local) + '/' + a
        expected = val + '/' + b
        for stage in range(6):
            if stage == 2:
                a = f'corrected{rng.randrange(1000000000)}'
                opts = dict(options[2]); opts['value'] = a if mode == 0 else '${zone}/' + a
                add(2, 2, opts)
                val = a if mode == 0 else (zone if mode == 1 else local) + '/' + a
                expected = val + '/' + b
            if stage == 3:
                if h % 2 == 0:
                    # Escaped pseudo-reference is literal, not a dependency.
                    add(0, 2, {'value': f'${{{names[4]}:value}}/$${{{names[7]}:value}}'})
                    expected = c + '/${' + names[7] + ':value}'
                else:
                    add(0, 2, {'value': f'${{{names[1]}:value}}/${{{names[4]}:value}}/${{zone}}'})
                    expected = val + '/' + c + '/' + zone
            request = dict(section=names[5] if stage == 5 else names[0],
                           option='value', scope='production')
            visible = [dict(r, options=dict(r['options'])) for r in archive]
            rng.shuffle(visible)
            stages.append(dict(id=f'{tag}/{stage}', stage=STAGES[stage],
                               request=request, records=visible,
                               expected='old/' + c if stage == 5 else expected))
        result.append(dict(id=tag, syntax_family=mode, episodes=stages))
    return result


def eligible(request, records):
    """Public, mandatory authority/scope rule shared by all policies."""
    index = {}
    for r in records:
        if r['scope'] == request['scope']:
            if r['section'] not in index or r['revision'] > index[r['section']]['revision']:
                index[r['section']] = r
    return [index[k] for k in sorted(index)]


def dependencies(record, index, grammar):
    """Public syntax representation, not a necessity label or examiner certificate.

    Scope: generated single-line INI options; local option recursion is supported.
    DEFAULT literal zone has no outgoing edges in this workload.
    """
    if grammar == 'explicit_only':
        return set(NAIVE.findall(record['options'].get('value', '')))
    found = set()
    visited = set()
    def walk(section, option):
        key = (section, option.lower())
        if key in visited:
            return
        visited.add(key)
        source = index.get(section)
        if source is None or key[1] not in source['options']:
            source = index.get('DEFAULT')
        if source is None or key[1] not in source['options']:
            raise ValueError(f'unresolved public source option {key}')
        if source['section'] != record['section']:
            found.add(source['section'])
            # That record's own representation handles further value references.
            if key[1] == 'value':
                return
        value = source['options'][key[1]]
        for token in TOKEN.finditer(value):
            if token.group(1) is None:  # $$ consumes both dollar signs
                continue
            parts = token.group(1).split(':')
            if len(parts) == 1:
                walk(section, parts[0])
            elif len(parts) == 2:
                walk(parts[0], parts[1])
            else:
                raise ValueError('unsupported interpolation syntax')
    if 'value' in record['options']:
        walk(record['section'], 'value')
    return found - {record['section']}


def represent(request, records, grammar):
    start = time.perf_counter()
    pool = eligible(request, records)
    index = {r['section']: r for r in pool}
    positions = {r['section']: i for i, r in enumerate(pool)}
    edges = []
    for i, r in enumerate(pool):
        for target in sorted(dependencies(r, index, grammar)):
            if target not in positions:
                raise ValueError('dependency missing from candidate pool')
            edges.append((i, positions[target]))
    return dict(pool=pool, edges=edges, root=positions[request['section']],
                seconds=time.perf_counter()-start,
                archive_records_scanned=len(records),
                option_characters_scanned=sum(len(k)+len(v) for r in pool for k,v in r['options'].items()))


def feature(z, rep):
    """Multilinear extension; binary unresolved edges encode actual complements."""
    root = 1-z[..., rep['root']]
    count = z.sum(axis=-1)
    unresolved = np.zeros_like(count)
    resolved = np.zeros_like(count)
    for i, j in rep['edges']:
        unresolved += z[..., i]*(1-z[..., j])
        resolved += z[..., i]*z[..., j]
    return np.stack([root, count, unresolved, resolved], axis=-1)


def vertices(n):
    return ((np.arange(2**n)[:, None] >> np.arange(n)) & 1).astype(np.float64)


def render(request, selected):
    """Complete downstream operation: unmodified native CPython interpreter."""
    start = time.perf_counter()
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    try:
        for r in selected:
            parser.read_dict({r['section']: r['options']})
        value = parser.get(request['section'], request['option'])
        answer = dict(value=value)
    except (configparser.Error, KeyError, ValueError) as error:
        answer = dict(error=type(error).__name__, message=str(error))
    answer['seconds'] = time.perf_counter()-start
    return answer


def grade(episode, chosen, answer):
    valid = {r['id'] for r in eligible(episode['request'], episode['records'])}
    return answer.get('value') == episode['expected'] and all(r['id'] in valid for r in chosen)


def closure(rep):
    chosen = {rep['root']}
    while True:
        expanded = chosen | {j for i, j in rep['edges'] if i in chosen}
        if expanded == chosen:
            return sorted(chosen)
        chosen = expanded


def selected(pool, indices):
    return [pool[i] for i in sorted(indices)]


def byte_count(rows):
    return len(json.dumps(rows, sort_keys=True).encode())


def search(rep, weights, method, seed=87):
    start = time.perf_counter(); n = len(rep['pool'])
    work = dict(discrete_evaluations=0, gradient_steps=0)
    if method == 'exact':
        z = vertices(n); scores = feature(z, rep) @ weights
        best = z[int(np.argmin(scores))]
        work['discrete_evaluations'] = len(z)
    else:
        rng = np.random.default_rng(seed)
        candidates = []
        starts = [np.full(n, .5), np.zeros(n), np.ones(n), rng.random(n)]
        for start_z in starts:
            z = start_z.copy()
            candidates.append((z >= .5).astype(float))
            for _ in range(60):
                grad = np.full(n, weights[1]); grad[rep['root']] -= weights[0]
                for i, j in rep['edges']:
                    grad[i] += weights[2]*(1-z[j]) + weights[3]*z[j]
                    grad[j] += (weights[3]-weights[2])*z[i]
                z = np.clip(z-.05*grad, 0, 1)
            candidates.append((z >= .5).astype(float))
        work['gradient_steps'] = 240
        scores = feature(np.array(candidates), rep) @ weights
        work['discrete_evaluations'] = len(candidates)
        best = candidates[int(np.argmin(scores))].copy()
        if method == 'relax_flip':
            for _ in range(20):
                proposals = np.repeat(best[None], n+1, axis=0)
                proposals[np.arange(1,n+1), np.arange(n)] = 1-best
                scores = feature(proposals, rep) @ weights
                work['discrete_evaluations'] += n+1
                winner = int(np.argmin(scores))
                if winner == 0:
                    break
                best = proposals[winner]
    work.update(seconds=time.perf_counter()-start, energy=float(feature(best, rep)@weights))
    return np.flatnonzero(best).tolist(), work


def acquire(data):
    start = time.perf_counter(); attempts=[]; rng=random.Random(518)
    for history in data:
        for ep in history['episodes']:
            rep = represent(ep['request'], ep['records'], 'native_syntax')
            good = closure(rep); n=len(rep['pool'])
            proposals=[('ordinary_closure', good)]
            proposals += [('omission', [j for j in good if j != i]) for i in good]
            proposals += [('superset', sorted(set(good)|{i})) for i in range(n) if i not in good]
            proposals += [('random', sorted(rng.sample(range(n), rng.randrange(n+1)))) for _ in range(24)]
            for origin, indices in proposals:
                chosen = selected(rep['pool'], indices)
                answer = render(ep['request'], chosen)
                attempts.append(dict(episode=ep['id'], origin=origin,
                                     ids=[r['id'] for r in chosen], size=len(chosen),
                                     answer=answer, complete=grade(ep,chosen,answer)))
    return attempts, dict(seconds=time.perf_counter()-start, executions=len(attempts),
                         parser_seconds=sum(x['answer']['seconds'] for x in attempts),
                         proposal_policy='24 random + ordinary closure + all omissions and single supersets')


def fit(data, attempts, grammar, balanced=False):
    start=time.perf_counter(); by_episode={}
    for attempt in attempts:
        by_episode.setdefault(attempt['episode'], []).append(attempt)
    differences=[]; kinds=[]; pair_types={'complete_over_failed':0,'shorter_success':0}
    for history in data:
        for ep in history['episodes']:
            rep=represent(ep['request'],ep['records'],grammar)
            positions={r['id']: i for i,r in enumerate(rep['pool'])}
            rows=by_episode[ep['id']]
            features=[]
            for row in rows:
                z=np.zeros(len(rep['pool'])); z[[positions[x] for x in row['ids']]]=1
                features.append(feature(z,rep))
            # All observed successes vs failures; among successes prefer fewer rows.
            for i,a in enumerate(rows):
                if not a['complete']:
                    continue
                for j,b in enumerate(rows):
                    kind = 'complete_over_failed' if not b['complete'] else 'shorter_success'
                    if not b['complete'] or a['size'] < b['size']:
                        differences.append(features[i]-features[j]); pair_types[kind]+=1;kinds.append(kind)
    x=torch.tensor(np.array(differences),dtype=torch.float64)
    pair_weight=torch.tensor([len(kinds)/(2*pair_types[k]) if balanced else 1. for k in kinds],dtype=torch.float64)
    # Four coefficients: smallest functioning structured specialist, no pretraining.
    initial=np.random.default_rng(23).normal(0,.2,4)
    w=torch.tensor(initial,dtype=torch.float64,requires_grad=True)
    optimizer=torch.optim.Adam([w],lr=.05)
    trace=[]
    for step in range(400):
        optimizer.zero_grad()
        loss=(pair_weight*torch.nn.functional.softplus(x@w + 1)).mean()+.0001*w.square().sum()
        loss.backward(); optimizer.step()
        if step in [0,49,99,199,399]:
            trace.append(dict(step=step+1,loss=float(loss.detach()),weights=w.detach().tolist()))
    return dict(grammar=grammar,balanced_pair_classes=balanced,weights=w.detach().tolist(),initial=initial.tolist(),
                train=dict(seconds=time.perf_counter()-start,optimizer_steps=400,
                           pairs=len(differences),pair_types=pair_types,
                           pair_presentations=400*len(differences),trace=trace))


def evaluate(data, model, grammar, methods):
    outcomes=[]
    for method in methods:
        for history in data:
            cache={}
            for ep in history['episodes']:
                # Cache validation/full execution do not need a dependency graph.
                eligibility_start=time.perf_counter()
                pool=eligible(ep['request'],ep['records'])
                eligibility_seconds=time.perf_counter()-eligibility_start
                key=json.dumps(ep['request'],sort_keys=True)
                current_ids={r['id'] for r in pool}
                entry=cache.get(key)
                hit=entry is not None and set(entry['ids']) <= current_ids
                invalidated=entry is not None and not hit
                work=dict(seconds=0.,discrete_evaluations=0,gradient_steps=0)
                rep=dict(pool=pool,seconds=0.,option_characters_scanned=0)
                if not hit and method!='all':
                    rep=represent(ep['request'],ep['records'],grammar)
                rep_seconds=rep['seconds']+eligibility_seconds
                if hit:
                    rows=[r for r in rep['pool'] if r['id'] in entry['ids']]
                    answer=dict(value=entry['value'],seconds=0.)
                    delivery_bytes=0; executions=0
                else:
                    if method=='ordinary':
                        t=time.perf_counter(); indices=closure(rep);work['seconds']=time.perf_counter()-t
                    elif method=='all':
                        indices=list(range(len(rep['pool'])))
                    else:
                        weights=np.array(model['initial'] if method=='untrained' else model['weights'])
                        indices,work=search(rep,weights,'exact' if method=='untrained' else method)
                    rows=selected(rep['pool'],indices)
                    answer=render(ep['request'],rows);executions=1;delivery_bytes=byte_count(rows)
                first_complete=grade(ep,rows,answer)
                first_ids=[r['id'] for r in rows]
                first_answer=dict(answer)
                repair=None
                # Public failure only. Exact-but-wrong native output does not trigger repair.
                if 'error' in answer:
                    t=time.perf_counter()
                    native_rep=represent(ep['request'],ep['records'],'native_syntax')
                    repaired_rows=selected(native_rep['pool'],closure(native_rep))
                    repair=dict(seconds=time.perf_counter()-t,ids=[r['id'] for r in repaired_rows],
                                delivery_bytes=byte_count(repaired_rows))
                    rows=repaired_rows;answer=render(ep['request'],rows)
                    repair['answer']=dict(answer);executions+=1;delivery_bytes+=repair['delivery_bytes']
                if 'value' in answer:
                    cache[key]=dict(ids=[r['id'] for r in rows],value=answer['value'])
                # Independent diagnostics are not eligible triggers or selection features.
                native=represent(ep['request'],ep['records'],'native_syntax')
                sufficient_ids={native['pool'][i]['id'] for i in closure(native)}
                outcomes.append(dict(method=method,history=history['id'],episode=ep['id'],stage=ep['stage'],
                    syntax_family=history['syntax_family'],cache_hit=hit,cache_invalidated=invalidated,
                    selected_ids=first_ids,answer=first_answer,first_complete=first_complete,
                    final_complete=grade(ep,rows,answer),repair=repair,executions=executions,
                    dependency_complete=sufficient_ids<=set(first_ids),minimum_dependency_count=len(sufficient_ids),
                    raw_candidate_count=len(ep['records']),eligible_count=len(rep['pool']),
                    representation_seconds=rep_seconds,representation_option_characters=rep['option_characters_scanned'],
                    work=work,delivery_bytes=delivery_bytes))
    summary={}
    for method in methods:
        rows=[x for x in outcomes if x['method']==method]
        summary[method]=dict(episodes=len(rows),first_complete=sum(x['first_complete'] for x in rows),
            final_complete=sum(x['final_complete'] for x in rows),cache_hits=sum(x['cache_hit'] for x in rows),
            cache_invalidations=sum(x['cache_invalidated'] for x in rows),
            repairs=sum(x['repair'] is not None for x in rows),
            parser_executions=sum(x['executions'] for x in rows),
            histories_all_first_complete=sum(all(x['first_complete'] for x in rows if x['history']==h['id']) for h in data),
            discrete_evaluations=sum(x['work']['discrete_evaluations'] for x in rows),
            gradient_steps=sum(x['work']['gradient_steps'] for x in rows),
            representation_seconds=sum(x['representation_seconds'] for x in rows),
            selection_seconds=sum(x['work']['seconds'] for x in rows),
            parser_seconds=sum(x['answer']['seconds']+(x['repair']['answer']['seconds'] if x['repair'] else 0) for x in rows),
            repair_selection_seconds=sum(x['repair']['seconds'] if x['repair'] else 0 for x in rows),
            delivery_bytes=sum(x['delivery_bytes'] for x in rows),
            selected_record_uses=sum(len(x['selected_ids']) for x in rows if not x['cache_hit']),
            raw_records_scanned=sum(x['raw_candidate_count'] for x in rows),
            representation_option_characters=sum(x['representation_option_characters'] for x in rows),
            by_stage={s:dict(n=sum(x['stage']==s for x in rows),
                            first_complete=sum(x['first_complete'] for x in rows if x['stage']==s)) for s in STAGES})
    return outcomes,summary


def refit(out, development):
    out=fresh(out); source=Path(development)
    data=load(source/'histories.json');attempts=load(source/'attempts.json')
    model=fit(data,attempts,'native_syntax',balanced=True)
    dump(out/'native_syntax-model.json',model)
    rows,summary=evaluate(data,model,'native_syntax',['ordinary','all','untrained','exact','relax','relax_flip'])
    dump(out/'outcomes.json',rows);dump(out/'summary.json',summary)
    dump(out/'provenance.json',dict(provenance(),reused_feedback={str(p.relative_to(ROOT)):sha(p)
                      for p in [source/'histories.json',source/'attempts.json']},new_label_executions=0))
    print(json.dumps(summary,indent=2))


def provenance():
    return dict(python=sys.version,torch=torch.__version__,numpy=np.__version__,platform=platform.platform(),
                configparser_sha256=sha(configparser.__file__),configparser_path=configparser.__file__,
                implementation_sha256=sha(__file__),torch_threads=torch.get_num_threads(),
                investigator=dict(model='gpt-6-astra',reasoning='high',provider='OpenAI',
                    session='01a0e7e4-68e2-7fb2-9a5d-2ea6873b86b8',source='observed turn_context',
                    backend_fingerprint=None,monetary_cost=None),
                git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))


def develop(out):
    out=fresh(out); data=histories(28092651,12,'development')
    dump(out/'histories.json',data)
    attempts,cost=acquire(data);dump(out/'attempts.json',attempts);dump(out/'acquisition-cost.json',cost)
    summaries={}
    for grammar in ['explicit_only','native_syntax']:
        model=fit(data,attempts,grammar);dump(out/f'{grammar}-model.json',model)
        rows,summary=evaluate(data,model,grammar,['untrained','exact','relax','relax_flip'])
        dump(out/f'{grammar}-outcomes.json',rows);summaries[grammar]=summary
    model=load(out/'native_syntax-model.json')
    rows,summary=evaluate(data,model,'native_syntax',['ordinary','all'])
    dump(out/'ordinary-outcomes.json',rows);summaries['ordinary']=summary
    dump(out/'summary.json',summaries);dump(out/'provenance.json',provenance())
    print(json.dumps(summaries,indent=2))


def freeze(out, development):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    files=[ROOT/'scripts/phase5_config.py',ROOT/'scripts/test_phase5_config.py',
           ROOT/'phase5/PROTOCOL.md',ROOT/'phase5/CLAIM.md',ROOT/'uv.lock',ROOT/'pyproject.toml',
           Path(development)/'native_syntax-model.json']
    dump(out,dict(files={str(p.relative_to(ROOT)):sha(p) for p in files},provenance=provenance(),
                  development=str(Path(development).relative_to(ROOT)),confirmation_seed=28092659,
                  confirmation_histories=12))


def confirm(out, frozen):
    freeze_data=load(frozen)
    for p,digest in freeze_data['files'].items():
        assert sha(ROOT/p)==digest,p
    out=fresh(out)
    # Only now, after validating the freeze, materialize later tasks and evaluator values.
    data=histories(freeze_data['confirmation_seed'],freeze_data['confirmation_histories'],'transfer')
    dump(out/'histories.json',data)
    model=load(ROOT/freeze_data['development']/'native_syntax-model.json')
    rows,summary=evaluate(data,model,'native_syntax',['ordinary','all','untrained','exact','relax','relax_flip'])
    dump(out/'outcomes.json',rows);dump(out/'summary.json',summary);dump(out/'provenance.json',provenance())
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    torch.set_num_threads(2)
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['develop','refit','freeze','confirm'])
    parser.add_argument('--out',required=True);parser.add_argument('--development',default=str(ROOT/'phase5/runs/development'))
    parser.add_argument('--freeze',default=str(ROOT/'phase5/freeze.json'))
    args=parser.parse_args()
    if args.command=='develop':develop(args.out)
    elif args.command=='refit':refit(args.out,args.development)
    elif args.command=='freeze':freeze(args.out,args.development)
    else:confirm(args.out,args.freeze)
