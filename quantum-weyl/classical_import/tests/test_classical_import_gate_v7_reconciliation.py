#!/usr/bin/env python3
"""Mutation tests for Gate-A v7 reconciliation."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_classical_import_gate_v7_reconciliation.py", "test_gate_v7_builder")
checker = module(HERE / "check_classical_import_gate_v7_reconciliation.py", "test_gate_v7_checker")
verifier = module(HERE / "verify_classical_import_gate_v7_reconciliation.py", "test_gate_v7_verifier")


class ClassicalImportGateV7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_candidate_hash_acceptance_fails(self) -> None:
        value = deepcopy(self.value)
        value["required_hash_disposition"]["q2_hash"]["accepted"] = value["required_hash_disposition"]["q2_hash"]["candidate"]
        self.assertTrue(checker.check(value))

    def test_D_q2_freeze_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        row = next(item for item in value["freeze_check_reconciliation"] if item["check_id"] == "D_q2_derivation")
        row["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(checker.check(value))

    def test_theory_identity_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["STRICT_386_CANDIDATE_THEORY_IDENTITY"] = True
        value["claim_flags"]["STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2"] = True
        self.assertTrue(checker.check(value))

    def test_gate_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["gate_a_status"] = "PASS"
        value["gate_disposition"]["accepted_common_snapshot_hashes"] = 1
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_candidate_count_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["m2_stabilized_candidate_resolution"]["unique_block_triples"] = 69
        self.assertTrue(checker.check(value))

    def test_export_order_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["export_reconciliation"][0], value["export_reconciliation"][1] = value["export_reconciliation"][1], value["export_reconciliation"][0]
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][-1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_drift_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["transitive_provenance_drift"]["drifted_files"] = 0
        value["transitive_provenance_drift"]["entries"] = []
        self.assertTrue(checker.check(value))

    def test_QME_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
