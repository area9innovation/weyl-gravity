import unittest

from local_bv.algebra import canonical_sha256
from local_bv.euler_bidegree_projection import euler_bidegree_projection_analysis


class EulerBidegreeProjectionTests(unittest.TestCase):
    def test_connecting_equations_and_negative_controls(self) -> None:
        result = euler_bidegree_projection_analysis()
        self.assertEqual(
            result["nonzero_residual_counts"],
            {"g2_p4": 0, "g3_p3": 0, "g4_p2": 0},
        )
        self.assertGreater(
            result["negative_controls"]["mixed_UP_coefficient_perturbation"]
            ["failing_case_count"],
            0,
        )
        self.assertEqual(
            result["negative_controls"]["Cotton_bridge_relative_sign_flip"],
            {
                "failing_case_count": 0,
                "status": "PHYSICAL_SUBSPACE_INSENSITIVE_BY_COTTON_IDENTITIES",
            },
        )
        self.assertEqual(
            result["negative_controls"]["raw_Cotton_row_wiring_probe"]["status"],
            "EXPECTED_WIRING_CHANGE_OBSERVED",
        )
        self.assertEqual(
            [row["pairing_status"] for row in result["cancellation_receipts"]],
            ["RIGHT_EQUALS_NEGATIVE_LEFT", "RIGHT_EQUALS_NEGATIVE_LEFT"],
        )
        self.assertTrue(
            all(row["left_term_count"] for row in result["cancellation_receipts"])
        )

    def test_rank_receipt_and_hash(self) -> None:
        result = euler_bidegree_projection_analysis()
        self.assertEqual(
            result["constraint_rank_receipt"],
            {
                "weyl_coordinate_dimension": 21,
                "weyl_constraint_rank": 11,
                "cotton_coordinate_dimension": 24,
                "cotton_constraint_rank": 8,
                "symmetric_schouten_dimension": 10,
            },
        )
        payload = {
            key: value for key, value in result.items() if key != "projection_sha256"
        }
        self.assertEqual(result["projection_sha256"], canonical_sha256(payload))

    def test_cached_analysis_is_returned_as_a_fresh_copy(self) -> None:
        first = euler_bidegree_projection_analysis()
        first["checks"]["QW_a14_plus_dh_a23"] = "CORRUPTED"
        second = euler_bidegree_projection_analysis()
        self.assertEqual(second["checks"]["QW_a14_plus_dh_a23"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
