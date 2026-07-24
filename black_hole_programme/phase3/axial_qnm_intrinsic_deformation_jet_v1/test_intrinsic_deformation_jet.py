import copy
import json
import unittest

from . import verify


class IntrinsicDeformationJetTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(verify.CERTIFICATE.read_text())

    def test_certificate_verifies(self):
        self.assertEqual(verify.verify_document(self.document), [])

    def test_dual_basis_transpose_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["dual_number_connection"]["basis"] = ["1", "epsilon"]
        self.assertIn(
            "dual-number basis convention drift",
            verify.verify_document(mutated),
        )

    def test_shift_sign_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["simple_zero_shift"]["omega_prime"] = "beta/alpha"
        self.assertIn(
            "simple-zero derivative formula drift",
            verify.verify_document(mutated),
        )

    def test_contour_residue_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["conditional_contour_moments"][
            "local_moment_residue"
        ] = "0"
        self.assertIn(
            "recorded general contour residue drift",
            verify.verify_document(mutated),
        )

    def test_cluster_resultant_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["conditional_finite_cluster_algebra"]["n3_exact_model"][
            "resultant"
        ] = "0"
        self.assertIn(
            "recorded N=3 resultant drift",
            verify.verify_document(mutated),
        )

    def test_cluster_loewner_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["conditional_finite_cluster_algebra"]["n3_exact_model"][
            "pencil_determinant_ratio"
        ] = "0"
        self.assertIn(
            "recorded N=3 Loewner spectrum drift",
            verify.verify_document(mutated),
        )

    def test_partial_jet_inverse_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["partial_jet_functor"]["inverse"][0][2] = "0"
        self.assertIn(
            "partial-jet inverse failed",
            verify.verify_document(mutated),
        )

    def test_partial_jet_tplus_promotion_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["partial_jet_functor"]["T_plus_recovered"] = True
        self.assertIn(
            "partial-jet physical field promoted: T_plus_recovered",
            verify.verify_document(mutated),
        )


if __name__ == "__main__":
    unittest.main()
