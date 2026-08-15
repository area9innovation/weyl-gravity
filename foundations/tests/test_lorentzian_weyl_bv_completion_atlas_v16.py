#!/usr/bin/env python3
"""Mutation tests for completion atlas V16."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v16.py", "test_atlas_v16_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v16.py", "test_atlas_v16_checker")
verifier = module(HERE / "verify_lorentzian_weyl_bv_completion_atlas_v16.py", "test_atlas_v16_verifier")


class LorentzianWeylBVCompletionAtlasV16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_d_inventory_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_full_d_action"]["D_coefficients"] = 385
        self.assertTrue(checker.check(value))

    def test_commutator_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_full_d_action"]["D_q1_commutator_defects"] = 1
        self.assertTrue(checker.check(value))

    def test_q2_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_full_d_action"]["full_q2_common_snapshot"] = True
        value["claim_flags"]["strict_386_full_carrier_q2_certified"] = True
        self.assertTrue(checker.check(value))

    def test_gate_hash_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_gate_v6_reconciliation"]["accepted_top_level_hashes"] = 1
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(checker.check(value))

    def test_non_strict_branch_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["branches"][1]["stages"][0]["status"] = "CERTIFIED"
        self.assertTrue(checker.check(value))

    def test_route_reordering_fails(self) -> None:
        value = deepcopy(self.value)
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assertTrue(checker.check(value))

    def test_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["lorentzian_full_theory_certified"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][-1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_drift_projection_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_gate_v6_reconciliation"]["transitive_provenance_drifted_files"] = 0
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
