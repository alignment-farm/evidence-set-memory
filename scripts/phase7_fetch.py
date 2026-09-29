"""Recover and verify pinned source trees; never alter an existing checkout."""
import subprocess
from pathlib import Path
import phase7_edit as s


for name,url,tag,commit in [
    ('dotenv','https://github.com/theskumar/python-dotenv.git','v1.0.1','d6c0b9638349a7dd605d60ee555ff60421c1a594'),
    ('slugify','https://github.com/un33k/python-slugify.git','v8.0.4','f85f9488520148d5f6899b5639199882b605e30a')]:
    root=Path(s.ASSETS[name]['root'])
    if not root.exists():subprocess.run(['git','clone','--depth','1','--branch',tag,url,str(root)],check=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==commit
    manifest=s.load(s.PHASE/f'assets-v2/{name}-source-manifest.json')
    for path,item in manifest.items():assert s.sha(root/path)==item['sha256'],path
    assert (root/'LICENSE').read_bytes()==(s.PHASE/f'assets-v2/{name}-LICENSE.txt').read_bytes()
    print(dict(asset=name,commit=commit,verified_files=len(manifest)))
