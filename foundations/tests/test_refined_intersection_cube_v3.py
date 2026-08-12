import json,unittest
from foundations.verify_refined_intersection_cube_v3 import REPORT,RESULT,verify
class RefinedIntersectionCubeV3Tests(unittest.TestCase):
    def test_repository_result(self): self.assertEqual([],verify()[0])
    def test_status_mutation_fails(self):
        v=json.loads(RESULT.read_text()); v["cells"][0]["status"]="NOT_MAPPED"; self.assertTrue(verify(result=v)[0])
    def test_migration_mutation_fails(self):
        v=json.loads(RESULT.read_text()); v["cells"][0]["migration_status"]="REVIEWED_NO_TRANSFER"; self.assertTrue(verify(result=v)[0])
    def test_report_drift_fails(self): self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])
if __name__=="__main__": unittest.main()
