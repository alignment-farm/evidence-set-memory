"""Create or verify the phase-1 publication manifest, excluding itself."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'runs/artifact-manifest.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        manifest = json.loads(TARGET.read_text())
        for rel, expected in manifest['files'].items():
            data = (ROOT/rel).read_bytes()
            assert len(data) == expected['bytes'], rel
            assert hashlib.sha256(data).hexdigest() == expected['sha256'], rel
        print(json.dumps(dict(verified_files=len(manifest['files']), all_passed=True)))
        return
    if TARGET.exists():
        raise RuntimeError('Manifest is write-once')
    paths = list(ROOT.glob('*.md')) + list((ROOT/'scripts').rglob('*.py'))
    paths += list((ROOT/'sources/phase1').rglob('*.md'))
    for name in ['development', 'diagnosis-longer', 'diagnosis-pairwise', 'confirmation', 'reader']:
        paths += list((ROOT/'runs'/name).glob('*.json'))
    paths += [ROOT/'runs'/name for name in ['audit.json', 'reader-analysis.json', 'provenance.json',
                                           'verification.json', 'freeze.json']]
    entries = {str(p.relative_to(ROOT)): dict(bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(paths))}
    TARGET.write_text(json.dumps(dict(base_revision='5a0e8f78ab9ee570dd69b80928f39aae4b72f481',
                                     files=entries), indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(files=len(entries), payload_bytes=sum(v['bytes'] for v in entries.values()))))


if __name__ == '__main__':
    main()
