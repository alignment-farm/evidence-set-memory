"""Code-edit interface and information-boundary tests, no reader calls."""
import json
from pathlib import Path
import tempfile
import unittest
import phase6_edit as study


class EditBoundary(unittest.TestCase):
    def test_scope_and_atomic_unique_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            case=Path(folder);(case/'src/dotenv').mkdir(parents=True)
            source=case/'src/dotenv/main.py';source.write_text('def f():\n    return 1\n')
            for path in ['tests/test_main.py','../other.py','src/dotenv/../../bad.py']:
                with self.assertRaises(ValueError):
                    study.apply_edits(case,{'edits':[dict(path=path,old='return 1',new='return 2')]})
            with self.assertRaises(ValueError):
                study.apply_edits(case,{'edits':[dict(path='src/dotenv/main.py',old='return 1',new='return 2'),
                                                dict(path='src/dotenv/main.py',old='not present',new='pass')]})
            self.assertIn('return 1',source.read_text())
            with self.assertRaises(SyntaxError):
                study.apply_edits(case,{'edits':[dict(path='src/dotenv/main.py',old='return 1',new='return (')]})
            self.assertIn('return 1',source.read_text())

    def test_json_only_recognized_actions(self):
        wrap=lambda text:{'choices':[{'message':{'content':text}}]}
        self.assertEqual(study.parse_response(wrap('text {"edits": []}')),{'edits':[]})
        self.assertEqual(study.parse_response(wrap('```json\n{"read":["src/dotenv/main.py"]}\n```'))['read'],['src/dotenv/main.py'])
        with self.assertRaises(ValueError):study.parse_response(wrap('{"answer":"done"}'))

    def test_selection_does_not_consume_hidden_tests(self):
        if not study.ASSET.exists():self.skipTest('Source asset not downloaded')
        rows,_,_=study.records(study.ASSET)
        task=study.load(study.PHASE/'development-tasks.json')[0]
        for policy in ['ordinary','all','pointwise','root_only']:
            original,_=study.select(task,rows,policy)
            task['hidden_test']='secret answer and desired support certificate'
            changed,_=study.select(task,rows,policy)
            self.assertEqual([r['id'] for r in original],[r['id'] for r in changed])


if __name__=='__main__':unittest.main()
