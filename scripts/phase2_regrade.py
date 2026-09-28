"""Apply declared final formatting extraction to preserved development responses."""
import argparse
import json
from pathlib import Path
from phase2_reader import parse,grade
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
if args.out.exists():raise RuntimeError('Existing output')
labels={l['id']:l for l in json.loads((ROOT/'.cache/phase2/partitions/development-labels.json').read_text())}
original=json.loads((args.run/'outcomes.json').read_text())
rows=[]
for row in original:
    response=json.loads((args.run/f"{row['request_hash']}-response.json").read_text())
    answer=parse(response['response'])
    rows.append(dict(id=row['id'],arm=row['arm'],selected=row['selected'],answer=answer,
                     **grade(answer,labels[row['id']],row['selected'])))
summary={arm:dict(n=sum(r['arm']==arm for r in rows),
                  answer_em=sum(r['answer_em'] for r in rows if r['arm']==arm),
                  complete=sum(r['complete'] for r in rows if r['arm']==arm),
                  parse_errors=sum(bool(r['answer'].get('parse_error')) for r in rows if r['arm']==arm))
         for arm in sorted({r['arm'] for r in rows})}
dump(args.out,dict(rows=rows,summary=summary,inference_calls=0,
                  intervention='Deterministic final-JSON extraction only; original responses unchanged'))
print(json.dumps(summary,indent=2))
