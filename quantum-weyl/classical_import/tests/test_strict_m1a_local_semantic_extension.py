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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1a_local_semantic_extension.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1a_local_semantic_extension.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1a_local_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1ALocalSemanticExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_auxiliary_dimension_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        row = next(row for row in mutated["local_extension_rows"] if row["block"] == "AUX_F_HAT")
        row["mass_dimension"] = 1
        self.assertTrue(any("auxiliary semantics" in error for error in self.checker.check(mutated)))

    def test_cone_dual_dimension_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        row = next(row for row in mutated["local_extension_rows"] if row["block"] == "CONE_X_ID_SHARP")
        row["mass_dimension"] += 1
        self.assertTrue(any("cone grading" in error for error in self.checker.check(mutated)))

    def test_replacing_not_applicable_weyl_action_by_scalar_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        row = next(row for row in mutated["local_extension_rows"] if row["block"].startswith("CONE_"))
        row["Weyl_weight"] = 0
        self.assertTrue(any("cone Weyl applicability" in error for error in self.checker.check(mutated)))

    def test_gate_promotions_are_rejected(self) -> None:
        for flag in ("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "QME_RESTORED"):
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
