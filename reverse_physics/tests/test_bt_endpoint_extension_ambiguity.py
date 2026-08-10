"""Falsification tests for the BT endpoint-extension classification."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json")
PROD=os.path.join(ROOT,"reverse_physics","bt_endpoint_extension_ambiguity.py")
VERIFY=os.path.join(ROOT,"reverse_physics","verify_bt_endpoint_extension_ambiguity.py")
class TestEndpoint(unittest.TestCase):
 def test_producer(self):
  r=subprocess.run([sys.executable,PROD,"--check"],cwd=ROOT,text=True,capture_output=True); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_verifier(self):
  r=subprocess.run([sys.executable,VERIFY],cwd=ROOT,text=True,capture_output=True); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def mutate(self,key,value):
  with open(CERT,encoding="utf-8") as h: p=json.load(h)
  p["target_test"][key]=value
  with tempfile.NamedTemporaryFile("w",suffix=".json",encoding="utf-8") as h:
   json.dump(p,h); h.flush(); return subprocess.run([sys.executable,VERIFY,"--verify",h.name],cwd=ROOT,text=True,capture_output=True)
 def test_target_fit_mutation_rejected(self):
  r=self.mutate("coefficient_that_fits_target_from_plus_base",{"numerator":1,"denominator":48}); self.assertNotEqual(r.returncode,0)
 def test_probability_boundary(self):
  with open(CERT,encoding="utf-8") as h: p=json.load(h)
  self.assertEqual(p["disposition"]["physical_nlo_probability"],"NOT_ESTABLISHED")
  self.assertEqual(p["disposition"]["one_over_48_from_current_data"],"UNDERDETERMINED")
if __name__=="__main__": unittest.main()
