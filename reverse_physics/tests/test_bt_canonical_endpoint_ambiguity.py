import json,os,subprocess,sys,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));C=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_CANONICAL_ENDPOINT_AMBIGUITY_V1.json");P=os.path.join(ROOT,"reverse_physics","bt_canonical_endpoint_ambiguity.py");V=os.path.join(ROOT,"reverse_physics","verify_bt_canonical_endpoint_ambiguity.py")
class T(unittest.TestCase):
 def x(self,a):return subprocess.run(a,cwd=ROOT,text=True,capture_output=True)
 def test_producer(self):self.assertEqual(self.x([sys.executable,P,"--check"]).returncode,0)
 def test_verifier(self):self.assertEqual(self.x([sys.executable,V]).returncode,0)
 def mutate(self,fn):
  with open(C,encoding="utf-8") as h:p=json.load(h)
  fn(p)
  with tempfile.NamedTemporaryFile("w",suffix=".json") as h:
   json.dump(p,h);h.flush();return self.x([sys.executable,V,"--verify",h.name])
 def test_norm_mutation(self):self.assertNotEqual(self.mutate(lambda p:p["canonical_family"]["rows"][1].update(norm_square={"numerator":2,"denominator":1})).returncode,0)
 def test_target_mutation(self):self.assertNotEqual(self.mutate(lambda p:p["target_comparison"].update(status="DERIVED")).returncode,0)
 def test_boundary_mutation(self):self.assertNotEqual(self.mutate(lambda p:p["disposition"].update(physical_nlo_probability="ESTABLISHED")).returncode,0)
if __name__=="__main__":unittest.main()
