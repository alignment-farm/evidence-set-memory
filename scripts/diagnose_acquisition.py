"""Preserve a longer-optimization diagnostic; does not change the initial run."""
import json
from pathlib import Path
import time
from quote_study import dump, fit, evaluate, summarize, digest

ROOT = Path(__file__).resolve().parents[1]
out = ROOT/'runs/diagnosis-longer'
if out.exists():
    raise RuntimeError('Write-once run already exists')
out.mkdir(parents=True)
histories = json.loads((ROOT/'runs/development/histories.json').read_text())
rows = json.loads((ROOT/'runs/development/closure_exploration-attempts.json').read_text())
start = time.perf_counter()
cp = fit(rows, epochs=10000)
dump(out/'checkpoint.json', cp)
results = evaluate(histories, dict(exact=cp, energy_swap=cp))
dump(out/'outcomes.json', results)
dump(out/'summary.json', summarize(results))
dump(out/'execution.json', dict(seconds=time.perf_counter()-start,
     script_sha256=digest(Path(__file__)), core_sha256=digest(ROOT/'scripts/quote_study.py')))
print((out/'summary.json').read_text())
