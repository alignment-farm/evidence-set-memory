"""Aggregate recorded native costs without counting shared inference twice."""
import argparse
import json
from pathlib import Path
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads((ROOT/path).read_text())
def sums(rows,fields):return {k:sum(r[k] for r in rows) for k in fields}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise RuntimeError('Write-once ledger')
    names=['pairwise-seed11-v2','pairwise-seed23','unary-seed11','semantic-pairwise','semantic-unary']
    fits={name:read(f'phase2/runs/{name}/costs.json') for name in names}
    enc={name:read(f'phase2/runs/encoding-{name}.json') for name in ['train','development','confirmation']}
    readers={name:read(f'phase2/runs/{name}/costs.json') for name in ['development-reader','semantic-development-reader','confirmation-reader']}
    selection={p.parent.name:json.loads(p.read_text()) for p in sorted((ROOT/'phase2/runs').glob('*/summary.json')) if (p.parent/'representation.json').exists()}
    representations={p.parent.name:json.loads(p.read_text()) for p in sorted((ROOT/'phase2/runs').glob('*/representation.json'))}
    phase3=read('phase3/runs/scaling/summary.json');phase4=read('phase4/runs/extension/summary.json')
    result=dict(
        training=dict(runs=names,totals=sums(list(fits.values()),['train_wall_seconds','train_cpu_seconds','optimizer_updates','contrast_presentations']),
            representation_wall_seconds=sum(r['representation']['seconds']+r['development_representation']['seconds'] for r in fits.values()),
            label_questions=253,label_contrasts_per_fit=8096,
            note='Imported benchmark labels, not earned feedback. Train timer includes validation/checkpoint writing; contrast construction before timer is not separately timed. Failed initial size assertion remains unmetered.'),
        encoder=dict(by_split=enc,totals=sums(list(enc.values()),['logical_texts','unique_texts','encoded_tokens','truncated_texts','encoding_wall_seconds','encoding_cpu_seconds','load_seconds','embedding_bytes']),
            note='Unique counts are per-partition, summed, not globally deduplicated. Imported pretraining/weight construction cost is unknown, not zero.'),
        selection=dict(by_run=selection,representation_by_run=representations,
            note='Each phase-2 relaxed and relaxed_swap arm was separately executed, so both costs count. Unary sorting time is uninstrumented (stored zero), not established free.'),
        primary=dict(by_run=readers,actual_total=sums(list(readers.values()),['requests','prompt_tokens','completion_tokens','request_seconds','wall_seconds','errors','usage_missing']),
            deployment_by_policy=read('phase2/runs/confirmation-reader/summary.json'),
            note='Physical totals deduplicate identical payloads. Deployment arm tokens count logical calls; add fallback tokens and fallback calls per policy. Fallback uses already executed all-source outputs, so do not add them again to physical totals. API-reported tokens; all-source-first order can affect cache/timing.'),
        optimizer_diagnostics=dict(phase3=phase3,phase4=phase4,
            phase4_actual_selection_gradients=read('phase4/runs/extension/provenance.json')['actual_selection_gradients'],
            phase4_refined_inclusive_wall_seconds=sum(r['refined']['seconds'] for r in phase4.values()),
            note='Phase 4 refined includes rounded predecessor: do not sum both. Phase 3 and phase 4 reuse embeddings, build features again, and fit no new weights.'),
        verification=read('phase2/runs/final-audit.json')['reproduction_costs'],
        unknown_or_unmetered=['Investigator tokens, monetary billing and backend fingerprint',
            'Machine energy, power and complete environment/network installation cost',
            'Imported encoder/reader pretraining and original benchmark annotation effort',
            'Python interpreter/import startup and some experiment orchestration time',
            'Exact split authoring and investigator method-development labor',
            'Separate coefficient forward timing for earliest lexical runs',
            'Additional offline acquisition diagnostics, tests, parsing and audit CPU are not fully timed'],
        separation='This ledger reports measured components; it is not a complete energy, monetary, or total-wall estimate. Phase 1 has its own ledger and is not folded into continuation totals.')
    dump(a.out,result)
    print(json.dumps(dict(training=result['training']['totals'],encoder=result['encoder']['totals'],primary=result['primary']['actual_total']),indent=2))


if __name__=='__main__':main()
