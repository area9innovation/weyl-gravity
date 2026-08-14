from __future__ import annotations
import json,unittest
from foundations.verify_scalar_minkowski_biwave_green import REPORT,RESULT,verify
class ScalarMinkowskiBiwaveGreenTests(unittest.TestCase):
    def value(self)->dict:return json.loads(RESULT.read_text())
    def test_repository_result(self):self.assertEqual(verify()[0],[])
    def test_right_inverse_mutation_fails(self):
        v=self.value();v["fixtures"][1]["retarded_interior"]["biwave_operator_multiplier"]=[2,1];self.assertTrue(verify(result=v)[0])
    def test_left_inverse_mutation_fails(self):
        v=self.value();v["fixtures"][2]["compact_test"]["u_factor_coefficients"][0]=[1,1];self.assertTrue(verify(result=v)[0])
    def test_duality_mutation_fails(self):
        v=self.value();v["fixtures"][3]["adjoint_pairing"]["right"]=[1,1];self.assertTrue(verify(result=v)[0])
    def test_energy_mutation_fails(self):
        v=self.value();v["fixtures"][0]["finite_horizon_energy"]["biwave_energy_bound"]=[3,1];self.assertTrue(verify(result=v)[0])
    def test_support_mutation_fails(self):
        v=self.value();v["support_samples"][0]["in_declared_causal_support"]=True;self.assertTrue(verify(result=v)[0])
    def test_bv_promotion_fails(self):
        v=self.value();v["claim_flags"]["weyl_bv_propagator_constructed"]=True;self.assertTrue(verify(result=v)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
