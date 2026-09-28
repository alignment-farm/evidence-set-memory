"""Boundary and arithmetic checks for the authored task, independent of fitting."""
import copy
import unittest
from quote_study import generate, execute, closure, correct, feature, current, select


class QuoteChecks(unittest.TestCase):
    def test_complete_and_omission(self):
        for history in generate(91, 3, 'test'):
            for episode in history['stages']:
                req, records = episode['request'], episode['records']
                selected = closure(req, records)
                self.assertTrue(correct(execute(req, selected), episode['expected']))
                for omitted in range(3):
                    self.assertFalse(correct(execute(req, selected[:omitted]+selected[omitted+1:]),
                                             episode['expected']))

    def test_corrections_change_complete_outcome(self):
        stages = generate(7, 1, 'test')[0]['stages']
        for before, after in [(1, 2), (2, 3)]:
            old = closure(stages[before]['request'], stages[before]['records'])
            answer = execute(stages[after]['request'], old)
            self.assertFalse(correct(answer, stages[after]['expected']))

    def test_labels_and_values_do_not_enter_features(self):
        episode = generate(81, 1, 'test')[0]['stages'][2]
        changed = copy.deepcopy(episode)
        changed['expected'] = {'secret': 'altered'}
        for record in changed['records']:
            if 'unit_cents' in record:
                record['unit_cents'] += 100000
        a = feature(episode['request'], episode['records'][:3], current(episode['records']))
        b = feature(changed['request'], changed['records'][:3], current(changed['records']))
        self.assertEqual(a, b)

    def test_half_up_tax(self):
        records = [dict(id='a@1', key='a', kind='item', revision=1, ref='b'),
                   dict(id='b@1', key='b', kind='contract', revision=1, ref='c', unit_cents=100),
                   dict(id='c@1', key='c', kind='tax', revision=1, bps=50)]
        self.assertEqual(execute(dict(item='a', quantity=1), records)['tax_cents'], 1)


if __name__ == '__main__':
    unittest.main()
