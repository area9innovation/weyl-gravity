import json
import unittest

from local_bv.basis_gap import TERMINAL_RESOLUTIONS, basis_gap_report
from local_bv.basis_gap_certificate import OUTPUT_PATH, SCHEMA_PATH, build_certificate
from local_bv.schema_validation import validate_instance


class BasisGapTests(unittest.TestCase):
    def test_counts_preserve_coarse_and_refined_stages(self) -> None:
        by_slice = {row["slice"]: row for row in basis_gap_report()["slices"]}
        self.assertEqual(
            (
                by_slice["H04_AFN0_EVEN"]["coarse_grading_signature_count"],
                by_slice["H04_AFN0_EVEN"]["refined_grading_signature_count"],
            ),
            (3, 2),
        )
        self.assertEqual(
            (
                by_slice["H14_AFN0_EVEN_WITHOUT_EULER"][
                    "coarse_grading_signature_count"
                ],
                by_slice["H14_AFN0_EVEN_WITHOUT_EULER"][
                    "refined_grading_signature_count"
                ],
            ),
            (9, 5),
        )
        self.assertEqual(
            by_slice["H04_AFN0_EVEN"]["top_form_signature_resolution_status"],
            "COMPLETE",
        )
        self.assertEqual(
            by_slice["H14_AFN0_EVEN_WITHOUT_EULER"][
                "pending_resolution_count"
            ],
            2,
        )
        self.assertEqual(
            by_slice["H04_AFN0_ODD"]["top_form_signature_resolution_status"],
            "COMPLETE",
        )

    def test_terminal_and_pending_proofs_fail_closed(self) -> None:
        records = [
            record
            for slice_ in basis_gap_report()["slices"]
            for record in slice_["records"]
        ]
        for record in records:
            if record["resolution"] in TERMINAL_RESOLUTIONS:
                self.assertRegex(record["proof_hash"], r"^[0-9a-f]{64}$")
                self.assertIsNotNone(record["terminal_witness"])
            else:
                self.assertEqual(record["resolution"], "PENDING")
                self.assertIsNone(record["proof_hash"])
                self.assertIsNone(record["terminal_witness"])

    def test_diff_sector_is_separate_and_total_complex_stays_open(self) -> None:
        report = basis_gap_report()
        self.assertEqual(
            [
                (row["coarse_signature_count"], row["refined_signature_count"])
                for row in report["diff_top_form_ledgers"]
            ],
            [(12, 7), (12, 7)],
        )
        self.assertEqual(
            report["total_complex_gates"]["TOTAL_COMPLEX_EXHAUSTIVE"],
            "NOT_COMPUTED",
        )

    def test_schema_and_checked_in_certificate(self) -> None:
        certificate = build_certificate()
        self.assertFalse(
            validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        )
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), certificate)


if __name__ == "__main__":
    unittest.main()
