"""Verify/recover the exact three preflight harness revisions (no execution)."""
import argparse
import hashlib
import phase6_edit as study


def main(out):
    out=study.fresh(out);current=(study.ROOT/'scripts/phase6_edit.py').read_text()
    old=current.replace("    out=fresh(out)\n    work_id=hashlib.sha256(str(out).encode()).hexdigest()[:20]\n    case=copy_case(source,ROOT/'.cache/phase6/work'/work_id)",
                        "    out=fresh(out);case=copy_case(source,out/'case')")
    old=old.replace("baseline['output'][-6000:].replace(str(case),'<CASE>')","baseline['output'][-6000:]")
    old=old.replace("public['output'][-14000:].replace(str(case),'<CASE>')","public['output'][-14000:]")
    versions={'v3':old}
    versions['v2']=old.replace(' (require-not (literal "/dev/ptmx"))','')
    original_line=next(line for line in old.splitlines() if '(deny file-write*' in line)
    versions['v1']=old.replace(original_line,'    (deny file-write* (require-not (subpath "{case}")))')
    hashes={}
    for version,text in versions.items():
        expected=study.load(study.PHASE/f'assets/{version}-provenance.json')['script_sha256']
        digest=hashlib.sha256(text.encode()).hexdigest();assert digest==expected,(version,digest,expected)
        (out/f'{version}.py').write_text(text);hashes[version]=digest
    study.dump(out/'verification.json',hashes);print(hashes)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    main(parser.parse_args().out)
