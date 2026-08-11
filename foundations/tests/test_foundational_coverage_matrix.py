from __future__ import annotations

import copy
import json
import unittest

from foundations.verify_foundational_coverage_matrix import (
    REPORT_PATH,
    RESULT_PATH,
    SEED_LEDGER_PATH,
    SUPPLEMENT_PATH,
    load_json,
    verify,
)


class FoundationalCoverageMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = load_json(SEED_LEDGER_PATH)
        cls.supplement = load_json(SUPPLEMENT_PATH)
        cls.result = load_json(RESULT_PATH)
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def run_mutation(self, *, seed=None, supplement=None, result=None, report=None):
        errors, _ = verify(
            seed=seed if seed is not None else copy.deepcopy(self.seed),
            supplement=supplement if supplement is not None else copy.deepcopy(self.supplement),
            result=result if result is not None else copy.deepcopy(self.result),
            report_text=report if report is not None else self.report,
        )
        return errors

    def test_repository_matrix_passes(self) -> None:
        self.assertEqual(self.run_mutation(), [])

    def test_unknown_source_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["attempts"][0]["representative_sources"] = ["unknown-source"]
        self.assertTrue(self.run_mutation(result=result))

    def test_six_axis_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        for cell in result["attempts"][0]["coverage"].values():
            cell["status"] = "DIRECT"
        self.assertTrue(self.run_mutation(result=result))

    def test_score_arithmetic_drift_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["opportunities"][0]["scores"]["priority_score"] -= 1
        self.assertTrue(self.run_mutation(result=result))

    def test_choice_free_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["claim_flags"]["choice_free_krein_completion"] = True
        self.assertTrue(self.run_mutation(result=result))

    def test_metadata_source_without_unresolved_control_is_rejected(self) -> None:
        supplement = copy.deepcopy(self.supplement)
        supplement["unresolved"] = [
            item for item in supplement["unresolved"] if "metadata-only" not in item.lower()
        ]
        self.assertTrue(self.run_mutation(supplement=supplement))

    def test_missing_stop_condition_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["opportunities"][1]["stop_condition"] = ""
        self.assertTrue(self.run_mutation(result=result))

    def test_lorentzian_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["dependency_tags"] = ["LORENTZIAN-CAUSAL"]
        self.assertTrue(self.run_mutation(result=result))

    def test_report_boundary_drift_is_rejected(self) -> None:
        report = self.report.replace("AVOIDED_BY_REFORMULATION", "AVOIDED")
        self.assertTrue(self.run_mutation(report=report))

    def test_changed_json_files_are_objects(self) -> None:
        for path in (SUPPLEMENT_PATH, RESULT_PATH):
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
