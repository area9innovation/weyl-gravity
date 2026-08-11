from __future__ import annotations
import copy,unittest
from foundations.verify_completion_matrix_markdown import DEFAULT_OUTPUT,RESULT,load,verify

class CompletionMatrixMarkdownCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=load(RESULT);cls.t=DEFAULT_OUTPUT.read_text()
    def v(self,result=None,report=None):return verify(result=copy.deepcopy(self.r) if result is None else result,report=self.t if report is None else report)[0]
    def test_pass(self):self.assertEqual(self.v(),[])
    def test_input_pin(self):
        r=copy.deepcopy(self.r);r["inputs"][0]["sha256"]="0"*64;self.assertTrue(self.v(r))
    def test_generator_pin(self):
        r=copy.deepcopy(self.r);r["generator"]["sha256"]="0"*64;self.assertTrue(self.v(r))
    def test_output_pin(self):
        r=copy.deepcopy(self.r);r["generated_report"]["sha256"]="0"*64;self.assertTrue(self.v(r))
    def test_dimensions(self):
        r=copy.deepcopy(self.r);r["dimensions"]["coverage_cells"]=95;self.assertTrue(self.v(r))
    def test_pin_counts(self):
        r=copy.deepcopy(self.r);r["dimensions"]["literature_pin_counts"]["METADATA_ONLY"]=0;self.assertTrue(self.v(r))
    def test_literature_promotion(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["literature_complete"]=True;self.assertTrue(self.v(r))
    def test_plain_language_legend_removed(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["plain_language_legend_rendered"]=False;self.assertTrue(self.v(r))
    def test_cube_removed(self):
        r=copy.deepcopy(self.r);r["claim_flags"]["intersection_cube_rendered"]=False;self.assertTrue(self.v(r))
    def test_cube_count_inflated(self):
        r=copy.deepcopy(self.r);r["dimensions"]["cube_assessed_cells"]=216;self.assertTrue(self.v(r))
    def test_stale_report(self):self.assertTrue(self.v(report=self.t.replace("25 records","24 records",1)))

if __name__=="__main__":unittest.main()
