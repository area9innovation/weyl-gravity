#!/usr/bin/env python3
"""Mutation tests for Atlas V19."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v19.py", "test_atlas_v19_builder")
checker = module(ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v19.py", "test_atlas_v19_checker")
verifier = module(ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v19.py", "test_atlas_v19_verifier")


class LorentzianWeylBVCompletionAtlasV19Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_cell_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["branches"][0]["stages"].pop()
        self.assertTrue(checker.check(value))

    def test_unrelated_stage_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["branches"][1]["stages"][0]["status"] = "PASS"
        self.assertTrue(checker.check(value))

    def test_polarized_tree_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_recursive_causal_tree_domains"]["retarded_all_finite_trees"] = False
        self.assertTrue(checker.check(value))

    def test_mixed_census_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_recursive_causal_tree_domains"]["four_leaf_admissible"] = 40
        value["strict_recursive_causal_tree_domains"]["four_leaf_not_uniformly_defined"] = 0
        self.assertTrue(checker.check(value))

    def test_unrestricted_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_recursive_causal_tree_domains"]["unrestricted_mixed_sign_trees"] = True
        value["claim_flags"]["strict_386_unrestricted_mixed_sign_trees_certified"] = True
        self.assertTrue(checker.check(value))

    def test_infinite_series_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_recursive_causal_tree_domains"]["infinite_tree_series_convergence"] = True
        value["claim_flags"]["strict_386_infinite_tree_series_convergence_certified"] = True
        self.assertTrue(checker.check(value))

    def test_authority_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_recursive_causal_tree_domains"]["authoritative_q2"] = True
        value["claim_flags"]["strict_386_authoritative_q2_recursive_trees_certified"] = True
        self.assertTrue(checker.check(value))

    def test_route_order_fails(self) -> None:
        value = deepcopy(self.value)
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assertTrue(checker.check(value))

    def test_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["strict_386_full_bv_hadamard_state_constructed"] = True
        value["claim_flags"]["strict_pure_weyl_qme_restored"] = True
        self.assertTrue(checker.check(value))

    def test_predecessor_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["predecessor"]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
