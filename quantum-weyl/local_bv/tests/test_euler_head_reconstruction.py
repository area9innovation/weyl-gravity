import unittest

from local_bv.algebra import canonical_sha256
from local_bv.euler_head_reconstruction import euler_head_reconstruction_analysis


class EulerHeadReconstructionTests(unittest.TestCase):
    def test_exact_lorentzian_reconstruction_and_controls(self) -> None:
        result = euler_head_reconstruction_analysis()
        self.assertEqual(result["verified_case_count"], 210)
        self.assertEqual(result["nonzero_residual_count"], 0)
        self.assertEqual(
            result["case_counts"],
            {
                "WEYL_QUADRATIC": 55,
                "SCHOUTEN_QUADRATIC": 55,
                "WEYL_SCHOUTEN": 100,
            },
        )
        self.assertGreater(
            result["negative_controls"]["reverse_carrier_orientation"]
            ["failing_case_count"],
            0,
        )
        self.assertEqual(
            result["negative_controls"]
            ["mixed_4WX_coefficient_times_5_over_4"],
            {
                "failing_case_count": 0,
                "status": "INSENSITIVE_BY_WEYL_TRACEFREENESS",
            },
        )
        self.assertGreater(
            result["negative_controls"]["4X2_coefficient_times_5_over_4"]
            ["failing_case_count"],
            0,
        )
        audit = result["independent_convention_audit"]
        self.assertEqual(audit["epsilon_mismatch_count"], 0)
        self.assertEqual(audit["hodge_contraction_nonzero_residual_count"], 0)
        self.assertEqual(
            audit["euclidean_signature_negative_control_failure_count"], 24
        )
        self.assertEqual(audit["status"], "VERIFIED_INDEPENDENTLY")

    def test_rank_hash_and_fresh_copy(self) -> None:
        result = euler_head_reconstruction_analysis()
        self.assertEqual(result["weyl_constraint_rank"], 11)
        self.assertEqual(result["weyl_basis_dimension"], 10)
        payload = {
            key: value
            for key, value in result.items()
            if key != "reconstruction_sha256"
        }
        self.assertEqual(
            result["reconstruction_sha256"], canonical_sha256(payload)
        )
        result["checks"]["frozen_orientation_used"] = "CORRUPTED"
        self.assertEqual(
            euler_head_reconstruction_analysis()["checks"]
            ["frozen_orientation_used"],
            "VERIFIED",
        )


if __name__ == "__main__":
    unittest.main()
