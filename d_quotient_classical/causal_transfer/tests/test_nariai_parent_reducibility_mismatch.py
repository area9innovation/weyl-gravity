from __future__ import annotations

import copy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_parent_reducibility_mismatch import (
    SCHEMA,
    build,
)


class NariaiParentReducibilityMismatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_metric_killing_lower_bound(self) -> None:
        metric = self.value["metric_reducibilities"]
        self.assertEqual(metric["Lie_derivative_defect_entries"], 0)
        self.assertEqual(metric["value_and_first_partial_jet_rank"], 6)
        self.assertEqual(metric["metric_H_minus_1_dimension_lower_bound"], 6)

    def test_parent_curvature_upper_bound(self) -> None:
        parent = self.value["parent_reducibilities"]
        self.assertEqual(parent["normal_tractor_curvature_rank"], 14)
        self.assertEqual(parent["common_curvature_kernel_dimension"], 1)
        self.assertEqual(parent["parent_H_minus_1_dimension_upper_bound"], 1)

    def test_quasi_isomorphism_obstructed(self) -> None:
        obstruction = self.value["obstruction"]
        self.assertEqual(obstruction["missing_reducibility_dimension_lower_bound"], 5)
        self.assertFalse(obstruction["direct_parent_metric_quasi_isomorphism_possible"])
        self.assertFalse(obstruction["contractible_equation_identity_rows_sufficient"])

    def test_strict_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)

    def test_schema_rejects_quasi_isomorphism_overpromotion(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["flags"]["CURRENT_NORMAL_TRACTOR_PARENT_METRIC_QUASI_ISOMORPHISM"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
