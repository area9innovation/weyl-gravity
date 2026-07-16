from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_hadamard_construction_gate import validate_gate
from lorentzian.berger_hadamard_construction_gate_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class BergerHadamardConstructionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (ROOT / "schema/berger-hadamard-construction-gate-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_causal_and_state_data_are_not_conflated(self) -> None:
        separation = self.certificate["logical_separation"]
        self.assertIn("ADVANCED_MINUS_RETARDED", separation["causal_propagator"])
        self.assertFalse(
            separation["reduced_positive_frequency_is_full_Hadamard_evidence"]
        )
        self.assertFalse(
            separation[
                "reduced_Krein_completion_is_covariant_distributional_completion"
            ]
        )

    def test_route_starts_with_base_wave_parametrix(self) -> None:
        route = self.certificate["construction_route"]
        self.assertEqual(route[0]["stage"], "BASE_ROUGH_WAVE_HADAMARD_PARAMETRIX")
        self.assertEqual(route[0]["status"], "NEXT")
        self.assertTrue(
            all(row["status"] == "BLOCKED_PREVIOUS_STAGE" for row in route[1:])
        )

    def test_full_kernel_contract_is_distributional_and_brst_complete(self) -> None:
        export = self.certificate["required_kernel_export"]
        self.assertEqual(export["required_row_count"], 54)
        self.assertEqual(len(export["required_checks"]), 11)
        self.assertIn("Hadamard_wavefront_set", export["required_checks"])
        self.assertIn("BRST_compatibility_left", export["required_checks"])
        self.assertIn("BRST_compatibility_right", export["required_checks"])

    def test_hadamard_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_HADAMARD_DATA"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate_gate(mutant)

    def test_reduced_evidence_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["logical_separation"][
            "reduced_positive_frequency_is_full_Hadamard_evidence"
        ] = True
        with self.assertRaisesRegex(ValueError, "reduced-mode"):
            validate_gate(mutant)


if __name__ == "__main__":
    unittest.main()
