from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import build
from d_quotient_classical.causal_transfer.verify_nariai_yang_mills_middle_compression import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-algebraic-endpoint-curvature-repair-obstruction-v1.schema.json"


class NariaiYangMillsMiddleCompressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_parent_and_endpoint_obstruction(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["corrected_parent_left_defect_entries"], 0)
        self.assertEqual(checks["wrong_sign_parent_left_defect_entries"], 144)
        self.assertEqual(checks["repaired_gauge_defect_nonzero_entries"], 0)
        self.assertEqual(checks["endpoint_cyclic_defect_rank"], 2)

    def test_scope(self) -> None:
        flags = self.value["flags"]
        self.assertTrue(flags["ALGEBRAIC_ENDPOINT_REPAIR_OBSTRUCTED"])
        self.assertTrue(flags["DIFFERENTIAL_TRANSLATION_LIFT_STILL_OPEN"])
        self.assertFalse(flags["NARIAI_CURVED_BGG_HPL_COMPRESSION"])

    def test_independent_consumer(self) -> None:
        verify()

    def test_cyclic_witness_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_checks"]["normalized_cyclic_witness_value"] = "0"
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_overpromotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
