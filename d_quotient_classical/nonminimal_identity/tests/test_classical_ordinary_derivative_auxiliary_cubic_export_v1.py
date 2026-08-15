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
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-ordinary-derivative-auxiliary-cubic-export-v1.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("classical_aux_cubic_check_test", HERE / "check_classical_ordinary_derivative_auxiliary_cubic_export_v1.py")
VERIFY = module("classical_aux_cubic_verify_test", HERE / "verify_classical_ordinary_derivative_auxiliary_cubic_export_v1.py")


class ClassicalAuxiliaryCubicExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run([sys.executable, str(HERE / "classical_ordinary_derivative_auxiliary_cubic_export_v1.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_polarization_mutation(self):
        self.mutation_fails(lambda value: value["auxiliary_cubic_interaction"]["witness"].__setitem__("mixed_derivative_d_t_d_s_squared_at_zero", "0"))

    def test_equivalence_overclaim(self):
        self.mutation_fails(lambda value: value["theory_identity_disposition"].__setitem__("cyclic_L_infinity_equivalence_obstructed", True))

    def test_full_export_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("FULL_386_NONMINIMAL_Q2_EXPORTED", True))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["scope"]["coefficient_field"] = 1.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
