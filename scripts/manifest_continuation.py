"""Write/verify exact locally published continuation artifacts, excluding caches."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'continuation-manifest.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:
        manifest=json.loads(MANIFEST.read_text())
        failed=[name for name,digest in manifest['files'].items() if not (ROOT/name).is_file() or sha(ROOT/name)!=digest]
        print(json.dumps(dict(checked=len(manifest['files']),failed=failed)))
        assert not failed
        return
    if MANIFEST.exists():raise RuntimeError('Manifest exists; do not silently overwrite a publication')
    paths=[]
    for directory in ['phase2','phase3','phase4']:
        paths.extend(path for path in (ROOT/directory).rglob('*') if path.is_file())
    for pattern in ['phase2*.py','phase3*.py','phase4*.py','test_phase2*.py']:
        paths.extend((ROOT/'scripts').glob(pattern))
    paths.extend(ROOT/p for p in ['README.md','pyproject.toml','uv.lock',
        'scripts/audit_continuation.py','scripts/continuation_costs.py','scripts/manifest_continuation.py',
        'scripts/snapshots/phase2_energy-lexical.py','scripts/snapshots/phase2_reader-v1.py','scripts/snapshots/phase2_reader-v2.py'])
    result=dict(parent_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        note='Local publication hashes, not an independent scientific review or signed timestamp. Cache/weights/environment excluded.',
        files={str(path.relative_to(ROOT)):sha(path) for path in sorted(set(paths))})
    dump(MANIFEST,result)
    print(json.dumps(dict(files=len(result['files']),bytes=sum(path.stat().st_size for path in set(paths)))))


if __name__=='__main__':main()
