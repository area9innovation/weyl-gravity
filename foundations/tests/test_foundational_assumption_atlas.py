from __future__ import annotations

import copy
import json
import unittest

from foundations.verify_foundational_assumption_atlas import (
    LEDGER_PATH,
    REPORT_PATH,
    RESULT_PATH,
    WORK_PATH,
    load_json,
    verify,
)


class FoundationalAssumptionAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = load_json(LEDGER_PATH)
        cls.result = load_json(RESULT_PATH)
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        cls.work = load_json(WORK_PATH)

    def run_mutation(self, *, ledger=None, result=None, report=None, work=None):
        errors, _ = verify(
            ledger=ledger if ledger is not None else copy.deepcopy(self.ledger),
            result=result if result is not None else copy.deepcopy(self.result),
            report_text=report if report is not None else self.report,
            work=work if work is not None else copy.deepcopy(self.work),
        )
        return errors

    def test_repository_atlas_passes(self) -> None:
        self.assertEqual(self.run_mutation(), [])

    def test_unknown_source_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["seed_findings"][0]["evidence_sources"] = ["not-a-source"]
        self.assertTrue(self.run_mutation(result=result))

    def test_lorentzian_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["dependency_tags"] = ["LORENTZIAN-CAUSAL"]
        self.assertTrue(self.run_mutation(result=result))

    def test_missing_boundary_is_rejected(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["entries"][0]["boundary"] = ""
        self.assertTrue(self.run_mutation(ledger=ledger))

    def test_claim_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["claim_flags"]["physical_postulate_implies_choice"] = True
        self.assertTrue(self.run_mutation(result=result))

    def test_report_status_drift_is_rejected(self) -> None:
        report = self.report.replace("AVOIDED_BY_REFORMULATION", "AVOIDED")
        self.assertTrue(self.run_mutation(report=report))

    def test_structured_files_have_canonical_json_syntax(self) -> None:
        for path in (LEDGER_PATH, RESULT_PATH, WORK_PATH):
            parsed = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
