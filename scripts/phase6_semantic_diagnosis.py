"""One post-freeze authored semantic intervention; zero model calls."""
import argparse
import ast
import phase6_edit as study


def run(out):
    out=study.fresh(out);root=study.PHASE/'runs/transfer'
    assert (root/'execution.json').exists(),'Wait for all frozen participant work to end'
    task=study.load(root/'tasks.json')[1]
    original=study.load(root/'transfer-preserve-newlines/ordinary_access/result.json')
    source=root/'states/transfer-get-key-literal'
    case=study.copy_case(source,study.ROOT/'.cache/phase6/semantic-diagnosis'/out.name)
    for patch in original['patches']:study.apply_edits(case,patch)
    before_hashes={str(p.relative_to(case)):study.sha(p) for p in (case/'src').rglob('*.py')}
    assert before_hashes==original['source_result']
    old_tasks=study.load(study.PHASE/'development-tasks.json')+[study.load(root/'tasks.json')[0]]
    prior=[t[field] for t in old_tasks for field in ['public_test','hidden_test']]
    for i,text in enumerate(prior):(case/f'prior_{i}.py').write_text(text)
    (case/'public_current.py').write_text(task['public_test']);(case/'heldout_current.py').write_text(task['hidden_test'])
    targets=['tests','public_current.py','heldout_current.py']+[f'prior_{i}.py' for i in range(len(prior))]
    before=study.test(case,targets,'before');study.dump(out/'before.json',before)
    path='src/dotenv/main.py';text=(case/path).read_text();lines=text.splitlines(keepends=True)
    helper=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='_detect_line_ending')
    old=''.join(lines[helper.lineno-1:helper.end_lineno]).rstrip('\n')
    new='''def _detect_line_ending(source: IO[str]) -> str:
    content = source.read()
    source.seek(0)
    first_lf = content.find("\\n")
    return "\\r\\n" if first_lf > 0 and content[first_lf - 1] == "\\r" else "\\n"'''
    patch={'edits':[dict(path=path,old=old,new=new)]};study.apply_edits(case,patch)
    after=study.test(case,targets,'after');study.dump(out/'after.json',after);study.dump(out/'authored-intervention.json',patch)
    study.dump(out/'summary.json',dict(original_complete=original['complete'],before_returncode=before['returncode'],
        after_returncode=after['returncode'],before_counts=before['counts'],after_counts=after['counts'],
        pytest_invocations=2,seconds=before['seconds']+after['seconds'],model_calls=0,
        original_patch_source_replayed=True,causal_claim='Only the helper changed; comparison is post-hoc and unblinded',
        script_sha256=study.sha(__file__),timestamp=study.stamp()))
    print(dict(before=before['counts'],after=after['counts']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
