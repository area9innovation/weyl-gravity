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
            "CAUSAL_CHAIN_AND_D_CARTAN_IMPORTED_THROUGH_ARITY_TWO_Q3_AND_HADAMARD_OPEN",
        )
        self.assertEqual(
            certificate["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
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
        self.assertIn(
            "RESTRICTED_PPWAVE_BRANCH_BLOCK",
            certificate["question_ledger"][0]["status"],
        )
        self.assertIn(
            "TRANSFERRED_TO_RETAINED_26_ROW_Q2_26",
            certificate["question_ledger"][0]["status"],
        )
        branch_question = next(
            item
            for item in certificate["question_ledger"]
            if item["question_id"] == "einstein_extra_weyl_branch_mixing"
        )
        self.assertIn("ALIGNED_PPWAVE_ELL2_ZERO", branch_question["status"])
        self.assertIn("NONALIGNED_FULL_BV_PENDING", branch_question["status"])
        amplitude_question = next(
            item
            for item in certificate["question_ledger"]
            if item["question_id"] == "einstein_projection_amplitude_fixture"
        )
        self.assertIn("REFERENCE_PARITY_PAIR_EXACT", amplitude_question["status"])
        self.assertIn(
            "SETTING_DEFECT_NORMALIZATION_GATES_READY", amplitude_question["status"]
        )
        self.assertIn("SETTING_MATCHED_PROJECTION_PENDING", amplitude_question["status"])
        d_question = next(
            item
            for item in certificate["question_ledger"]
            if item["question_id"] == "D_quotient_interaction_stability"
        )
        self.assertIn("BARE_LOCAL_UNARY_OBSTRUCTION_BYPASSED", d_question["status"])
        self.assertIn("26_AND_54_ROW_GREEN_HOMOTOPIES", d_question["status"])
        self.assertIn("CYCLIC_D_CARTAN_THROUGH_ARITY_TWO_IMPORTED", d_question["status"])
        self.assertIn("ARITY_THREE_OPEN", d_question["status"])
        self.assertEqual(
            d_question["next_certificate"],
            "BERGER_ARITY_THREE_D_CARTAN_OR_HADAMARD",
        )

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
            "berger_54_row_local_D_import_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_54_row_q2_arrival_readiness_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_54_row_q2_replay_engine_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_support_local_q2_import_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_support_local_q2_scientific_replay_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_unary_D_Cartan_obstruction_import_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "berger_retained_26_q2_transfer_sha256",
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
        self.assertIn(
            "ppwave_branch_transfer_import_sha256",
            certificate["provenance"],
        )
        self.assertIn(
            "einstein_projection_MHV_fixture_sha256",
            certificate["provenance"],
        )
        self.assertIn("berger_total_D_disposition_sha256", certificate["provenance"])
        self.assertIn("nd3_arity_three_cartan_engine_sha256", certificate["provenance"])
        self.assertIn("berger_causal_chain_v2_import_sha256", certificate["provenance"])
        self.assertIn("berger_hadamard_construction_gate_sha256", certificate["provenance"])
        hadamard_stage = next(
            item for item in certificate["programme_stages"] if item["stage"] == "HTH"
        )
        self.assertEqual(
            hadamard_stage["status"],
            "CAUSAL_COMMUTATOR_READY_BASE_WAVE_HADAMARD_PARAMETRIX_NEXT",
        )
        self.assertTrue(
            any(
                "complete conformal-gravity q3" in claim
                for claim in certificate["scope"]["not_established"]
            )
        )
        self.assertTrue(
            any(
                "26 retained and all 54 gauge-fixed rows" in claim
                for claim in certificate["scope"]["established"]
            )
        )

    def test_missing_nonlinear_and_contraction_exports_are_named(self) -> None:
        blocked = {
            item["export_id"]
            for item in CERTIFICATE.build_certificate()["input_blockers"]
        }
        self.assertNotIn("local_classical_bv_differential_q0", blocked)
        self.assertNotIn("support_local_classical_bv_q2", blocked)
        self.assertNotIn("local_D_action_on_bv_generators", blocked)
        self.assertNotIn("classical_projection_pi_cl", blocked)
        self.assertNotIn("classical_inclusion_iota_cl", blocked)
        self.assertNotIn("classical_homotopy_s_cl", blocked)
        self.assertNotIn("cyclic_pairing", blocked)


if __name__ == "__main__":
    unittest.main()
