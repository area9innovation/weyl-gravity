"""Tests for the maximal parity-even five-form-factor assembly boundary."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean import parity_even_third_curvature_five_form_factor_assembly as producer
from spectral.euclidean import (
    verify_parity_even_third_curvature_five_form_factor_assembly as verifier,
)


class FiveFormFactorAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()
        cls.schema = json.loads(producer.SCHEMA.read_text())

    def test_strict_schema_and_independent_reconstruction(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)
        verifier.verify_value(self.value)

    def test_maximal_quotient_is_partial_bv(self) -> None:
        self.assertEqual(
            self.value["maximal_determined_quotient"]["status"],
            "COEFFICIENT_COMPUTED_PARTIAL_BV",
        )
        self.assertFalse(
            self.value["claim_flags"]["FULL_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED"]
        )
        self.assertEqual(
            len(self.value["maximal_determined_quotient"]["channel_row_digests"]),
            11,
        )

    def test_channel_contact_scale_zero_mode_mutations_rejected(self) -> None:
        self.assertEqual(verifier.mutation_suite(self.value), 5)

    def test_full_bv_promotion_rejected_by_schema(self) -> None:
        mutation = deepcopy(self.value)
        mutation["claim_flags"]["FULL_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutation)

    def test_local_constants_remain_separate(self) -> None:
        for row in self.value["local_normalization_constants"].values():
            self.assertFalse(row["folded_into_nonlocal_functions"])

    def test_receiver_contract_is_zero_mode_explicit(self) -> None:
        contract = self.value["first_missing_analytic_datum"]["receiver_contract"]
        self.assertIn("Pi_0", contract["weight"])
        self.assertTrue(
            any("zero-mode projector" in row for row in contract["required_checks"])
        )
        self.assertTrue(any("primed Green" in row for row in contract["required_data"]))


if __name__ == "__main__":
    unittest.main()
