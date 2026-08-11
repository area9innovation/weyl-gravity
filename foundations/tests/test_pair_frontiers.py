from __future__ import annotations

import copy
import unittest

from foundations.analyze_pair_frontiers import generated
from foundations.check_pair_frontiers import check
from foundations.verify_pair_frontiers import CUBE, REPORT, REQUEST, RESULT, load, verify


class PairFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.cube = load(CUBE)
        cls.report = REPORT.read_text()
        cls.request = load(REQUEST)

    def checked(self, result=None, report=None, request=None):
        return verify(
            result=copy.deepcopy(self.result) if result is None else result,
            cube=copy.deepcopy(self.cube),
            report=self.report if report is None else report,
            request=copy.deepcopy(self.request) if request is None else request,
        )[0]

    def test_passes(self):
        self.assertEqual(self.checked(), [])

    def test_all_pair_products_are_present(self):
        self.assertEqual(len(self.result["projections"]), 108)
        self.assertEqual(len({item["id"] for item in self.result["projections"]}), 108)

    def test_generated_artifacts_are_current(self):
        result_text, report_text = generated()
        self.assertEqual(RESULT.read_text(), result_text)
        self.assertEqual(REPORT.read_text(), report_text)

    def test_score_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["projections"][0]["bridge_score"] += 1
        self.assertTrue(check(result, self.cube)[0])

    def test_projection_loss_fails(self):
        result = copy.deepcopy(self.result)
        result["projections"].pop()
        self.assertTrue(check(result, self.cube)[0])

    def test_pair_family_partition_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["pair_families"][0]["projection_ids"].pop()
        self.assertTrue(check(result, self.cube)[0])

    def test_rank_reordering_fails(self):
        result = copy.deepcopy(self.result)
        result["ranked_frontier_ids"][0:2] = reversed(result["ranked_frontier_ids"][0:2])
        self.assertTrue(check(result, self.cube)[0])

    def test_unmapped_cannot_be_recommended(self):
        result = copy.deepcopy(self.result)
        result["recommended_cells"][0]["status"] = "NOT_MAPPED"
        self.assertTrue(self.checked(result=result))

    def test_ranking_cannot_be_promoted_to_evidence(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["ranking_is_scientific_evidence"] = True
        self.assertTrue(self.checked(result=result))

    def test_forge_registration_cannot_be_implied(self):
        result = copy.deepcopy(self.result)
        result["forge_projection"]["state"] = "REGISTERED"
        self.assertTrue(self.checked(result=result))

    def test_report_keeps_unseeded_gap_distinction(self):
        self.assertTrue(self.checked(report=self.report.replace("0 — important but unseeded", "0 — easy gap")))

    def test_request_forbids_absence_claims(self):
        request = copy.deepcopy(self.request)
        request["body"]["forbid"] = request["body"]["forbid"].replace("No node or absence claim for an unassessed coordinate", "")
        self.assertTrue(self.checked(request=request))


if __name__ == "__main__":
    unittest.main()
