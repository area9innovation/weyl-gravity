import copy
import json
import unittest

from . import verify


class ProjectiveCocycleTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(verify.CERTIFICATE.read_text())

    def test_certificate_verifies(self):
        self.assertEqual(verify.verify_document(self.document), [])

    def test_cocycle_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["projective_cocycle"]["calI"] = "0"
        self.assertIn(
            "projective cocycle mismatch",
            verify.verify_document(mutated),
        )

    def test_rank_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["rational_nonexactness"]["augmented_rank"] = 3
        self.assertIn(
            "rational nonexactness record drift",
            verify.verify_document(mutated),
        )

    def test_reduced_representative_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["reduced_representative"]["calI_reduced"] = "0"
        self.assertIn(
            "reduced representative mismatch",
            verify.verify_document(mutated),
        )

    def test_angular_scope_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["angular_class_test"]["classification"] = "physical tangent"
        self.assertIn("angular scope drift", verify.verify_document(mutated))

    def test_qnm_promotion_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["claim_flags"]["beta_n_evaluated"] = True
        self.assertIn(
            "open flag promoted: beta_n_evaluated",
            verify.verify_document(mutated),
        )

    def test_specialization_promotion_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["finite_specialization_corollary"]["safe_reading"] = (
            "Splitting is excluded at every specialization."
        )
        self.assertIn(
            "specialization boundary overpromoted",
            verify.verify_document(mutated),
        )

    def test_left_null_obstruction_mutation_is_rejected(self):
        mutated = copy.deepcopy(self.document)
        mutated["rational_nonexactness"]["left_null_obstruction"] = "0"
        self.assertIn(
            "rational specialization obstruction drift",
            verify.verify_document(mutated),
        )


if __name__ == "__main__":
    unittest.main()
