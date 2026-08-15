from __future__ import annotations
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24.json"

def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path); assert spec and spec.loader
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value; spec.loader.exec_module(value); return value

CHECK = module("atlas_v24_check_test", ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v24.py")
VERIFY = module("atlas_v24_verify_test", ROOT / "foundations/verify_lorentzian_weyl_bv_completion_atlas_v24.py")

class AtlasV24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.value = json.loads(RESULT.read_text())
    def test_repository(self): self.assertEqual(CHECK.check(self.value), []); self.assertEqual(VERIFY.verify(self.value), [])
    def test_generated(self):
        result = subprocess.run([sys.executable, str(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v24.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    def mutation_fails(self, mutate):
        value = copy.deepcopy(self.value); mutate(value); self.assertTrue(CHECK.check(value))
    def test_arity_count(self): self.mutation_fails(lambda value: value["strict_minimal_q3_completion"].__setitem__("arity_three_channels", 71))
    def test_386_firewall(self): self.mutation_fails(lambda value: value["strict_minimal_q3_completion"].__setitem__("strict_386_q3_stabilized", True))
    def test_route_order(self): self.mutation_fails(lambda value: value["route_selection"].reverse())

if __name__ == "__main__": unittest.main()
