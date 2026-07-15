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
            "NONTRIVIAL_COMPLETE",
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
            checks["lower_descendant_complete_cancellation"],
            "VERIFIED_FOR_FROZEN_EULER_CARRIER_ALGEBRA",
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
            "INTRINSIC_EULER_TOWER_VERIFIED",
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
        self.assertEqual(
            expansion["checks"]["bottom_factor_rule_closure"], "VERIFIED"
        )
        preflight = certificate["euler_intrinsic_transgression"][
            "connecting_identity_preflight"
        ]
        self.assertEqual(
            preflight["cotton_convention_bridge"]["bridge"],
            "C_source[a,b,c] = -A_project[a,b,c]",
        )
        self.assertEqual(preflight["bottom_QW_residual"], [])
        self.assertEqual(
            preflight["QW_squared_on_generators"]["W_two_form"],
            "NOT_COMPUTED_GAMMA_AND_WEIGHT_ACTION",
        )
        self.assertEqual(
            preflight["QW_squared_on_generators"]["Cotton_two_form"],
            "NOT_COMPUTED_DERIVED_CURVATURE_ACTION",
        )
        self.assertEqual(
            preflight["checks"]["horizontal_generator_rows"], "NOT_COMPUTED"
        )
        self.assertEqual(
            preflight["connecting_tensor_sector_audit"]["claim_boundary"]
            ["full_total_form_connecting_identity"],
            "NOT_COMPUTED",
        )
        self.assertEqual(
            expansion["ordinary_bidegree_projection"]["checks"]
            ["QW_a14_plus_dh_a23"],
            "VERIFIED",
        )
        self.assertEqual(
            expansion["epsilon_head_reconstruction"]["nonzero_residual_count"],
            0,
        )
        self.assertEqual(
            expansion["epsilon_head_reconstruction"]
            ["independent_convention_audit"]["status"],
            "VERIFIED_INDEPENDENTLY",
        )

    def test_schema_fails_closed_on_unknown_nested_claim(self) -> None:
        certificate = deepcopy(build_certificate())
        certificate["checks"]["tower_secretly_complete"] = "VERIFIED"
        errors = validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        self.assertTrue(any("additional property is forbidden" in error for error in errors))

    def test_schema_fails_closed_on_head_control_drift(self) -> None:
        certificate = deepcopy(build_certificate())
        head = certificate["euler_intrinsic_transgression"][
            "ordinary_bidegree_expansion"
        ]["epsilon_head_reconstruction"]
        head["negative_controls"]["reverse_carrier_orientation"][
            "failing_case_count"
        ] = 0
        errors = validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        self.assertTrue(errors)

        certificate = deepcopy(build_certificate())
        head = certificate["euler_intrinsic_transgression"][
            "ordinary_bidegree_expansion"
        ]["epsilon_head_reconstruction"]
        head["claim_boundary"]["relative_cohomology_status"] = "NONTRIVIAL"
        errors = validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
