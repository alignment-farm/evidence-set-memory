"""Archive existing preflight evidence or reacquire the immutable upstream source."""
import argparse
import shutil
import subprocess
import phase6_edit as study


def main(command):
    if command=='archive':
        dest=study.fresh(study.PHASE/'assets')
        for version in ['v1','v2','v3']:
            source=study.ROOT/f'.cache/phase6/preflight-{version}'
            for name in ['upstream-tests.json','provenance.json']:
                shutil.copy2(source/name,dest/f'{version}-{name}')
        shutil.copy2(study.ROOT/'.cache/phase6/preflight-v3/source-manifest.json',dest/'source-manifest.json')
        assert (study.PHASE/'UPSTREAM_LICENSE.txt').read_bytes()==(study.ASSET/'LICENSE').read_bytes()
    elif command=='fetch':
        if not study.ASSET.exists():
            subprocess.run(['git','clone','--depth','1','--branch','v1.0.1',
                            'https://github.com/theskumar/python-dotenv.git',str(study.ASSET)],check=True)
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=study.ASSET,text=True).strip()==study.COMMIT
        manifest=study.load(study.PHASE/'assets/source-manifest.json')
        for path,entry in manifest.items():assert study.sha(study.ASSET/path)==entry['sha256'],path
        print({'verified_source_files':len(manifest)})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['archive','fetch'])
    main(parser.parse_args().command)
