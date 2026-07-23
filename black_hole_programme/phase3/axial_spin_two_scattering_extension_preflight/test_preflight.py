import copy
import json
import unittest

from . import verify


class SpinTwoExtensionPreflightTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(verify.CERTIFICATE.read_text())

    def test_committed_certificate_verifies(self):
        self.assertEqual(verify.verify_document(self.document), [])

    def test_extension_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["exact_local_extension"]["matrix"][0][0] = "0"
        self.assertIn(
            "exact local extension mismatch",
            verify.verify_document(mutated),
        )

    def test_phase_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["declaration"]["damped_QNM_half_plane"] = "Im(omega)<0"
        self.assertIn(
            "frequency convention drift",
            verify.verify_document(mutated),
        )

    def test_residue_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["rational_gauge_trace_test"]["residue_at_r=2"] = "0"
        self.assertIn(
            "rational-gauge residue mismatch",
            verify.verify_document(mutated),
        )

    def test_scattering_class_promotion_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["claim_flags"][
            "scattering_extension_coefficient_c_computed"
        ] = True
        self.assertIn(
            "open flag promoted: scattering_extension_coefficient_c_computed",
            verify.verify_document(mutated),
        )


if __name__ == "__main__":
    unittest.main()
