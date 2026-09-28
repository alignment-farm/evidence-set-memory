"""Read-only scientific replay audit, saving a new audit file when requested."""
import argparse
import itertools
import json
from pathlib import Path
from quote_study import dump, digest, generate, evaluate, summarize, current, feature, dot

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise RuntimeError('Audit outputs are write-once')
    frozen = json.loads((ROOT/'runs/freeze.json').read_text())
    checks = {f: digest(ROOT/f) == sha for f, sha in frozen['files'].items()}
    initial = json.loads((ROOT/'runs/development/execution.json').read_text())
    checks['initial_implementation_snapshot'] = digest(ROOT/'scripts/snapshots/quote_study-v1.py') == initial['script_sha256']
    dev = json.loads((ROOT/'runs/development/histories.json').read_text())
    fresh = json.loads((ROOT/'runs/confirmation/histories.json').read_text())
    checks['development_generation_replay'] = dev == generate(28092026, 4, 'development')
    checks['fresh_generation_replay'] = fresh == generate(frozen['confirmation_seed'], frozen['histories'], 'confirmation')
    dev_ids = {r['id'] for h in dev for e in h['stages'] for r in e['records']}
    fresh_ids = {r['id'] for h in fresh for e in h['stages'] for r in e['records']}
    checks['disjoint_source_identifiers'] = not bool(dev_ids & fresh_ids)
    cp = json.loads((ROOT/'runs/diagnosis-pairwise/checkpoint.json').read_text())
    pointwise = json.loads((ROOT/'runs/diagnosis-pairwise/pointwise-checkpoint.json').read_text())
    cps = dict(zero=dict(weights=[0.]*8, interactions=True), exact=cp, energy_swap=cp, pointwise=pointwise)
    replay = evaluate(fresh, cps)
    original = json.loads((ROOT/'runs/confirmation/outcomes.json').read_text())
    stable = lambda rows: [{k:v for k,v in r.items() if k != 'selection_seconds'} for r in rows]
    checks['all_confirmation_outcomes_replay'] = stable(replay) == stable(original)
    checks['all_candidates_reachable'] = all(set(e['expected']['citations']).issubset({r['id'] for r in e['records']})
                                              for h in fresh for e in h['stages'])
    # Explain a DEVELOPMENT local optimum without adjusting the frozen method.
    e = dev[0]['stages'][3]
    diagnostic = json.loads((ROOT/'runs/diagnosis-pairwise/outcomes.json').read_text())
    selected_ids = next(r['selected'] for r in diagnostic if r['task_id']==e['request']['task_id'] and r['arm']=='energy_swap')
    records = e['records']
    index = current(records)
    by_id = {r['id']:r for r in records}
    score = lambda ids: dot(cp['weights'], feature(e['request'], [by_id[i] for i in ids], index))
    neighbors = {(tuple(sorted(set(selected_ids)-{old}|{new}))) for old in selected_ids
                 for new in by_id if new not in selected_ids}
    best_neighbor = max(score(ids) for ids in neighbors)
    exact_score = max(score(ids) for ids in itertools.combinations(sorted(by_id), 3))
    trap = dict(task_id=e['request']['task_id'], selected=selected_ids,
                selected_score=score(selected_ids), best_one_swap_score=best_neighbor,
                global_best_score=exact_score, neighbors=len(neighbors))
    checks['development_local_optimum_suboptimal'] = best_neighbor <= trap['selected_score']+1e-12 < exact_score
    checkpoints = ['runs/development/random-checkpoint.json',
                   'runs/development/closure_exploration-checkpoint.json',
                   'runs/development/pointwise-checkpoint.json',
                   'runs/diagnosis-longer/checkpoint.json',
                   'runs/diagnosis-pairwise/checkpoint.json',
                   'runs/diagnosis-pairwise/pointwise-checkpoint.json']
    training = {f:json.loads((ROOT/f).read_text())['training'] for f in checkpoints}
    acquisition = dict(executed_attempts=1080, final_recipe_attempts=760,
                       pairwise_rows=1472, unique_positive_vs_negative_contrasts=736,
                       training_runs=training,
                       total_training_wall_seconds=sum(t['seconds'] for t in training.values()),
                       total_example_gradient_evaluations=sum(t['example_gradient_evaluations'] for t in training.values()),
                       actual_cpu_seconds=None, investigator_cost=None, teacher_calls=0, embedding_calls=0,
                       note='320 random attempts were re-executed inside the 760-attempt recipe; not independent extra evidence.')
    result = dict(checks=checks, all_passed=all(checks.values()), development_local_optimum=trap,
                  acquisition_costs=acquisition)
    dump(args.out, result)
    print(json.dumps(result, indent=2))
    assert result['all_passed']


if __name__ == '__main__':
    main()
