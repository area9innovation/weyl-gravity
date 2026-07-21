from __future__ import annotations
import copy,json,unittest
import jsonschema
from bridge.einstein_sector.einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate import ATLAS_OUTPUT,DEFAULT_OUTPUT,SCHEMA_PATH,build_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate import IndependentCompactCauchyVerificationError,verify_certificate
class CompactCauchyConstraintFredholmGateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=build_certificate();cls.s=json.loads(SCHEMA_PATH.read_text())
 def test_schema_imports(self):jsonschema.Draft202012Validator(self.s).validate(self.p);self.assertEqual(len(self.p["provenance"]["imported_artifacts"]),6)
 def test_counts(self):self.assertEqual((self.p["action_derived_constraint_ledger"]["local_phase_space_rank"],self.p["action_derived_constraint_ledger"]["first_class_count"],self.p["action_derived_constraint_ledger"]["physical_phase_space_rank"]),(30,7,16))
 def test_raw_right_elliptic(self):self.assertEqual((self.p["douglis_nirenberg_symbol"]["raw_rank"],self.p["douglis_nirenberg_symbol"]["raw_surjective_minor"]["determinant"]),(7,"-16"))
 def test_gauge_complete(self):self.assertEqual(self.p["douglis_nirenberg_symbol"]["gauge_on_gauge_orbit_determinant"],"-16")
 def test_physical_kernel(self):self.assertEqual((self.p["douglis_nirenberg_symbol"]["combined_rank"],self.p["douglis_nirenberg_symbol"]["symbol_kernel_dimension"]),(14,16))
 def test_not_fredholm(self):self.assertTrue(self.p["functional_analytic_verdict"]["raw_constraint_range_closed_on_compact_slice"]);self.assertFalse(self.p["functional_analytic_verdict"]["combined_operator_fredholm"])
 def test_exact_five_open(self):self.assertEqual(self.p["adjoint_cokernel_ledger"]["exactly_five"],"OPEN")
 def test_mutation(self):self.assertEqual(self.p["douglis_nirenberg_symbol"]["mutation_control"]["mutated_rank"],15)
 def test_schema_rejects_promotion(self):
  q=copy.deepcopy(self.p);q["classification"]["fredholm_constraint_plus_gauge_operator"]=True
  with self.assertRaises(jsonschema.ValidationError):jsonschema.Draft202012Validator(self.s).validate(q)
 def test_payload_and_verifier(self):self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()),self.p);verify_certificate()
 def test_atlas_hash_mutation(self):
  q=copy.deepcopy(json.loads(ATLAS_OUTPUT.read_text()));q["entries"][0]["evidence"][0]["sha256"]="0"*64;t=ATLAS_OUTPUT.with_suffix(".mutation-test.json")
  try:
   t.write_text(json.dumps(q))
   with self.assertRaises(IndependentCompactCauchyVerificationError):verify_certificate(DEFAULT_OUTPUT,t)
  finally:t.unlink(missing_ok=True)
if __name__=="__main__":unittest.main()
