"""Build or verify the bounded phase-5 publication manifest."""
import argparse
import json
from pathlib import Path
import phase5_config as study


def run(build):
    root=study.ROOT;target=root/'phase5/manifest.json'
    if build:
        if target.exists():raise FileExistsError(target)
        files=[p for p in (root/'phase5').rglob('*') if p.is_file() and p!=target]
        files+=list((root/'scripts').glob('phase5_*.py'))
        files+=[root/x for x in ['scripts/test_phase5_config.py','README.md','AGENTS.md','START.md',
                                'FEASIBILITY.md','pyproject.toml','uv.lock']]
        study.dump(target,dict(scope='Phase 5 publication; prior manifests remain scoped to prior commits',
            freeze_commit='f8651b89a9ce7eb4301c363e7156a9e22348af2c',
            files={str(p.relative_to(root)):dict(sha256=study.sha(p),bytes=p.stat().st_size) for p in sorted(set(files))}))
    data=study.load(target)
    for path,item in data['files'].items():
        assert study.sha(root/path)==item['sha256'],path
        assert (root/path).stat().st_size==item['bytes'],path
    print(json.dumps(dict(verified_files=len(data['files']),bytes=sum(x['bytes'] for x in data['files'].values()))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--build',action='store_true')
    run(parser.parse_args().build)
