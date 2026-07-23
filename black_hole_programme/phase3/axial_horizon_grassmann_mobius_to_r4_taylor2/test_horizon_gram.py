import copy
import json
import unittest

from . import verify_horizon_gram as verify


class HorizonGramVerifierTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(verify.CERTIFICATE.read_text())
        self.factor_document = json.loads(
            verify.FACTOR_CERTIFICATE.read_text()
        )

    def test_committed_certificate_verifies(self):
        self.assertEqual(verify.verify_document(self.document), [])

    def test_outward_sign_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["orientation"]["future_horizon_outward"] = (
            "H_out=+I*Hframe^dagger*Jhat*Hframe"
        )
        self.assertIn(
            "future-horizon Stokes sign mismatch",
            verify.verify_document(mutated),
        )

    def test_minor_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["leading_principal_minors"][1] = "1"
        self.assertIn(
            "leading principal minor mismatch",
            verify.verify_document(mutated),
        )

    def test_semidefinite_shortcut_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["stokes_rank_shortcut"]["activated"] = True
        mutated["stokes_rank_shortcut"]["direct_endpoint_rank_bound"] = 3
        self.assertIn(
            "semidefinite Stokes shortcut was unsoundly activated",
            verify.verify_document(mutated),
        )

    def test_factor_quotient_verifies(self):
        self.assertEqual(
            verify.verify_factor_document(self.factor_document),
            [],
        )

    def test_unit_quotient_sign_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.factor_document)
        mutated["spin_one_quotient"]["unit_quotient_norm"] = "32/(15*omega)"
        self.assertIn(
            "unit spin-one quotient norm mismatch",
            verify.verify_factor_document(mutated),
        )


if __name__ == "__main__":
    unittest.main()
