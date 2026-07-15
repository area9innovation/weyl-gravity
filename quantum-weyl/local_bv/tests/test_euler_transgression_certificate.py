import json
import unittest
from copy import deepcopy

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
            "PARTIAL_CONNECTING_IDENTITIES_PENDING",
        )
        self.assertEqual(
            [
                row["coefficient"]
                for row in certificate["euler_intrinsic_transgression"][
                    "generalized_connection_total_form"
                ]["components"]
            ],
            [
                {"numerator": 1, "denominator": 1},
                {"numerator": -4, "denominator": 1},
                {"numerator": 4, "denominator": 1},
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
            "RESOLVED_BY_GLOBAL_TOP_COMPONENT_SCALE",
        )
        self.assertEqual(
            template["source_convention_map"][
                "source_top_coefficient_in_project_density"
            ],
            {"numerator": 1, "denominator": 4},
        )
        self.assertEqual(
            template["certificate_status"],
            "COMPONENT_EXPANSION_VERIFIED_CONNECTING_IDENTITIES_PENDING",
        )
        self.assertEqual(
            template["normalization_contract"]["global_source_to_project_scale"],
            {"numerator": 4, "denominator": 1},
        )
        self.assertEqual(
            [(row["ghost_number"], row["form_degree"]) for row in template["bidegree_manifests"]],
            [(1, 4), (2, 3), (3, 2), (4, 1), (5, 0)],
        )
        expansion = certificate["euler_intrinsic_transgression"][
            "ordinary_bidegree_expansion"
        ]
        self.assertEqual(
            [row["term_count"] for row in expansion["components"]],
            [3, 2, 1, 0, 0],
        )
        self.assertEqual(expansion["checks"]["bottom_QW_closure"], "VERIFIED")
        self.assertIn("connecting intrinsic descent", " ".join(certificate["not_computed"]))

    def test_schema_fails_closed_on_unknown_nested_claim(self) -> None:
        certificate = deepcopy(build_certificate())
        certificate["checks"]["tower_secretly_complete"] = "VERIFIED"
        errors = validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        self.assertTrue(any("additional property is forbidden" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
