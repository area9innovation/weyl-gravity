import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy import OUTPUT, build


class SameSignL1ActiveRestrictedCurrentDegeneracyTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_smooth_projective_radical_is_exact(self) -> None:
        witness = build()["universal_smooth_radical"]
        self.assertEqual(witness["jacobian_rank"], 3)
        self.assertEqual(witness["restricted_tangent_nullity"], 1)
        self.assertEqual(witness["absolute_current_occupation_ratio_positive_over_negative"], "13/192")
        self.assertEqual(witness["fixed_norm_tangency"], {"f_inner_delta_f": "0", "g_inner_delta_g": "0"})

    def test_both_scalar_cones_contain_the_degeneracy_ratio(self) -> None:
        payload = build()
        self.assertEqual([row["candidate_index"] for row in payload["scalar_cone_witnesses"]], [17, 20])
        self.assertTrue(payload["classification"]["degeneracy_occurs_inside_each_exact_scalar_cone"])
        self.assertFalse(payload["classification"]["proper_moment_map_connected_fibre_theorem_applicable_globally"])
        self.assertFalse(payload["classification"]["candidate18_active_restricted_current_classified"])


if __name__ == "__main__":
    unittest.main()
