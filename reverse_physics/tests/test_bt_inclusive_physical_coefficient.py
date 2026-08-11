import json,os,subprocess,sys,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));C=os.path.join(ROOT,"reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1.json");P=os.path.join(ROOT,"reverse_physics/bt_inclusive_physical_coefficient.py");V=os.path.join(ROOT,"reverse_physics/verify_bt_inclusive_physical_coefficient.py")
class InclusivePhysicalCoefficientTests(unittest.TestCase):
 def cmd(self,a):return subprocess.run(a,cwd=ROOT,capture_output=True,text=True)
 def mut(self,f):
  with open(C) as h:x=json.load(h)
  f(x)
  with tempfile.NamedTemporaryFile("w",suffix=".json") as h:json.dump(x,h);h.flush();return self.cmd([sys.executable,V,"--verify",h.name])
 def test_producer(self):self.assertEqual(self.cmd([sys.executable,P,"--check"]).returncode,0)
 def test_verifier(self):self.assertEqual(self.cmd([sys.executable,V]).returncode,0)
 def test_block_mutation(self):self.assertNotEqual(self.mut(lambda x:x["orthogonal_detector_lemma"]["fixtures"][0]["Born_order_two"][0][0].update(numerator=9)).returncode,0)
 def test_kernel_mutation(self):self.assertNotEqual(self.mut(lambda x:x["complete_signed_kernel"]["fixtures"][0]["raised_trace"].update(numerator=1)).returncode,0)
 def test_detector_mutation(self):self.assertNotEqual(self.mut(lambda x:x["inclusive_detector_limit"]["finite_cell_masks"][0]["coefficient"].update(numerator=1)).returncode,0)
 def test_nlo_promotion(self):self.assertNotEqual(self.mut(lambda x:x["physical_coefficient"].update(complete_NLO_probability="COMPUTED")).returncode,0)
 def test_eq19_promotion(self):self.assertNotEqual(self.mut(lambda x:x["disposition"].update(Eq19_all_orders="PROVED")).returncode,0)
if __name__=="__main__":unittest.main()
