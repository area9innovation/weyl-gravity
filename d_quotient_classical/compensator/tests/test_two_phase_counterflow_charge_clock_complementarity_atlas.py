import json,unittest
from d_quotient_classical.atlas.generate_two_phase_counterflow_charge_clock_complementarity_atlas_fragment import OUTPUT,build
class AtlasTests(unittest.TestCase):
 def test_current(self): self.assertEqual(json.loads(OUTPUT.read_text()),build())
 def test_separate_branches(self): self.assertNotEqual(build()["entries"][0]["descriptions"]["symplectic"],build()["entries"][1]["descriptions"]["symplectic"])
if __name__=="__main__":unittest.main()
