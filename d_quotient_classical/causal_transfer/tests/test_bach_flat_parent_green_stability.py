from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.bach_flat_parent_green_stability import SCHEMA, build


class BachFlatParentGreenStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_nonzero_relative_radius(self) -> None:
        self.assertEqual(self.value["background_class"]["radius"], "1/4")
        self.assertTrue(self.value["background_class"]["relatively_open"])
        self.assertTrue(self.value["nonconstant_consumer"]["inside_radius"])
        self.assertTrue(self.value["nonconstant_consumer"]["nonconstant"])

    def test_universal_parent_causal_theorem(self) -> None:
        self.assertTrue(all(self.value["exact_checks"].values()))
        self.assertTrue(self.value["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"])
        self.assertTrue(self.value["flags"]["ALL_GLOBALLY_HYPERBOLIC_BACH_FLAT_PARENT_COMPLEXES"])

    def test_fail_closed_metric_boundary(self) -> None:
        self.assertFalse(self.value["flags"]["OPEN_CLASS_IN_FULL_METRIC_SPACE"])
        self.assertFalse(self.value["flags"]["METRIC_BACH_GREEN_HOMOTOPY_ON_CLASS"])
        self.assertFalse(self.value["flags"]["RANK_310_SDR_ON_CLASS"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_metric_overpromotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["METRIC_BACH_GREEN_HOMOTOPY_ON_CLASS"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
