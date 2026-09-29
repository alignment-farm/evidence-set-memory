"""One post-hoc fixed-reader continuation with authored public-scope feedback."""
import argparse
import ast
import json
import phase7_edit as s


def run(out):
    assert (s.PHASE/'runs/transfer/execution.json').exists()
    out=s.fresh(out);calls=out/'calls';calls.mkdir();run=s.PHASE/'runs/transfer'
    row=s.load(run/'transfer-cli-regex/ordinary_access/result.json');task=s.load(run/'tasks.json')[1]
    assert row['finished'];last=row['events'][-1]['request_hash']
    payload=s.load(run/f'calls/{last}-request.json')
    final=s.load(run/f'calls/{last}-response.json')['response']['choices'][0]['message']['content']
    payload['messages'].append(dict(role='assistant',content=final))
    feedback='Public requirement review: the current request explicitly asks to update the relevant function documentation. Your submitted patch forwards regex_pattern but leaves slugify_params without a docstring. Update that function documentation to describe the forwarding behavior while preserving the working implementation. Return one JSON edit action. This review supplies no private-test feedback.'
    payload['messages'].append(dict(role='user',content=json.dumps({'public_requirement_review':feedback})))
    asset=s.ASSETS['slugify'];case=s.copy_case(s.ROOT/row['source'],asset,s.ROOT/'.cache/phase7/review-repair'/out.name)
    for patch in row['patches']:s.apply_edits(case,asset,patch)
    assert s.source_hashes(case,asset)==row['source_result']
    assert not (case/'heldout_current.py').exists()
    key,response,reused=s.old.request(payload,calls);action=None;error=None
    try:
        if response['error']:raise ValueError(response['error'])
        action=s.parse(response['response'])
        if 'edits' not in action:raise ValueError('One response allotted to reviewed edit; no inferred extra calls')
        s.apply_edits(case,asset,action)
    except (ValueError,KeyError,TypeError,SyntaxError) as exc:error=str(exc)
    # No further participant response: private tests are only now materialized.
    (case/'public_current.py').write_text(task['public_test']);(case/'heldout_current.py').write_text(task['hidden_test'])
    for i,text in enumerate(row['prior_tests']):(case/f'prior_{i}.py').write_text(text)
    report=s.execute(case,asset,asset['tests']+['public_current.py','heldout_current.py']+[f'prior_{i}.py' for i in range(len(row['prior_tests']))],'reviewed')
    text=(case/'slugify/__main__.py').read_text()
    function=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='slugify_params')
    doc=ast.get_docstring(function)
    s.dump(out/'result.json',dict(timestamp=s.old.stamp(),script_sha256=s.sha(__file__),request_hash=key,
        original_logical_calls=len(row['events']),extra_model_calls=1,reused=reused,action=action,interface_error=error,
        authoritative_test=report,docstring=doc,executable_and_documentation_gate=report['returncode']==0 and bool(doc) and error is None,
        source_before=row['source_result'],source_after=s.source_hashes(case,asset),
        teacher='Investigator-authored public requirement/diff review, not reader self-detection or private-test feedback',
        scope='Post-hoc continuation; frozen outcomes and test-accepted canonical history unchanged'))
    print(dict(interface_error=error,tests=report['counts'],docstring=doc))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
