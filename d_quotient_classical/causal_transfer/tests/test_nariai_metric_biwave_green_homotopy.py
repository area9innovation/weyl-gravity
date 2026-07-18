from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_metric_biwave_green_homotopy import (
    SCHEMA, build,
)


class NariaiMetricBiwaveGreenHomotopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_unique_lower_order_completion(self) -> None:
        solve = self.value["unique_lower_order_solve"]
        self.assertTrue(solve["unique"])
        self.assertEqual(solve["solution"], ["1/3", "4/3", "1/3"])

    def test_exact_factors(self) -> None:
        checks = self.value["exact_checks"]
        for name, result in checks.items():
            if name.endswith("_entries"):
                self.assertEqual(result, 0, name)
        self.assertEqual(checks["projector_ranks"], [4, 1, 4])

    def test_causal_scope(self) -> None:
        self.assertTrue(self.value["flags"]["NARIAI_METRIC_GREEN_HOMOTOPY"])
        self.assertTrue(self.value["flags"]["NARIAI_METRIC_CAUSAL_SUPPORT"])
        self.assertFalse(self.value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_rank310_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
