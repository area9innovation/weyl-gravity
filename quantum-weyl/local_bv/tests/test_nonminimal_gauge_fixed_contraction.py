from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from local_bv.nonminimal_gauge_fixed_contraction import analysis
from local_bv.nonminimal_gauge_fixed_contraction_certificate import (
    H04_OUTPUT,
    H14_OUTPUT,
    OUTPUT,
    RESULT_SCHEMA,
    SCHEMA,
    build_outputs,
    validate,
)
from local_bv.verify_nonminimal_gauge_fixed_contraction import verify


class NonminimalGaugeFixedContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analysis = analysis()
        cls.outputs = build_outputs()

    def test_ten_pairs_contract_over_minimal_coefficients(self) -> None:
        self.assertEqual(self.analysis["contraction"]["pair_count"], 10)
        self.assertEqual(self.analysis["field_dictionary"]["atom_count"], 20)
        self.assertEqual(self.analysis["contraction"]["regression_monomial_count"], 25080)

    def test_canonical_transport_identities_reduce_to_zero(self) -> None:
        normal_forms = self.analysis["canonical_gauge_fixing_transport"]["normal_forms"]
        self.assertEqual(len(normal_forms), 6)
        self.assertTrue(all(value == {} for value in normal_forms.values()))

    def test_gauge_fixed_groups_equal_minimal_groups(self) -> None:
        result = self.analysis["gauge_fixed_cohomology"]
        self.assertEqual((result["H04_even_dimension"], result["H04_odd_dimension"]), (2, 1))
        self.assertEqual((result["H14_even_dimension"], result["H14_odd_dimension"]), (2, 1))
        self.assertEqual(result["H14_exact_rows"], ["ANOM_OMEGA_BOX_R"])

    def test_outputs_reproduce_and_validate(self) -> None:
        checked = {path: json.loads(path.read_text()) for path in (OUTPUT, H04_OUTPUT, H14_OUTPUT)}
        self.assertEqual(checked, self.outputs)
        self.assertEqual(checked[OUTPUT], verify())
        main_schema = json.loads(SCHEMA.read_text())
        result_schema = json.loads(RESULT_SCHEMA.read_text())
        Draft202012Validator(main_schema).validate(checked[OUTPUT])
        Draft202012Validator(result_schema).validate(checked[H04_OUTPUT])
        Draft202012Validator(result_schema).validate(checked[H14_OUTPUT])
        validate(checked[OUTPUT])


if __name__ == "__main__":
    unittest.main()
