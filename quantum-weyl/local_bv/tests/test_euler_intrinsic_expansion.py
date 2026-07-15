import unittest

from local_bv.algebra import canonical_sha256
from local_bv.euler_intrinsic_expansion import (
    euler_intrinsic_component_expansion,
)


class EulerIntrinsicExpansionTests(unittest.TestCase):
    def test_component_counts_and_coefficients(self) -> None:
        result = euler_intrinsic_component_expansion()
        components = result["components"]
        self.assertEqual(
            [(row["ghost_number"], row["form_degree"]) for row in components],
            [(1, 4), (2, 3), (3, 2), (4, 1), (5, 0)],
        )
        self.assertEqual([row["term_count"] for row in components], [3, 2, 1, 0, 0])
        self.assertEqual(
            [[term["coefficient"] for term in row["terms"]] for row in components],
            [
                [
                    {"numerator": 1, "denominator": 1},
                    {"numerator": 4, "denominator": 1},
                    {"numerator": 4, "denominator": 1},
                ],
                [
                    {"numerator": -4, "denominator": 1},
                    {"numerator": -8, "denominator": 1},
                ],
                [{"numerator": 4, "denominator": 1}],
                [],
                [],
            ],
        )
        cross_term = components[1]["terms"][1]
        self.assertEqual(
            [row["word"] for row in cross_term["expanded_words"]], ["UP", "PU"]
        )
        self.assertTrue(
            all(row["canonicalization_sign"] == 1 for row in cross_term["expanded_words"])
        )

    def test_verified_and_open_gates_are_separate(self) -> None:
        result = euler_intrinsic_component_expansion()
        checks = result["checks"]
        self.assertEqual(
            checks["top_carrier_polynomial_matches_declared_E4_decomposition"],
            "VERIFIED",
        )
        self.assertEqual(checks["bottom_factor_rule_closure"], "VERIFIED")
        self.assertEqual(
            checks["QW_a14_plus_dh_a23"],
            "VERIFIED_FOR_FROZEN_EULER_CARRIER_ALGEBRA",
        )
        self.assertEqual(
            result["ordinary_bidegree_projection"]["checks"]
            ["QW_a23_minus_dh_a32"],
            "VERIFIED",
        )
        self.assertEqual(
            result["epsilon_head_reconstruction"]["checks"]
            ["direct_RR_equals_W2_plus_4WX_plus_4X2"],
            "VERIFIED",
        )
        self.assertEqual(result["claim_boundary"]["intrinsic_tower_status"], "COMPLETE")
        payload = {
            key: value for key, value in result.items() if key != "expansion_sha256"
        }
        self.assertEqual(result["expansion_sha256"], canonical_sha256(payload))


if __name__ == "__main__":
    unittest.main()
