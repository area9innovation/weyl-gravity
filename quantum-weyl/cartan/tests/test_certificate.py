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

    def test_physical_ledgers_fail_closed(self) -> None:
        certificate = build_certificate()
        self.assertEqual(certificate["classical_commit"], "UNFROZEN")
        self.assertTrue(
            all(
                item["status"] == "UNDEFINED_ANALYTICALLY"
                for item in certificate["candidate_sector_ledger"]
            )
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

    def test_source_and_dependency_hashes_reproduce(self) -> None:
        certificate = build_certificate()
        for relative, expected in certificate["provenance"]["source_manifest"].items():
            self.assertEqual(
                hashlib.sha256((PACKAGE_ROOT / relative).read_bytes()).hexdigest(),
                expected,
            )
        self.assertEqual(len(certificate["provenance"]["dependency_manifest"]), 7)

    def test_classical_sector_split_is_imported_without_quantum_promotion(self) -> None:
        vacuum = build_certificate()["setting_ledger"][0]
        self.assertEqual(
            vacuum["D_charge"],
            "SECTOR_DEPENDENT_CLASSICALLY_P_LIN_CHARGED_P_TAUB0_GAUGE",
        )
        self.assertEqual(
            vacuum["classical_input_status"],
            "CERTIFIED_HASH_PINNED_NOT_A_QUANTUM_VERDICT",
        )
        self.assertEqual(vacuum["verdict"], "ANALYTIC_FRAMEWORK_MISSING")

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
