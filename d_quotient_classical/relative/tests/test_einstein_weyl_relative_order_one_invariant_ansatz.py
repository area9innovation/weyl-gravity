import unittest
from d_quotient_classical.relative.einstein_weyl_relative_order_one_invariant_ansatz import build,validate

class OrderOneInvariantAnsatzTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.value=build()
    def test_schema_and_dimensions(self):
        validate(self.value); dims=self.value['homogeneous_symbol_dimensions']; self.assertEqual(dims['A1_exact_order_0_1_2'],[80,284,626]); self.assertEqual(dims['A2_exact_order_0_1_2'],[14,42,86])
    def test_solver_contract(self): self.assertEqual(self.value['order_one_solver_contract']['total_free_symbol_and_lower_coefficients'],406)
    def test_input_boundary(self):
        gate=self.value['input_adequacy']; self.assertEqual(gate['required_current_coefficient_jet_order_for_order_one_A1_C'],2); self.assertFalse(gate['current_payload_sufficient_for_full_order_one_incidence'])
    def test_fail_closed(self):
        flags=self.value['classification']; self.assertTrue(flags['complete_invariant_Hom_ansatz_through_order_one']); self.assertFalse(flags['order_one_top_descent_solved']); self.assertFalse(flags['positive_order_lift_exists']); self.assertFalse(flags['positive_order_lift_obstructed'])

if __name__=='__main__': unittest.main()
