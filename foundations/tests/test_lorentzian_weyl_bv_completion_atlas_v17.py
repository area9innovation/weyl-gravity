#!/usr/bin/env python3
"""Mutation tests for completion atlas V17."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v17.py", "test_atlas_v17_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v17.py", "test_atlas_v17_checker")
verifier = module(HERE / "verify_lorentzian_weyl_bv_completion_atlas_v17.py", "test_atlas_v17_verifier")


class LorentzianWeylBVCompletionAtlasV17Tests(unittest.TestCase):
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

    def test_q2_channel_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_stabilized_q2_lift_preflight"]["expanded_component_channels"] = 141
        self.assertTrue(checker.check(value))

    def test_authoritative_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_stabilized_q2_lift_preflight"]["authoritative_full_q2_imported"] = True
        value["claim_flags"]["strict_386_authoritative_full_q2_imported"] = True
        self.assertTrue(checker.check(value))

    def test_q2_hash_acceptance_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_gate_v7_reconciliation"]["candidate_q2_hash_accepted"] = True
        value["strict_gate_v7_reconciliation"]["accepted_top_level_hashes"] = 1
        self.assertTrue(checker.check(value))

    def test_gate_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["strict_gate_v7_reconciliation"]["gate_a_status"] = "PASS"
        value["claim_flags"]["strict_pure_weyl_classical_gate_passed"] = True
        self.assertTrue(checker.check(value))

    def test_route_order_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["route_selection"][0], value["route_selection"][1] = value["route_selection"][1], value["route_selection"][0]
        self.assertTrue(checker.check(value))

    def test_QME_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["strict_pure_weyl_qme_restored"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][-1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_digest_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["independent_checker"]["expected_digest"] = "f" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
