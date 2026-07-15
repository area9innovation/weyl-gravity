import json
import unittest

from local_bv.schema_validation import validate_instance
from local_bv.triviality_certificate import OUTPUT_PATH, SCHEMA_PATH, build_certificate


class TrivialityCertificateTests(unittest.TestCase):
    def test_checked_in_artifact_reproduces_exactly(self) -> None:
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), build_certificate())

    def test_schema_and_claim_boundary(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        certificate = build_certificate()
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(
            certificate["trivializations"]["ANOM_OMEGA_BOX_R"]["class_status"],
            "EXACT",
        )


if __name__ == "__main__":
    unittest.main()
