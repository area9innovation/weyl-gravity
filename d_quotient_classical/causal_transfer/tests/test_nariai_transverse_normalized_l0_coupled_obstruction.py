import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_normalized_l0_coupled_obstruction import exact_data


class TransverseNormalizedL0CoupledObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_complete_normalized_family(self):
        self.assertEqual(self.data["normalized_L0_family"]["family_dimension"], 44)
        self.assertEqual(len(self.data["induced_corrections"]), 44)
        self.assertEqual(self.data["first_square"]["max_nonzero_defect_coefficients"], 0)

    def test_rank_obstruction(self):
        system = self.data["shifted_chain_system"]
        self.assertEqual(system["shape"], [7380, 44])
        self.assertEqual(system["rank"], 44)
        self.assertEqual(system["augmented_rank"], 45)
        self.assertEqual(system["kernel_dimension"], 0)
        self.assertEqual(len(system["full_column_rank_minor_rows"]), 44)
        self.assertNotEqual(system["full_column_rank_minor_determinant"], "0")

    def test_witness_and_scope(self):
        witness = self.data["normalized_left_null_witness"]
        self.assertEqual(witness["support_size"], 5)
        self.assertEqual(witness["left_null_map_defect"]["rank"], 0)
        self.assertEqual(witness["left_null_target_value"], "1")
        self.assertTrue(self.data["superseded_phi_witness"]["reachable"])
        self.assertFalse(self.data["interpretation"]["normalized_L0_coupled_repair_exists"])
        self.assertFalse(self.data["interpretation"]["complete_coupled_SDR_obstructed"])


if __name__ == "__main__":
    unittest.main()
