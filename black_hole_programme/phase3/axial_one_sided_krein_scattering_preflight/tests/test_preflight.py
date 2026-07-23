import copy
import json
import unittest

from .. import verify


class OneSidedKreinPreflightTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(verify.CERTIFICATE.read_text())

    def test_committed_certificate_verifies(self):
        self.assertEqual(verify.verify_document(self.document), [])

    def test_physical_activation_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["claim_flags"]["physical_one_sided_J_isometry_certified"] = True
        self.assertIn(
            "physical scattering claim escaped the fail-closed gate",
            verify.verify_document(mutated),
        )

    def test_normalizer_ratio_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["determinant_audit"][
            "endpoint_normalizer_determinant_ratio"
        ] = "1"
        self.assertIn(
            "endpoint normalizer determinant ratio failed",
            verify.verify_document(mutated),
        )

    def test_alpha_gamma_mu_reduction_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["triangular_J0_identities"][
            "alpha_gamma_mu_reduction"
        ] = "CERTIFIED"
        self.assertIn(
            "alpha/gamma/mu reduction was unsoundly promoted",
            verify.verify_document(mutated),
        )

    def test_triangular_component_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["triangular_J0_identities"]["independent_equations"][0] = (
            "sum_X conjugate(a_X)*c_X=0"
        )
        self.assertIn(
            "recorded upper triangular equations changed",
            verify.verify_document(mutated),
        )

    def test_horizon_scope_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["horizon_positive_real_scope_audit"][
            "promoted_beyond_pilot"
        ] = False
        self.assertIn(
            "positive-real horizon extension was dropped",
            verify.verify_document(mutated),
        )


if __name__ == "__main__":
    unittest.main()
