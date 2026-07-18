import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_phi_second_order_obstruction import exact_data


class TransversePhiSecondOrderObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_complete_rank_screen(self):
        system = self.data["coefficient_system"]
        self.assertEqual(system["shape"], [525, 135])
        self.assertEqual(system["rank"], 130)
        self.assertEqual(system["kernel_dimension"], 5)
        self.assertEqual(len(system["full_rank_minor"]["rows"]), 130)
        self.assertEqual(len(system["full_rank_minor"]["columns"]), 130)

    def test_obstruction_multiplicity_and_witness(self):
        system = self.data["coefficient_system"]
        self.assertEqual(len(system["consistent_rows"]), 29)
        self.assertEqual(len(system["obstructed_rows"]), 31)
        self.assertEqual(self.data["normalized_left_null_witness"]["support_size"], 2)
        self.assertEqual(self.data["normalized_left_null_witness"]["left_null_target_value"], "1")

    def test_scope(self):
        self.assertFalse(self.data["interpretation"]["order_two_Phi_only_repair_exists"])
        self.assertFalse(self.data["interpretation"]["complete_coupled_SDR_obstructed"])


if __name__ == "__main__":
    unittest.main()
