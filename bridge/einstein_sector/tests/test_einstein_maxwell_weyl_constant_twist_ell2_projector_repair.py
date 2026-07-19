import json,unittest
from bridge.einstein_sector import einstein_maxwell_weyl_constant_twist_ell2_projector_repair as t
class TestRepair(unittest.TestCase):
 @classmethod
 def setUpClass(c):c.v=t.build()
 def test_current(s):s.assertEqual(json.loads(t.OUTPUT.read_text()),s.v)
 def test_type(s):s.assertTrue(s.v['type_audit']['type_mismatch_certified'])
 def test_zero(s):s.assertEqual(s.v['corrected_position_maps']['extra'],'zero');s.assertEqual(s.v['corrected_position_maps']['Einstein_plus_minus'],'zero')
 def test_product(s):s.assertTrue(s.v['bounded_cone_repair']['necessity_and_sufficiency'])
 def test_fail_closed(s):s.assertFalse(s.v['classification']['other_ell_or_momentum_classified']);s.assertEqual(s.v['correction_classes']['CAUSAL_RETARDED']['status'],'NO_CERTIFIED_MAP')
if __name__=='__main__':unittest.main()
