from __future__ import annotations
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26.json"

def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path); assert spec and spec.loader
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value; spec.loader.exec_module(value); return value

CHECK = module("atlas_v26_check_test", ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v26.py")
VERIFY = module("atlas_v26_verify_test", ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v26.py")

class AtlasV26Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.value = json.loads(RESULT.read_text())
    def test_repository(self): self.assertEqual(CHECK.check(self.value), []); self.assertEqual(VERIFY.verify(self.value), [])
    def test_generated(self):
        result = subprocess.run([sys.executable, str(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v26.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value); mutate(value); self.assertTrue(CHECK.check(value))
    def test_defect(self): self.mutation_fails(lambda value: value["strict_nonminimal_theory_identity_obstruction"].__setitem__("source_minus_candidate_defect", "0"))
    def test_no_go_firewall(self): self.mutation_fails(lambda value: value["strict_nonminimal_theory_identity_obstruction"].__setitem__("nonlinear_equivalence_obstructed", True))
    def test_gate_firewall(self): self.mutation_fails(lambda value: value["claim_flags"].__setitem__("strict_pure_weyl_classical_gate_passed", True))
    def test_gate_v8_projection(self): self.mutation_fails(lambda value: value["strict_gate_v8_reconciliation"].__setitem__("accepted_top_level_hashes", 1))
    def test_route_order(self): self.mutation_fails(lambda value: value["route_selection"].reverse())

if __name__ == "__main__": unittest.main()
