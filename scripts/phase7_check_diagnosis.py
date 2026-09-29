"""Post-hoc mutation test of an already-completed reader's own scratch suite."""
import argparse
import ast
import xml.etree.ElementTree as ET
import phase7_edit as s


def failed_ids(case,label):
    tree=ET.parse(case/'tmp'/f'{label}.xml')
    return sorted(t.attrib.get('name') for t in tree.iter('testcase') if t.find('failure') is not None or t.find('error') is not None)


def run(out):
    out=s.fresh(out);run=s.PHASE/'runs/development';row=s.load(run/'ordinary_access-True/result.json')
    task=s.load(run/'task.json');asset=s.ASSETS['dotenv'];source=s.ROOT/row['source']
    results=[]
    for mutant in [False,True]:
        case=s.copy_case(source,asset,s.ROOT/'.cache/phase7/check-diagnosis'/out.name/str(mutant))
        for patch in row['patches']:s.apply_edits(case,asset,patch)
        assert s.source_hashes(case,asset)==row['source_result']
        if mutant:
            path='src/dotenv/main.py';text=(case/path).read_text();lines=text.splitlines(keepends=True)
            node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='_detect_line_ending')
            before=''.join(lines[node.lineno-1:node.end_lineno]).rstrip('\n')
            after='''def _detect_line_ending(source: IO[str]) -> str:
    content = source.read()
    source.seek(0)
    return "\\r\\n" if "\\r\\n" in content else "\\n"'''
            patch={'edits':[dict(path=path,old=before,new=after)]};s.apply_edits(case,asset,patch);s.dump(out/'authored-mutant.json',patch)
        for check in row['scratch']:(case/check['path']).write_text(check['content'])
        # No participant call follows these post-hoc examiner executions.
        (case/'heldout_current.py').write_text(task['hidden_test'])
        own=s.execute(case,asset,[c['path'] for c in row['scratch']],'own')
        hidden=s.execute(case,asset,['heldout_current.py'],'hidden')
        results.append(dict(mutant=mutant,own=own,hidden=hidden,own_failed_ids=failed_ids(case,'own'),hidden_failed_ids=failed_ids(case,'hidden')))
    s.dump(out/'results.json',results)
    s.dump(out/'summary.json',dict(timestamp=s.old.stamp(),script_sha256=s.sha(__file__),reader_calls=0,
        pytest_invocations=4,pytest_seconds=sum(r[k]['seconds'] for r in results for k in ['own','hidden']),
        same_own_failure_ids=results[0]['own_failed_ids']==results[1]['own_failed_ids'],
        own_failure_ids=[r['own_failed_ids'] for r in results],hidden_failure_ids=[r['hidden_failed_ids'] for r in results],
        scope='Post-hoc unblinded investigator mutation of one helper; not acquisition or a fresh task result'))
    print([(r['mutant'],r['own']['counts'],r['hidden']['counts']) for r in results])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
