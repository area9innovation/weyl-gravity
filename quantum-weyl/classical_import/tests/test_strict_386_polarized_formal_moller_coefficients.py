#!/usr/bin/env python3
"""Mutation tests for polarized formal Møller-coefficient evidence."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from build_strict_386_polarized_formal_moller_coefficients import build, generated  # noqa: E402
from check_strict_386_polarized_formal_moller_coefficients import check  # noqa: E402


class PolarizedFormalMollerCoefficientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_generated_artifacts_current(self) -> None:
        result, report = generated()
        self.assertEqual(result, (HERE / "certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json").read_bytes())
        self.assertEqual(report, (HERE / "REPORT_STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.md").read_bytes())

    def test_baseline(self) -> None:
        self.assertEqual(check(copy.deepcopy(self.value)), [])

    def assert_mutation_fails(self, mutate) -> None:
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(check(value))

    def test_tree_count_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["catalan_tree_formula"]["checked_rows"][3].__setitem__("plane_tree_count", 39))

    def test_tree_hash_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["catalan_tree_formula"]["checked_rows"][4].__setitem__("canonical_tree_list_sha256", "0" * 64))

    def test_rational_weight_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["catalan_tree_formula"]["checked_rows"][2].__setitem__("coefficient_per_plane_tree", "1/8"))

    def test_formal_boundary_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["coefficient_recurrence"].__setitem__("analytic_norm_or_radius", "1"))

    def test_support_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["polarized_support_and_continuity"]["plus"].__setitem__("coefficient_support_for_m_ge_1", "future compact"))

    def test_bv_residual_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["bv_equation_diagnostic"].__setitem__("order_lambda_squared_residual", "0"))

    def test_bv_promotion_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["bv_equation_diagnostic"].__setitem__("order_lambda_squared_zero_certified", True))

    def test_analytic_convergence_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["claim_flags"].__setitem__("STRICT_386_CANDIDATE_ANALYTIC_SERIES_CONVERGENCE_CERTIFIED", True))

    def test_moller_promotion_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["claim_flags"].__setitem__("STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED", True))

    def test_qme_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["claim_flags"].__setitem__("QME_RESTORED", True))

    def test_foundation_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["foundational_strength"].__setitem__("choice_operation_added", True))

    def test_dependency_hash_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["provenance"]["inputs"][0].__setitem__("sha256", "f" * 64))

    def test_canonical_hash_mutation(self) -> None:
        self.assert_mutation_fails(lambda v: v["canonical_hashes"].__setitem__("bv_equation_diagnostic_sha256", "a" * 64))


if __name__ == "__main__":
    unittest.main()
