from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v27.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("atlas_v27_check_test", HERE / "check_lorentzian_weyl_bv_completion_atlas_v27.py")
VERIFY = module("atlas_v27_verify_test", HERE / "verify_lorentzian_weyl_bv_completion_atlas_v27.py")


class CompletionAtlasV27Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run([sys.executable, str(HERE / "build_lorentzian_weyl_bv_completion_atlas_v27.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_residual_mutation(self):
        self.mutation_fails(lambda value: value["strict_quadratic_auxiliary_elimination"].__setitem__("residual", "1"))

    def test_full_equivalence_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("strict_386_nonlinear_equivalence_constructed", True))

    def test_route_reorder(self):
        self.mutation_fails(lambda value: value["route_selection"].reverse())

    def test_gate_promotion(self):
        self.mutation_fails(lambda value: value["strict_gate_v9_reconciliation"].__setitem__("gate_a_status", "PASS"))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_quadratic_auxiliary_elimination"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
