"""Recover exact intermediate source bytes from the frozen final implementation.

No worktree checkout or overwrite. Every reconstruction must match its recorded
run hash before writing. The two earlier revisions are available directly in Git.
"""
import argparse
import hashlib
import subprocess
from pathlib import Path
import phase5_config as study


def replace_once(text, old, new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def restore(out):
    out=study.fresh(out)
    current=(study.ROOT/'scripts/phase5_config.py').read_text()
    versions={}
    for name,commit in [('development','f9959c3'),('balanced','d263f86')]:
        versions[name]=subprocess.check_output(['git','show',f'{commit}:scripts/phase5_config.py'],
                                              cwd=study.ROOT,text=True)
    # These edits reverse only changes made after the balanced-final run finished.
    start=current.index('\ndef extend_chains(');end=current.index('\ndef dependencies(',start)
    v4=current[:start]+current[end:]
    v4=replace_once(v4,"                    transfer_regime=history.get('transfer_regime','development'),\n",'')
    v4=replace_once(v4,"data=extend_chains(histories(freeze_data['confirmation_seed'],freeze_data['confirmation_histories'],'transfer'))",
                       "data=histories(freeze_data['confirmation_seed'],freeze_data['confirmation_histories'],'transfer')")
    v4=replace_once(v4,"    work.update(seconds=time.perf_counter()-start,\n                energy=float(best.sum() if method=='hard' else feature(best, rep)@weights))",
                       "    work.update(seconds=time.perf_counter()-start, energy=float(feature(best, rep)@weights))")
    versions['balanced-final']=v4
    v3=replace_once(v4,"    if method in ['exact','hard']:","    if method == 'exact':")
    v3=replace_once(v3,"        if method=='hard':\n            f=feature(z,rep)\n            # Public logical constraints plus record count; no learned reward.\n            scores=np.where((f[:,0]==0)&(f[:,2]==0),f[:,1],np.inf)\n",'')
    v3=replace_once(v3,"           Path(development).resolve()/'native_syntax-model.json',\n           ROOT/'phase5/runs/constraint-energy/native_syntax-model.json']",
                       "           Path(development).resolve()/'native_syntax-model.json']")
    v3=replace_once(v3,"    rows,summary=evaluate(data,model,'native_syntax',['ordinary','all','untrained','exact','relax','hard'])\n    diagnostic=load(ROOT/'phase5/runs/constraint-energy/native_syntax-model.json')\n    diagnostic_rows,diagnostic_summary=evaluate(data,diagnostic,'native_syntax',['exact'])\n    for row in diagnostic_rows:row['method']='constraint_exact'\n    rows+=diagnostic_rows;summary['constraint_exact']=diagnostic_summary['exact']",
                       "    rows,summary=evaluate(data,model,'native_syntax',['ordinary','all','untrained','exact','relax','relax_flip'])")
    versions['constraint-energy']=v3
    result={}
    for name,source in versions.items():
        expected='3c7da4af6fa8cfe4f99c4146aca8a22ef44c3bfb01260560504b4e546c51ff36' if name=='balanced' else study.load(study.ROOT/f'phase5/runs/{name}/provenance.json')['implementation_sha256']
        actual=hashlib.sha256(source.encode()).hexdigest()
        assert actual==expected,(name,actual,expected)
        (out/f'{name}.py').write_text(source)
        result[name]=actual
    study.dump(out/'verification.json',result)
    print(result)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    restore(parser.parse_args().out)
