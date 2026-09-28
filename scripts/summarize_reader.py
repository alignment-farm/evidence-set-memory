"""Offline field-level reader audit. No extra inference or method changes."""
import json
from pathlib import Path
from quote_study import dump, correct

ROOT = Path(__file__).resolve().parents[1]
out = ROOT/'runs/reader-analysis.json'
if out.exists():
    raise RuntimeError('Analysis already exists')
episodes = json.loads((ROOT/'runs/confirmation/histories.json').read_text())[0]['stages']
gold = {e['request']['task_id']:e['expected'] for e in episodes}
rows = json.loads((ROOT/'runs/reader/outcomes.json').read_text())
details = []
for row in rows:
    response = json.loads((ROOT/f"runs/reader/{row['request_hash']}-response.json").read_text())
    answer = response['answer']
    expected = gold[row['task_id']]
    mismatches = [k for k,v in expected.items() if
                  (sorted(answer.get(k, [])) != v if k=='citations' else answer.get(k)!=v)]
    details.append(dict(arm=row['arm'], task_id=row['task_id'], sufficient=row['sufficient'],
                        mismatches=mismatches, invalid_json=answer.get('error')=='invalid JSON',
                        answer=answer, expected=expected))
dump(out, dict(details=details, total_controller_validation_tool_calls=sum(r['controller_tool_calls'] for r in rows),
               total_controller_validation_record_visits=sum(r['controller_validation_source_records'] for r in rows),
               all_repaired_complete=all(r['repaired_complete'] for r in rows),
               note='27 mapped outcomes share 17 unique LLM calls; duplicates are not independent observations.'))
print(json.dumps([r for r in details if r['arm']=='ordinary'], indent=2))
