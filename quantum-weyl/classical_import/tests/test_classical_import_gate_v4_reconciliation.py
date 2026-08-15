from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import check_classical_import_gate_v4_reconciliation as checker
import verify_classical_import_gate_v4_reconciliation as verifier


RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V4_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V4.md"


class ClassicalImportGateV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value)[0], [])
        self.assertEqual(verifier.verify(self.value, self.report), [])

    def test_only_two_scoped_rows_promoted(self) -> None:
        exports = {row["export_id"]: row for row in self.value["export_reconciliation"]}
        checks = {row["check_id"]: row for row in self.value["freeze_check_reconciliation"]}
        self.assertEqual(exports["support_local_classical_bv_q2"]["status"], "RECEIVER_VERIFIED_SCOPED")
        self.assertEqual(checks["q1_q2_arity_two_nilpotency"]["status"], "RECEIVER_VERIFIED_SCOPED")
        self.assertEqual(checks["D_q1_commutator_zero"]["status"], "CERTIFIED_DIFFERENT_THEORY")
        self.assertEqual(checks["q2_cyclic_compatibility"]["status"], "CERTIFIED_DIFFERENT_THEORY")

    def test_D_promotion_fails_closed(self) -> None:
        value = copy.deepcopy(self.value)
        next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "D_q2_derivation")["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(any("unlicensed" in item for item in checker.check(value)[0]))

    def test_common_hash_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        first = next(iter(value["required_hash_disposition"].values()))
        first["accepted"] = "0" * 64
        self.assertTrue(any("hash promotion" in item for item in checker.check(value)[0]))

    def test_minimal_scope_erasure_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["m2_minimal_resolution"]["boundary"] = "globally complete"
        self.assertTrue(any("M2 minimal resolution" in item for item in checker.check(value)[0]))

    def test_gate_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(any("claim promotion" in item for item in checker.check(value)[0]))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("Gate A remains fail closed", "Gate A passed")
        self.assertTrue(any("report token" in item for item in verifier.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
