#!/usr/bin/env python3
"""Mutation tests for Atlas V21."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v21.py", "test_atlas_v21_builder")
checker = module(ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v21.py", "test_atlas_v21_checker")
verifier = module(ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v21.py", "test_atlas_v21_verifier")


class LorentzianWeylBVCompletionAtlasV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def assert_mutation_fails(self, mutate) -> None:
        value = deepcopy(self.value)
        mutate(value)
        self.assertTrue(checker.check(value))

    def test_cell_removal_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["branches"][0]["stages"].pop())

    def test_unrelated_stage_mutation_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["branches"][1]["stages"][0].__setitem__("status", "PASS"))

    def test_field_count_mutation_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["strict_field_equation_green_quotient_inverse"].__setitem__("field_rows", 115))

    def test_full_inverse_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["strict_field_equation_green_quotient_inverse"].__setitem__("full_ungauge_fixed_two_sided_inverse", True))

    def test_source_closure_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["strict_field_equation_green_quotient_inverse"].__setitem__("all_order_nonlinear_source_closure", True))

    def test_route_order_fails(self) -> None:
        def mutate(value):
            value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assert_mutation_fails(mutate)

    def test_quantum_promotion_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["claim_flags"].__setitem__("strict_pure_weyl_qme_restored", True))

    def test_predecessor_hash_mutation_fails(self) -> None:
        self.assert_mutation_fails(lambda v: v["predecessor"].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
