import json,unittest
from foundations.verify_coded_wave_frontier_v2 import LEDGER,REPORT,RESULT,verify
class CodedWaveFrontierV2Tests(unittest.TestCase):
    def test_repository_result(self):self.assertEqual([],verify()[0])
    def test_action_mutation_fails(self):
        r=json.loads(RESULT.read_text());r["cell_actions"][0]["old"]="NOT_MAPPED";self.assertTrue(verify(result=r)[0])
    def test_framework_collapse_fails(self):
        r=json.loads(RESULT.read_text());r["framework_distinctions"][0]["framework"]="COMPUTABLE_TTE";self.assertTrue(verify(result=r)[0])
    def test_pin_mutation_fails(self):
        l=json.loads(LEDGER.read_text());l["entries"][1]["artifact"]["sha256"]="0"*64;self.assertTrue(verify(ledger=l)[0])
    def test_report_drift_fails(self):self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__":unittest.main()
