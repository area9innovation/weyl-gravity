import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_phi_only_shifted_chain_obstruction import exact_data


class TransversePhiOnlyShiftedChainObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_rank_obstruction(self):
        self.assertEqual(self.data["linear_system"]["shape"], [225, 45])
        self.assertEqual(self.data["linear_system"]["rank"], 45)
        self.assertEqual(len(self.data["linear_system"]["consistent_rows"]), 22)
        self.assertEqual(len(self.data["linear_system"]["obstructed_rows"]), 38)
        self.assertEqual(
            sorted(map(int, self.data["consistent_row_solutions"])),
            self.data["linear_system"]["consistent_rows"],
        )

    def test_normalized_witness(self):
        witness = self.data["normalized_left_null_witness"]
        self.assertEqual(witness["support_size"], 2)
        self.assertEqual(witness["left_null_map_defect"]["rank"], 0)
        self.assertEqual(witness["left_null_target_value"], "1")

    def test_scope(self):
        self.assertFalse(self.data["interpretation"]["first_order_Phi_only_repair_exists"])
        self.assertFalse(self.data["interpretation"]["full_coupled_SDR_repair_obstructed"])


if __name__ == "__main__":
    unittest.main()
