import json,os,subprocess,sys,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));C=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json");P=os.path.join(ROOT,"reverse_physics","bt_full_off_resonant_projector.py");V=os.path.join(ROOT,"reverse_physics","verify_bt_full_off_resonant_projector.py")
class T(unittest.TestCase):
 def x(self,a):return subprocess.run(a,cwd=ROOT,text=True,capture_output=True)
 def test_producer(self):self.assertEqual(self.x([sys.executable,P,"--check"]).returncode,0)
 def test_verifier(self):self.assertEqual(self.x([sys.executable,V]).returncode,0)
 def mutate(self,fn):
  with open(C,encoding="utf-8") as h:p=json.load(h)
  fn(p)
  with tempfile.NamedTemporaryFile("w",suffix=".json") as h:
   json.dump(p,h);h.flush();return self.x([sys.executable,V,"--verify",h.name])
 def test_sample_mutation(self):self.assertNotEqual(self.mutate(lambda p:p["off_resonant_kernel"]["samples"][0]["gram_cross"]["real"].update(numerator=-1)).returncode,0)
 def test_residue_mutation(self):self.assertNotEqual(self.mutate(lambda p:p["soft_blowup"].update(scaling_degree=0)).returncode,0)
 def test_claim_mutation(self):self.assertNotEqual(self.mutate(lambda p:p["disposition"].update(one_over_48="DERIVED")).returncode,0)
if __name__=="__main__":unittest.main()
