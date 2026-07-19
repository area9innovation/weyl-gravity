from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.candidate13_reduced_source_support_local_upgrade_obstruction import SCHEMA, build


class Candidate13SupportLocalUpgradeObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_support_obstruction(self) -> None:
        self.assertTrue(self.value["flags"]["CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1"])
        self.assertTrue(all(self.value["exact_checks"].values()))
        self.assertFalse(self.value["flags"]["DIRECT_REDUCED_RECEIVER_TO_LOCAL_BV_UPGRADE"])

    def test_scope_guard(self) -> None:
        self.assertFalse(self.value["flags"]["ALTERNATIVE_LOCAL_COFIBER_GLOBALLY_OBSTRUCTED"])
        self.assertEqual(self.value["category_disposition"]["causal_retarded_crosswalk"], "NO_CERTIFIED_MAP")
        self.assertEqual(
            self.value["category_disposition"]["candidate13_bounded_pullback"],
            "CERTIFIED_REDUCED_MODE_ORIGIN_ONLY",
        )
        self.assertEqual(
            self.value["category_disposition"]["candidate13_smooth_pullback"],
            "CERTIFIED_REDUCED_MODE_NONTRIVIAL",
        )

    def test_strict_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_global_no_go(self) -> None:
        bad = json.loads(json.dumps(self.value))
        bad["flags"]["ALTERNATIVE_LOCAL_COFIBER_GLOBALLY_OBSTRUCTED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(bad)


if __name__ == "__main__":
    unittest.main()
