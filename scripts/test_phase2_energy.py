import copy
import unittest
import numpy as np
import torch
from phase2_energy import project,search,score_sets,represent,load,Energy,scores


class Checks(unittest.TestCase):
    def test_projection_and_gradient(self):
        rng=np.random.default_rng(8)
        z=project(rng.normal(size=20))
        self.assertAlmostEqual(float(z.sum()),4,places=6)
        self.assertTrue(np.all((z>=0)&(z<=1)))
        u=rng.normal(size=20);v=rng.normal(size=(20,20));v=(v+v.T)/2
        np.fill_diagonal(v,0)
        zz=torch.tensor(z,requires_grad=True)
        score=torch.tensor(u)@zz+.5*zz@torch.tensor(v)@zz
        gradient=torch.autograd.grad(score,zz)[0].numpy()
        np.testing.assert_allclose(gradient,u+v@z,rtol=1e-10)

    def test_exact_and_sign_equivalence(self):
        rng=np.random.default_rng(9)
        u=rng.normal(size=20);v=np.zeros((20,20))
        selected,_=search(u,v,'exact')
        self.assertEqual(set(selected),set(np.argsort(-u)[:4]))
        relaxed,_=search(u,v,'relaxed_swap')
        self.assertEqual(set(selected),set(relaxed))

    def test_input_boundary_and_permutation(self):
        examples,_,_,_,_=load('development')
        e=examples[0]
        x,p=represent(e)
        changed=copy.deepcopy(e)
        changed['answer']='EXAMINER SECRET'
        changed['supports']=[0,1]
        xx,pp=represent(changed)
        np.testing.assert_array_equal(x,xx);np.testing.assert_array_equal(p,pp)
        changed['paragraphs'].reverse()
        xx,pp=represent(changed)
        np.testing.assert_allclose(x,xx[::-1],atol=1e-7)
        np.testing.assert_allclose(p,pp[::-1,::-1],atol=1e-7)


if __name__=='__main__': unittest.main()
