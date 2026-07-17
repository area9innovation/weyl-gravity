import json
import unittest
from fractions import Fraction

from cartan.local_anomaly_comparison import comparison_analysis, comparison_payload
from cartan.local_anomaly_comparison_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class LocalAnomalyComparisonTests(unittest.TestCase):
    def test_exact_pullback_matrices(self) -> None:
        analysis = comparison_analysis()
        self.assertEqual(analysis["coefficient_vector"], (Fraction(199, 30), Fraction(-87, 20)))
        self.assertEqual(analysis["cylinder_map"].apply(analysis["coefficient_vector"]), (0, 0))
        self.assertEqual(
            analysis["minkowski_map"].apply(analysis["coefficient_vector"]),
            (Fraction(-199, 30), Fraction(87, 20)),
        )

    def test_comparison_fails_closed_at_named_missing_arrow(self) -> None:
        payload = comparison_payload()
        self.assertEqual(
            payload["source_local_cohomology"]["full_BV_lift_status"],
            "COMPLETE_ON_REGULAR_BACH_LOCUS",
        )
        self.assertEqual(payload["cartan_defect_comparison"]["classification_status"], "NO_VERDICT")
        self.assertFalse(payload["cartan_defect_comparison"]["zero_local_pullback_implies_zero_cartan_defect"])
        self.assertEqual(payload["source_target_degree_audit"]["missing_arrow"], "RENORMALIZED_LOCAL_WARD_INSERTION")
        self.assertEqual(
            {row["carrier_id"] for row in payload["minimal_missing_carrier_theorem"]["carriers"]},
            {
                "FROZEN_CLASSICAL_D_ACTION", "RENORMALIZED_Q1", "RENORMALIZED_IOTA_D_1",
                "RENORMALIZED_L_D_1", "LOCAL_INSERTION_TO_ADMISSIBLE_DERIVATION_MAP",
                "REGULATED_SLAVNOV_BREAKING",
            },
        )

    def test_berger_classical_input_is_setting_specific(self) -> None:
        payload = comparison_payload()
        self.assertEqual(
            payload["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "LORENTZIAN-CAUSAL"],
        )
        berger = payload["setting_specific_classical_inputs"][0]
        self.assertEqual(
            berger["classical_D_action"],
            "AVAILABLE_SETTING_SPECIFIC_BERGER_54_ROWS",
        )
        self.assertEqual(berger["causal_54_to_26_reduction"], "VERIFIED_CONDITIONAL")
        self.assertEqual(
            berger["retained_26_row_green_homotopy"],
            "CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED",
        )
        self.assertEqual(berger["cartan_classification_status"], "NO_VERDICT")

    def test_analytic_interfaces_are_ready_without_physical_promotion(self) -> None:
        contracts = comparison_payload()["prepared_input_contracts"]
        green = contracts["berger_26_row_green_hadamard_endpoint"]
        ward = contracts["renormalized_D_Ward_insertion"]
        self.assertEqual(green["status"], "CAUSAL_GREEN_IMPORTED_HADAMARD_OPEN")
        self.assertEqual(green["physical_green_status"], "CONSTRUCTED_CLASSICAL_CAUSAL")
        self.assertEqual(ward["status"], "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED")
        self.assertEqual(ward["quantum_cartan_status"], "NO_VERDICT")

    def test_schema_and_checked_in_certificate_reproduce(self) -> None:
        certificate = build_certificate()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")), certificate)


if __name__ == "__main__":
    unittest.main()
