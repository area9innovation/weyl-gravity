from __future__ import annotations
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]; HERE = ROOT / "foundations"
def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise ImportError(path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v6.py", "test_atlas_v6_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v6.py", "test_atlas_v6_checker")
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6.json"; REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v6.md"

class CompletionAtlasV6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.value = json.loads(RESULT.read_text())
    def test_repository_result(self): self.assertEqual(checker.check(self.value), [])
    def test_generated_current(self):
        result, report = builder.generated(); self.assertEqual(RESULT.read_bytes(), result); self.assertEqual(REPORT.read_bytes(), report)
    def test_sign_mutation_fails(self):
        value = copy.deepcopy(self.value); value["strict_suspended_adjoint_bridge"]["full_R_negative"] = 9; self.assertTrue(checker.check(value))
    def test_pairing_promotion_fails(self):
        value = copy.deepcopy(self.value); value["claim_flags"]["strict_386_component_pairing_serialized"] = True; self.assertTrue(checker.check(value))
    def test_d_promotion_fails(self):
        value = copy.deepcopy(self.value); value["claim_flags"]["strict_386_local_d_certified"] = True; self.assertTrue(checker.check(value))
    def test_q2_promotion_fails(self):
        value = copy.deepcopy(self.value); value["claim_flags"]["strict_386_q2_green_compatibility_certified"] = True; self.assertTrue(checker.check(value))
    def test_quantum_promotion_fails(self):
        value = copy.deepcopy(self.value); value["claim_flags"]["lorentzian_full_theory_certified"] = True; self.assertTrue(checker.check(value))

if __name__ == "__main__": unittest.main()
