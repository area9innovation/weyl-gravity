from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v23_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v23_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V23_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V23.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v23_source")
checker = load(CHECKER, "classical_import_gate_v23_checker")


class ClassicalImportGateV23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_formal_completion_does_not_pass_gate(self):
        resolution = self.value["m3rc_formal_cotangent_dual_resolution"]
        self.assertEqual(resolution["M3RC_A_FORMAL_COTANGENT_DUAL_COMPARISON"], "COMPLETE")
        self.assertEqual(resolution["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION"], "OPEN")
        self.assertEqual(resolution["M4R_TYPED_RESIDUAL_CYCLICITY"], "BLOCKED_BY_M3RC_B")
        self.assertEqual(self.value["gate_disposition"]["gate_a_status"], "FAIL_CLOSED")

    def test_missing_bundle_is_dependency_ordered(self):
        self.assertEqual(
            [item["id"] for item in self.value["minimal_missing_bundle"]],
            [
                "M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION",
                "M4R_TYPED_RESIDUAL_CYCLICITY",
                "M1_COMMON_STRICT_SNAPSHOT",
            ],
        )

    def test_same_source_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["m3rc_formal_cotangent_dual_resolution"]["same_source_retract_to_940_possible"] = True
        self.assertTrue(checker.check(value))

    def test_action_support_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE"] = True
        self.assertTrue(checker.check(value))

    def test_downstream_promotions_fail(self):
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
