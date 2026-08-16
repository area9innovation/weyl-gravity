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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_IMMUTABLE_TYPED_LEDGER_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1a_immutable_typed_ledger.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1a_immutable_typed_ledger.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1a4_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1AImmutableTypedLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_local_namespace_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["local_386_rows"][0]["ce_ghost_number"] = 0
        self.assertTrue(any("endpoint namespaces" in error for error in self.checker.check(mutated)))

    def test_centered_degree_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["centered_cochain_row_index"][0]["ce_ghost_number"] = 4
        self.assertTrue(any("centered row" in error for error in self.checker.check(mutated)))

    def test_excluded_test_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["exclusion_ledger"][0]["disposition"] = "AUTHORITATIVE_TYPED_SOURCE"
        self.assertIn("test exclusion", self.checker.check(mutated))

    def test_component_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["component_payloads"][0]["row_payload_sha256"] = "0" * 64
        self.assertTrue(any("component payload" in error for error in self.checker.check(mutated)))

    def test_gate_promotions_are_rejected(self) -> None:
        for flag in ("M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
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
