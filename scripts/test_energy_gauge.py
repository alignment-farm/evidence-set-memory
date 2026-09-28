"""Fixed-cardinality quadratic-score equivalence, independent of benchmark labels."""
import itertools
import unittest
import numpy as np


class FixedCardinalityGauge(unittest.TestCase):
    def test_same_discrete_score_different_fractional_extension(self):
        rng=np.random.default_rng(22);n=20;k=4
        u=rng.normal(size=n);v=rng.normal(size=(n,n));v=(v+v.T)/2;np.fill_diagonal(v,0)
        sets=np.zeros((4845,n))
        for index,chosen in enumerate(itertools.combinations(range(n),k)):sets[index,list(chosen)]=1
        def score(z,a,b):return z@a+.5*np.einsum('bi,ij,bj->b',z,b,z)
        fractional=rng.dirichlet(np.ones(n)*20,size=50)*k
        self.assertTrue(np.all(fractional<=1))
        for weight in [-4.,-1.,-.25,0.,.25,1.,4.]:
            transformed_u=u+(k-1)*weight
            transformed_v=v-2*weight;np.fill_diagonal(transformed_v,0)
            np.testing.assert_allclose(score(sets,u,v),score(sets,transformed_u,transformed_v),atol=1e-12)
            expected=score(fractional,u,v)-weight*np.sum(fractional*(1-fractional),axis=1)
            np.testing.assert_allclose(expected,score(fractional,transformed_u,transformed_v),atol=1e-12)


if __name__=='__main__':unittest.main()
