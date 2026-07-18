import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_incidence_l1_rigidity import exact_data


class TransverseIncidenceL1RigidityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_complete_constraint_map_is_invertible(self):
        system = self.data["constraint_system"]
        self.assertEqual(system["shape"], [60, 60])
        self.assertEqual(system["rank"], 60)
        self.assertEqual(system["determinant"], "-1/68719476736")
        self.assertEqual(system["kernel_dimension"], 0)

    def test_normalization_and_unrepaired_target(self):
        self.assertEqual(
            self.data["normalization"]["p0_L0_minus_identity"]["nonzero_coefficients"],
            0,
        )
        self.assertEqual(self.data["unrepaired_shifted_chain"]["nonzero_coefficients"], 207)

    def test_scope(self):
        interpretation = self.data["interpretation"]
        self.assertFalse(interpretation["nonzero_homogeneous_incidence_L1_correction_exists"])
        self.assertFalse(interpretation["shifted_chain_repaired_in_this_ansatz"])
        self.assertFalse(interpretation["complete_coupled_SDR_obstructed"])


if __name__ == "__main__":
    unittest.main()
