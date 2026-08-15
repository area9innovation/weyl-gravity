from __future__ import annotations
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "d_quotient_classical/nonminimal_identity"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"

def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path); assert spec and spec.loader
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value; spec.loader.exec_module(value); return value

CHECK = module("quadratic_map_test_check", HERE / "check_classical_quadratic_auxiliary_elimination_map_v1.py")
VERIFY = module("quadratic_map_test_verify", HERE / "verify_classical_quadratic_auxiliary_elimination_map_v1.py")

class ClassicalQuadraticAuxiliaryMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.value = json.loads(RESULT.read_text())
    def test_repository(self): self.assertEqual(CHECK.check(self.value), []); self.assertEqual(VERIFY.verify(self.value), [])
    def test_generated(self):
        result = subprocess.run([sys.executable, str(HERE / "classical_quadratic_auxiliary_elimination_map_v1.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    def mutation_fails(self, mutate): value = copy.deepcopy(self.value); mutate(value); self.assertTrue(CHECK.check(value))
    def test_shift_sign(self): self.mutation_fails(lambda value: value["quadratic_auxiliary_map"]["fixture"].__setitem__("inverse_shift_mass_cross_mixed_polarization", "-1"))
    def test_residual(self): self.mutation_fails(lambda value: value["quadratic_auxiliary_map"]["fixture"].__setitem__("corrected_channel_residual", "1"))
    def test_full_equivalence_overclaim(self): self.mutation_fails(lambda value: value["claim_flags"].__setitem__("FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED", True))
    def test_float_fails(self): self.mutation_fails(lambda value: value["quadratic_auxiliary_map"]["fixture"]["G_b_quadratic_tensor"][0].__setitem__(0, -0.25))

if __name__ == "__main__": unittest.main()
