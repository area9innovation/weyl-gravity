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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V28_RECONCILIATION.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v28_reconciliation.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_classical_import_gate_v28_reconciliation.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("gate_v28_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClassicalImportGateV28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_authoritative_row_count_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["m1a_completion_resolution"]["authoritative_rows_total"] = 17778
        self.assertIn("M1A resolution authoritative_rows_total", self.checker.check(mutated))

    def test_m1b_or_gate_promotion_is_rejected(self) -> None:
        for flag in ("M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "QME_RESTORED"):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn(f"fail-closed flag {flag}", self.checker.check(mutated))

    def test_field_dictionary_acceptance_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["required_hash_disposition"]["field_dictionary_hash"]["accepted"] = mutated["required_hash_disposition"]["field_dictionary_hash"]["candidate"]
        self.assertIn("field dictionary candidate/acceptance", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
