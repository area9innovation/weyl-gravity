import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy import OUTPUT, build


class Candidate18ActiveRestrictedCurrentDegeneracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(OUTPUT.read_text())

    def test_certificate_rebuilds_exactly(self) -> None:
        self.assertEqual(self.payload, build())

    def test_two_smooth_projective_radical_families(self) -> None:
        rows = self.payload["active_current_reduction"]["smooth_radical_families"]
        self.assertEqual([row["z"] for row in rows], [["1", "1"], ["1", "-1"]])
        self.assertTrue(all(row["projective_current_radical_complex_dimension"] == 4 for row in rows))
        self.assertTrue(all(row["active_rank_one_factors_nonzero"] for row in rows))

    def test_ratio_one_lift_is_bounded_and_fail_closed(self) -> None:
        scalar = self.payload["scalar_cone_witness"]
        flags = self.payload["classification"]
        self.assertEqual(scalar["ray_mixture"], "R3+s18*R1")
        self.assertEqual(scalar["resulting_positive_over_negative_ratio"], "1")
        self.assertTrue(flags["degenerate_points_are_bounded_second_order_tangents"])
        self.assertFalse(flags["candidate18_global_active_component_symplectic_orbifold"])
        self.assertFalse(flags["complete_candidate18_degeneracy_divisor_classified"])


if __name__ == "__main__":
    unittest.main()
