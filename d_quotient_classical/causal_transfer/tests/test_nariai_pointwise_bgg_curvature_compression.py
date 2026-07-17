from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_pointwise_bgg_curvature_compression import build
from d_quotient_classical.causal_transfer.verify_nariai_pointwise_bgg_curvature_compression import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-pointwise-bgg-curvature-compression-obstruction-v1.schema.json"


class NariaiPointwiseBGGCurvatureCompressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_exact_rank_and_witness(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual([checks["curvature_action_rank"], checks["compressed_rank"], checks["cyclic_defect_rank"]], [54, 9, 2])
        self.assertEqual(checks["normalized_witness_value"], "1")

    def test_scope(self) -> None:
        self.assertTrue(self.value["flags"]["DERIVATIVE_BGG_CORRECTIONS_REQUIRED"])
        self.assertFalse(self.value["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"])
        self.assertFalse(self.value["flags"]["ALL_CURVED_COMPRESSIONS_OBSTRUCTED"])

    def test_independent_replay(self) -> None:
        verify()

    def test_witness_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_checks"]["normalized_witness_value"] = "0"
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_full_hpl_overpromotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["flags"]["NARIAI_CURVED_BGG_HPL_COMPRESSION"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
