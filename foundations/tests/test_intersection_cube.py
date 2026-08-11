from __future__ import annotations
import copy,unittest
from foundations.check_intersection_cube import check
from foundations.verify_intersection_cube import REPORT,RESULT,load,verify

class IntersectionCubeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load(RESULT);cls.t=REPORT.read_text()
    def v(self,result=None,report=None):return verify(result=copy.deepcopy(self.r) if result is None else result,report=self.t if report is None else report)[0]
    def test_pass(self):self.assertEqual(self.v(),[])
    def test_axis_loss(self):
        r=copy.deepcopy(self.r);r["axes"][0]["keys"].pop();self.assertTrue(check(r)[0])
    def test_duplicate_coordinate(self):
        r=copy.deepcopy(self.r);r["cells"][1]=copy.deepcopy(r["cells"][0]);self.assertTrue(check(r)[0])
    def test_bad_coordinate(self):
        r=copy.deepcopy(self.r);r["cells"][0]["foundation"]="NO-SUCH-REGIME";self.assertTrue(check(r)[0])
    def test_bad_evidence(self):
        r=copy.deepcopy(self.r);r["cells"][0]["evidence"]=["NO-SUCH-SOURCE"];self.assertTrue(self.v(r))
    def test_digest(self):
        r=copy.deepcopy(self.r);r["independent_checker"]["expected_digest"]="0"*64;self.assertTrue(self.v(r))
    def test_all_cells_promotion(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["all_216_cells_claimed_assessed"]=True;self.assertTrue(self.v(r))
    def test_cell_completion_promotion(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["cell_status_means_complete_solution"]=True;self.assertTrue(self.v(r))
    def test_state_cell_promotion_removal(self):
        r=copy.deepcopy(self.r)
        cell=next(x for x in r["cells"] if x["foundation"]=="WEAK_CHOICE_ZF" and x["carrier"]=="KREIN_INDEFINITE" and x["obligation"]=="STATES_PROBABILITY")
        cell["status"]="PRIORITY_GAP"
        self.assertTrue(self.v(r))
    def test_report_gap_removed(self):self.assertTrue(self.v(report=self.t.replace("Priority gap","Unknown gap")))

if __name__=="__main__":unittest.main()
