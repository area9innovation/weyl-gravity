from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("classical_import_gate_v5_check", HERE / "check_classical_import_gate_v5_reconciliation.py")
VERIFY = module("classical_import_gate_v5_verify", HERE / "verify_classical_import_gate_v5_reconciliation.py")


class ClassicalImportGateV5ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_GATE_V5.md").read_text()

    def test_repository_result(self) -> None:
        errors, counts = CHECK.check(self.value)
        self.assertEqual(errors, [])
        self.assertEqual(counts, {"exports": 20, "checks": 10, "inputs": 21})

    def test_schema_determinism_and_report(self) -> None:
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_full_pairing_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "cyclic_compatibility")
        row["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(any("full cyclic-SDR" in error or "count firewall" in error for error in CHECK.check(value)[0]))

    def test_D_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        row = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "D_q2_derivation")
        row["status"] = "RECEIVER_VERIFIED_SCOPED"
        self.assertTrue(any("D check" in error or "count firewall" in error for error in CHECK.check(value)[0]))

    def test_common_hash_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        first = next(iter(value["required_hash_disposition"].values()))
        first["accepted"] = first.get("candidate") or "0" * 64
        self.assertTrue(any("common hash" in error for error in CHECK.check(value)[0]))

    def test_cyclic_count_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["m4_minimal_resolution"]["translated_convention_defect_coefficient_count"] = 1
        self.assertTrue(any("M4 minimal" in error for error in CHECK.check(value)[0]))

    def test_report_overclaim_fails(self) -> None:
        report = self.report.replace("Gate A remains fail closed", "Gate A passed")
        self.assertTrue(any("report token" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
