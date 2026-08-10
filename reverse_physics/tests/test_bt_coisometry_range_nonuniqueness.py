import json,os,subprocess,sys,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_COISOMETRY_RANGE_NONUNIQUENESS_V1.json");P=os.path.join(ROOT,"reverse_physics","bt_coisometry_range_nonuniqueness.py");V=os.path.join(ROOT,"reverse_physics","verify_bt_coisometry_range_nonuniqueness.py")
class T(unittest.TestCase):
 def x(self,a):return subprocess.run(a,cwd=ROOT,text=True,capture_output=True)
 def test_producer(self):self.assertEqual(self.x([sys.executable,P,"--check"]).returncode,0)
 def test_verifier(self):self.assertEqual(self.x([sys.executable,V]).returncode,0)
 def test_mutation(self):
  with open(CERT,encoding="utf-8") as h:p=json.load(h)
  p["finite_krein_model"]["rows"][1]["pushforward_trace"]={"numerator":1,"denominator":48}
  with tempfile.NamedTemporaryFile("w",suffix=".json") as h:
   json.dump(p,h);h.flush();r=self.x([sys.executable,V,"--verify",h.name]);self.assertNotEqual(r.returncode,0)
 def test_open(self):
  with open(CERT,encoding="utf-8") as h:p=json.load(h)
  self.assertEqual(p["disposition"]["physical_nlo_probability"],"NOT_ESTABLISHED")
if __name__=="__main__":unittest.main()
