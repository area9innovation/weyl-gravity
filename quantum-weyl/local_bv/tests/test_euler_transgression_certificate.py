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
            "IN_PROGRESS",
        )
        self.assertEqual(
            [
                row["coefficient"]
                for row in certificate["euler_intrinsic_transgression"][
                    "generalized_connection_total_form"
                ]["components"]
            ],
            [
                {"numerator": 4, "denominator": 1},
                {"numerator": -4, "denominator": 1},
                {"numerator": 1, "denominator": 1},
            ],
        )
        checks = certificate["checks"]
        self.assertEqual(checks["euler_top_transgression_regression"], "VERIFIED")
        self.assertEqual(checks["unresolved_domega_theta_regression"], "VERIFIED")
        self.assertEqual(
            checks["lower_descendant_complete_cancellation"], "IN_PROGRESS"
        )
        template = certificate["euler_intrinsic_transgression"][
            "generalized_connection_total_form"
        ]
        self.assertEqual(template["dimension_specialization"], 4)
        self.assertEqual(
            template["source_dimension_four_coefficients"],
            [
                {"numerator": 1, "denominator": 4},
                {"numerator": -1, "denominator": 1},
                {"numerator": 1, "denominator": 1},
            ],
        )
        self.assertEqual(
            template["source_convention_map"]["carrier_normalization_status"],
            "UNRESOLVED_SOURCE_PROJECT_COEFFICIENT_MISMATCH",
        )
        self.assertEqual(
            template["source_convention_map"]["source_to_project_top_factor"],
            {"numerator": 1, "denominator": 4},
        )
        self.assertEqual(
            template["certificate_status"],
            "TEMPLATE_CANDIDATE_NOT_YET_VERIFIED_TOWER",
        )
        self.assertIn("omega E4", " ".join(certificate["not_computed"]))


if __name__ == "__main__":
    unittest.main()
