"""Acquire full author-linked raw MuSiQue dev; split without component leakage."""
import hashlib
import json
from pathlib import Path
import random
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://drive.google.com/uc?export=download&id=1TRXU68wveSehVbQrRRtWsUsFkKUF43QS'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def main():
    dest = ROOT/'.cache/phase2/musique-raw-dev.jsonl'
    out = ROOT/'phase2/data'
    if out.exists():
        raise RuntimeError('Existing partition is immutable')
    dest.parent.mkdir(parents=True, exist_ok=True)
    t = time.perf_counter()
    downloaded = 0
    if not dest.exists():
        request = urllib.request.Request(URL, headers={'User-Agent':'evidence-set-memory-phase2/1.0 research'})
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read(60_000_001)
        if len(payload)>60_000_000:
            raise ValueError('Unexpected file size exceeds bound')
        for line in payload.splitlines():
            json.loads(line)
        dest.write_bytes(payload)
        downloaded = len(payload)
    raw = [json.loads(line) for line in dest.read_text().splitlines()]
    rng = random.Random(28092602)
    rng.shuffle(raw)
    # Reserve confirmation/development first, solely by IDs/component IDs.
    # No question text or answer quality is used in choosing the partition.
    occupied = set()
    partition = {}
    for name, target in [('confirmation',64), ('development',48), ('train',256)]:
        chosen, local = [], set()
        for row in raw:
            components = {str(d['id']) for d in row['decomposed_instances']}
            if components & occupied:
                continue
            chosen.append(row)
            local.update(components)
            if len(chosen) == target:
                break
        if len(chosen)!=target:
            raise ValueError(f'Only {len(chosen)} eligible {name} rows')
        occupied.update(local)
        partition[name] = chosen
    aliases_path = ROOT/'.cache/reconnaissance/MuSiQue/.answer_aliases.json'
    # The reconnaissance includes this author mapping when present in manifest.
    aliases = json.loads(aliases_path.read_text()) if aliases_path.exists() else {}
    component_sets = {}
    for name, rows in partition.items():
        inputs, labels = [], []
        component_sets[name] = sorted({str(d['id']) for r in rows for d in r['decomposed_instances']})
        for row in rows:
            contexts = row['contexts']
            inputs.append(dict(id=row['id'], question=row['composed_question_text'],
                               paragraphs=[dict(idx=i,title=p['wikipedia_title'],text=p['paragraph_text'])
                                           for i,p in enumerate(contexts)]))
            end_id = str(row['id'].split('__')[1].split('_')[-1])
            text = ' '.join(p['wikipedia_title']+' '+p['paragraph_text'] for p in contexts).lower()
            labels.append(dict(id=row['id'], answer=row['answer_text'],
                 aliases=[a for a in aliases.get(end_id,[]) if a.lower().strip() in text],
                 supports=[i for i,p in enumerate(contexts) if p['is_supporting']],
                 component_ids=[str(d['id']) for d in row['decomposed_instances']]))
        # Downloaded text remains cache, tracked labels/inputs identified by hashes.
        cache = ROOT/'.cache/phase2/partitions'
        dump(cache/f'{name}-inputs.json',inputs)
        dump(cache/f'{name}-labels.json',labels)
        dump(out/f'{name}-manifest.json',dict(ids=[r['id'] for r in inputs],
             components=component_sets[name],count=len(rows),
             inputs_sha256=hashlib.sha256((cache/f'{name}-inputs.json').read_bytes()).hexdigest(),
             labels_sha256=hashlib.sha256((cache/f'{name}-labels.json').read_bytes()).hexdigest()))
    assert all(not set(component_sets[a]) & set(component_sets[b]) for a,b in
               [('train','development'),('train','confirmation'),('development','confirmation')])
    dump(out/'acquisition.json',dict(url=URL, source_commit='922ac98f19a201998dbdae6d7f2887a5258dbdeb',
         source_file_pinned=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
         bytes=dest.stat().st_size,downloaded_payload_bytes=downloaded,raw_records=len(raw),
         elapsed_seconds=time.perf_counter()-t,alias_mapping_available=bool(aliases),
         cache_partition_hashes='see split manifests',split_seed=28092602,
         lineage='MuSiQue-Ans raw dev, author-linked Google Drive; benchmark supervision',
         license='CC BY 4.0 per pinned author repository',
         timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    print((out/'acquisition.json').read_text())


if __name__=='__main__':
    main()
