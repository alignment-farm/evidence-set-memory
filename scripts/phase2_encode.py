"""Frozen MiniLM representation diagnostic; no labels are read."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from huggingface_hub import HfApi
from sentence_transformers import SentenceTransformer
from phase2_assets import dump

ROOT=Path(__file__).resolve().parents[1]
MODEL='sentence-transformers/all-MiniLM-L6-v2'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--split',required=True,
                choices=['train','development','confirmation']);args=parser.parse_args()
    torch.set_num_threads(2)
    provenance=ROOT/'phase2/encoder.json'
    if provenance.exists(): revision=json.loads(provenance.read_text())['revision']
    else:
        revision=HfApi().model_info(MODEL).sha
        dump(provenance,dict(model=MODEL,revision=revision,device='cpu',threads=2,
                            pretraining='imported pretrained sentence encoder; overlap with QA seed corpora possible',
                            source='https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2'))
    if args.split=='confirmation': assert (ROOT/'phase2/freeze.json').exists()
    out=ROOT/f'.cache/phase2/semantic/{args.split}.npz'
    if out.exists():raise RuntimeError('Existing embeddings')
    out.parent.mkdir(parents=True,exist_ok=True)
    load_start=time.perf_counter()
    model=SentenceTransformer(MODEL,revision=revision,device='cpu',cache_folder=str(ROOT/'.cache/phase2/encoder'))
    load_seconds=time.perf_counter()-load_start
    path=ROOT/f'.cache/phase2/partitions/{args.split}-inputs.json'
    rows=[e for e in json.loads(path.read_text()) if len(e['paragraphs'])==20]
    texts=[]
    for e in rows:
        texts.append(e['question'])
        texts.extend(p['title']+'\n'+p['text'] for p in e['paragraphs'])
        texts.extend(p['title'] for p in e['paragraphs'])
    # Exact-string cache is ordinary reuse, charged as actual encoded unique strings.
    unique=list(dict.fromkeys(texts));lookup={s:i for i,s in enumerate(unique)}
    untruncated=model.tokenizer(unique,truncation=False,padding=False)['input_ids']
    t=time.perf_counter();cpu=time.process_time()
    encoded=model.encode(unique,batch_size=32,normalize_embeddings=True,show_progress_bar=False)
    vectors=encoded[[lookup[s] for s in texts]].reshape(len(rows),41,-1)
    np.savez_compressed(out,query=vectors[:,0],documents=vectors[:,1:21],titles=vectors[:,21:],ids=np.array([e['id'] for e in rows]))
    dump(ROOT/f'phase2/runs/encoding-{args.split}.json',dict(model=MODEL,revision=revision,
         unique_texts=len(unique),logical_texts=len(texts),encoded_tokens=sum(min(len(s),model.max_seq_length) for s in untruncated),
         untruncated_tokens=sum(map(len,untruncated)),truncated_texts=sum(len(s)>model.max_seq_length for s in untruncated),
         max_sequence_length=model.max_seq_length,dimensions=encoded.shape[1],load_seconds=load_seconds,
         encoding_wall_seconds=time.perf_counter()-t,encoding_cpu_seconds=time.process_time()-cpu,
         input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
         embeddings_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),embedding_bytes=out.stat().st_size,
         model_parameters=sum(p.numel() for p in model.parameters()),
         created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    print((ROOT/f'phase2/runs/encoding-{args.split}.json').read_text())


if __name__=='__main__':main()
