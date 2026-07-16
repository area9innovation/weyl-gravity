import json
import unittest

from local_bv.algebra import canonical_sha256
from local_bv.basis_gap import (
    TERMINAL_RESOLUTIONS,
    basis_gap_graph_bundle,
    basis_gap_report,
)
from local_bv.basis_gap_certificate import (
    GRAPH_BUNDLE_DIR,
    GRAPH_BUNDLE_SCHEMA_PATH,
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
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
                by_slice["H14_AFN0_EVEN"][
                    "coarse_grading_signature_count"
                ],
                by_slice["H14_AFN0_EVEN"][
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
            by_slice["H14_AFN0_EVEN"][
                "pending_resolution_count"
            ],
            0,
        )
        self.assertEqual(
            by_slice["H14_AFN0_EVEN"]["top_form_signature_resolution_status"],
            "COMPLETE",
        )
        self.assertEqual(
            by_slice["H14_AFN0_EVEN"]["forward_reverse_span_agreement"],
            "VERIFIED",
        )
        self.assertEqual(
            by_slice["H04_AFN0_ODD"]["top_form_signature_resolution_status"],
            "COMPLETE",
        )
        self.assertEqual(
            by_slice["H14_AFN0_ODD"]["top_form_signature_resolution_status"],
            "COMPLETE",
        )
        self.assertEqual(
            by_slice["H14_AFN0_ODD"]["forward_reverse_span_agreement"],
            "VERIFIED",
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
        self.assertEqual(
            report["total_complex_gates"][
                "LOWER_FORM_COCYCLE_BASIS_EXHAUSTIVE"
            ],
            "IN_PROGRESS_GRADING_EXHAUSTIVE_CANDIDATE_CARRIERS_COMPLETE",
        )
        self.assertEqual(
            report["lower_form_carrier_inventory"]["counts"]["all_carriers"],
            64,
        )
        self.assertEqual(
            report["ambient_lower_form_signature_inventory"]["totals"],
            {
                "coarse_signature_count": 2480,
                "refined_signature_count": 720,
                "rejected_signature_count": 1760,
            },
        )
        self.assertEqual(
            report["ambient_lower_form_signature_inventory"][
                "tensor_graph_realizability"
            ],
            "COMPLETE_FACTORED",
        )
        self.assertEqual(
            report["ambient_lower_form_signature_inventory"][
                "factor_profile_count"
            ],
            1224,
        )

    def test_raw_matching_does_not_promote_tensor_realizability(self) -> None:
        records = [
            record
            for slice_ in basis_gap_report()["slices"]
            for record in slice_["records"]
        ]
        unresolved = [
            record for record in records
            if not record["candidate_ids"]
            and record["refined_grading_status"] == "REFINED_ADMISSIBLE"
            and record["resolution"] not in {
                "GENERATED_NONZERO", "IDENTICALLY_ZERO_BY_SYMMETRY"
            }
        ]
        self.assertTrue(unresolved)
        self.assertTrue(
            all(
                record["tensor_realizability"]
                == "UNDECIDED_PENDING_BIANCHI_AND_DIMENSION_IDENTITIES"
                for record in unresolved
            )
        )
        total_derivatives = [
            record for record in unresolved
            if record["resolution"] == "TOTAL_DERIVATIVE_ONLY"
        ]
        self.assertTrue(total_derivatives)
        self.assertTrue(
            all(
                record["graphwise_divergence_status"]
                == "VERIFIED_EVERY_RAW_GRAPH"
                for record in total_derivatives
            )
        )

    def test_schema_and_checked_in_certificate(self) -> None:
        certificate = build_certificate()
        self.assertFalse(
            validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        )
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), certificate)
        bundle = basis_gap_graph_bundle()
        self.assertFalse(
            validate_instance(
                bundle, json.loads(GRAPH_BUNDLE_SCHEMA_PATH.read_text())
            )
        )
        checked_bundle = json.loads(
            (GRAPH_BUNDLE_DIR / f"{bundle['bundle_hash']}.json").read_text()
        )
        self.assertEqual(checked_bundle, bundle)
        payload = {key: value for key, value in bundle.items() if key != "bundle_hash"}
        self.assertEqual(bundle["bundle_hash"], canonical_sha256(payload))
        for artifact in bundle["artifacts"]:
            artifact_payload = {
                key: value for key, value in artifact.items()
                if key != "artifact_hash"
            }
            self.assertEqual(
                artifact["artifact_hash"], canonical_sha256(artifact_payload)
            )


if __name__ == "__main__":
    unittest.main()
