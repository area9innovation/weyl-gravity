from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_curvature_incidence_first_square import build
from d_quotient_classical.causal_transfer.verify_nariai_curvature_incidence_first_square import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-first-square-v1.schema.json"


class NariaiCurvatureIncidenceFirstSquareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_exact_identity(self) -> None:
        checks = self.value["exact_checks"]
        self.assertTrue(checks["residual_equals_incidence"])
        self.assertEqual(checks["relative_defect_nonzero_entries"], 0)
        self.assertEqual(checks["normalized_coefficient_value"], "1")

    def test_typed_support(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["incidence_shape"], [60, 4])
        self.assertEqual(checks["incidence_rank"], 4)
        self.assertEqual(checks["incidence_nonzero_entries"], 12)
        self.assertEqual(checks["adjoint_support_indices"], list(range(4, 10)))
        self.assertTrue(checks["adjoint_curvature_equals_normal_tractor_square"])
        self.assertEqual(checks["normal_tractor_square_defect_nonzero_entries"], 0)

    def test_independent_replay(self) -> None:
        verify()

    def test_sign_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_checks"]["wrong_sign_defect_nonzero_entries"] = 0
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_mapping_cone_overpromotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["flags"]["CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
