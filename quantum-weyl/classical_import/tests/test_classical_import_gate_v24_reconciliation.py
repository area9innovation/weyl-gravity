from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_classical_import_gate_v24_reconciliation.py"
CHECKER = HERE / "check_classical_import_gate_v24_reconciliation.py"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V24_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V24.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "classical_import_gate_v24_source")
checker = load(CHECKER, "classical_import_gate_v24_checker")


class ClassicalImportGateV24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_m3rc_b_closes_without_passing_gate(self):
        resolution = self.value["m3rc_action_support_dual_resolution"]
        self.assertEqual(resolution["M3RC_B_ACTION_SUPPORT_DUAL_IDENTIFICATION"], "COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6")
        self.assertEqual(resolution["M4R_TYPED_RESIDUAL_CYCLICITY"], "READY")
        self.assertEqual(self.value["gate_disposition"]["gate_a_status"], "FAIL_CLOSED")

    def test_missing_bundle_is_dependency_ordered(self):
        self.assertEqual(
            [item["id"] for item in self.value["minimal_missing_bundle"]],
            ["M4R_TYPED_RESIDUAL_CYCLICITY", "M1_COMMON_STRICT_SNAPSHOT"],
        )

    def test_pairing_rank_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["m3rc_action_support_dual_resolution"]["action_pairing_rank"] = 939
        self.assertTrue(checker.check(value))

    def test_full_dual_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["FULL_ALL_ENERGY_CONTINUOUS_DUAL_IDENTIFIED"] = True
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
