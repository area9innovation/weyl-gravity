from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_einstein_sourced_defect_preflight


class CompensatedEinsteinSourcedDefectPreflightTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        compensated_einstein_sourced_defect_preflight.verify_certificate()

    def test_linearized_tensor_factorization_is_gauge_covariant(self) -> None:
        result = compensated_einstein_sourced_defect_preflight.build_certificate()
        theorem = result["linearized_tensor_theorem"]
        self.assertIn("B1_mn=Q(G1)_mn", theorem["linearized_bach_factorization"])
        self.assertIn("G1(delta_xi h_hat)=0", theorem["identities"])
        self.assertIn("tr(B1)=0", theorem["identities"])

    def test_source_ward_identities_include_compensator_source(self) -> None:
        result = compensated_einstein_sourced_defect_preflight.build_certificate()
        ward = result["source_ward_theorem"]
        self.assertEqual(
            ward["weyl_ward_identity"],
            "tr(T)-phi J_phi=0; on phi=v this is tr(T)-v J_phi=0",
        )
        self.assertIn("traceful metric source", ward["metric_only_source_warning"])

    def test_same_source_compatibility_is_qt_zero(self) -> None:
        result = compensated_einstein_sourced_defect_preflight.build_certificate()
        source = result["source_compatibility_theorem"]
        self.assertEqual(source["necessary_and_sufficient_same_source_condition"], "Q(T)=0")
        self.assertIn("Q(T)=(1/2)T!=0", source["conserved_counterexample"]["properties"])
        self.assertTrue(
            result["claim_flags"]["arbitrary_same_source_einstein_truncation_refuted"]
        )

    def test_reduced_obstruction_matches_previous_source_audit(self) -> None:
        result = compensated_einstein_sourced_defect_preflight.build_certificate()
        reduced = result["source_compatibility_theorem"]["reduced_tt_check"]
        self.assertEqual(reduced["compatibility"], "D J=0")
        self.assertEqual(
            reduced["defect_equation"], "(D+M2)delta=-(D J)/M2"
        )

    def test_dressed_source_is_not_same_source_equivalence(self) -> None:
        result = compensated_einstein_sourced_defect_preflight.build_certificate()
        dressed = result["source_compatibility_theorem"]["dressed_source_alternative"]
        self.assertIn("T_EW=T_E", dressed["formula"])
        self.assertIn("not same-source", dressed["classification"])

    def test_fixed_external_source_is_affine_not_bv(self) -> None:
        result = compensated_einstein_sourced_defect_preflight.build_certificate()
        classification = result["affine_vs_bv_classification"]
        self.assertIn("affine translate", classification["external_source_geometry"])
        self.assertFalse(result["claim_flags"]["fixed_external_source_locus_is_bv_subcomplex"])
        self.assertFalse(result["claim_flags"]["matter_inclusive_bv_complex_constructed"])

    def test_forged_generic_source_closure_is_rejected(self) -> None:
        payload = compensated_einstein_sourced_defect_preflight.build_certificate()
        payload["claim_flags"][
            "arbitrary_ward_compatible_external_source_preserves_einstein_sector"
        ] = True
        with self.assertRaises(
            compensated_einstein_sourced_defect_preflight.CompensatedEinsteinSourcedDefectPreflightError
        ):
            compensated_einstein_sourced_defect_preflight._validate_contract(payload)

    def test_forged_bv_completion_is_rejected(self) -> None:
        payload = compensated_einstein_sourced_defect_preflight.build_certificate()
        payload["claim_flags"]["compensated_quadratic_bv_complex_certified"] = True
        with self.assertRaises(
            compensated_einstein_sourced_defect_preflight.CompensatedEinsteinSourcedDefectPreflightError
        ):
            compensated_einstein_sourced_defect_preflight._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = compensated_einstein_sourced_defect_preflight.build_certificate()
        payload["verdict"] = "GENERIC_SOURCE_CLOSURE"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(
                compensated_einstein_sourced_defect_preflight.CompensatedEinsteinSourcedDefectPreflightError
            ):
                compensated_einstein_sourced_defect_preflight.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
