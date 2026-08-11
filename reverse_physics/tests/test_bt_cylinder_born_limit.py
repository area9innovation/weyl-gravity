import json, os, subprocess, sys, tempfile, unittest
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT=os.path.join(ROOT,"reverse_physics/certificates/REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1.json")
P=os.path.join(ROOT,"reverse_physics/bt_cylinder_born_limit.py"); V=os.path.join(ROOT,"reverse_physics/verify_bt_cylinder_born_limit.py")
class CylinderBornLimitTests(unittest.TestCase):
    def cmd(self,a):return subprocess.run(a,cwd=ROOT,capture_output=True,text=True)
    def mutate(self,f):
        with open(CERT) as h:x=json.load(h)
        f(x)
        with tempfile.NamedTemporaryFile("w",suffix=".json") as h:json.dump(x,h);h.flush();return self.cmd([sys.executable,V,"--verify",h.name])
    def test_producer(self):self.assertEqual(self.cmd([sys.executable,P,"--check"]).returncode,0)
    def test_verifier(self):self.assertEqual(self.cmd([sys.executable,V]).returncode,0)
    def test_weight_mutation(self):self.assertNotEqual(self.mutate(lambda x:x["finite_local_process"]["output_rows"][0]["weight"].update(numerator=8)).returncode,0)
    def test_spectator_mutation(self):self.assertNotEqual(self.mutate(lambda x:x["spectator_extension"]["projection_trace"].update(numerator=2)).returncode,0)
    def test_volume_mutation(self):self.assertNotEqual(self.mutate(lambda x:x["directed_limit"]["volume_rows"][4]["positive_trace_norm"].update(numerator=1)).returncode,0)
    def test_physical_mutation(self):self.assertNotEqual(self.mutate(lambda x:x["disposition"].update(physical_full_probability="ESTABLISHED")).returncode,0)
    def test_eq19_mutation(self):self.assertNotEqual(self.mutate(lambda x:x["disposition"].update(Eq19_all_orders="PROVED")).returncode,0)
if __name__=="__main__":unittest.main()
