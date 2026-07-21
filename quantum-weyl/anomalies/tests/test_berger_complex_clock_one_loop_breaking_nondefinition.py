from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import ValidationError

from anomalies.berger_complex_clock_one_loop_breaking_nondefinition import (
    ATLAS_OUTPUT,
    OUTPUT,
    build,
    validate,
)
from anomalies.verify_berger_complex_clock_one_loop_breaking_nondefinition import (
    verify,
    verify_payload,
)


class BergerComplexClockOneLoopBreakingNondefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(self.value, build())

    def test_method_distinct_audit(self) -> None:
        self.assertEqual(
            verify()["result_state"],
            "NONDEFINED_MISSING_ACTION_DERIVED_EUCLIDEAN_BV_INTEGRATION_SLICE",
        )

    def test_atlas_row_is_a_nonmode_open_gate(self) -> None:
        atlas = json.loads(ATLAS_OUTPUT.read_text(encoding="utf-8"))
        row = atlas["entries"][0]
        self.assertEqual(
            row["quantum_data"]["entry_kind"],
            "NON_MODE_PARTICLE_GUARD",
        )
        self.assertEqual(
            row["quantum_data"]["anomaly_QME_dependency"]["status"],
            "OPEN",
        )
        self.assertEqual(
            row["quantum_data"]["carrier_crosswalk"]["status"],
            "NO_CERTIFIED_MAP",
        )

    def test_borrowed_strict_coefficient_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["coefficient_ledger"][0]["prequotient_coefficient"] = "199/30"
        with self.assertRaises((ValidationError, ValueError)):
            verify_payload(mutant)

    def test_zero_quotient_is_not_zero_coefficient(self) -> None:
        mutant = deepcopy(self.value)
        mutant["coefficient_ledger"][1]["prequotient_coefficient"] = "0"
        with self.assertRaises((ValidationError, ValueError)):
            validate(mutant)

    def test_classical_unary_not_promoted_to_loop_operator(self) -> None:
        mutant = deepcopy(self.value)
        mutant["missing_input_ledger"][
            "action_derived_gauge_fixed_Lagrangian_integration_slice"
        ] = "CERTIFIED_BY_54_ROW_UNARY"
        with self.assertRaises((ValidationError, ValueError)):
            verify_payload(mutant)

    def test_qme_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["LOCAL_GRAVITY_CLOCK_QME_RESTORED"] = True
        with self.assertRaises((ValidationError, ValueError)):
            validate(mutant)

    def test_ward_promotion_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["ward_disposition"]["K_Berger_compatibility"] = "VERIFIED"
        with self.assertRaises((ValidationError, ValueError)):
            verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
