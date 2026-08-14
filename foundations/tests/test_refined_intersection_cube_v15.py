from __future__ import annotations
import json,unittest
from foundations.verify_refined_intersection_cube_v15 import REPORT,RESULT,verify
class RefinedIntersectionCubeV15Tests(unittest.TestCase):
    def value(self)->dict:return json.loads(RESULT.read_text())
    def test_repository_result(self):self.assertEqual(verify()[0],[])
    def test_undeclared_mutation_fails(self):
        v=self.value();v["cells"][0]["summary"]+=" drift";self.assertTrue(verify(result=v)[0])
    def test_status_promotion_fails(self):
        v=self.value();c=next(x for x in v["cells"] if x.get("biwave_delta_revision") and x["obligation"]=="GAUGE_BV_COHOMOLOGY");c["status"]="LOCAL_RESULT";self.assertTrue(verify(result=v)[0])
    def test_role_mutation_fails(self):
        v=self.value();c=next(x for x in v["cells"] if "FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1" in x["evidence"]);c["evidence_roles"]["FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1"]="SUPPORTING";self.assertTrue(verify(result=v)[0])
    def test_weyl_promotion_fails(self):
        v=self.value();v["claim_flags"]["weyl_bv_green_established"]=True;self.assertTrue(verify(result=v)[0])
    def test_classical_gate_promotion_fails(self):
        v=self.value();v["claim_flags"]["classical_import_gate_passed"]=True;self.assertTrue(verify(result=v)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
