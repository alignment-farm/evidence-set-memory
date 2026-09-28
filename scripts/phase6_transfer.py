"""Freeze then materialize fresh source-edit requests; never trains on transfer."""
import argparse
import shutil
import phase6_edit as study
import phase6_energy as energy
import phase6_prompt
from phase6_packaging import files_selection


def tasks():
    # Authored requirements/checks; not read by acquisition and not in source inventory.
    return [dict(id='transfer-get-key-literal',request=
        'Extend get_key with an optional trailing interpolate: bool = True parameter after encoding. Forward it to DotEnv so interpolate=False returns the literal stored expression rather than expanding variables. Preserve existing positional/default behavior, encoding, missing-key handling, and every earlier accepted change. Update the docstring; do not edit tests.',
        public_test='''import dotenv

def test_get_key_literal(tmp_path, monkeypatch):
    monkeypatch.setenv('EXTERNAL', 'expanded')
    p = tmp_path / '.env'
    p.write_text('A=${EXTERNAL}\\n', encoding='utf-8')
    assert dotenv.get_key(p, 'A', interpolate=False) == '${EXTERNAL}'
    assert dotenv.get_key(p, 'A') == 'expanded'
''',hidden_test='''import dotenv

def test_literal_encoding_missing_and_positionals(tmp_path, monkeypatch):
    monkeypatch.setenv('EXTERNAL', 'outside')
    p = tmp_path / 'latin.env'
    p.write_bytes('A=é${EXTERNAL}\\nEMPTY=\\nNOVALUE\\n'.encode('latin-1'))
    assert dotenv.get_key(p, 'A', 'latin-1', False) == 'é${EXTERNAL}'
    assert dotenv.get_key(p, 'A', encoding='latin-1') == 'éoutside'
    assert dotenv.get_key(p, 'EMPTY', 'latin-1', False) == ''
    assert dotenv.get_key(p, 'NOVALUE', 'latin-1', False) is None
    assert dotenv.get_key(p, 'MISSING', 'latin-1', False) is None
'''),dict(id='transfer-preserve-newlines',request=
        'Update file rewriting used by set_key and unset_key to preserve untouched line-ending bytes, including mixed LF/CRLF files. For set_key, each new or replaced assignment and any separator inserted before an appended key must use the first LF or CRLF line-ending style found in the existing file; default to LF when there is no line ending. Do not normalize untouched lines. Preserve quoting, literal-backslash round trips, export, encoding, and all prior accepted APIs/behavior. This request does not require support for bare-CR files. Do not edit tests.',
        public_test='''import dotenv

def test_crlf_update_and_remove(tmp_path):
    p = tmp_path / '.env'
    p.write_bytes(b'A=old\\r\\nB=keep\\r\\n')
    dotenv.set_key(p, 'A', 'new')
    assert p.read_bytes() == b"A='new'\\r\\nB=keep\\r\\n"
    dotenv.unset_key(p, 'A')
    assert p.read_bytes() == b'B=keep\\r\\n'
''',hidden_test='''import dotenv
import pytest

@pytest.mark.parametrize('before, key, expected', [
    (b'B=keep\\r\\nA=old\\nC=tail', 'A', b"B=keep\\r\\nA='new'\\r\\nC=tail"),
    (b'B=keep\\r\\nC=tail', 'A', b"B=keep\\r\\nC=tail\\r\\nA='new'\\r\\n"),
    (b'B=keep\\nC=tail\\r\\n', 'A', b"B=keep\\nC=tail\\r\\nA='new'\\n"),
    (b'B=keep', 'A', b"B=keep\\nA='new'\\n"),
    (b'', 'A', b"A='new'\\n"),
])
def test_newline_variants(tmp_path, before, key, expected):
    p = tmp_path / '.env'; p.write_bytes(before)
    assert dotenv.set_key(p, key, 'new') == (True, key, 'new')
    assert p.read_bytes() == expected

def test_latin_export_backslash_and_unset(tmp_path):
    p = tmp_path / 'latin.env'
    p.write_bytes('B=é\\r\\nC=stay\\n'.encode('latin-1'))
    value = 'é' + chr(92)*2
    dotenv.set_key(p, 'A', value, export=True, encoding='latin-1')
    raw = p.read_bytes()
    assert raw.startswith('B=é\\r\\nC=stay\\n'.encode('latin-1'))
    assert raw.endswith(b'\\r\\n')
    assert dotenv.dotenv_values(p, encoding='latin-1', interpolate=False)['A'] == value
    dotenv.unset_key(p, 'B', encoding='latin-1')
    assert p.read_bytes().startswith(b'C=stay\\n')
''')]


def freeze():
    target=study.PHASE/'freeze.json'
    if target.exists():raise FileExistsError(target)
    paths=[study.ROOT/f'scripts/{name}' for name in ['phase6_edit.py','phase6_packaging.py','phase6_energy.py','phase6_transfer.py','phase6_prompt.py','test_phase6_edit.py']]
    paths += [study.PHASE/p for p in ['PROTOCOL.md','CLAIM.md','development-tasks.json','pyproject.toml','uv.lock','runs/acquisition/model.json','runs/acquisition/examples.json']]
    paths += [study.ROOT/'uv.lock',study.PHASE/'INTERFACE_CONTROL.md']
    paths += list((study.PHASE/'runs/development/states').rglob('*.py'))
    paths += list((study.PHASE/'runs/development/states').rglob('lineage.json'))
    study.dump(target,dict(timestamp=study.stamp(),files={str(p.relative_to(study.ROOT)):study.sha(p) for p in paths},
                          model=study.MODEL,source_commit=study.COMMIT,reader_cap=4096,attempt_call_cap=4,
                          future_tasks_materialized=False))


def transfer(out):
    frozen=study.load(study.PHASE/'freeze.json')
    for path,digest in frozen['files'].items():assert study.sha(study.ROOT/path)==digest,path
    phase6_prompt.install()
    out=study.fresh(out);calls=out/'calls';calls.mkdir();later=tasks()
    study.dump(out/'tasks.json',later)
    earlier=study.load(study.PHASE/'development-tasks.json')
    source=study.PHASE/f'runs/development/states/{earlier[-1]["id"]}'
    memory=study.load(source/'lineage.json');prior=[t[field] for t in earlier for field in ['public_test','hidden_test']]
    model=study.load(study.PHASE/'runs/acquisition/model.json');results=[]
    for task in later:
        candidates={}
        for policy in ['ordinary_access','full_context','empirical_reuse','learned_energy']:
            if policy=='learned_energy':chosen,work=energy.choose(task,source,model)
            else:
                actual=model[{'empirical_reuse':'ordinary_experience_policy',
                              'ordinary_access':'ordinary_baseline_policy',
                              'full_context':'broad_baseline_policy'}[policy]]
                if actual.endswith('_files'):chosen,work=files_selection(task,source,actual)
                else:
                    rows,_,_=study.records(source);chosen,work=study.select(task,rows,actual)
                work['chosen_proposal']=actual
            result,case=study.attempt(task,source,out/f'{task["id"]}/{policy}',policy,calls,prior,memory,(chosen,work))
            results.append(result);candidates[policy]=(result,case)
            study.dump(out/'results.json',results)
        passed=[p for p in candidates if candidates[p][0]['complete']]
        if not passed:
            study.dump(out/'blocked.json',dict(task=task['id'],reason='No complete canonical revision; diagnose, do not invent a successful history'))
            break
        chosen_policy=passed[0];result,case=candidates[chosen_policy]
        state=study.fresh(out/f'states/{task["id"]}');shutil.copytree(case/'src',state/'src');source=state
        memory.append(dict(requirement=task['request'],accepted_policy=chosen_policy,patches=result['patches'],source_hashes=result['source_result']))
        study.dump(state/'lineage.json',memory);prior.extend([task['public_test'],task['hidden_test']])
    # Repeated old obligations are retention/no-op probes, not new edit instances.
    for task in earlier:
        repeat=dict(task,id='retention-'+task['id'])
        chosen,work=files_selection(repeat,source,'ordinary_files')
        result,_=study.attempt(repeat,source,out/repeat['id'],'retention',calls,prior,memory,(chosen,work))
        results.append(result)
    study.dump(out/'results.json',results)
    study.dump(out/'execution.json',dict(timestamp=study.stamp(),script_sha256=study.sha(__file__),
        frozen_manifest_sha256=study.sha(study.PHASE/'freeze.json'),calls=len(list(calls.glob('*-response.json')))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','transfer']);parser.add_argument('--out')
    args=parser.parse_args()
    if args.command=='freeze':freeze()
    else:transfer(args.out)
