#!/usr/bin/env python3
"""Mutation tests for Gate-A v6 reconciliation."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_classical_import_gate_v6_reconciliation.py", "test_gate_v6_builder")
checker = module(HERE / "check_classical_import_gate_v6_reconciliation.py", "test_gate_v6_checker")
verifier = module(HERE / "verify_classical_import_gate_v6_reconciliation.py", "test_gate_v6_verifier")


class ClassicalImportGateV6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value)[0], [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_d_export_demotion_fails(self) -> None:
        value = deepcopy(self.value)
        row = next(row for row in value["export_reconciliation"] if row["export_id"] == "local_D_action_on_bv_generators")
        row["status"] = "CERTIFIED_DIFFERENT_THEORY"
        self.assertTrue(checker.check(value)[0])

    def test_d_q1_demotion_fails(self) -> None:
        value = deepcopy(self.value)
        row = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "D_q1_commutator_zero")
        row["status"] = "CERTIFIED_DIFFERENT_THEORY"
        self.assertTrue(checker.check(value)[0])

    def test_d_q2_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        row = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "D_q2_derivation")
        row["status"] = "RECEIVER_VERIFIED_SCOPED"
        value["claim_flags"]["STRICT_386_D_Q2_DERIVATION"] = True
        self.assertTrue(checker.check(value)[0])

    def test_candidate_hash_acceptance_fails(self) -> None:
        value = deepcopy(self.value)
        value["required_hash_disposition"]["D_action_hash"]["accepted"] = value["required_hash_disposition"]["D_action_hash"]["candidate"]
        value["gate_disposition"]["accepted_common_snapshot_hashes"] = 1
        self.assertTrue(checker.check(value)[0])

    def test_m2_reintroduces_d_missing_fails(self) -> None:
        value = deepcopy(self.value)
        row = next(row for row in value["minimal_missing_bundle"] if row["id"] == "M2_STRICT_Q2_D")
        row["unlocks"].append("D_q1_commutator_zero")
        self.assertTrue(checker.check(value)[0])

    def test_m3_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["m3_scoped_resolution"]["status"] = "PASS"
        self.assertTrue(checker.check(value)[0])

    def test_gate_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["gate_a_status"] = "PASS"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(checker.check(value)[0])

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][-1]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value)[0])

    def test_drift_ledger_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["transitive_provenance_drift"]["entries"].pop()
        value["transitive_provenance_drift"]["drifted_files"] -= 1
        self.assertTrue(checker.check(value)[0])


if __name__ == "__main__":
    unittest.main()
