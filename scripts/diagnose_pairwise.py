"""Within-task outcome contrasts using only previously earned attempt feedback."""
import json
from pathlib import Path
import time
from quote_study import dump, fit, evaluate, summarize, digest

ROOT = Path(__file__).resolve().parents[1]
out = ROOT/'runs/diagnosis-pairwise'
if out.exists():
    raise RuntimeError('Write-once run already exists')
out.mkdir(parents=True)
histories = json.loads((ROOT/'runs/development/histories.json').read_text())
attempts = json.loads((ROOT/'runs/development/closure_exploration-attempts.json').read_text())
pairs = []
for task_id in sorted({r['task_id'] for r in attempts}):
    positives = [r for r in attempts if r['task_id'] == task_id and r['y']]
    negatives = [r for r in attempts if r['task_id'] == task_id and not r['y']]
    # Deduplicate repeated successful sets; do not turn duplicates into extra feedback.
    seen = set()
    for pos in positives:
        ids = tuple(sorted(pos['selected']))
        if ids in seen:
            continue
        seen.add(ids)
        for neg in negatives:
            difference = [a-b for a,b in zip(pos['x'], neg['x'])]
            pairs.append(dict(task_id=task_id, positive=pos['selected'], negative=neg['selected'],
                              x=difference, y=1))
            pairs.append(dict(task_id=task_id, positive=neg['selected'], negative=pos['selected'],
                              x=[-x for x in difference], y=0))
dump(out/'pairs.json', pairs)
start = time.perf_counter()
cp = fit(pairs, epochs=1000)
cp['objective'] = 'within-task pairwise logistic on observed outcome differences'
dump(out/'checkpoint.json', cp)
pointwise = fit(pairs, interactions=False, epochs=1000)
pointwise['objective'] = cp['objective']
dump(out/'pointwise-checkpoint.json', pointwise)
results = evaluate(histories, dict(exact=cp, energy_swap=cp, pointwise=pointwise))
dump(out/'outcomes.json', results)
dump(out/'summary.json', summarize(results))
dump(out/'execution.json', dict(seconds=time.perf_counter()-start,
     script_sha256=digest(Path(__file__)), core_sha256=digest(ROOT/'scripts/quote_study.py')))
print((out/'summary.json').read_text())
