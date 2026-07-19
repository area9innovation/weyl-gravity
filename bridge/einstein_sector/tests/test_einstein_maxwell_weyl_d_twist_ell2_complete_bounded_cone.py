"""Tests for the d-enlarged twist/ell2 cone."""
import json, unittest
from bridge.einstein_sector import einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone as theorem

class DTwistEll2ConeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls)->None: cls.value=theorem.build()
 def test_current(self)->None: self.assertEqual(json.loads(theorem.OUTPUT.read_text()),self.value)
 def test_stratified_union(self)->None:
  z=self.value["complete_bounded_zero_locus"]; self.assertTrue(z["union_is_necessary_and_sufficient"]); self.assertIn("d=0",z["wave_stratum"]); self.assertIn("d",z["static_stratum"])
 def test_nonzero_wave_forces_d_zero(self)->None: self.assertTrue(self.value["classification"]["nonzero_wave_forces_d_zero"])
 def test_predecessor_cokernel_is_separated(self)->None: self.assertIn("zero bounded adjoint pairing",self.value["necessity_proof"]["predecessor_cokernel_zero"])
 def test_larger_dynamics_fail_closed(self)->None:
  c=self.value["classification"]; self.assertFalse(c["radion_or_electric_tangent_classified"]); self.assertFalse(c["other_ell_or_momentum_classified"])
 def test_causal_fail_closed(self)->None: self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"],"NO_CERTIFIED_MAP")
if __name__=="__main__": unittest.main()
