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
            "COMPLETE_54_ROW_UNARY_CONTRACTION",
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
        self.assertIn("ALL_INTEGER_WEIGHT_HOMOGENEOUS_NONZERO_SOURCE_CARTAN", d_question["status"])
        self.assertIn("EXACT_NONZERO_PRIMITIVE", d_question["status"])
        self.assertIn("FINITE_TRUNCATIONS_OBSTRUCTED", d_question["status"])
        self.assertIn("FULL_4D_SUPPORT_LOCAL_54_ROW_INPUT_BLOCKED", d_question["status"])

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
        self.assertIn(
            "berger_gauge_fixed_nonminimal_import_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_first_arity_two_cartan_verdict_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_nonzero_weight_closure_no_go_import_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_all_weight_arity_two_cartan_import_sha256",
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
                "complete 54-row arity-two Cartan" in claim
                for claim in certificate["scope"]["not_established"]
            )
        )

    def test_missing_nonlinear_and_contraction_exports_are_named(self) -> None:
        blocked = {
            item["export_id"]
            for item in CERTIFICATE.build_certificate()["input_blockers"]
        }
        self.assertNotIn("local_classical_bv_differential_q0", blocked)
        self.assertIn("support_local_classical_bv_q2", blocked)
        self.assertIn("local_D_action_on_bv_generators", blocked)
        self.assertNotIn("classical_projection_pi_cl", blocked)
        self.assertNotIn("classical_inclusion_iota_cl", blocked)
        self.assertNotIn("classical_homotopy_s_cl", blocked)
        self.assertNotIn("cyclic_pairing", blocked)


if __name__ == "__main__":
    unittest.main()
