#!/usr/bin/env python3
"""Mutation tests for Lorentzian Weyl BV completion atlas V14."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V14.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v14.py", "test_atlas_v14_builder")
checker = module(ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v14.py", "test_atlas_v14_checker")
verifier = module(ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v14.py", "test_atlas_v14_verifier")


class CompletionAtlasV14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_unrelated_branch_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["branches"][1]["stages"][0]["status"] = "CERTIFIED"
        self.assertTrue(checker.check(value))

    def test_graph_inventory_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_graph_q1_sdr_component_jets"]["nonzero_rational_coefficients"] = 4373
        self.assertTrue(checker.check(value))

    def test_obsolete_suspension_laundering_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_graph_q1_sdr_component_jets"]["old_diagonal_suspension_cyclicity_defects"] = 0
        self.assertTrue(checker.check(value))

    def test_green_and_gate_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["strict_386_represented_green_actions_serialized"] = True
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(checker.check(value))

    def test_route_reordering_fails(self) -> None:
        value = deepcopy(self.value)
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assertTrue(checker.check(value))

    def test_provenance_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][-1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
