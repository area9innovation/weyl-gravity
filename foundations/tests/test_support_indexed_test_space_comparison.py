from __future__ import annotations
import json
import unittest
from foundations.verify_support_indexed_test_space_comparison import REPORT, RESULT, verify

class SupportIndexedTestSpaceComparisonTests(unittest.TestCase):
    def value(self)->dict: return json.loads(RESULT.read_text())
    def test_repository_result(self): self.assertEqual(verify()[0],[])
    def test_stage_mutation_fails(self):
        value=self.value(); value["fixtures"][2]["support_stage"][0]=[1,2]; self.assertTrue(verify(result=value)[0])
    def test_roundtrip_mutation_fails(self):
        value=self.value(); value["fixtures"][3]["sample_name"]["tagged_union"][0]=9; self.assertTrue(verify(result=value)[0])
    def test_inclusion_mutation_fails(self):
        value=self.value(); value["inclusion_checks"][7]["nested"]=False; self.assertTrue(verify(result=value)[0])
    def test_lf_promotion_fails(self):
        value=self.value(); value["claim_flags"]["full_lf_locally_convex_topology_identified"]=True; self.assertTrue(verify(result=value)[0])
    def test_h2_surjectivity_promotion_fails(self):
        value=self.value(); value["claim_flags"]["h2_embedding_surjective"]=True; self.assertTrue(verify(result=value)[0])
    def test_choice_promotion_fails(self):
        value=self.value(); value["claim_flags"]["choice_principle_used"]=True; self.assertTrue(verify(result=value)[0])
    def test_report_drift_fails(self): self.assertTrue(verify(report=REPORT.read_text()+"drift\n")[0])

if __name__=="__main__": unittest.main()
