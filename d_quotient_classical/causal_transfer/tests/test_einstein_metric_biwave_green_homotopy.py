from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.einstein_metric_biwave_green_homotopy import (
    SCHEMA,
    build,
)


class EinsteinMetricBiwaveGreenHomotopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_exact_calibration(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["detour_solution"], ["-1", "-1/3"])
        self.assertEqual(checks["detour_coefficient_rank"], 2)
        self.assertEqual(checks["detour_augmented_rank"], 2)
        for name, result in checks.items():
            if name.endswith("_entries") or name.endswith("_defect_rank"):
                self.assertEqual(result, 0, name)

    def test_einstein_scope_and_rank310_guard(self) -> None:
        flags = self.value["flags"]
        self.assertTrue(flags["FOUR_DIMENSIONAL_EINSTEIN_METRIC_BIWAVE_THEOREM"])
        self.assertTrue(flags["KANTOWSKI_SACHS_COMMON_SLAB_METRIC_GREEN_HOMOTOPY"])
        self.assertTrue(flags["VARIABLE_WEYL_ALLOWED"])
        self.assertFalse(flags["PARALLEL_WEYL_REQUIRED"])
        self.assertFalse(flags["KANTOWSKI_SACHS_RANK310_GREEN_TRANSFER"])
        self.assertFalse(flags["NON_EINSTEIN_BACH_FLAT_METRIC_THEOREM"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_rank310_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["KANTOWSKI_SACHS_RANK310_GREEN_TRANSFER"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)

    def test_schema_rejects_non_einstein_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["NON_EINSTEIN_BACH_FLAT_METRIC_THEOREM"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
