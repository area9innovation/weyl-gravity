#!/usr/bin/env python3
"""Mutation tests for Atlas V18."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v18.py", "test_atlas_v18_builder")
checker = module(ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v18.py", "test_atlas_v18_checker")
verifier = module(ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v18.py", "test_atlas_v18_verifier")


class LorentzianWeylBVCompletionAtlasV18Tests(unittest.TestCase):
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

    def test_response_defect_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_q2_green_composition_preflight"]["response_identity_defects"] = 1
        self.assertTrue(checker.check(value))

    def test_authority_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_q2_green_composition_preflight"]["authoritative_q2_green_compatibility"] = True
        value["claim_flags"]["strict_386_authoritative_q2_green_compatibility_certified"] = True
        self.assertTrue(checker.check(value))

    def test_recursive_tree_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_q2_green_composition_preflight"]["recursive_nonlinear_green_trees"] = True
        value["claim_flags"]["strict_386_recursive_nonlinear_green_trees_certified"] = True
        self.assertTrue(checker.check(value))

    def test_foundation_collapse_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_q2_green_composition_preflight"]["completed_infinite_spaces_required"] = False
        value["strict_q2_green_composition_preflight"]["weakest_complete_foundational_base"] = "PRA"
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
