"""Post-hoc audit of an explicit requirement not covered by native tests."""
import argparse
import ast
import phase7_edit as s


def doc(text,symbol):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==symbol)
    return ast.get_docstring(node)


def run(out):
    assert (s.PHASE/'runs/transfer/execution.json').exists(),'Do not report final gates while transfer is running'
    out=s.fresh(out);results=[]
    for row in s.load(s.PHASE/'runs/transfer/results.json'):
        path,symbol=('slugify/slugify.py','slugify') if row['task']=='transfer-iterable-options' else ('slugify/__main__.py','slugify_params')
        source=s.ROOT/row['source'];before=(source/path).read_text();after=before
        for patch in row['patches']:
            for edit in patch['edits']:
                if edit['path']==path:
                    assert after.count(edit['old'])==1;after=after.replace(edit['old'],edit['new'],1)
        old_doc=doc(before,symbol);new_doc=doc(after,symbol)
        changed=bool(new_doc) and old_doc!=new_doc
        results.append(dict(task=row['task'],policy=row['policy'],frozen_executable_complete=row['complete'],
            explicit_finish=row['finished'],documentation_updated=changed,
            executable_and_documentation_gate=row['complete'] and changed,
            before_docstring=old_doc,after_docstring=new_doc,
            doc_scope='Requested relevant function documentation; unchanged/missing is a clear omission. Changed text still needs semantic review.'))
    s.dump(out/'results.json',results)
    s.dump(out/'provenance.json',dict(timestamp=s.old.stamp(),script_sha256=s.sha(__file__),reader_calls=0,
        native_test_calls=0,scope='Post-hoc requirement audit, not a refit, new model attempt or overwritten frozen score'))
    print([{k:r[k] for k in ['task','policy','documentation_updated','executable_and_documentation_gate']} for r in results])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
