from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import berger_einstein_incidence as incidence


class BergerEinsteinIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = incidence.build_certificate()

    def test_canonical_certificate_is_current(self) -> None:
        self.assertEqual(
            json.loads(incidence.DEFAULT_OUTPUT.read_text(encoding="utf-8")),
            self.result,
        )

    def test_all_three_background_incidence_tests_are_refuted(self) -> None:
        tests = self.result["incidence_tests"]
        self.assertTrue(all(row["status"].startswith("REFUTED") for row in tests.values()))
        self.assertEqual(
            tests["einstein_with_same_clock_stress"]["proportionality_minor_00_11"],
            "q*(q - 1)/(8*a**6)",
        )

    def test_branch_classification_is_fail_closed(self) -> None:
        classification = self.result["classification"]
        self.assertTrue(classification["berger_background_is_genuine_non_einstein_weyl_matter_branch"])
        self.assertFalse(classification["same_base_point_linearized_einstein_clock_complex_exists"])
        self.assertFalse(classification["retained_berger_q1_is_einstein_tangent_subcomplex"])
        self.assertEqual(self.result["tangent_gate"]["status"], "NOT_APPLICABLE_AT_THIS_BASE_POINT")

    def test_no_causal_or_matter_lift_promotion(self) -> None:
        flags = self.result["claim_flags"]
        self.assertFalse(flags["berger_tangent_einstein_embedding_constructed"])
        self.assertFalse(flags["berger_matter_bv_to_flat_source_ward_lift_constructed"])
        self.assertFalse(flags["lorentzian_causal_claim"])

    def test_altered_certificate_is_rejected(self) -> None:
        payload = json.loads(json.dumps(self.result))
        payload["classification"]["retained_berger_q1_is_einstein_tangent_subcomplex"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(incidence.BergerEinsteinIncidenceError):
                incidence.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
