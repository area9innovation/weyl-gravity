from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V9_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V9.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("gate_v9_check_test", HERE / "check_classical_import_gate_v9_reconciliation.py")
VERIFY = module("gate_v9_verify_test", HERE / "verify_classical_import_gate_v9_reconciliation.py")


class GateV9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "build_classical_import_gate_v9_reconciliation.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_residual_mutation(self):
        self.mutation_fails(lambda value: value["m2_quadratic_elimination_resolution"].__setitem__("residual", "1"))

    def test_full_equivalence_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("STRICT_386_NONLINEAR_EQUIVALENCE_CONSTRUCTED", True))

    def test_hash_acceptance(self):
        self.mutation_fails(lambda value: value["required_hash_disposition"]["q2_hash"].__setitem__("accepted", "bad"))

    def test_gate_promotion(self):
        self.mutation_fails(lambda value: value["gate_disposition"].__setitem__("gate_a_status", "PASS"))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["m2_quadratic_elimination_resolution"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
