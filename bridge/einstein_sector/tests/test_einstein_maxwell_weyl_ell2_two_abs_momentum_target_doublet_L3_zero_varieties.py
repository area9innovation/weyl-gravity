import json,unittest
from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties import CERT,verify
class TargetDoubletL3Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.v=json.loads(CERT.read_text())
 def test_replay(self): verify()
 def test_two_fibres(self): self.assertEqual([x["candidate_index"] for x in self.v["decompositions"]],[1,16])
 def test_irreducible_dimension_twelve(self): self.assertTrue(all(x["zero_variety"]["dimension_over_C"]==12 and x["zero_variety"]["irreducible_components_over_C"]==1 for x in self.v["decompositions"]))
 def test_tangent_cone_open(self): self.assertFalse(self.v["classification"]["complete_two_fibre_tangent_cone_classified"])
if __name__=="__main__": unittest.main()
