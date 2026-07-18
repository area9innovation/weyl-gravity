from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_repaired_parent_green_witness_preflight import (
    SCHEMA,
    build,
)


class NariaiRepairedParentGreenWitnessPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_typed_scalar_biwave_symbols(self) -> None:
        checks = self.value["exact_checks"]
        self.assertTrue(checks["actual_K_matches_universal_K"])
        self.assertTrue(checks["action_Bach_is_evaluation_dual_operator"])
        self.assertTrue(checks["ghost_symbol_is_scalar_biwave"])
        self.assertTrue(checks["field_symbol_is_scalar_biwave_after_fibre_identification"])
        self.assertEqual(checks["ghost_completed_symbol_rank"], 0)
        self.assertEqual(checks["field_completed_symbol_rank"], 0)

    def test_parent_divergence_is_rejected(self) -> None:
        self.assertTrue(self.value["exact_checks"]["parent_divergence_cubic_symbol_zero"])
        self.assertEqual(self.value["rejected_candidate"]["cubic_symbol_rank"], 0)

    def test_scope_is_fail_closed(self) -> None:
        self.assertTrue(self.value["flags"]["NARIAI_METRIC_SCALAR_BIWAVE_PRINCIPAL_SYMBOL"])
        self.assertFalse(self.value["flags"]["NARIAI_LOWER_ORDER_FACTOR_COMPLETION"])
        self.assertFalse(self.value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_green_overpromotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
