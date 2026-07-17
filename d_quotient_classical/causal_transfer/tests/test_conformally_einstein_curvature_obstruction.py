from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.conformally_einstein_curvature_obstruction import build
from d_quotient_classical.causal_transfer.verify_conformally_einstein_curvature_obstruction import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/conformally-einstein-tractor-curvature-obstruction-v1.schema.json"


class ConformallyEinsteinCurvatureObstructionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_exact_nariai_geometry(self) -> None:
        self.assertEqual(self.value["target_background"]["scalar_curvature"], "4")
        self.assertEqual(self.value["exact_curvature"]["weyl_components"]["C_2323"], "2/3")
        self.assertTrue(self.value["target_background"]["bach_flat"])

    def test_normalized_obstruction_and_scope(self) -> None:
        self.assertEqual(self.value["obstruction"]["normalized_witness_value"], "1")
        self.assertTrue(self.value["flags"]["CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1"])
        self.assertFalse(self.value["flags"]["CURVED_DIFFERENTIAL_HPL_CORRECTION_EXISTS"])
        self.assertFalse(self.value["flags"]["ALL_BACH_FLAT_BACKGROUNDS_OBSTRUCTED"])
        self.assertEqual(self.value["dependency_tags"], ["LOCAL-ALGEBRAIC"])

    def test_independent_replay(self) -> None:
        verify()

    def test_witness_mutation_fails_schema(self) -> None:
        mutated = deepcopy(self.value)
        mutated["obstruction"]["normalized_witness_value"] = "0"
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_causal_overpromotion_fails_schema(self) -> None:
        mutated = deepcopy(self.value)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
