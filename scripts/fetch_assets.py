"""Fetch hash-pinned public reconnaissance assets, or verify existing cache only.

Run with uv run --no-project python scripts/fetch_assets.py --verify-only.
Omit --verify-only to fetch missing files. No model or credential access.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/reconnaissance'
MANIFEST = ROOT / 'sources/reconnaissance/fetch-manifest.json'


def valid(data, entry):
    return len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    downloaded = 0
    checked = 0
    for relative, entry in manifest['files'].items():
        target = CACHE / relative
        if target.exists():
            if not valid(target.read_bytes(), entry):
                raise ValueError(f'Cached hash/size mismatch: {relative}; preserve and inspect it before reacquisition.')
        elif args.verify_only:
            raise FileNotFoundError(target)
        else:
            request = urllib.request.Request(entry['url'], headers={'User-Agent': 'Construct-2-evidence-set-memory-reconnaissance/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                if entry['method'] == 'first_jsonl_lines':
                    data = b''.join(response.readline(1024 * 1024) for _ in range(entry['lines']))
                    if len(data.splitlines()) != entry['lines']:
                        raise ValueError(f'Unexpected JSONL sample length: {relative}')
                    for line in data.splitlines():
                        json.loads(line)
                else:
                    data = response.read(entry['bytes'] + 1)
            if not valid(data, entry):
                raise ValueError(f'Fetched hash/size mismatch: {relative}; upstream may have changed. Nothing written.')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            downloaded += len(data)
        checked += 1
    print(json.dumps({'verified_files': checked, 'downloaded_payload_bytes': downloaded,
                      'expected_payload_bytes': sum(e['bytes'] for e in manifest['files'].values()),
                      'mode': 'verify_only' if args.verify_only else 'fetch_missing'}, indent=2))


if __name__ == '__main__':
    main()
