from __future__ import annotations

import hashlib
import json
import unittest

from cartan.certificate import (
    OUTPUT_PATH,
    PACKAGE_ROOT,
    SCHEMA_PATH,
    build_certificate,
)


class CartanDefectCertificateTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, build_certificate())

    def test_exact_mechanics_cover_all_decision_statuses_except_analytic(self) -> None:
        certificate = build_certificate()
        self.assertEqual(
            [item["classification"] for item in certificate["mechanics_fixtures"]],
            ["ZERO", "EXACT_REMOVABLE", "NONTRIVIAL_ANOMALY"],
        )
        exact = certificate["mechanics_fixtures"][1]
        nontrivial = certificate["mechanics_fixtures"][2]
        self.assertIsNotNone(exact["primitive"])
        self.assertIsNotNone(nontrivial["dual_witness"])

    def test_sourced_consistency_is_retained_when_qme_source_is_nonzero(self) -> None:
        fixture = build_certificate()["sourced_consistency_fixture"]
        self.assertEqual(fixture["qme_source_status"], "NONZERO")
        self.assertEqual(fixture["defect_closure_status"], "SOURCED_NONZERO")
        self.assertEqual(fixture["sourced_identity"], "VERIFIED")
        for field in ("degree", "shape", "entries"):
            self.assertEqual(
                fixture["consistency_left"][field],
                fixture["consistency_right"][field],
            )

    def test_admissibility_can_reject_an_ambient_primitive(self) -> None:
        fixture = build_certificate()["admissibility_fixture"]
        self.assertEqual(fixture["ambient_classification"], "EXACT_REMOVABLE")
        self.assertEqual(
            fixture["admissible_classification"], "NONTRIVIAL_ANOMALY"
        )
        self.assertEqual(
            fixture["admissible_complex_manifest"]["subcomplex_status"],
            "VERIFIED",
        )

    def test_scheme_covariance_preserves_class_and_rejects_illegal_shift(self) -> None:
        fixture = build_certificate()["scheme_covariance_fixture"]
        self.assertEqual(fixture["baseline_representative_status"], "ZERO")
        self.assertEqual(
            fixture["uncompensated_representative_status"], "EXACT_REMOVABLE"
        )
        self.assertEqual(
            fixture["quotient_class_relation"],
            "SAME_TRIVIAL_CLASS_BY_EXPLICIT_Q_EXACT_SHIFT",
        )
        self.assertEqual(fixture["inadmissible_scheme_shift_status"], "REJECTED")
        self.assertEqual(fixture["scheme_covariance_status"], "VERIFIED")

    def test_physical_ledgers_fail_closed(self) -> None:
        certificate = build_certificate()
        self.assertEqual(certificate["classical_commit"], "UNFROZEN")
        self.assertTrue(
            all(
                item["analytic_operator_status"] == "UNDEFINED_ANALYTICALLY"
                for item in certificate["candidate_sector_ledger"]
            )
        )
        self.assertTrue(
            all(
                item["coefficient_status"] == "NOT_COMPUTED"
                for item in certificate["candidate_sector_ledger"]
            )
        )
        self.assertEqual(
            certificate["candidate_sector_ledger"][0][
                "algebraic_classification_status"
            ],
            "IN_PROGRESS",
        )
        self.assertTrue(
            all(
                item["verdict"] == "ANALYTIC_FRAMEWORK_MISSING"
                for item in certificate["setting_ledger"]
            )
        )
        self.assertEqual(
            certificate["lifecycle_gates"]["RESIDUAL_TRANSFERRED"],
            "BLOCKED_PENDING_QME_RESTORED",
        )
        self.assertEqual(
            certificate["input_gates"]["Euler_intrinsic_descent"],
            "NONTRIVIAL_COMPLETE_LOCAL_ALGEBRAIC",
        )
        self.assertEqual(
            certificate["input_gates"]["AFN0_local_relative_basis"],
            "IN_PROGRESS",
        )

    def test_source_and_dependency_hashes_reproduce(self) -> None:
        certificate = build_certificate()
        for relative, expected in certificate["provenance"]["source_manifest"].items():
            self.assertEqual(
                hashlib.sha256((PACKAGE_ROOT / relative).read_bytes()).hexdigest(),
                expected,
            )
        self.assertEqual(len(certificate["provenance"]["dependency_manifest"]), 6)
        self.assertNotIn(
            "commission", certificate["provenance"]["dependency_manifest"]
        )

    def test_classical_sector_split_is_imported_without_quantum_promotion(self) -> None:
        certificate = build_certificate()
        vacuum = certificate["setting_ledger"][0]
        self.assertEqual(
            vacuum["D_charge"],
            "SECTOR_DEPENDENT_CLASSICALLY_P_LIN_CHARGED_P_TAUB0_GAUGE",
        )
        self.assertEqual(
            vacuum["classical_input_status"],
            "CERTIFIED_HASH_PINNED_NOT_A_QUANTUM_VERDICT",
        )
        self.assertEqual(vacuum["verdict"], "ANALYTIC_FRAMEWORK_MISSING")
        self.assertEqual(
            certificate["classical_D_import"]["semantic_validation"],
            "REQUIRED_SETTINGS_VERIFIED_ADDITIONAL_SETTINGS_ENUMERATED_NOT_CONSUMED",
        )
        self.assertEqual(
            certificate["classical_D_import"]["sha256"],
            certificate["provenance"]["dependency_manifest"][
                "classical_D_quotient_status"
            ],
        )

    def test_schema_contract_is_fail_closed(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        certificate = build_certificate()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            set(schema["required"]),
            set(certificate),
        )
        self.assertEqual(
            schema["properties"]["allowed_candidate_statuses"]["const"],
            certificate["allowed_candidate_statuses"],
        )


if __name__ == "__main__":
    unittest.main()
