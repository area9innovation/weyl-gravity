from __future__ import annotations
import copy,unittest
from foundations.check_ranked_opportunity_completion import check
from foundations.verify_ranked_opportunity_completion import REPORT,RESULT,load,verify

class RankedOpportunityCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load(RESULT);cls.t=REPORT.read_text()
    def v(self,result=None,ranking=None,report=None,children=False):return verify(result=copy.deepcopy(self.r) if result is None else result,ranking=ranking,report=self.t if report is None else report,run_child_verifiers=children)[0]
    def test_pass_with_child_verifiers(self):self.assertEqual(self.v(children=True),[])
    def test_rank_loss(self):
        r=copy.deepcopy(self.r);r["entries"].pop();self.assertTrue(check(r)[0])
    def test_rank_swap(self):
        r=copy.deepcopy(self.r);r["entries"][0]["rank"]=2;self.assertTrue(check(r)[0])
    def test_incomplete(self):
        r=copy.deepcopy(self.r);r["entries"][0]["first_artifact_status"]="OPEN";self.assertTrue(check(r)[0])
    def test_unexpected_sharing(self):
        r=copy.deepcopy(self.r);r["entries"][3]["artifact"]=copy.deepcopy(r["entries"][0]["artifact"]);self.assertTrue(check(r)[0])
    def test_digest(self):
        r=copy.deepcopy(self.r);r["independent_checker"]["expected_digest"]="0"*64;self.assertTrue(self.v(r))
    def test_artifact_hash(self):
        r=copy.deepcopy(self.r);r["entries"][0]["artifact"]["sha256"]="f"*64;self.assertTrue(self.v(r))
    def test_ranking_text(self):
        r=copy.deepcopy(self.r);r["entries"][0]["first_artifact"]="shorter";self.assertTrue(self.v(r))
    def test_programme_promotion(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["all_deeper_programmes_complete"]=True;self.assertTrue(self.v(r))
    def test_lorentzian_promotion(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["lorentzian_qme_proved"]=True;self.assertTrue(self.v(r))
    def test_aggregate_inflation(self):
        r=copy.deepcopy(self.r);r["aggregate"]["distinct_artifact_count"]=9;self.assertTrue(check(r)[0])
    def test_report_boundary(self):self.assertTrue(self.v(report=self.t.replace("every row retains","rows omit")))

if __name__=="__main__":unittest.main()
