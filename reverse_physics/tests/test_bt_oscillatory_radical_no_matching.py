"""Falsification tests for the BT oscillatory radical no-matching theorem."""
import json,os,subprocess,sys,tempfile,unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json");PROD=os.path.join(ROOT,"reverse_physics","bt_oscillatory_radical_no_matching.py");VER=os.path.join(ROOT,"reverse_physics","verify_bt_oscillatory_radical_no_matching.py")
class TestNoMatching(unittest.TestCase):
 def execute(self,cmd):return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
 def test_producer(self):
  r=self.execute([sys.executable,PROD,"--check"]);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_verifier(self):
  r=self.execute([sys.executable,VER]);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_positive_charge_mutation_rejected(self):
  with open(CERT,encoding="utf-8") as source:p=json.load(source)
  p["charge_ledger"]["q_b_Upsilon_dagger"]=1
  with tempfile.NamedTemporaryFile("w",suffix=".json",encoding="utf-8") as h:
   json.dump(p,h);h.flush();r=self.execute([sys.executable,VER,"--verify",h.name]);self.assertNotEqual(r.returncode,0);self.assertIn("[FAIL] published_charge_assignments",r.stdout)
 def test_probability_open(self):
  with open(CERT,encoding="utf-8") as source:p=json.load(source)
  self.assertEqual(p["disposition"]["physical_nlo_probability"],"NOT_ESTABLISHED")
if __name__=="__main__":unittest.main()
