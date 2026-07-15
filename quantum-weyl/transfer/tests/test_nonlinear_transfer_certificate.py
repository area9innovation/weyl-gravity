from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = TRANSFER_ROOT / "nonlinear_transfer_certificate.py"
SPEC = importlib.util.spec_from_file_location("nonlinear_transfer_certificate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CERTIFICATE)


class NonlinearTransferCertificateTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_scientific_questions_fail_closed(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(
            certificate["result_state"],
            "ENGINE_READY_HT1_RESIDUAL_AND_LOCAL_SEEDS_COMPUTED_INPUT_BLOCKED",
        )
        self.assertEqual(
            certificate["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        )
        self.assertTrue(certificate["input_blockers"])
        self.assertTrue(
            all(
                item["status"] != "COMPUTED"
                for item in certificate["question_ledger"]
            )
        )
        self.assertEqual(
            certificate["programme_stages"][-1]["status"],
            "BLOCKED_PENDING_QME_RESTORED",
        )
        self.assertIn(
            "COMPLETE_MINIMAL_CONTRACTION",
            certificate["programme_stages"][1]["status"],
        )
        self.assertIn(
            "TWO_DIRECT_LOCAL_SEEDS",
            certificate["question_ledger"][0]["status"],
        )
        d_question = next(
            item
            for item in certificate["question_ledger"]
            if item["question_id"] == "D_quotient_interaction_stability"
        )
        self.assertIn("SELECTED_RESIDUAL_Q2_D_DERIVATION_VERIFIED", d_question["status"])
        self.assertIn("SCOPED_D_GAUGE_COMPLETE_34_ROW_MINIMAL_CONTRACTION", d_question["status"])
        self.assertIn("RETAINED_Q1", d_question["status"])
        self.assertIn("ARITY_ONE_PBW_BACKEND_READY", d_question["status"])
        self.assertIn("Q2_D_ADMISSIBILITY_INPUT_BLOCKED", d_question["status"])
        self.assertIn("ND2_ROUTER_AND_ND3_SOLVER_READY", d_question["status"])

    def test_nd2_engine_is_registered_without_promoting_the_physical_claim(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertTrue(
            any("ND2 canonical" in claim for claim in certificate["scope"]["established"])
        )
        self.assertIn(
            "nd2_arity_two_cartan_engine_sha256",
            certificate["provenance"],
        )
        self.assertIn("nd2_physical_run_contract_sha256", certificate["provenance"])
        self.assertIn("berger_clock_nonlinear_import_sha256", certificate["provenance"])
        self.assertIn("berger_clock_partial_sdr_import_sha256", certificate["provenance"])
        self.assertIn(
            "berger_retained_minimal_q1_import_sha256", certificate["provenance"]
        )
        self.assertIn(
            "berger_pbw_operator_backend_sha256", certificate["provenance"]
        )
        self.assertIn(
            "berger_minimal_34_contraction_import_sha256",
            certificate["provenance"],
        )
        self.assertIn("berger_total_D_disposition_sha256", certificate["provenance"])
        self.assertIn("nd3_arity_three_cartan_engine_sha256", certificate["provenance"])
        self.assertTrue(
            any(
                "complete conformal-gravity q2" in claim
                for claim in certificate["scope"]["not_established"]
            )
        )
        self.assertTrue(
            any(
                "PBW-module-valued Cartan solver" in claim
                for claim in certificate["scope"]["not_established"]
            )
        )

    def test_missing_nonlinear_and_contraction_exports_are_named(self) -> None:
        blocked = {
            item["export_id"]
            for item in CERTIFICATE.build_certificate()["input_blockers"]
        }
        self.assertIn("local_classical_bv_differential_q0", blocked)
        self.assertIn("support_local_classical_bv_q2", blocked)
        self.assertIn("local_D_action_on_bv_generators", blocked)
        self.assertNotIn("classical_projection_pi_cl", blocked)
        self.assertNotIn("classical_inclusion_iota_cl", blocked)
        self.assertNotIn("classical_homotopy_s_cl", blocked)
        rows = {
            item["export_id"]: item
            for item in CERTIFICATE.build_certificate()["input_blockers"]
        }
        self.assertEqual(rows["local_classical_bv_differential_q0"]["status"], "INCOMPLETE")
        self.assertIn(
            "34-row minimal Berger unary differential",
            rows["local_classical_bv_differential_q0"]["reason"],
        )


if __name__ == "__main__":
    unittest.main()
