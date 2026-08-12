import json,unittest
from foundations.verify_cylinder_wave_strength_ladder_v2 import REPORT,RESULT,verify
class CylinderWaveStrengthLadderV2Tests(unittest.TestCase):
    def test_repository_result(self):self.assertEqual([],verify()[0])
    def test_l2_demotion_fails(self):
        r=json.loads(RESULT.read_text());r["ladder"][2]["status"]="FORMALIZATION_TARGET";self.assertTrue(verify(result=r)[0])
    def test_causal_promotion_fails(self):
        r=json.loads(RESULT.read_text());r["claim_flags"]["causal_green_operator_constructed"]=True;self.assertTrue(verify(result=r)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
