from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import build
from d_quotient_classical.causal_transfer.verify_nariai_first_differential_bgg_correction import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-first-bgg-zeroth-order-strictification-obstruction-v1.schema.json"


class NariaiFirstDifferentialBGGCorrectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_exact_obstruction(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["transverse_rank_set"], [9])
        self.assertEqual(checks["cross_form_defect_count"], 12)
        self.assertEqual(checks["normalized_witness_value"], "1")

    def test_scope(self) -> None:
        flags = self.value["flags"]
        self.assertFalse(flags["ZEROTH_ORDER_STRICTIFICATION_EXISTS"])
        self.assertTrue(flags["GENUINELY_DERIVATIVE_CORRECTION_STILL_OPEN"])
        self.assertFalse(flags["ALL_CURVED_COMPRESSIONS_OBSTRUCTED"])

    def test_independent_replay(self) -> None:
        verify()

    def test_witness_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_checks"]["normalized_witness_value"] = "0"
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_overpromotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
