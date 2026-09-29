"""Repository boundary-test evidence and exact phase-7 publication manifest."""
import argparse
import subprocess
import sys
import time
import phase7_edit as s


def run(command):
    target=s.PHASE/'manifest.json'
    if command=='tests':
        out=s.fresh(s.PHASE/'runs/boundary-tests');start=time.perf_counter()
        cmd=[sys.executable,'-m','unittest','discover','-s','scripts','-p','test_*.py','-v']
        r=subprocess.run(cmd,cwd=s.ROOT,text=True,capture_output=True)
        s.dump(out/'result.json',dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,
            seconds=time.perf_counter()-start,script_sha256=s.sha(__file__)))
        print(r.stderr);assert r.returncode==0;return
    if command=='build':
        assert not target.exists()
        paths=[p for p in s.PHASE.rglob('*') if p.is_file() and p!=target and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(s.PHASE).parts)]
        paths+=list((s.ROOT/'scripts').glob('phase7_*.py'))+[s.ROOT/'scripts/test_phase7_edit.py']
        paths += [s.ROOT/p for p in ['README.md','AGENTS.md','START.md','FEASIBILITY.md','pyproject.toml','uv.lock',
            'scripts/phase6_edit.py','scripts/phase6_energy.py','scripts/phase6_packaging.py','scripts/phase6_prompt.py',
            'phase6/runs/acquisition/model.json','phase6/runs/acquisition/examples.json',
            'phase6/runs/transfer/tasks.json','phase6/development-tasks.json']]
        paths += [p for p in (s.ROOT/'phase6/runs/transfer/states/transfer-get-key-literal').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        s.dump(target,dict(scope='Phase 7, including reused phase-6 mechanism and source history; older manifests remain historical',
            files={str(p.relative_to(s.ROOT)):dict(sha256=s.sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))}))
    data=s.load(target)
    for path,item in data['files'].items():assert s.sha(s.ROOT/path)==item['sha256'],path
    print(dict(files=len(data['files']),bytes=sum(i['bytes'] for i in data['files'].values())))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['tests','build','verify']);run(p.parse_args().command)
