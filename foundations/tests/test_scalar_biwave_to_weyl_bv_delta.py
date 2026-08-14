from __future__ import annotations
import json,unittest
from foundations.verify_scalar_biwave_to_weyl_bv_delta import REPORT,RESULT,verify
class ScalarBiwaveToWeylBVDeltaTests(unittest.TestCase):
    def value(self)->dict:return json.loads(RESULT.read_text())
    def test_repository_result(self):self.assertEqual(verify()[0],[])
    def test_status_mutation_fails(self):
        v=self.value();v["dependency_delta"][3]["status"]="PROVED_SCALAR";self.assertTrue(verify(result=v)[0])
    def test_classical_gate_mutation_fails(self):
        v=self.value();v["classical_import_gate"]["status"]="PASS";self.assertTrue(verify(result=v)[0])
    def test_lifecycle_mutation_fails(self):
        v=self.value();v["lifecycle_gate"]["states_reached_for_full_weyl_bv"]=["LORENTZIAN_CERTIFIED"];self.assertTrue(verify(result=v)[0])
    def test_propagator_promotion_fails(self):
        v=self.value();v["claim_flags"]["full_weyl_bv_propagator_constructed"]=True;self.assertTrue(verify(result=v)[0])
    def test_hadamard_promotion_fails(self):
        v=self.value();v["claim_flags"]["brst_compatible_hadamard_state_constructed"]=True;self.assertTrue(verify(result=v)[0])
    def test_no_go_broadening_fails(self):
        v=self.value();v["dependency_delta"][12]["status"]="FORBIDDEN_TRANSFER";self.assertTrue(verify(result=v)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
