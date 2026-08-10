import json,os,subprocess,sys,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));C=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json");P=os.path.join(ROOT,"reverse_physics","bt_perturbative_coisometry_rigidity.py");V=os.path.join(ROOT,"reverse_physics","verify_bt_perturbative_coisometry_rigidity.py")
class T(unittest.TestCase):
 def x(self,a):return subprocess.run(a,cwd=ROOT,text=True,capture_output=True)
 def test_producer(self):self.assertEqual(self.x([sys.executable,P,"--check"]).returncode,0)
 def test_verifier(self):self.assertEqual(self.x([sys.executable,V]).returncode,0)
 def test_CCR_mutation(self):
  with open(C,encoding="utf-8") as h:p=json.load(h)
  p["free_CCR_gate"]["rows"][0]["a_cross_commutator"]={"numerator":3,"denominator":1}
  with tempfile.NamedTemporaryFile("w",suffix=".json") as h:
   json.dump(p,h);h.flush();r=self.x([sys.executable,V,"--verify",h.name]);self.assertNotEqual(r.returncode,0)
 def test_prior_scope_restricted(self):
  with open(C,encoding="utf-8") as h:p=json.load(h)
  self.assertEqual(p["supersession"]["status"],"SCOPE_RESTRICTED_TO_NONPERTURBATIVE_OR_DISCONNECTED_BRANCHES")
if __name__=="__main__":unittest.main()
