import unittest

from local_bv.algebra import canonical_sha256
from local_bv.generalized_connection import (
    euler_bidegree_manifests,
    euler_normalization_contract,
    generalized_connection_dictionary,
)


class GeneralizedConnectionContractTests(unittest.TestCase):
    def test_global_top_rescaling_resolves_source_coefficients(self) -> None:
        contract = euler_normalization_contract()
        self.assertEqual(
            contract["project_coefficients"],
            [
                {"numerator": 1, "denominator": 1},
                {"numerator": -4, "denominator": 1},
                {"numerator": 4, "denominator": 1},
            ],
        )
        self.assertEqual(
            contract["legacy_vector_status"],
            "REJECTED_AS_UNDERIVED_CARRIER_RESCALING",
        )

    def test_dictionary_and_all_bidegrees_are_frozen(self) -> None:
        dictionary = generalized_connection_dictionary()
        self.assertEqual(
            dictionary["dictionary_status"], "FROZEN_FOR_BIDEGREE_EXPANSION"
        )
        manifests = euler_bidegree_manifests()
        self.assertEqual(
            [(row["ghost_number"], row["form_degree"]) for row in manifests],
            [(1, 4), (2, 3), (3, 2), (4, 1), (5, 0)],
        )
        self.assertTrue(all(row["total_degree"] == 5 for row in manifests))
        self.assertEqual(
            [row["coarse_carrier_signature_count"] for row in manifests],
            [3, 2, 1, 0, 0],
        )
        self.assertEqual(
            [row["intrinsic_component_status"] for row in manifests[-2:]],
            [
                "STRUCTURALLY_ZERO_BY_R_LE_N_OVER_2",
                "STRUCTURALLY_ZERO_BY_R_LE_N_OVER_2",
            ],
        )
        self.assertEqual(
            [row["d_h_sign_on_this_component"] for row in manifests],
            [-1, 1, -1, 1, -1],
        )
        for manifest in manifests:
            payload = {
                key: value for key, value in manifest.items() if key != "manifest_sha256"
            }
            self.assertEqual(manifest["manifest_sha256"], canonical_sha256(payload))


if __name__ == "__main__":
    unittest.main()
