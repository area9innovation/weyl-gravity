from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.conformally_einstein_yang_mills_detour import build
from d_quotient_classical.causal_transfer.verify_conformally_einstein_yang_mills_detour import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-einstein-yang-mills-detour-correction-v1.schema.json"


class ConformallyEinsteinYangMillsDetourTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_universal_compositions(self) -> None:
        fixture = self.value["exact_matrix_fixture"]
        self.assertEqual(fixture["corrected_left_defect_rank"], 0)
        self.assertEqual(fixture["corrected_right_defect_rank"], 0)
        self.assertEqual(fixture["naive_left_defect_rank"], 2)
        self.assertEqual(fixture["naive_right_defect_rank"], 2)

    def test_nariai_parent_scope(self) -> None:
        self.assertTrue(self.value["flags"]["NARIAI_CURVED_PARENT_DETOUR_COMPLEX"])
        self.assertFalse(self.value["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"])
        self.assertFalse(self.value["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"])

    def test_independent_replay(self) -> None:
        verify()

    def test_wrong_naive_rank_fails_schema(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_matrix_fixture"]["naive_left_defect_rank"] = 0
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_causal_promotion_fails_schema(self) -> None:
        mutated = deepcopy(self.value)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
