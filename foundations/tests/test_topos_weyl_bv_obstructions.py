from __future__ import annotations
import copy,unittest
from foundations.check_topos_weyl_bv_obstructions import check
from foundations.verify_topos_weyl_bv_obstructions import REPORT,RESULT,load,verify

class ToposWeylBVObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load(RESULT);cls.t=REPORT.read_text()
    def v(self,result=None,report=None):return verify(result=copy.deepcopy(self.r) if result is None else result,report=self.t if report is None else report)[0]
    def test_pass(self):self.assertEqual(self.v(),[])
    def test_digest(self):
        r=copy.deepcopy(self.r);r["independent_checker"]["expected_digest"]="0"*64;self.assertTrue(self.v(r))
    def test_glossary_loss(self):
        r=copy.deepcopy(self.r);r["glossary"].pop();self.assertTrue(check(r)[0])
    def test_glossary_collapse(self):
        r=copy.deepcopy(self.r);r["glossary"][1]["id"]="LOGIC";self.assertTrue(check(r)[0])
    def test_missing_prerequisite(self):
        r=copy.deepcopy(self.r);r["obstructions"][3]["requires"]=["NO-SUCH-NODE"];self.assertTrue(check(r)[0])
    def test_cycle(self):
        r=copy.deepcopy(self.r);r["obstructions"][0]["requires"]=["O12-EXTERNAL-COMPARISON"];self.assertTrue(check(r)[0])
    def test_candidate_promotion(self):
        r=copy.deepcopy(self.r);r["lowest_risk_candidate"]["constructed_internally"]=True;self.assertTrue(self.v(r))
    def test_internal_bv_promotion(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["internal_weyl_bv_constructed"]=True;self.assertTrue(self.v(r))
    def test_lorentzian_promotion(self):
        r=copy.deepcopy(self.r);r["dependency_tags"]=["LORENTZIAN-CAUSAL"];self.assertTrue(self.v(r))
    def test_source_pin(self):
        r=copy.deepcopy(self.r);r["source_dependencies"][0]["pinned_pdf_sha256"]="f"*64;self.assertTrue(self.v(r))
    def test_local_provenance(self):
        r=copy.deepcopy(self.r);r["provenance"]["local_inputs"][0]["sha256"]="f"*64;self.assertTrue(self.v(r))
    def test_report_boundary(self):self.assertTrue(self.v(report=self.t.replace("LORENTZIAN-CAUSAL","CAUSAL")))

if __name__=="__main__":unittest.main()
