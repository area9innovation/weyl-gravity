import json
import unittest

from local_bv.dimension_four_candidate_certificate import (
    ANOMALY_PATH,
    ANOMALY_RESULT_PATH,
    CATALOGUE_SCHEMA_PATH,
    COUNTERTERM_PATH,
    COUNTERTERM_RESULT_PATH,
    DETAILED_PATH,
    SCHEMA_PATH,
    build_anomaly_catalogue,
    build_certificate,
    build_counterterm_catalogue,
    build_anomaly_result_envelope,
    build_counterterm_result_envelope,
)
from local_bv.schema_validation import validate_instance


class DimensionFourCandidateCertificateTests(unittest.TestCase):
    def test_checked_in_artifacts_reproduce_exactly(self) -> None:
        expected = {
            DETAILED_PATH: build_certificate(),
            COUNTERTERM_RESULT_PATH: build_counterterm_result_envelope(),
            ANOMALY_RESULT_PATH: build_anomaly_result_envelope(),
            COUNTERTERM_PATH: build_counterterm_catalogue(),
            ANOMALY_PATH: build_anomaly_catalogue(),
        }
        for path, payload in expected.items():
            self.assertEqual(json.loads(path.read_text()), payload)

    def test_detailed_and_catalogue_schemas(self) -> None:
        detailed_schema = json.loads(SCHEMA_PATH.read_text())
        catalogue_schema = json.loads(CATALOGUE_SCHEMA_PATH.read_text())
        self.assertFalse(validate_instance(build_certificate(), detailed_schema))
        self.assertFalse(validate_instance(build_counterterm_catalogue(), catalogue_schema))
        self.assertFalse(validate_instance(build_anomaly_catalogue(), catalogue_schema))

    def test_claim_boundary_is_fail_closed(self) -> None:
        certificate = build_certificate()
        self.assertEqual(certificate["checks"]["full_local_bv_cohomology"], "NOT_COMPUTED")
        self.assertEqual(
            build_counterterm_result_envelope()["cohomology_status"],
            "NOT_COMPUTED",
        )
        self.assertEqual(build_counterterm_result_envelope()["ghost_number"], 0)
        self.assertEqual(build_anomaly_result_envelope()["ghost_number"], 1)
        self.assertIn("antifield", " ".join(certificate["not_computed"]).lower())


if __name__ == "__main__":
    unittest.main()
