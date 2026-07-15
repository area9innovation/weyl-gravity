import json
import unittest

from local_bv.relative_cohomology_certificate import OUTPUT_PATH, SCHEMA_PATH, build_certificate
from local_bv.schema_validation import validate_instance


class RelativeCohomologyCertificateTests(unittest.TestCase):
    def test_checked_in_artifact_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), build_certificate())

    def test_schema_and_production_claim_boundary(self) -> None:
        certificate = build_certificate()
        self.assertFalse(validate_instance(certificate, json.loads(SCHEMA_PATH.read_text())))
        self.assertEqual(certificate["fixture"]["total_quotient_dimension"], 2)
        self.assertEqual(certificate["fixture"]["anchored_quotient_dimension"], 1)
        self.assertEqual(certificate["fixture"]["lower_only_total_class_dimension"], 1)
        self.assertEqual(
            certificate["fixture"]["dual_witness_pairings"],
            [{"numerator": 1, "denominator": 1}],
        )
        self.assertEqual(
            certificate["checks"]["dual_nontriviality_witnesses"], "VERIFIED"
        )
        self.assertIn("production", " ".join(certificate["not_computed"]))


if __name__ == "__main__":
    unittest.main()
