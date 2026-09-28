"""Freeze developed phase-2 methods before any held-out representation/inference."""
import hashlib
import json
from pathlib import Path
import time
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'phase2/freeze.json'
if out.exists():raise RuntimeError('Freeze already exists')
files=['phase2/CLAIM.md','phase2/PROTOCOL.md','phase2/encoder.json','pyproject.toml','uv.lock',
       'scripts/phase2_energy.py','scripts/phase2_reader.py','scripts/phase2_encode.py',
       'phase2/runs/semantic-pairwise/checkpoint.json','phase2/runs/semantic-unary/checkpoint.json',
       'phase2/data/train-manifest.json','phase2/data/development-manifest.json','phase2/data/confirmation-manifest.json']
dump(out,dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
     files={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
     reader_model='docker.io/ai/qwen3.8:27b-q4_K_M',reader_cases=24,
     ordinary_weight=1.,pairwise_checkpoint='phase2/runs/semantic-pairwise/checkpoint.json',
     unary_checkpoint='phase2/runs/semantic-unary/checkpoint.json',
     provenance='Development choices only; confirmation embeddings/inference not run yet'))
print(out.read_text())
