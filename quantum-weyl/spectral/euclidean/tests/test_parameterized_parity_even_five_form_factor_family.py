"""Tests for the globally parameterized parity-even five-factor family."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean import parameterized_parity_even_five_form_factor_family as producer
from spectral.euclidean import (
    verify_parameterized_parity_even_five_form_factor_family as verifier,
)


class ParameterizedFiveFactorFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = producer.build()
        cls.schema = json.loads(producer.SCHEMA.read_text())

    def test_schema_and_independent_rank_replay(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)
        verifier.verify_value(self.value)

    def test_ambiguity_rank_and_annihilator(self) -> None:
        self.assertEqual(self.value["ambiguity_module"]["rank"], 10)
        self.assertEqual(
            self.value["universal_content"][
                "complete_finite_Schur_sensitive_linear_combinations"
            ]["dimension"],
            0,
        )

    def test_partial_bv_is_preserved(self) -> None:
        self.assertTrue(
            self.value["decision"]["predecessor_partial_BV_coefficients_preserved"]
        )
        self.assertFalse(
            self.value["decision"]["background_specific_evaluation_authorized_without_D"]
        )

    def test_mutations_rejected(self) -> None:
        self.assertEqual(verifier.mutation_suite(self.value), 5)

    def test_universal_table_promotion_rejected(self) -> None:
        mutation = deepcopy(self.value)
        mutation["claim_flags"][
            "COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED"
        ] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutation)

    def test_local_constants_separate(self) -> None:
        for row in self.value["local_normalizations"].values():
            self.assertFalse(row["folded_into_nonlocal_functions"])


if __name__ == "__main__":
    unittest.main()
