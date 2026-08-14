from __future__ import annotations
import json,unittest
from foundations.verify_refined_intersection_cube_v14 import REPORT,RESULT,verify
class RefinedIntersectionCubeV14Tests(unittest.TestCase):
    def value(self)->dict:return json.loads(RESULT.read_text())
    def test_repository_result(self):self.assertEqual(verify()[0],[])
    def test_undeclared_cell_mutation_fails(self):
        value=self.value();value["cells"][0]["summary"]+=" drift";self.assertTrue(verify(result=value)[0])
    def test_status_mutation_fails(self):
        value=self.value();cell=next(c for c in value["cells"] if c.get("vertical_slice_revision",{}).get("previous_status")=="PIECES_ONLY");cell["status"]="PIECES_ONLY";self.assertTrue(verify(result=value)[0])
    def test_evidence_role_mutation_fails(self):
        value=self.value();cell=next(c for c in value["cells"] if "FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1" in c["evidence"]);cell["evidence_roles"]["FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1"]="SUPPORTING";self.assertTrue(verify(result=value)[0])
    def test_lf_promotion_fails(self):
        value=self.value();value["claim_flags"]["full_lf_test_topology_established"]=True;self.assertTrue(verify(result=value)[0])
    def test_weyl_green_promotion_fails(self):
        value=self.value();value["claim_flags"]["weyl_bv_green_established"]=True;self.assertTrue(verify(result=value)[0])
    def test_interface_mutation_fails(self):
        value=self.value();value["certified_interfaces"][0]["status"]="OPEN";self.assertTrue(verify(result=value)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
