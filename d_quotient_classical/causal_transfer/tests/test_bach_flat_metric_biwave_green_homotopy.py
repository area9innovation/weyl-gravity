from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.bach_flat_metric_biwave_green_homotopy import SCHEMA, build


class BachFlatMetricBiwaveGreenHomotopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value, cls.proofs = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_metric_homotopy(self) -> None:
        self.assertTrue(self.value["flags"]["BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS"])
        self.assertTrue(all(self.value["exact_checks"].values()))
        self.assertEqual(self.value["witness"]["remainder_maximum_order"], 2)

    def test_boundary(self) -> None:
        self.assertFalse(self.value["flags"]["BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS"])
        self.assertFalse(self.value["flags"]["HADAMARD_STATE"])
        self.assertFalse(self.value["witness"]["exact_same_bundle_factorization_required"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_order_three(self) -> None:
        bad = json.loads(json.dumps(self.value))
        bad["witness"]["remainder_maximum_order"] = 3
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(bad)


if __name__ == "__main__":
    unittest.main()
