import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current import build


class Candidate1720AxisymmetricRestrictedCurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_both_active_cones_have_strict_occupation_imbalance(self) -> None:
        self.assertEqual([row["candidate_index"] for row in self.payload["candidate_rows"]], [17, 20])
        for row in self.payload["candidate_rows"]:
            self.assertEqual(len(row["active_ray_gap_witnesses"]), 2)
            self.assertTrue(all(item["negative_minus_positive"]["strictly_positive"] for item in row["active_ray_gap_witnesses"]))

    def test_singular_zariski_tangent_current_is_nondegenerate(self) -> None:
        theorem = self.payload["restricted_current_theorem"]
        self.assertEqual(theorem["two_parity_channel_affine_inertia"], [6, 10, 0])
        self.assertEqual(theorem["projective_zariski_tangent_inertia"], [5, 9, 0])
        self.assertEqual(theorem["projective_zariski_tangent_real_symplectic_rank"], 28)

    def test_smooth_locus_and_topology_remain_open(self) -> None:
        flags = self.payload["classification"]
        self.assertTrue(flags["axisymmetric_sections_singular"])
        self.assertFalse(flags["full_smooth_locus_restricted_current_classified"])
        self.assertFalse(flags["rotation_zero_fibre_connected"])
        self.assertFalse(flags["candidate18_active_variety_classified"])


if __name__ == "__main__":
    unittest.main()
