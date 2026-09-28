"""Read-only asset audit and scorer plumbing, not a selector experiment.

Run from anywhere with uv run --no-project python /path/to/scripts/check_assets.py.
One valid JSON document goes to stdout. Upstream code is imported from pinned cache.
"""
import collections
import gzip
import hashlib
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/reconnaissance'
ser = CACHE / 'SERBench'
sys.path.insert(0, str(ser / 'src'))
from serbench import load_dataset, load_labels
from serbench._reference_scorer import score_prediction

manifest = json.loads((ROOT / 'sources/reconnaissance/fetch-manifest.json').read_text())
for relative, entry in manifest['files'].items():
    data = (CACHE / relative).read_bytes()
    assert len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256'], relative
rows = list(load_dataset('cal500', data_dir=ser / 'data'))
raw_labels = load_labels('cal500', data_dir=ser / 'data')
labels = list(raw_labels.values()) if isinstance(raw_labels, dict) else list(raw_labels)
minimum = collections.Counter()
for label in labels:
    universe = sorted({i for g in label['required_evidence_groups'] for i in g['acceptable_evidence_ids']} |
                      {i for a in label['alternative_minimal_sets'] for i in a})
    def complete(selected):
        return all(len(selected & set(g['acceptable_evidence_ids'])) >= g.get('minimum_required', 1)
                   for g in label['required_evidence_groups']) or any(
                       set(a) <= selected for a in label['alternative_minimal_sets'])
    minimum[next(k for k in range(len(universe)+1)
                 if any(complete(set(a)) for a in itertools.combinations(universe, k)))] += 1
label = labels[0]
ids = label['alternative_minimal_sets'][0]
assert score_prediction(ids, label, len(ids))['mss_complete@' + str(len(ids))] == 1
assert score_prediction([], label, 8)['mss_complete@8'] == 0
assert all('required_evidence_groups' not in d for d in rows)
result = {'cache_hashes': {'verified_files': len(manifest['files']), 'passed': True},
          'serbench_cal500': {'rows': len(rows), 'labels': len(labels),
                             'minimum_certified_sizes': dict(minimum),
                             'oracle_empty_scorer_assertions': 'passed', 'loader_label_separation': 'passed'}}
test = list(load_dataset('test500', data_dir=ser / 'data'))
result['serbench_test500'] = {
    'inference_rows': len(test), 'labels_loaded': False,
    'observed_lists_nonempty': sum(bool(d['observed_evidence_ids']) for d in test),
    'observed_candidate_overlap': sum(bool(set(d['observed_evidence_ids']) &
                                         {e['evidence_id'] for e in d['candidate_evidence']}) for d in test)}
mu = CACHE / 'MuSiQue'
sys.path.insert(0, str(mu))
from metrics.answer import AnswerMetric
from metrics.support import SupportMetric
answer = AnswerMetric()
support = SupportMetric()
samples = [json.loads(line) for line in (mu / 'raw-dev-first3.jsonl').read_text().splitlines()]
for row in samples:
    answer(row['answer_text'], [row['answer_text']])
    indices = [i for i, context in enumerate(row['contexts']) if context['is_supporting']]
    support(indices, indices)
assert answer.get_metric() == (1.0, 1.0)
assert support.get_metric() == (1.0, 1.0)
result['musique'] = {'samples': len(samples), 'answer_metric_oracle': answer.get_metric(),
                     'support_metric_oracle': support.get_metric()}
result['scope'] = 'Asset/scorer plumbing only; no model or selector predictions, training, or private Test500 labels.'
print(json.dumps(result, indent=2))
