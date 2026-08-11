from __future__ import annotations

import copy
import unittest

from foundations.check_free_bv_energy2_primitive import check
from foundations.verify_free_bv_energy2_weak_base import (
    REPORT_PATH,
    RESULT_PATH,
    SOURCE_CERTIFICATE_PATH,
    load_json,
    verify,
)


class FreeBVEnergy2WeakBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = load_json(RESULT_PATH)
        cls.source = load_json(SOURCE_CERTIFICATE_PATH)
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def verify_mutation(self, *, result=None, source=None, report=None):
        errors, _ = verify(
            result=result if result is not None else copy.deepcopy(self.result),
            source_certificate=source if source is not None else copy.deepcopy(self.source),
            report_text=report if report is not None else self.report,
        )
        return errors

    def test_repository_certificate_passes(self) -> None:
        self.assertEqual(self.verify_mutation(), [])

    def test_primitive_checker_rejects_nonunit_pair(self) -> None:
        result = copy.deepcopy(self.result)
        result["module"]["contractible_pairs"][0]["q_coefficient"] = 2
        errors, _ = check(result)
        self.assertTrue(errors)

    def test_primitive_checker_rejects_overlap(self) -> None:
        result = copy.deepcopy(self.result)
        result["module"]["physical_slice"]["full_start"] = 179
        errors, _ = check(result)
        self.assertTrue(errors)

    def test_wrong_source_hash_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(self.verify_mutation(result=result))

    def test_necessity_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["claim_flags"]["necessity_or_reversal_proved"] = True
        self.assertTrue(self.verify_mutation(result=result))

    def test_weakest_base_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["foundational_classification"]["minimality_status"] = "PROVED"
        self.assertTrue(self.verify_mutation(result=result))

    def test_avoidance_relation_drift_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["avoidance_classification"]["relation"] = "UNKNOWN"
        self.assertTrue(self.verify_mutation(result=result))

    def test_matrix_digest_drift_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_matrix_digest"] = "f" * 64
        self.assertTrue(self.verify_mutation(result=result))

    def test_source_dimension_drift_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["levels"][0]["cohomology_dimension"] = 11
        self.assertTrue(self.verify_mutation(source=source))

    def test_lorentzian_promotion_is_rejected(self) -> None:
        result = copy.deepcopy(self.result)
        result["dependency_tags"] = ["LORENTZIAN-CAUSAL"]
        self.assertTrue(self.verify_mutation(result=result))

    def test_report_relation_drift_is_rejected(self) -> None:
        report = self.report.replace("AVOIDED_BY_REFORMULATION", "AVOIDED")
        self.assertTrue(self.verify_mutation(report=report))


if __name__ == "__main__":
    unittest.main()
