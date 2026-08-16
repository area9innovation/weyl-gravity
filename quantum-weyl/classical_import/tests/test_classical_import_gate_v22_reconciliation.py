from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v22_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v22_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V22.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v22_source")
checker = load(CHECKER, "classical_import_gate_v22_checker")


class ClassicalImportGateV22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_gate_remains_fail_closed(self):
        gate = self.value["gate_disposition"]
        self.assertEqual(gate["accepted_common_snapshot_hashes"], 1)
        self.assertEqual(gate["freeze_checks_blocked"], 1)
        self.assertEqual(gate["gate_a_status"], "FAIL_CLOSED")

    def test_missing_bundle_is_dependency_ordered(self):
        self.assertEqual(
            [item["id"] for item in self.value["minimal_missing_bundle"]],
            [
                "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION",
                "M4R_TYPED_RESIDUAL_CYCLICITY",
                "M1_COMMON_STRICT_SNAPSHOT",
            ],
        )

    def test_rank_obstruction_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["residual_cyclic_carrier_obstruction_resolution"]["current_induced_odd_pairing_rank"] = 470
        self.assertTrue(checker.check(value))

    def test_m3rc_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self):
        for flag in (
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A",
            "HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
