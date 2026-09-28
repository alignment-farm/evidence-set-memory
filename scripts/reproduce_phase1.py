"""Replay all CPU development and frozen confirmation into a NEW directory.

uv run --no-project python scripts/reproduce_phase1.py --out runs/reproduction-1
No model requests. Never overwrites published evidence.
"""
import argparse
import json
from pathlib import Path
from quote_study import develop, dump, fit, evaluate, summarize, generate

ROOT = Path(__file__).resolve().parents[1]


def stable_checkpoint(cp):
    cp = json.loads(json.dumps(cp))
    cp['training'].pop('seconds')
    return cp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    if out.exists():
        raise RuntimeError('Use a new output directory')
    out.mkdir(parents=True)
    develop(out/'development')
    histories = json.loads((out/'development/histories.json').read_text())
    rows = json.loads((out/'development/closure_exploration-attempts.json').read_text())
    long_cp = fit(rows, epochs=10000)
    dump(out/'longer-checkpoint.json', long_cp)
    # Pairs are reproduced from attempt outcomes; no private expected values used.
    pairs = []
    for task_id in sorted({r['task_id'] for r in rows}):
        positives = [r for r in rows if r['task_id']==task_id and r['y']]
        negatives = [r for r in rows if r['task_id']==task_id and not r['y']]
        seen = set()
        for pos in positives:
            ids = tuple(sorted(pos['selected']))
            if ids in seen:
                continue
            seen.add(ids)
            for neg in negatives:
                diff = [a-b for a,b in zip(pos['x'],neg['x'])]
                pairs.extend([dict(x=diff,y=1), dict(x=[-v for v in diff],y=0)])
    cp, pointwise = fit(pairs), fit(pairs, interactions=False)
    for model in [cp, pointwise]:
        model['objective'] = 'within-task pairwise logistic on observed outcome differences'
    dump(out/'pairwise-checkpoint.json', cp)
    dump(out/'pointwise-checkpoint.json', pointwise)
    fresh = generate(28102026,6,'confirmation')
    cps = dict(zero=dict(weights=[0.]*8,interactions=True),exact=cp,energy_swap=cp,pointwise=pointwise)
    outcomes = evaluate(fresh,cps)
    dump(out/'confirmation-outcomes.json',outcomes)
    dump(out/'confirmation-summary.json',summarize(outcomes))
    expected_cp = json.loads((ROOT/'runs/diagnosis-pairwise/checkpoint.json').read_text())
    expected_rows = json.loads((ROOT/'runs/confirmation/outcomes.json').read_text())
    stable_rows = lambda rs: [{k:v for k,v in r.items() if k!='selection_seconds'} for r in rs]
    checks = dict(fitted_checkpoint_reproduced=stable_checkpoint(cp)==stable_checkpoint(expected_cp),
                  confirmation_reproduced=stable_rows(outcomes)==stable_rows(expected_rows))
    dump(out/'checks.json',checks)
    print(json.dumps(checks,indent=2))
    assert all(checks.values())


if __name__=='__main__':
    main()
