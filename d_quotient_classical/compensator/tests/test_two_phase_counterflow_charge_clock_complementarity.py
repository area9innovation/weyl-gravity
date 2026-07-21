import unittest
import sympy as sp
from d_quotient_classical.compensator.two_phase_counterflow_charge_clock_complementarity import documents, finite_rank_fixture

class ChargeClockTests(unittest.TestCase):
    def test_documents(self):
        c,p=documents(); self.assertFalse(c["bounded_stability"]); self.assertEqual(c["real_exponential_growing_roots"],0); self.assertTrue(p["branch_dichotomy"]["no_averaging"])
    def test_rank_theorem(self):
        self.assertTrue(finite_rank_fixture(sp.Matrix([[1]]),sp.Matrix([1]))["D_null_on_constraint_tangent"])
        self.assertFalse(finite_rank_fixture(sp.Matrix([[1,0]]),sp.Matrix([0,1]))["D_null_on_constraint_tangent"])
    def test_no_fixed_clock_promotion(self): self.assertEqual(documents()[1]["branch_dichotomy"]["fixed_Q_rel"]["relative_clock_dimension"],0)
if __name__=="__main__": unittest.main()
