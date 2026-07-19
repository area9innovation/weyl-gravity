from __future__ import annotations
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class ResonanceEllipseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.r=json.loads((ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json").read_text())
 def test_ellipse(self): self.assertEqual(self.r["parameterization"]["ellipse"],"16*r_x^2+3*r_p^2=115*d^2")
 def test_controls(self):
  self.assertIn("ell2_polar_e1",self.r["parameterization"]); self.assertIn("ell2_polar_e2",self.r["parameterization"])
 def test_resonance_nonempty(self): self.assertTrue(self.r["classification"]["axisymmetric_L1_L2_resonance_zero_locus_nonempty"])
 def test_hamiltonian_not_closed(self):
  self.assertFalse(self.r["classification"]["Hamiltonian_moment_map_zero"]); self.assertTrue(self.r["classification"]["Einstein_minus_balance_required"])
 def test_fail_closed(self):
  self.assertFalse(self.r["classification"]["complete_second_order_source_solved"]); self.assertFalse(self.r["classification"]["causal_or_quantum_claim"])
if __name__=="__main__": unittest.main()
