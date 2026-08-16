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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1c_common_snapshot.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1c_common_snapshot.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1c_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1CCommonSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.checker = load_checker()

    def test_independent_structural_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_pin_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["artifact_pins"][0]["sha256"] = "0" * 64
        self.assertIn("artifact pins", self.checker.check(mutated))

    def test_export_removal_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["export_bindings"].pop()
        self.assertIn("export binding census", self.checker.check(mutated))

    def test_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["accepted_top_level_hashes"]["differential_hash"] = "f" * 64
        self.assertIn("top-level hash binding", self.checker.check(mutated))

    def test_gate_check_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["gate_a_replay"][5]["defects"] = 1
        self.assertIn("Gate-A replay payload", self.checker.check(mutated))

    def test_formal_source_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["claim_flags"]["FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX"] = True
        self.assertIn("fail-closed flag FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX", self.checker.check(mutated))

    def test_gate_and_quantum_promotions_are_rejected(self) -> None:
        for flag in ("CLASSICAL_IMPORT_GATE_PASSED", "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_runs_all_receivers(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
