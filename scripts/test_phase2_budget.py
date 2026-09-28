import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import phase2_reader_budget as budget


class BudgetBoundary(unittest.TestCase):
    def test_only_length_retry_precedes_label_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'phase2/runs/confirmation-reader'
            def save(path,value):
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
            payload=dict(model='fixture',messages=[],max_tokens=1024)
            key=budget.digest(payload)
            other=dict(payload,messages=[{'role':'user','content':'other'}]);otherkey=budget.digest(other)
            response=lambda answer,finish:dict(choices=[dict(message=dict(content=json.dumps(answer)),finish_reason=finish)],usage=dict(prompt_tokens=10,completion_tokens=5))
            answer=dict(answer='yes',citations=[0])
            save(source/'costs.json',dict(requests=2))
            save(source/f'{key}-request.json',payload);save(source/f'{otherkey}-request.json',other)
            save(source/f'{key}-response.json',dict(response=response(answer,'length')))
            save(source/f'{otherkey}-response.json',dict(response=response(answer,'stop')))
            save(source/'outcomes.json',[dict(id='a',arm='all',selected=[0],request_hash=key),dict(id='a',arm='exact',selected=[0],request_hash=otherkey)])
            for name in ['development-reader','semantic-development-reader']:
                save(root/f'phase2/runs/{name}/costs.json',dict(requests=0))
            save(root/'.cache/phase2/partitions/confirmation-labels.json',[dict(id='a',answer='yes',aliases=[],supports=[0])])
            (root/'phase2/READER_BUDGET_DIAGNOSTIC.md').write_text('fixture')
            opened=[];read=budget.read
            def tracked(path):
                if path.name=='confirmation-labels.json':opened.append('labels')
                return read(path)
            def request(req,timeout):
                self.assertEqual(opened,[])
                self.assertEqual(json.loads(req.data),dict(payload,max_tokens=4096))
                return contextlib.closing(io.BytesIO(json.dumps(response(answer,'stop')).encode()))
            out=root/'result'
            with patch.object(budget,'ROOT',root),patch.object(budget,'read',tracked),patch.object(budget.urllib.request,'urlopen',request) as call,patch('sys.argv',['budget','--out',str(out)]),contextlib.redirect_stdout(io.StringIO()):
                budget.main()
            self.assertEqual(read(out/'costs.json')['requests'],1)
            self.assertEqual(opened,['labels'])
            self.assertEqual(read(out/'summary.json')['all']['complete'],1)
            self.assertEqual(read(out/'summary.json')['exact']['repaired_calls'],0)


if __name__=='__main__':unittest.main()
