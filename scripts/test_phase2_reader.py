import unittest
from phase2_reader import parse,grade


class Checks(unittest.TestCase):
    def test_public_format_repair(self):
        response=dict(choices=[dict(message=dict(content='An explanation.\n```json\n{"answer":"Paris","citations":[1,3]}\n```'))])
        self.assertEqual(parse(response),dict(answer='Paris',citations=[1,3]))

    def test_truncation_and_invalid_citations(self):
        response=dict(choices=[dict(message=dict(content='{"answer":"Paris", "citations":['))])
        self.assertTrue(parse(response)['parse_error'])
        m=grade(dict(answer='Paris',citations=[1,3]),dict(answer='Paris',aliases=[],supports=[1,3]),[1,2])
        self.assertEqual(m['answer_em'],1);self.assertEqual(m['complete'],0)


if __name__=='__main__':unittest.main()
