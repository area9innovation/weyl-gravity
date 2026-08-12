import json,unittest
from foundations.verify_coded_polygonal_wave_rca0 import REPORT,RESULT,verify
class CodedPolygonalWaveRCA0Tests(unittest.TestCase):
    def test_repository_result(self):self.assertEqual([],verify()[0])
    def test_energy_mutation_fails(self):
        r=json.loads(RESULT.read_text());r["fixtures"][0]["total_energy"]=[99,1];self.assertTrue(verify(result=r)[0])
    def test_base_mutation_fails(self):
        r=json.loads(RESULT.read_text());r["formal_proof"][4]["base"]="WKL_0";self.assertTrue(verify(result=r)[0])
    def test_causal_promotion_fails(self):
        r=json.loads(RESULT.read_text());r["claim_flags"]["causal_green_operator_constructed"]=True;self.assertTrue(verify(result=r)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
