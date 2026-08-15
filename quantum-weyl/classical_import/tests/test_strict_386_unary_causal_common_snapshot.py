#!/usr/bin/env python3
"""Mutation tests for the scoped strict unary-causal snapshot."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_unary_causal_common_snapshot.py", "test_unary_snapshot_builder")
checker = module(HERE / "check_strict_386_unary_causal_common_snapshot.py", "test_unary_snapshot_checker")
verifier = module(HERE / "verify_strict_386_unary_causal_common_snapshot.py", "test_unary_snapshot_verifier")


class Strict386UnaryCausalCommonSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_pairing_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["accepted_objects"]["odd_pairing_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_green_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["accepted_objects"]["plus_green_name_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_scoped_label_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["common_snapshot"]["receiver_status"] = "ACCEPTED"
        self.assertTrue(checker.check(value))

    def test_missing_bundle_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_v5_reconciliation"]["missing_bundle"].pop()
        self.assertTrue(checker.check(value))

    def test_gate_hash_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_v5_reconciliation"]["top_level_hashes_accepted_by_this_scoped_result"] = 2
        self.assertTrue(checker.check(value))

    def test_gate_a_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_v5_reconciliation"]["gate_a_status"] = "VERIFIED"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_qme_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["QME_RESTORED"] = True
        value["claim_flags"]["LORENTZIAN_QUANTUM_THEORY"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
