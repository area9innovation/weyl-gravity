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
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_strict_m1a_carrier_grading_convention_audit.py"
BUILDER = ROOT / "quantum-weyl/classical_import/build_strict_m1a_carrier_grading_convention_audit.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("m1a_convention_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class M1ACarrierGradingConventionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.checker = load_checker()

    def test_independent_checker_accepts(self) -> None:
        self.assertEqual(self.checker.check(copy.deepcopy(self.value)), [])

    def test_wrong_endpoint_bv_sign_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["local_endpoint_typed_rows"][0]["bv_ghost_number"] = -1
        self.assertTrue(any("endpoint semantics" in error for error in self.checker.check(mutated)))

    def test_compact_alias_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["convention_collision_witness"]["compact_degree_collision"]["same_semantic_field"] = True
        self.assertIn("collision witness", self.checker.check(mutated))

    def test_gate_or_qme_promotion_is_rejected(self) -> None:
        for flag in ("M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE", "CLASSICAL_IMPORT_GATE_PASSED", "QME_RESTORED"):
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(self.value)
                mutated["claim_flags"][flag] = True
                self.assertIn("claim flags", self.checker.check(mutated))

    def test_generator_is_current(self) -> None:
        completed = subprocess.run([sys.executable, str(BUILDER), "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_cli_checker_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
