"""Tests for the generic finite Schur kernel nonuniqueness theorem."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean import (
    generic_primed_schur_finite_relative_trace_kernel_nonuniqueness as producer,
)
from spectral.euclidean import (
    verify_generic_primed_schur_finite_relative_trace_kernel_nonuniqueness
    as verifier,
)


class SchurKernelNonuniquenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()
        cls.schema = json.loads(producer.SCHEMA.read_text())

    def test_schema_and_independent_matrix_series_replay(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)
        verifier.verify_value(self.value)

    def test_finite_value_shifts(self) -> None:
        rows = self.value["rank_one_finite_value_witness"]["finite_trace_shifts"]
        self.assertEqual(rows["Delta_R_mu0_K"], {"numerator": 7, "denominator": 11})
        self.assertEqual(
            rows["Delta_FP_R_mu0_K2"], {"numerator": 126, "denominator": 121}
        )
        self.assertEqual(rows["Delta_log_Det_3_R"], "log(47/33)")

    def test_cubic_row_shift_is_unit(self) -> None:
        row = self.value["third_curvature_row_witness"][
            "mixed_third_variation_shifts"
        ]["Delta_d123_log_Det_3_R"]
        self.assertEqual(row, {"numerator": 1, "denominator": 1})

    def test_mutations_rejected(self) -> None:
        self.assertEqual(verifier.mutation_suite(self.value), 5)

    def test_full_bv_promotion_rejected(self) -> None:
        mutation = deepcopy(self.value)
        mutation["claim_flags"]["COMPLETE_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutation)

    def test_global_spectral_input_is_explicit(self) -> None:
        data = self.value["minimal_additional_global_input"]["data"]
        self.assertTrue(any("primed resolvent" in row for row in data))
        self.assertTrue(any("spectral measure" in row for row in data))


if __name__ == "__main__":
    unittest.main()
