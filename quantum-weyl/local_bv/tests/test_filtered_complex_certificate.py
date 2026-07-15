import json
import unittest

from local_bv.filtered_complex_certificate import OUTPUT_PATH, build_certificate


class FilteredComplexCertificateTests(unittest.TestCase):
    def test_checked_in_artifact_and_claim_boundary(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), certificate)
        self.assertEqual(
            certificate["result_state"], "INTERFACE_READY_EXPORT_PENDING"
        )
        self.assertIn("minimal-BV quotient", certificate["not_computed"])


if __name__ == "__main__":
    unittest.main()
