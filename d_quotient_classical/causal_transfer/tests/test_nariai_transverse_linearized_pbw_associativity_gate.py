import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_linearized_pbw_associativity_gate import exact_data


class TransverseLinearizedPBWAssociativityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_phi_definition_is_exact(self):
        self.assertEqual(self.data["phi_definition"]["base_defect_coefficients"], 0)
        self.assertEqual(self.data["phi_definition"]["variation_defect_coefficients"], 0)

    def test_linearized_associator_is_nonzero(self):
        self.assertEqual(self.data["associator"]["base_nonzero_coefficients"], 0)
        self.assertEqual(self.data["associator"]["variation_nonzero_coefficients"], 209)
        self.assertEqual(self.data["associator"]["normalized_witness"]["normalized_value"], "1")

    def test_claim_is_fail_closed(self):
        self.assertFalse(self.data["reported_shifted_chain"]["operator_obstruction_authoritative"])
        self.assertTrue(self.data["interpretation"]["shifted_chain_obstruction_superseded"])
        self.assertFalse(self.data["interpretation"]["rank_310_transverse_SDR_decided"])


if __name__ == "__main__":
    unittest.main()
