"""Replay reviewed repair and supplement the immutable frozen-run cost ledger."""
import argparse
import ast
import copy
import phase7_edit as s


def strip_target_doc(text):
    tree=ast.parse(text)
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='slugify_params' and ast.get_docstring(node):
            node.body=node.body[1:]
    return ast.dump(tree,include_attributes=False)


def run(out):
    out=s.fresh(out);root=s.PHASE/'runs';repair=s.load(root/'review-repair/result.json')
    original=s.load(root/'transfer/transfer-cli-regex/ordinary_access/result.json');task=s.load(root/'transfer/tasks.json')[1]
    response=s.load(root/f'review-repair/calls/{repair["request_hash"]}-response.json')
    asset=s.ASSETS['slugify'];case=s.copy_case(s.ROOT/original['source'],asset,s.ROOT/'.cache/phase7/repair-audit'/out.name)
    for patch in original['patches']:s.apply_edits(case,asset,patch)
    before=(case/'slugify/__main__.py').read_text();s.apply_edits(case,asset,repair['action'])
    after=(case/'slugify/__main__.py').read_text()
    assert strip_target_doc(before)==strip_target_doc(after)
    assert s.source_hashes(case,asset)==repair['source_after']
    changed=[p for p in repair['source_after'] if repair['source_after'][p]!=repair['source_before'][p]]
    assert changed==['slugify/__main__.py']
    (case/'public_current.py').write_text(task['public_test']);(case/'heldout_current.py').write_text(task['hidden_test'])
    for i,text in enumerate(original['prior_tests']):(case/f'prior_{i}.py').write_text(text)
    test=s.execute(case,asset,asset['tests']+['public_current.py','heldout_current.py']+[f'prior_{i}.py' for i in range(len(original['prior_tests']))],'repair_replay')
    assert test['returncode']==0
    ledger=s.load(root/'audit/native-costs.json');audit=s.load(root/'audit/audit.json');docs=s.load(root/'documentation-audit/results.json')
    usage=response['response']['usage'];runs=ledger['runs'];original_tests=sum(g['pytest_invocations'] for r in runs for g in r['groups'].values())
    rows=[]
    for policy in ['ordinary_access','full_context','empirical_reuse','learned_energy']:
        native=runs[1]['groups'][policy+':checks=True'];part=[r for r in docs if r['policy']==policy]
        rows.append(dict(policy=policy,executable_complete=native['complete'],documentation_gate=sum(r['executable_and_documentation_gate'] for r in part),
            explicit_finish=native['finished'],logical_tokens=native['prompt_tokens']+native['completion_tokens'],logical_calls=native['logical_calls']))
    s.dump(out/'repair-replay.json',dict(test=test,source_hash_replayed=True,only_target_docstring_ast_changed=True,reader_calls=0))
    s.dump(out/'final-costs.json',dict(timestamp=s.old.stamp(),script_sha256=s.sha(__file__),frozen_transfer=rows,
        physical_calls=ledger['physical_calls']+1,prompt_tokens=ledger['prompt_tokens']+usage['prompt_tokens'],
        completion_tokens=ledger['completion_tokens']+usage['completion_tokens'],
        reader_seconds=ledger['reader_seconds']+response['seconds'],
        server_cached_prompt_tokens=sum(r['cached_prompt_tokens'] for r in runs)+usage['prompt_tokens_details']['cached_tokens'],
        review_repair=dict(model_calls=1,prompt_tokens=usage['prompt_tokens'],completion_tokens=usage['completion_tokens'],
            seconds=response['seconds'],pytest_invocations=1,pytest_seconds=repair['authoritative_test']['seconds'],
            provenance='Investigator-authored public requirement review; post-hoc ordinary continuation, not autonomous or frozen result'),
        native_pytest_invocations=dict(original_attempts=original_tests,preflight=ledger['preflight_tests'],retention=1,
            check_mutation=4,main_audit=audit['pytest_invocations'],review_repair=1,repair_audit=1),
        review_assisted_ordinary_sequence_tokens=rows[0]['logical_tokens']+usage['total_tokens'],
        new_training_fits=0,inherited_acquisition=ledger['inherited_acquisition'],
        backend_provenance_correction='The frozen ledger lists backend build unknown. runtime.json records the observed local serving binary/version; independent HTTPS endpoint attestation remains unknown.',
        extra_uninstrumented_work=['Two small read-only proposal inspections during transfer','provenance/status queries and unsuccessful metrics probe','investigator review and authoring labor'],
        interpretation='Tokens are native work, not dollars or joules. Logical cached deliveries are not free standalone deployment. Post-hoc review is separate from frozen comparison.'))
    print(rows)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
