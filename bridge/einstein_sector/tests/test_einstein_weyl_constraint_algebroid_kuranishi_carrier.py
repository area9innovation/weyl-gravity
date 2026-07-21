import copy,json,unittest
import jsonschema
from bridge.einstein_sector.einstein_weyl_constraint_algebroid_kuranishi_carrier import DEFAULT_OUTPUT,build
from bridge.einstein_sector.verify_einstein_weyl_constraint_algebroid_kuranishi_carrier import verify_payload
class CarrierTests(unittest.TestCase):
 def setUp(self):self.p=json.loads(DEFAULT_OUTPUT.read_text())
 def test_independent(self):self.assertEqual(build(),self.p);verify_payload(self.p)
 def test_fixed_group_mutation(self):
  q=copy.deepcopy(self.p);q["classification"]["phase_dependent_bracket_retained"]=False
  with self.assertRaises(jsonschema.ValidationError):verify_payload(q,False)
 def test_linear_zero_mutation(self):
  q=copy.deepcopy(self.p);q["classification"]["plain_linear_zero_subspace_substituted"]=True
  with self.assertRaises(jsonschema.ValidationError):verify_payload(q,False)
 def test_false_projection(self):
  q=copy.deepcopy(self.p);q["classification"]["linear_cofiber_projects_derived_zero_fibre"]=True
  with self.assertRaises(jsonschema.ValidationError):verify_payload(q,False)
 def test_no_sobolev_promotion(self):
  q=copy.deepcopy(self.p);q["classification"]["sobolev_Einstein_Weyl_derived_exact_sequence"]=True
  with self.assertRaises(jsonschema.ValidationError):verify_payload(q,False)
if __name__=="__main__":unittest.main()
