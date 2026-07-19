from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.bach_flat_rank310_natural_sdr import SCHEMA, build


class BachFlatRank310NaturalSDRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_class_wide_sdr(self) -> None:
        self.assertTrue(self.value["flags"]["BACH_FLAT_RELATIVE_G3_RANK310_SDR"])
        self.assertTrue(self.value["flags"]["BACH_FLAT_RANK310_CYCLICITY"])
        self.assertTrue(all(self.value["exact_checks"].values()))

    def test_green_claims_remain_false(self) -> None:
        flags = self.value["flags"]
        self.assertFalse(flags["BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS"])
        self.assertFalse(flags["BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS"])
        self.assertFalse(flags["HADAMARD_STATE"])

    def test_typed_six_blocks(self) -> None:
        self.assertEqual(len(self.value["operator_registry"]), 6)
        self.assertEqual(len({item["name"] for item in self.value["operator_registry"]}), 6)

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_green_overpromotion(self) -> None:
        broken = json.loads(json.dumps(self.value))
        broken["flags"]["BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(broken)


if __name__ == "__main__":
    unittest.main()
