from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json"
CHECKER = HERE / "check_classical_import_gate_v30_reconciliation.py"
BUILDER = HERE / "build_classical_import_gate_v30_reconciliation.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("gate_v30_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV30Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_snapshot_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["m1c_common_snapshot_resolution"]["snapshot_sha256"] = "0" * 64
        self.assertIn("M1C snapshot resolution", self.checker.check(mutated))

    def test_incomplete_export_surface_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["export_reconciliation"].pop()
        self.assertIn("common export decision", self.checker.check(mutated))

    def test_open_gate_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["gate_disposition"]["gate_a_status"] = "FAIL_CLOSED"
        self.assertIn("Gate-A disposition", self.checker.check(mutated))

    def test_common_freeze_flag_is_required(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["COMMON_GATE_A_FREEZE_BOUND"] = False
        self.assertIn("required flag COMMON_GATE_A_FREEZE_BOUND", self.checker.check(mutated))

    def test_stale_pre_gate_nonclaim_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["does_not_establish"].append("a passed classical freeze gate")
        self.assertIn("stale pre-V30 nonclaim", self.checker.check(mutated))

    def test_quantum_promotions_are_rejected(self) -> None:
        for flag in (
            "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED",
            "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"quantum firewall {flag}", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
