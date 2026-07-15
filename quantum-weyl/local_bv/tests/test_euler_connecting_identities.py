import unittest

from local_bv.algebra import canonical_sha256
from local_bv.euler_connecting_identities import euler_connecting_identity_analysis


class EulerConnectingIdentityTests(unittest.TestCase):
    def test_exact_tensor_bases_close_every_reduced_covariant_sector(self) -> None:
        result = euler_connecting_identity_analysis()
        self.assertEqual(
            result["result_id"], "EULER_CONNECTING_TENSOR_SECTOR_AUDIT"
        )
        self.assertEqual(result["weyl_basis_dimension"], 10)
        self.assertEqual(result["cotton_basis_dimension"], 16)
        self.assertEqual(
            result["sector_nonzero_residual_counts"],
            {
                "Domega_Phi1_linear_W": 0,
                "Dtilde_Phi1_bilinear_W_Cotton": 0,
                "Domega_Phi2_dimension_identity": 0,
                "DW_Phi1_plus_Dtilde_Phi2": 0,
            },
        )
        self.assertEqual(
            result["checks"]["ordinary_bidegree_projection"], "NOT_COMPUTED"
        )
        self.assertEqual(
            result["claim_boundary"]["full_total_form_connecting_identity"],
            "NOT_COMPUTED",
        )

    def test_analysis_hash_is_reproducible(self) -> None:
        result = euler_connecting_identity_analysis()
        payload = {
            key: value for key, value in result.items() if key != "analysis_sha256"
        }
        self.assertEqual(result["analysis_sha256"], canonical_sha256(payload))

    def test_cached_analysis_is_returned_as_a_fresh_copy(self) -> None:
        first = euler_connecting_identity_analysis()
        first["checks"]["ordinary_bidegree_projection"] = "CORRUPTED"
        second = euler_connecting_identity_analysis()
        self.assertEqual(
            second["checks"]["ordinary_bidegree_projection"], "NOT_COMPUTED"
        )


if __name__ == "__main__":
    unittest.main()
