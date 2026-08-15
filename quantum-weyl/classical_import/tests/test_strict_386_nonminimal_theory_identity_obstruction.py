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
RESULT = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("strict_identity_obstruction_check_test", HERE / "check_strict_386_nonminimal_theory_identity_obstruction.py")
VERIFY = module("strict_identity_obstruction_verify_test", HERE / "verify_strict_386_nonminimal_theory_identity_obstruction.py")


class Strict386NonminimalTheoryIdentityObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run([sys.executable, str(HERE / "build_strict_386_nonminimal_theory_identity_obstruction.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_defect_mutation(self):
        self.mutation_fails(lambda value: value["exact_channel_comparison"].__setitem__("source_minus_candidate_defect", "0"))

    def test_candidate_promotion(self):
        self.mutation_fails(lambda value: value["theory_identity_disposition"].__setitem__("candidate_is_authoritative_ordinary_derivative_nonminimal_theory", True))

    def test_equivalence_no_go_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_OBSTRUCTED", True))

    def test_gate_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("CLASSICAL_IMPORT_GATE_PASSED", True))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["scope"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
