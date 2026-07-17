from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from local_bv.diff_mixed_total_complex import analysis
from local_bv.diff_mixed_total_complex_certificate import OUTPUT, SCHEMA, build, validate
from local_bv.verify_diff_mixed_total_complex import verify


class DiffMixedTotalComplexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analysis = analysis()
        cls.certificate = build()

    def test_small_algebra_kills_four_dimensional_gravitational_anomaly(self) -> None:
        spaces = self.analysis["small_algebra"]["symmetric_invariant_spaces"]
        self.assertEqual([row["degree"] for row in spaces], [1, 2, 3, 4])
        self.assertEqual([row["invariant_dimension"] for row in spaces], [0, 2, 0, 3])
        self.assertEqual(spaces[2]["matrix_rank"], 56)
        self.assertEqual(spaces[2]["independent_modular_ranks"], {"101": 56, "103": 56, "107": 56})

    def test_total_complex_reduces_to_three_weyl_classes(self) -> None:
        quotient = self.analysis["AFN0_H14"]
        self.assertEqual(quotient["pure_Diff"], {"even_dimension": 0, "odd_dimension": 0})
        self.assertEqual(
            quotient["mixed_independent"], {"even_dimension": 0, "odd_dimension": 0}
        )
        self.assertEqual(quotient["even_dimension"], 2)
        self.assertEqual(quotient["odd_dimension"], 1)
        self.assertEqual(quotient["exact_rows"], ["ANOM_OMEGA_BOX_R"])

    def test_ambient_inventory_is_bound_without_raw_expansion(self) -> None:
        accounting = self.analysis["ambient_accounting"]
        self.assertEqual(accounting["refined_signature_count"], 720)
        self.assertEqual(accounting["raw_graph_count_not_materialized"], 2_860_932_903)
        self.assertEqual(
            accounting["refined_signatures_by_total_degree"],
            {"3": 42, "4": 102, "5": 210, "6": 366},
        )

    def test_certificate_reproduces_and_remains_fail_closed(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, self.certificate)
        self.assertEqual(value, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        validate(value)


if __name__ == "__main__":
    unittest.main()
