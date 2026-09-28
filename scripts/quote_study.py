"""Authored evidence-set mechanism experiment; stdlib only, run with uv.

Commands: develop --out runs/development; freeze; confirm --out runs/confirmation.
Every output directory is write-once. Evaluator gold never enters feature/search APIs.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['bias', 'query_item', 'current_fraction', 'item_fraction',
            'contract_fraction', 'tax_fraction', 'resolved_edges', 'root_edge']


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current(records):
    index = {}
    for record in records:
        key = record['key']
        if key not in index or record['revision'] > index[key]['revision']:
            index[key] = record
    return index


def generate(seed, count, prefix):
    """Generate ordered histories. Private expected values stay outside visible input."""
    rng = random.Random(seed)
    histories = []
    for h in range(count):
        tag = f'{prefix}-{h}-{rng.randrange(100000, 999999)}'
        keys = {kind: [f'{kind}-{tag}-{i}' for i in range(3)]
                for kind in ('item', 'contract', 'tax')}
        prices = [rng.randrange(100, 2500) for _ in range(3)]
        rates = [rng.choice([375, 625, 825, 975]) for _ in range(3)]
        routes = list(range(3))
        records = []
        for i in range(3):
            records.extend([
                dict(key=keys['item'][i], kind='item', revision=1,
                     ref=keys['contract'][i]),
                dict(key=keys['contract'][i], kind='contract', revision=1,
                     ref=keys['tax'][i], unit_cents=prices[i]),
                dict(key=keys['tax'][i], kind='tax', revision=1, bps=rates[i])])
        for r in records:
            r['id'] = f"{r['key']}@{r['revision']}"
        stages = []
        for stage in range(5):
            if stage == 2:
                prices[0] += rng.randrange(51, 201)
                records.append(dict(key=keys['contract'][0], kind='contract', revision=2,
                                    ref=keys['tax'][0], unit_cents=prices[0],
                                    id=keys['contract'][0] + '@2'))
            if stage == 3:
                routes[0] = 2
                records.append(dict(key=keys['item'][0], kind='item', revision=2,
                                    ref=keys['contract'][2], id=keys['item'][0] + '@2'))
            item_i = 1 if stage == 4 else 0
            route = routes[item_i]
            quantity = stages[0]['request']['quantity'] if stage == 1 else rng.randrange(2, 20)
            request = dict(item=keys['item'][item_i], quantity=quantity,
                           task_id=f'{prefix}-{h}-s{stage}')
            subtotal = quantity * prices[route]
            tax = (subtotal * rates[route] + 5000) // 10000
            # Independent private-world arithmetic, not calls to the production executor.
            citations = [f"{keys['item'][item_i]}@{2 if stage >= 3 and item_i == 0 else 1}",
                         f"{keys['contract'][route]}@{2 if stage >= 2 and route == 0 else 1}",
                         keys['tax'][route] + '@1']
            expected = dict(item=request['item'], quantity=quantity,
                            subtotal_cents=subtotal, tax_cents=tax,
                            total_cents=subtotal + tax, citations=sorted(citations))
            visible = [dict(r) for r in records]
            rng.shuffle(visible)
            stages.append(dict(stage=stage, request=request, records=visible, expected=expected))
        histories.append(dict(id=tag, stages=stages))
    return histories


def execute(request, selected):
    """Public quote tool: reference traversal and integer arithmetic, no evaluator access."""
    index = current(selected)
    try:
        item = index[request['item']]
        contract = index[item['ref']]
        tax_record = index[contract['ref']]
        if (item['kind'], contract['kind'], tax_record['kind']) != ('item', 'contract', 'tax'):
            return {'error': 'invalid record kinds'}
        subtotal = request['quantity'] * contract['unit_cents']
        tax = (subtotal * tax_record['bps'] + 5000) // 10000
        return dict(item=request['item'], quantity=request['quantity'], subtotal_cents=subtotal,
                    tax_cents=tax, total_cents=subtotal + tax,
                    citations=sorted([item['id'], contract['id'], tax_record['id']]))
    except KeyError:
        return {'error': 'missing dependency'}


def correct(answer, expected):
    return isinstance(answer, dict) and all(
        (sorted(answer.get(k, [])) == v if k == 'citations' else answer.get(k) == v)
        for k, v in expected.items())


def closure(request, records):
    index = current(records)
    result = []
    key = request['item']
    while key:
        r = index[key]
        result.append(r)
        key = r.get('ref')
    return result


def feature(request, selected, index, interactions=True):
    ids = {r['key']: r for r in selected}
    root = [r for r in selected if r['key'] == request['item']]
    edges = sum(r.get('ref') in ids for r in selected)
    root_edges = sum(r.get('ref') in ids for r in root)
    return [1., float(len(root)), sum(index[r['key']]['id'] == r['id'] for r in selected) / 3,
            *[sum(r['kind'] == kind for r in selected) / 3 for kind in ('item', 'contract', 'tax')],
            edges / 2 if interactions else 0., float(root_edges) if interactions else 0.]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def select(request, records, weights, mode='exact', interactions=True):
    start = time.perf_counter()
    index = current(records)
    ordered = sorted(records, key=lambda r: r['id'])
    n = len(ordered)
    evaluations, moves = 0, 0

    def score(indices):
        nonlocal evaluations
        evaluations += 1
        return dot(weights, feature(request, [ordered[i] for i in indices], index, interactions))

    if mode == 'exact':
        best = max(itertools.combinations(range(n), 3), key=score)
    else:
        # A fixed visible-only unary initialization, common across all histories.
        initial = sorted(range(n), key=lambda i: (
            ordered[i]['key'] == request['item'],
            index[ordered[i]['key']]['id'] == ordered[i]['id'],
            ordered[i]['kind'] == 'contract'), reverse=True)[:3]
        best = tuple(sorted(initial))
        best_score = score(best)
        for _ in range(10):
            candidates = sorted({tuple(sorted((set(best) - {old}) | {new}))
                                 for old in best for new in range(n) if new not in best})
            scored = [(score(candidate), candidate) for candidate in candidates]
            value, candidate = max(scored, key=lambda pair: (pair[0], tuple(-i for i in pair[1])))
            if value <= best_score + 1e-12:
                break
            best, best_score = candidate, value
            moves += 1
    return [ordered[i] for i in best], dict(feature_evaluations=evaluations, accepted_moves=moves,
                                           selection_seconds=time.perf_counter()-start)


def attempts(histories, recipe, seed):
    rng = random.Random(seed)
    rows = []
    for history in histories:
        for episode in history['stages']:
            request, records = episode['request'], episode['records']
            candidates = [rng.sample(records, 3) for _ in range(16)]
            if recipe == 'closure_exploration':
                ordinary = closure(request, records)
                candidates.append(ordinary)
                for i in range(3):
                    for replacement in records:
                        if replacement['id'] not in {r['id'] for r in ordinary}:
                            candidates.append(ordinary[:i] + [replacement] + ordinary[i+1:])
            index = current(records)
            for selected in candidates:
                answer = execute(request, selected)
                rows.append(dict(task_id=request['task_id'], selected=[r['id'] for r in selected],
                                 x=feature(request, selected, index),
                                 outcome=answer, y=int(correct(answer, episode['expected'])),
                                 recipe=recipe))
    return rows


def fit(rows, interactions=True, epochs=1000):
    start = time.perf_counter()
    weights = [0.] * len(FEATURES)
    xs = [r['x'][:] if interactions else r['x'][:6]+[0., 0.] for r in rows]
    positives = sum(r['y'] for r in rows)
    factors = [len(rows)/(2*max(1, positives if r['y'] else len(rows)-positives)) for r in rows]
    losses = []
    for epoch in range(epochs):
        gradient = [0.] * len(weights)
        loss = 0.
        for x, row, factor in zip(xs, rows, factors):
            z = dot(weights, x)
            p = 1/(1+math.exp(-max(-40, min(40, z))))
            error = (p-row['y'])*factor
            for j in range(len(weights)):
                gradient[j] += error*x[j]
            loss += factor*(max(z, 0)-row['y']*z+math.log1p(math.exp(-abs(z))))
        for j in range(len(weights)):
            weights[j] -= .2*(gradient[j]/len(rows) + .0005*weights[j])
        if epoch in (0, 99, epochs-1):
            losses.append(dict(epoch=epoch+1, binary_loss=loss/len(rows)))
    return dict(weights=weights, features=FEATURES, interactions=interactions,
                training=dict(examples=len(rows), positives=positives, epochs=epochs,
                              scalar_parameter_count=len(weights), example_gradient_evaluations=epochs*len(rows),
                              seconds=time.perf_counter()-start, losses=losses))


def evaluate(histories, checkpoints):
    rows = []
    for history in histories:
        caches = {name: [] for name in ['ordinary', *checkpoints]}
        for episode in history['stages']:
            request, records = episode['request'], episode['records']
            index = current(records)
            for name in caches:
                start = time.perf_counter()
                reuse = next((a for a in caches[name] if a['item'] == request['item']
                              and a['quantity'] == request['quantity']
                              and all(i in {r['id'] for r in index.values()} for i in a['citations'])), None)
                if name == 'ordinary':
                    selected = closure(request, records)
                    costs = dict(feature_evaluations=0, accepted_moves=0,
                                 selection_seconds=time.perf_counter()-start)
                else:
                    cp = checkpoints[name]
                    selected, costs = select(request, records, cp['weights'],
                                             'swap' if name == 'energy_swap' else 'exact',
                                             cp['interactions'])
                answer = reuse or execute(request, selected)
                success = correct(answer, episode['expected'])
                # All arms have identical public fallback. No evaluator-triggered fallback.
                selected_ids = {r['id'] for r in selected}
                stale = sum(index[r['key']]['id'] != r['id'] for r in selected)
                missing = 'error' in answer
                fallback = int(bool(stale or missing))
                repaired = execute(request, closure(request, records)) if fallback else answer
                if 'error' not in repaired:
                    caches[name].append(repaired)
                rows.append(dict(history=history['id'], task_id=request['task_id'], stage=episode['stage'],
                                 arm=name, selected=sorted(selected_ids), complete=success,
                                 sufficient=set(episode['expected']['citations']).issubset(selected_ids),
                                 stale_records=stale, answer=answer, fallback=fallback,
                                 repaired_complete=correct(repaired, episode['expected']), cache_hit=int(reuse is not None),
                                 candidate_records=len(records), candidate_bytes=len(json.dumps(records).encode()),
                                 delivered_bytes=len(json.dumps(selected).encode()),
                                 fallback_delivered_bytes=len(json.dumps(closure(request, records)).encode()) if fallback else 0,
                                 index_record_visits=len(records), tool_calls=0 if reuse else 1,
                                 fallback_tool_calls=fallback, **costs))
    return rows


def summarize(rows):
    summary = {}
    for name in sorted({r['arm'] for r in rows}):
        group = [r for r in rows if r['arm'] == name]
        summary[name] = dict(n=len(group), **{key: sum(r[key] for r in group) for key in
            ['complete', 'sufficient', 'stale_records', 'fallback', 'repaired_complete', 'cache_hit',
             'feature_evaluations', 'accepted_moves', 'selection_seconds', 'candidate_bytes',
             'delivered_bytes', 'fallback_delivered_bytes', 'index_record_visits', 'tool_calls', 'fallback_tool_calls']},
            stages={str(stage): sum(r['complete'] for r in group if r['stage'] == stage) for stage in range(5)})
    return summary


def develop(out):
    histories = generate(28092026, 4, 'development')
    dump(out/'histories.json', histories)
    checkpoints = {'zero': dict(weights=[0.]*len(FEATURES), interactions=True)}
    for recipe in ('random', 'closure_exploration'):
        rows = attempts(histories, recipe, 761)
        dump(out/f'{recipe}-attempts.json', rows)
        cp = fit(rows)
        dump(out/f'{recipe}-checkpoint.json', cp)
        checkpoints[recipe] = cp
    ablated = fit(rows, interactions=False)
    dump(out/'pointwise-checkpoint.json', ablated)
    checkpoints['pointwise'] = ablated
    checkpoints['energy_swap'] = checkpoints['closure_exploration']
    results = evaluate(histories, checkpoints)
    dump(out/'outcomes.json', results)
    dump(out/'summary.json', summarize(results))


def freeze():
    path = ROOT/'runs/freeze.json'
    if path.exists():
        raise RuntimeError('Freeze already exists; do not overwrite')
    files = ['PROTOCOL.md', 'scripts/quote_study.py', 'scripts/reader_check.py',
             'runs/diagnosis-pairwise/checkpoint.json',
             'runs/diagnosis-pairwise/pointwise-checkpoint.json',
             'runs/diagnosis-pairwise/summary.json', 'CLAIM.md']
    dump(path, dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    files={f: digest(ROOT/f) for f in files}, confirmation_seed=28102026,
                    histories=6, weights_frozen=True))


def confirm(out):
    frozen = json.loads((ROOT/'runs/freeze.json').read_text())
    for f, sha in frozen['files'].items():
        assert digest(ROOT/f) == sha, f'Frozen file changed: {f}'
    histories = generate(frozen['confirmation_seed'], frozen['histories'], 'confirmation')
    dump(out/'histories.json', histories)
    cp = json.loads((ROOT/'runs/diagnosis-pairwise/checkpoint.json').read_text())
    pointwise = json.loads((ROOT/'runs/diagnosis-pairwise/pointwise-checkpoint.json').read_text())
    cps = dict(zero=dict(weights=[0.]*len(FEATURES), interactions=True),
               exact=cp, energy_swap=cp, pointwise=pointwise)
    results = evaluate(histories, cps)
    dump(out/'outcomes.json', results)
    dump(out/'summary.json', summarize(results))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['develop', 'freeze', 'confirm'])
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.command == 'freeze':
        freeze()
        return
    out = args.out
    if out is None or out.exists():
        raise ValueError('Pass a new --out directory; existing runs are immutable')
    out.mkdir(parents=True)
    start = time.perf_counter()
    (develop if args.command == 'develop' else confirm)(out)
    dump(out/'execution.json', dict(command=sys.argv, python=sys.version, platform=platform.platform(),
                                  script_sha256=digest(Path(__file__)), seconds=time.perf_counter()-start,
                                  finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    print((out/'summary.json').read_text())


if __name__ == '__main__':
    main()
