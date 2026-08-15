#!/usr/bin/env python3
"""Mutation tests for the field-equation Green quotient inverse."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from build_strict_386_field_equation_green_quotient_inverse import build, generated  # noqa: E402
from check_strict_386_field_equation_green_quotient_inverse import check  # noqa: E402


class FieldEquationGreenQuotientInverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_generated_artifacts_current(self) -> None:
        result, report = generated()
        self.assertEqual(result, (HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json").read_bytes())
        self.assertEqual(report, (HERE / "REPORT_STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.md").read_bytes())

    def test_baseline(self) -> None:
        self.assertEqual(check(copy.deepcopy(self.value)), [])

    def assert_mutation_fails(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(check(value))

    def test_field_count_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["typed_complex"]["field_space"].__setitem__("rows", 115))

    def test_kinetic_count_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["typed_complex"]["field_equation_operator"].__setitem__("nonzero_rational_jet_coefficients", 3263))

    def test_source_identity_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["restricted_homotopy_identities"].__setitem__("source_identity", "K G=identity"))

    def test_field_identity_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["restricted_homotopy_identities"].__setitem__("field_identity", "G K=identity"))

    def test_left_inverse_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["full_inverse_obstruction"].__setitem__("full_left_inverse_of_K_on_C0", True))

    def test_right_inverse_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["full_inverse_obstruction"].__setitem__("full_right_inverse_of_K_on_C1", True))

    def test_lambda_squared_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["nonlinear_consequence"].__setitem__("lambda_squared_source_cocycle_certified", True))

    def test_choice_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["foundational_strength"].__setitem__("quotient_requires_representative_selection", True))

    def test_moller_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["claim_flags"].__setitem__("STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED", True))

    def test_qme_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["claim_flags"].__setitem__("QME_RESTORED", True))

    def test_dependency_hash_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))

    def test_canonical_hash_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["canonical_hashes"].__setitem__("nonlinear_consequence_sha256", "f" * 64))


if __name__ == "__main__":
    unittest.main()
