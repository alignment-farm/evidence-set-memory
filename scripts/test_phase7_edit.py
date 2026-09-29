import json
from pathlib import Path
import tempfile
import unittest
import phase7_edit as s


class SelfCheckBoundary(unittest.TestCase):
    def test_actions_are_exclusive_and_bounded(self):
        response=lambda x:{'choices':[{'message':{'content':json.dumps(x)}}]}
        self.assertEqual(s.parse(response({'finish':True})),{'finish':True})
        self.assertIn('check',s.parse(response({'check':'def test_x(): assert True'})))
        for obj in [{'finish':False},{'check':'x'*12001},{'read':[],'check':'pass'},{'shell':'pwd'}]:
            with self.assertRaises(ValueError):s.parse(response(obj))

    def test_patch_is_scope_limited_atomic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'slugify').mkdir();p=root/'slugify/a.py';p.write_text('x = 1\n')
            asset={'package':'slugify'}
            with self.assertRaises(ValueError):s.apply_edits(root,asset,{'edits':[{'path':'test.py','old':'x','new':'y'}]})
            with self.assertRaises(SyntaxError):s.apply_edits(root,asset,{'edits':[{'path':'slugify/a.py','old':'x = 1','new':'x = ('}]})
            self.assertEqual(p.read_text(),'x = 1\n')

    def test_private_content_does_not_change_selection(self):
        source=Path(s.ASSETS['slugify']['root'])
        if not source.exists():self.skipTest('Fetch pinned source for representation check')
        rows,_,_=s.records(source,s.ASSETS['slugify'])
        task={'request':'Preserve slugify behavior','public_test':'import slugify','hidden_test':'secret A'}
        a,_=s.selection(task,source,rows,'learned_energy');task['hidden_test']='completely different secret B'
        b,_=s.selection(task,source,rows,'learned_energy')
        self.assertEqual(a,b)


if __name__=='__main__':unittest.main()
