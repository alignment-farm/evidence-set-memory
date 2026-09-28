"""Development-only intact-file delivery comparison; preserves original run."""
import argparse
import time
import phase6_edit as study


def files_selection(task,source,policy):
    start=time.perf_counter();rows,_,_=study.records(source)
    chosen,_=study.select(task,rows,'ordinary' if policy=='ordinary_files' else 'all')
    paths=sorted({r['path'] for r in chosen});files=[]
    for path in paths:
        files.append(dict(id=path+'::whole_file',path=path,line=1,
                          text=(source/path).read_text(),sha256=study.sha(source/path)))
    return files,dict(seconds=time.perf_counter()-start,records=len(files),
                     bytes=sum(len(r['text'].encode()) for r in files),whole_file=True)


def run(out):
    out=study.fresh(out);calls=out/'calls';calls.mkdir();tasks=study.load(study.PHASE/'development-tasks.json')
    source=study.ASSET;prior=[];memory=[];results=[]
    for task in tasks:
        for policy in ['ordinary_files','all_files']:
            selected=files_selection(task,source,policy)
            result,_=study.attempt(task,source,out/f'{task["id"]}/{policy}',policy,calls,prior,memory,selected)
            results.append(result)
        source=study.PHASE/f'runs/development/states/{task["id"]}'
        if not source.exists():raise RuntimeError('Original development has not established shared source revision')
        memory=study.load(source/'lineage.json')
        prior.extend([task['public_test'],task['hidden_test']])
    study.dump(out/'results.json',results)
    study.dump(out/'execution.json',dict(timestamp=study.stamp(),script_sha256=study.sha(__file__),
        harness_sha256=study.sha(study.ROOT/'scripts/phase6_edit.py'),calls=len(list(calls.glob('*-response.json')))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
