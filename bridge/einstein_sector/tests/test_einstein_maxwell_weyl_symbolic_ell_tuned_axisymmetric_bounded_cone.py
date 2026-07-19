import json,unittest
from bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone import OUTPUT,build
class Tests(unittest.TestCase):
 def test_current(self): self.assertEqual(json.loads(OUTPUT.read_text()),build())
 def test_scope(self):
  d=build(); self.assertTrue(d["classification"]["complete_tuned_axisymmetric_standard_branch_bounded_cone_classified"]); self.assertFalse(d["classification"]["extra_primary_or_multiple_abs_momentum_inputs_classified"])
if __name__=="__main__": unittest.main()
