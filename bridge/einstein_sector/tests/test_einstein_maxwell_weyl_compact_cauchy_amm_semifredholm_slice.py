from __future__ import annotations
import copy,json,unittest,jsonschema
from bridge.einstein_sector.einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice import build_certificate,DEFAULT_OUTPUT,SCHEMA_PATH
from bridge.einstein_sector.verify_einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice import verify_certificate
class AMMSemifredholmTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):c.p=build_certificate();c.s=json.loads(SCHEMA_PATH.read_text())
 def test_schema(s):jsonschema.Draft202012Validator(s.s).validate(s.p)
 def test_split(s):s.assertIn("bounded isomorphism",s.p["split_semifredholm_theorem"]["bounded_inverse"])
 def test_five(s):s.assertEqual(s.p["kuranishi_normal_form"]["second_order_tangent_cone"].count("mu_"),5)
 def test_positive_boundary(s):s.assertTrue(s.p["classification"]["sobolev_second_order_tangent_cone"])
 def test_negative_boundary(s):s.assertFalse(s.p["classification"]["full_fixed_group_AMM_hypotheses"])
 def test_structure_witness(s):s.assertEqual(s.p["gauge_slice_audit"]["structure_function_witness"]["metric_fixture_2"]["shift_coefficient"],"-1/4")
 def test_no_fredholm(s):s.assertIn("TT",s.p["split_semifredholm_theorem"]["physical_kernel"])
 def test_mutation(s):s.assertTrue(s.p["mutation_controls"]["omit_H"]["false_cone_has_extra_directions"])
 def test_schema_rejects_promotion(s):
  q=copy.deepcopy(s.p);q["classification"]["full_fixed_group_AMM_hypotheses"]=True
  with s.assertRaises(jsonschema.ValidationError):jsonschema.Draft202012Validator(s.s).validate(q)
 def test_payload_verifier(s):s.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()),s.p);verify_certificate()
if __name__=="__main__":unittest.main()
