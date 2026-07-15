import json
import unittest

from local_bv.euler_transgression_certificate import OUTPUT_PATH, SCHEMA_PATH, build_certificate
from local_bv.schema_validation import validate_instance


class EulerTransgressionCertificateTests(unittest.TestCase):
    def test_checked_in_artifact_reproduces_exactly(self) -> None:
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), build_certificate())

    def test_schema_and_intrinsic_anomaly_boundary(self) -> None:
        certificate = build_certificate()
        self.assertFalse(validate_instance(certificate, json.loads(SCHEMA_PATH.read_text())))
        self.assertEqual(
            certificate["checks"]["omega_E4_intrinsic_descent_continuation"],
            "NOT_COMPUTED",
        )
        self.assertIn("omega E4", " ".join(certificate["not_computed"]))


if __name__ == "__main__":
    unittest.main()
