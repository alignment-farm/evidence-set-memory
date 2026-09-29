"""Native upstream and scratch-containment preflights; no participant inference."""
import argparse
from pathlib import Path
import shutil
import subprocess
import phase7_edit as s


def run(out):
    out=s.fresh(out);reports={}
    for name,asset in s.ASSETS.items():
        source=Path(asset['root']);case=s.copy_case(source,asset,s.ROOT/'.cache/phase7/preflights'/out.name/name)
        report=s.execute(case,asset,asset['tests'],'upstream');s.dump(out/f'{name}-upstream.json',report);reports[name]=report['returncode']
        s.dump(out/f'{name}-source-manifest.json',s.old.file_manifest(source))
        shutil.copy2(source/'LICENSE',out/f'{name}-LICENSE.txt')
        if name=='slugify':
            text=f'''from pathlib import Path
import pytest

def test_archive_read_denied():
    with pytest.raises(PermissionError):
        Path({str(s.ROOT/'README.md')!r}).read_text()

def test_source_and_test_write_denied():
    for path in ['slugify/slugify.py', 'test.py']:
        with pytest.raises(PermissionError):
            Path(path).write_text('MUST NOT WRITE')

def test_private_file_absent_and_tmp_writable(tmp_path):
    assert not Path('heldout_current.py').exists()
    p = tmp_path / 'ok'; p.write_text('ok'); assert p.read_text() == 'ok'
'''
            (case/'scratch_security.py').write_text(text)
            checks=s.execute(case,asset,['scratch_security.py'],'security');s.dump(out/'scratch-security.json',checks)
            assert s.source_hashes(source,asset)==s.source_hashes(case,asset)
            reports['scratch_security']=checks['returncode']
    s.dump(out/'provenance.json',dict(timestamp=s.old.stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=s.ASSETS['slugify']['root'],text=True).strip(),
        python=subprocess.check_output([str(s.PYTHON),'--version'],text=True).strip(),
        dmr_inspect=s.json.loads(subprocess.check_output(['docker','model','inspect','qwen3.8:27b-q4_K_M'],text=True)),
        dmr_ps=subprocess.check_output(['docker','model','ps'],text=True),script_sha256=s.sha(__file__),
        investigator=dict(model='gpt-6-astra',reasoning='high',provider='openai',cli='0.158.0',session='01a0e7e4-68e2-7fb2-9a5d-2ea6873b86b8'),
        setup_failures=['Git clone tag 8.0.4 failed: remote branch absent; corrected to v8.0.4 after ls-remote.',
                        'Web open of GitHub tag URL failed; source verified through Git clone.']))
    print(reports);assert not any(reports.values())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
