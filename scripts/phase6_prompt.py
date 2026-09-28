"""Remove runtime-only pytest display variation, not task facts, before caching."""
import argparse
import json
import re
import phase6_edit as study


def canonical_output(text):
    text=re.sub(r'(object at )0x[0-9a-fA-F]+',r'\1<address>',text)
    return re.sub(r'(?m)( in )\d+(?:\.\d+)?s$',r'\1<elapsed>',text)


def normalize(payload):
    payload=json.loads(json.dumps(payload))
    for message in payload['messages']:
        if message['role']!='user':continue
        try:obj=json.loads(message['content'])
        except ValueError:continue
        for key in ['baseline_test_output','public_test_failure']:
            if key in obj:obj[key]=canonical_output(obj[key])
        message['content']=json.dumps(obj,sort_keys=True)
    return payload


def install():
    original=study.request
    study.request=lambda payload,calls:original(normalize(payload),calls)


def validate(out):
    out=study.fresh(out);calls=out/'calls';calls.mkdir();install()
    tasks=study.load(study.PHASE/'development-tasks.json');task=tasks[1]
    source=study.PHASE/f'runs/development/states/{tasks[0]["id"]}'
    memory=study.load(source/'lineage.json');prior=[tasks[0]['public_test'],tasks[0]['hidden_test']]
    rows,_,_=study.records(source);chosen,work=study.select(task,rows,'pointwise');results=[]
    for policy in ['pointwise','identical_delivery_replay']:
        result,_=study.attempt(task,source,out/policy,policy,calls,prior,memory,(chosen,work));results.append(result)
    assert [e['request_hash'] for e in results[0]['events']]==[e['request_hash'] for e in results[1]['events']]
    assert all(e['reused'] for e in results[1]['events'])
    study.dump(out/'results.json',results)
    study.dump(out/'execution.json',dict(timestamp=study.stamp(),script_sha256=study.sha(__file__),
        physically_identical_delivery_cached=True,extra_acquisition_labels=False,calls=len(list(calls.glob('*-response.json')))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    validate(parser.parse_args().out)
