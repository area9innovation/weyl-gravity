from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.bach_flat_rank310_causal_transfer import SCHEMA, build


class BachFlatRank310CausalTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_transfer(self) -> None:
        self.assertTrue(self.value["flags"]["BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS"])
        self.assertTrue(all(self.value["exact_checks"].values()))
        self.assertEqual(self.value["scope"]["degree_ranks"], [15, 140, 140, 15])

    def test_boundary(self) -> None:
        self.assertFalse(self.value["flags"]["PURE_PARENT_TO_METRIC_SDR"])
        self.assertFalse(self.value["flags"]["HADAMARD_STATE"])

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_parent_crosswalk(self) -> None:
        bad = json.loads(json.dumps(self.value))
        bad["flags"]["PURE_PARENT_TO_METRIC_SDR"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(bad)


if __name__ == "__main__":
    unittest.main()
