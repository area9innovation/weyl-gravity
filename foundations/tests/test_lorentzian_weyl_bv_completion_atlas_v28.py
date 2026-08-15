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
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v28.md"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


CHECK = module("atlas_v28_check_test", HERE / "check_lorentzian_weyl_bv_completion_atlas_v28.py")
VERIFY = module("atlas_v28_verify_test", HERE / "verify_lorentzian_weyl_bv_completion_atlas_v28.py")


class CompletionAtlasV28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text())
        cls.report = REPORT.read_text()

    def test_repository(self):
        self.assertEqual(CHECK.check(self.value), [])
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_generated(self):
        result = subprocess.run([sys.executable, str(HERE / "build_lorentzian_weyl_bv_completion_atlas_v28.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value)
        mutate(value)
        self.assertTrue(CHECK.check(value))

    def test_family_count_mutation(self):
        self.mutation_fails(lambda value: value["strict_shifted_auxiliary_cubic_inventory"].__setitem__("known_required_cubic_families", 8))

    def test_full_equivalence_overclaim(self):
        self.mutation_fails(lambda value: value["claim_flags"].__setitem__("strict_386_nonlinear_equivalence_constructed", True))

    def test_route_reorder(self):
        self.mutation_fails(lambda value: value["route_selection"].reverse())

    def test_gate_promotion(self):
        self.mutation_fails(lambda value: value["strict_gate_v10_reconciliation"].__setitem__("gate_a_status", "PASS"))

    def test_float_fails(self):
        value = copy.deepcopy(self.value)
        value["strict_shifted_auxiliary_cubic_inventory"]["carrier_rows"] = 386.0
        self.assertTrue(VERIFY.verify(value, self.report))


if __name__ == "__main__":
    unittest.main()
