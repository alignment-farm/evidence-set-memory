import unittest
import numpy as np
import torch
import phase5_config as study


class ConfigStudy(unittest.TestCase):
    def setUp(self):
        self.data=study.histories(100,6,'unit')

    def test_native_matches_independent_expected_and_minimal_closure(self):
        for h in self.data:
            for ep in h['episodes']:
                rep=study.represent(ep['request'],ep['records'],'native_syntax')
                chosen=study.closure(rep)
                full=study.render(ep['request'],rep['pool'])
                compact=study.render(ep['request'],study.selected(rep['pool'],chosen))
                self.assertEqual(full['value'],ep['expected'])
                self.assertEqual(compact['value'],ep['expected'])
                for removed in chosen:
                    omitted=study.selected(rep['pool'],[i for i in chosen if i!=removed])
                    self.assertFalse(study.grade(ep,omitted,study.render(ep['request'],omitted)))

    def test_revision_scope_and_cache_validity(self):
        for h in self.data:
            eps=h['episodes']
            self.assertEqual(eps[0]['expected'],eps[1]['expected'])
            self.assertNotEqual(eps[1]['expected'],eps[2]['expected'])
            self.assertNotEqual(eps[2]['expected'],eps[3]['expected'])
            self.assertEqual(eps[3]['expected'],eps[4]['expected'])
            for ep in eps:
                pool=study.eligible(ep['request'],ep['records'])
                self.assertEqual(len(pool),9)
                self.assertTrue(all(r['scope']=='production' for r in pool))

    def test_representation_is_label_blind_and_escape_default_cases_differ(self):
        differences=0
        for h in self.data:
            for ep in h['episodes']:
                ep['expected']='deliberately incorrect private expected'
                a=study.represent(ep['request'],ep['records'],'explicit_only')
                b=study.represent(ep['request'],ep['records'],'native_syntax')
                differences+=a['edges']!=b['edges']
                self.assertNotIn('expected',a)
        self.assertGreater(differences,0)

    def test_energy_multilinear_gradient_and_discrete_score_identity(self):
        ep=self.data[1]['episodes'][0]
        rep=study.represent(ep['request'],ep['records'],'native_syntax')
        z=np.random.default_rng(5).random(9);w=np.array([4.,.2,3.,-.1])
        t=torch.tensor(z,requires_grad=True)
        loss=w[0]*(1-t[rep['root']])+w[1]*t.sum()
        for i,j in rep['edges']:loss+=w[2]*t[i]*(1-t[j])+w[3]*t[i]*t[j]
        loss.backward()
        eps=1e-6
        fd=[]
        for i in range(9):
            delta=np.zeros(9);delta[i]=eps
            fd.append((study.feature(z+delta,rep)@w-study.feature(z-delta,rep)@w)/(2*eps))
        np.testing.assert_allclose(t.grad.numpy(),fd,atol=1e-8)
        x=study.vertices(9);energy=study.feature(x,rep)@w
        self.assertEqual(int(np.argmin(energy)),int(np.argmax(-energy)))

    def test_hard_energy_equals_ordinary_without_learned_parameters(self):
        for h in self.data:
            for ep in h['episodes']:
                rep=study.represent(ep['request'],ep['records'],'native_syntax')
                indices,_=study.search(rep,np.zeros(4),'hard')
                self.assertEqual(indices,study.closure(rep))

    def test_longer_chain_constructor_preserves_native_result(self):
        expanded=study.extend_chains(self.data)
        for h in expanded:
            for ep in h['episodes']:
                rep=study.represent(ep['request'],ep['records'],'native_syntax')
                self.assertEqual(study.render(ep['request'],rep['pool'])['value'],ep['expected'])
                indices,_=study.search(rep,np.zeros(4),'hard')
                self.assertEqual(indices,study.closure(rep))

    def test_cache_invalidation_and_repair_do_not_use_hidden_grade(self):
        model={'weights':[20.,1.,10.,0.],'initial':[0.,0.,0.,0.]}
        rows,summary=study.evaluate(self.data[:1],model,'native_syntax',['ordinary'])
        self.assertEqual(summary['ordinary']['cache_hits'],2)
        self.assertEqual(summary['ordinary']['cache_invalidations'],2)
        self.assertEqual(summary['ordinary']['repairs'],0)
        self.data[0]['episodes'][0]['expected']='examiner-only corruption'
        rows,summary=study.evaluate(self.data[:1],model,'native_syntax',['ordinary'])
        self.assertFalse(rows[0]['first_complete'])
        self.assertIsNone(rows[0]['repair'])
        self.assertTrue(rows[1]['cache_hit'])


if __name__=='__main__':unittest.main()
