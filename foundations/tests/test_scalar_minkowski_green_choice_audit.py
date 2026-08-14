from __future__ import annotations
import json,unittest
from foundations.verify_scalar_minkowski_green_choice_audit import REPORT,RESULT,verify
class ScalarMinkowskiGreenChoiceAuditTests(unittest.TestCase):
    def value(self)->dict:return json.loads(RESULT.read_text())
    def test_repository_result(self):self.assertEqual(verify()[0],[])
    def test_pg_mutation_fails(self):
        value=self.value();value["fixtures"][1]["retarded_interior"]["wave_operator_multiplier"]=[2,1];self.assertTrue(verify(result=value)[0])
    def test_gp_mutation_fails(self):
        value=self.value();value["fixtures"][2]["compact_test"]["retarded_G_P_identity"]=False;self.assertTrue(verify(result=value)[0])
    def test_duality_mutation_fails(self):
        value=self.value();value["fixtures"][3]["adjoint_pairing"]["right"]=[1,1];self.assertTrue(verify(result=value)[0])
    def test_support_mutation_fails(self):
        value=self.value();value["support_samples"][0]["in_declared_causal_support"]=True;self.assertTrue(verify(result=value)[0])
    def test_weyl_promotion_fails(self):
        value=self.value();value["claim_flags"]["weyl_bv_propagator_constructed"]=True;self.assertTrue(verify(result=value)[0])
    def test_hadamard_promotion_fails(self):
        value=self.value();value["claim_flags"]["hadamard_state_constructed"]=True;self.assertTrue(verify(result=value)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
