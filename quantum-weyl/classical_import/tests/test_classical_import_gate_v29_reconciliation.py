#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V29_RECONCILIATION.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v29_reconciliation.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_classical_import_gate_v29_reconciliation.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("gate_v29_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV29Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_primal_count_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["m1b_primal_completion_resolution"]["represented_endpoint_rows"] = 4490
        self.assertIn("M1B primal resolution", self.checker.check(mutated))

    def test_support_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["m1b_primal_completion_resolution"]["harmonic_restriction_support_local"] = True
        self.assertIn("M1B primal resolution", self.checker.check(mutated))

    def test_full_m1b_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE"] = True
        self.assertIn("fail-closed flag M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", self.checker.check(mutated))

    def test_gate_and_quantum_promotions_are_rejected(self) -> None:
        for flag in ("CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
