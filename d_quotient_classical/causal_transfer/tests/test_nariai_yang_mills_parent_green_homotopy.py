from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_yang_mills_parent_green_homotopy import SCHEMA, build


class NariaiYangMillsParentGreenHomotopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_parent_witness_algebra(self) -> None:
        for name in ("Q_squared", "QW_plus_WQ_equals_declared_wave", "Q_commutes_with_wave"):
            self.assertTrue(self.value["exact_checks"][name], name)

    def test_analytic_inputs(self) -> None:
        self.assertTrue(self.value["geometry"]["globally_hyperbolic"])
        self.assertTrue(self.value["normal_hyperbolicity"]["degreewise_normally_hyperbolic"])
        self.assertTrue(self.value["exact_checks"]["advanced_retarded_existence_uniqueness"])
        self.assertTrue(self.value["exact_checks"]["causal_support"])

    def test_scope_boundary(self) -> None:
        self.assertTrue(self.value["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"])
        self.assertFalse(self.value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"])
        self.assertFalse(self.value["flags"]["NARIAI_METRIC_GREEN_HOMOTOPY"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_transfer_promotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
