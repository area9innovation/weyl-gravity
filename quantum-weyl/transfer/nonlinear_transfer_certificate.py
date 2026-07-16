"""Emit the fail-closed nonlinear homological-transfer bootstrap certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = TRANSFER_ROOT.parent
SNAPSHOT_PATH = QUANTUM_ROOT / "classical_import" / "snapshots" / "bootstrap-v1.json"
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json"
BERGER_IMPORT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_CLOCK_NONLINEAR_IMPORT.json"
TOTAL_D_DISPOSITION_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_TOTAL_D_DISPOSITION.json"
)
BERGER_PARTIAL_SDR_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_CLOCK_PARTIAL_SDR_IMPORT.json"
)
BERGER_RETAINED_Q1_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_RETAINED_MINIMAL_Q1_IMPORT.json"
)
BERGER_PBW_BACKEND_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_PBW_OPERATOR_BACKEND.json"
)
BERGER_MINIMAL_CONTRACTION_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_MINIMAL_34_CONTRACTION_IMPORT.json"
)
BERGER_GAUGE_FIXED_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json"
)
BERGER_54_ROW_LOCAL_D_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_54_ROW_LOCAL_D_IMPORT.json"
)
BERGER_REDUCED_CARTAN_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_FIRST_ARITY_TWO_CARTAN_VERDICT.json"
)
BERGER_NONZERO_WEIGHT_NO_GO_PATH = (
    TRANSFER_ROOT
    / "certificates"
    / "BERGER_NONZERO_WEIGHT_CLOSURE_NO_GO_IMPORT.json"
)
BERGER_ALL_WEIGHT_CARTAN_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_ALL_WEIGHT_ARITY_TWO_CARTAN_IMPORT.json"
)
PPWAVE_BRANCH_TRANSFER_PATH = (
    TRANSFER_ROOT / "certificates" / "PPWAVE_BRANCH_TRANSFERRED_ELL2.json"
)
EINSTEIN_MHV_FIXTURE_PATH = (
    TRANSFER_ROOT / "certificates" / "EINSTEIN_PROJECTION_MHV_FIXTURE.json"
)


REQUIRED_EXPORTS = (
    "field_ghost_antifield_dictionary",
    "field_gradings",
    "local_classical_bv_differential_q0",
    "support_local_classical_bv_q2",
    "local_D_action_on_bv_generators",
    "classical_inclusion_iota_cl",
    "classical_projection_pi_cl",
    "classical_homotopy_s_cl",
    "cyclic_pairing",
    "normalized_weyl_square_representatives",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "homological_transfer.py",
        "d_derivation_defect.py",
        "d_derivation_certificate.py",
        "arity_two_cartan.py",
        "block_sparse_arity_two.py",
        "evaluator_registry.py",
        "local_expression_ast.py",
        "support_local_q2_consumer.py",
        "nd2_arity_two_certificate.py",
        "nd2_physical_run.py",
        "nd2_physical_run_certificate.py",
        "berger_clock_import.py",
        "berger_clock_import_certificate.py",
        "berger_clock_sdr_import.py",
        "berger_clock_sdr_import_certificate.py",
        "berger_retained_q1_import.py",
        "berger_retained_q1_import_certificate.py",
        "operator_backend_registry.py",
        "berger_pbw_backend.py",
        "berger_pbw_backend_certificate.py",
        "berger_minimal_contraction_import.py",
        "berger_minimal_contraction_import_certificate.py",
        "berger_gauge_fixed_nonminimal_import.py",
        "berger_gauge_fixed_nonminimal_import_certificate.py",
        "berger_54_row_local_d_import.py",
        "berger_54_row_local_d_import_certificate.py",
        "../reports/berger-54-row-local-d-import.md",
        "berger_reduced_mode_cartan.py",
        "berger_reduced_mode_cartan_certificate.py",
        "berger_nonzero_weight_no_go_import.py",
        "berger_nonzero_weight_no_go_import_certificate.py",
        "berger_all_weight_cartan_import.py",
        "berger_all_weight_cartan_import_certificate.py",
        "ppwave_branch_transfer_import.py",
        "ppwave_branch_transfer_import_certificate.py",
        "../reports/ppwave-branch-transfer.md",
        "einstein_projection_amplitude_fixture.py",
        "einstein_projection_amplitude_fixture_certificate.py",
        "../reports/einstein-projection-amplitude-fixture.md",
        "total_d_disposition.py",
        "total_d_disposition_certificate.py",
        "arity_three_cartan.py",
        "arity_three_cartan_certificate.py",
        "local_bach_seed_lift.py",
        "local_bach_seed_certificate.py",
        "local_bach_seed_direct_audit.py",
        "nonlinear_transfer_certificate.py",
        "schema/local-bach-seed-lift-v2.schema.json",
        "schema/local-bach-seed-direct-audit-v1.schema.json",
        "schema/selected-residual-d-derivation-v1.schema.json",
        "schema/nd2-arity-two-cartan-engine-v1.schema.json",
        "schema/nd2-physical-run-input-v1.schema.json",
        "schema/nd2-physical-run-certificate-v1.schema.json",
        "schema/berger-clock-nonlinear-import-v1.schema.json",
        "schema/berger-clock-partial-sdr-import-v1.schema.json",
        "schema/berger-clock-partial-sdr-portable-v1.schema.json",
        "schema/berger-retained-minimal-q1-import-v1.schema.json",
        "schema/berger-pbw-operator-backend-v1.schema.json",
        "schema/berger-minimal-34-contraction-import-v1.schema.json",
        "schema/berger-gauge-fixed-nonminimal-import-v1.schema.json",
        "schema/berger-54-row-local-d-import-v1.schema.json",
        "schema/berger-first-arity-two-cartan-verdict-v1.schema.json",
        "schema/berger-nonzero-weight-closure-no-go-import-v1.schema.json",
        "schema/berger-all-weight-arity-two-cartan-import-v1.schema.json",
        "schema/ppwave-branch-transfer-import-v1.schema.json",
        "schema/einstein-projection-amplitude-fixture-v1.schema.json",
        "schema/total-d-disposition-v1.schema.json",
        "schema/arity-three-cartan-engine-v1.schema.json",
        "schema/nonlinear_classical_export.schema.json",
        "residual_cubic_block.py",
        "residual_cubic_certificate.py",
        "tests/test_homological_transfer.py",
        "tests/test_d_derivation_defect.py",
        "tests/test_arity_two_cartan.py",
        "tests/test_block_sparse_arity_two.py",
        "tests/test_evaluator_registry.py",
        "tests/test_local_expression_ast.py",
        "tests/test_support_local_q2_consumer.py",
        "tests/test_nd2_arity_two_certificate.py",
        "tests/test_nd2_physical_run.py",
        "tests/test_berger_clock_import.py",
        "tests/test_berger_clock_sdr_import.py",
        "tests/test_berger_retained_q1_import.py",
        "tests/test_berger_pbw_backend.py",
        "tests/test_berger_minimal_contraction_import.py",
        "tests/test_berger_gauge_fixed_nonminimal_import.py",
        "tests/test_berger_54_row_local_d_import.py",
        "tests/test_berger_reduced_mode_cartan.py",
        "tests/test_berger_nonzero_weight_no_go_import.py",
        "tests/test_berger_all_weight_cartan_import.py",
        "tests/test_ppwave_branch_transfer_import.py",
        "tests/test_einstein_projection_amplitude_fixture.py",
        "tests/test_total_d_disposition.py",
        "tests/test_arity_three_cartan.py",
        "tests/test_arity_three_cartan_certificate.py",
        "tests/test_local_bach_seed_lift.py",
        "tests/test_local_bach_seed_direct_audit.py",
        "tests/test_nonlinear_transfer_certificate.py",
        "tests/test_residual_cubic_block.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    berger_import = json.loads(BERGER_IMPORT_PATH.read_text(encoding="utf-8"))
    total_D_disposition = json.loads(
        TOTAL_D_DISPOSITION_PATH.read_text(encoding="utf-8")
    )
    berger_partial_sdr = json.loads(
        BERGER_PARTIAL_SDR_PATH.read_text(encoding="utf-8")
    )
    berger_retained_q1 = json.loads(
        BERGER_RETAINED_Q1_PATH.read_text(encoding="utf-8")
    )
    berger_pbw_backend = json.loads(
        BERGER_PBW_BACKEND_PATH.read_text(encoding="utf-8")
    )
    berger_minimal_contraction = json.loads(
        BERGER_MINIMAL_CONTRACTION_PATH.read_text(encoding="utf-8")
    )
    berger_gauge_fixed = json.loads(
        BERGER_GAUGE_FIXED_PATH.read_text(encoding="utf-8")
    )
    berger_54_row_local_D = json.loads(
        BERGER_54_ROW_LOCAL_D_PATH.read_text(encoding="utf-8")
    )
    berger_reduced_cartan = json.loads(
        BERGER_REDUCED_CARTAN_PATH.read_text(encoding="utf-8")
    )
    berger_nonzero_weight_no_go = json.loads(
        BERGER_NONZERO_WEIGHT_NO_GO_PATH.read_text(encoding="utf-8")
    )
    berger_all_weight_cartan = json.loads(
        BERGER_ALL_WEIGHT_CARTAN_PATH.read_text(encoding="utf-8")
    )
    ppwave_branch_transfer = json.loads(
        PPWAVE_BRANCH_TRANSFER_PATH.read_text(encoding="utf-8")
    )
    einstein_mhv_fixture = json.loads(
        EINSTEIN_MHV_FIXTURE_PATH.read_text(encoding="utf-8")
    )
    if (
        berger_import.get("result_state")
        != "BACKGROUND_CHARGE_SCOPED_D_GAUGE_AND_PARTIAL_CLOCK_SDR_IMPORTED_FULL_BV_OPEN"
        or berger_import.get("D_disposition", {}).get("status") != "D_GAUGE"
    ):
        raise ValueError("Berger nonlinear import is absent or has crossed its certified boundary")
    if (
        total_D_disposition.get("schema") != "pure-weyl-total-d-disposition-v1"
        or total_D_disposition.get("assessment_status") != "COMPUTED"
        or total_D_disposition.get("verdict") != "D_GAUGE"
        or total_D_disposition.get("fail_closed", {}).get("D_quotient_authorized")
        is not True
    ):
        raise ValueError("Berger total-D disposition contract was promoted or removed")
    if (
        berger_partial_sdr.get("schema")
        != "quantum-weyl-berger-clock-partial-sdr-import-v1"
        or berger_partial_sdr.get("result_state")
        != "PARTIAL_CLOCK_SECTOR_SDR_AVAILABLE_PORTABLE_MAPS_BLOCKED"
        or berger_partial_sdr.get("coverage", {}).get("contracted_clock_dimension")
        != 8
        or berger_partial_sdr.get("coverage", {}).get("full_minimal_dimension")
        != 34
        or berger_partial_sdr.get("nd2_gate", {}).get(
            "classical_contraction_artifact_satisfied"
        )
        is not False
    ):
        raise ValueError("Berger partial SDR evidence import was promoted or removed")
    if (
        berger_retained_q1.get("schema")
        != "quantum-weyl-berger-retained-minimal-q1-import-v1"
        or berger_retained_q1.get("result_state")
        != "RETAINED_26_ROW_MINIMAL_Q1_IMPORTED_ND2_INPUT_INCOMPLETE"
        or berger_retained_q1.get("coverage", {}).get("retained_minimal_rows")
        != 26
        or berger_retained_q1.get("coverage", {}).get(
            "retained_minimal_q1_rows_complete"
        )
        is not True
        or berger_retained_q1.get("coverage", {}).get(
            "complete_classical_contraction"
        )
        is not False
        or berger_retained_q1.get("nd2_gate", {}).get(
            "physical_execution_authorized"
        )
        is not False
    ):
        raise ValueError("Berger retained minimal-q1 import was promoted or removed")
    if (
        berger_pbw_backend.get("schema")
        != "quantum-weyl-berger-pbw-operator-backend-v1"
        or berger_pbw_backend.get("result_state")
        != "ARITY_ONE_OPERATOR_BACKEND_READY_ND2_ASSEMBLY_BLOCKED"
        or berger_pbw_backend.get("descriptor", {}).get("supported_arities")
        != [1]
        or berger_pbw_backend.get("nd2_compatibility", {}).get(
            "operator_backend_registered"
        )
        is not True
        or berger_pbw_backend.get("nd2_compatibility", {}).get(
            "finite_cartan_evaluator_registered"
        )
        is not False
        or berger_pbw_backend.get("nd2_compatibility", {}).get(
            "assembly_adapter_registered"
        )
        is not False
        or berger_pbw_backend.get("nd2_compatibility", {}).get(
            "physical_execution_authorized"
        )
        is not False
    ):
        raise ValueError("Berger PBW operator backend was promoted or removed")
    if (
        berger_minimal_contraction.get("schema")
        != "quantum-weyl-berger-minimal-34-contraction-import-v1"
        or berger_minimal_contraction.get("result_state")
        != "COMPLETE_34_ROW_MINIMAL_UNARY_CONTRACTION_IMPORTED_ND2_NONLINEAR_INPUT_BLOCKED"
        or berger_minimal_contraction.get("coverage", {}).get(
            "complete_minimal_classical_contraction"
        )
        is not True
        or berger_minimal_contraction.get("coverage", {}).get(
            "nonminimal_rows_complete"
        )
        is not False
        or berger_minimal_contraction.get("nd2_gate", {}).get(
            "physical_execution_authorized"
        )
        is not False
    ):
        raise ValueError("Berger minimal contraction import was promoted or removed")
    if (
        berger_gauge_fixed.get("schema")
        != "quantum-weyl-berger-gauge-fixed-nonminimal-import-v1"
        or berger_gauge_fixed.get("coverage", {}).get("total_rows") != 54
        or berger_gauge_fixed.get("coverage", {}).get(
            "gauge_fixed_classical_unary_complete"
        )
        is not True
        or berger_gauge_fixed.get("nd2_gate", {}).get(
            "unary_nonminimal_prerequisite_satisfied"
        )
        is not True
        or berger_gauge_fixed.get("nd2_gate", {}).get(
            "physical_execution_authorized"
        )
        is not False
    ):
        raise ValueError("Berger gauge-fixed unary import was promoted or removed")
    if (
        berger_54_row_local_D.get("schema")
        != "quantum-weyl-berger-54-row-local-d-import-v1"
        or berger_54_row_local_D.get("result_state")
        != "COMPLETE_54_ROW_LOCAL_D_ACTION_IMPORTED_SUPPORT_LOCAL_Q2_BLOCKED"
        or berger_54_row_local_D.get("coverage", {}).get("total_rows") != 54
        or berger_54_row_local_D.get("coverage", {}).get(
            "local_D_action_complete"
        )
        is not True
        or berger_54_row_local_D.get("coverage", {}).get(
            "contraction_equivariance_complete"
        )
        is not True
        or berger_54_row_local_D.get("generality_assessment", {}).get(
            "promotion_to_G2_authorized"
        )
        is not False
        or berger_54_row_local_D.get("nd2_gate", {}).get(
            "support_local_classical_binary_q2"
        )
        != "NOT_AVAILABLE"
        or berger_54_row_local_D.get("nd2_gate", {}).get(
            "physical_execution_authorized"
        )
        is not False
    ):
        raise ValueError("Berger 54-row local-D import was promoted or removed")
    if (
        berger_reduced_cartan.get("schema")
        != "quantum-weyl-berger-first-arity-two-cartan-verdict-v1"
        or berger_reduced_cartan.get("cartan_equation", {}).get("binary_verdict")
        != "ADMISSIBLE_EXACT_PRIMITIVE"
        or berger_reduced_cartan.get("claim_flags", {}).get(
            "BERGER_REDUCED_MODE_ARITY_TWO_CARTAN_EXISTS"
        )
        is not True
        or berger_reduced_cartan.get("claim_flags", {}).get(
            "BERGER_SUPPORT_LOCAL_ARITY_TWO_CARTAN_EXISTS"
        )
        is not False
    ):
        raise ValueError("Berger reduced-mode Cartan verdict was promoted or removed")
    if (
        berger_nonzero_weight_no_go.get("schema")
        != "quantum-weyl-berger-nonzero-weight-closure-no-go-import-v1"
        or berger_nonzero_weight_no_go.get("result_state")
        != "FINITE_NONZERO_WEIGHT_CYCLIC_Q2_BLOCK_EXACTLY_OBSTRUCTED"
        or berger_nonzero_weight_no_go.get("claim_flags", {}).get(
            "FINITE_NONZERO_WEIGHT_CLOSURE_OBSTRUCTED"
        )
        is not True
        or berger_nonzero_weight_no_go.get("cartan_disposition", {}).get(
            "cartan_equation_reached"
        )
        is not False
        or berger_nonzero_weight_no_go.get("claim_flags", {}).get(
            "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"
        )
        is not False
    ):
        raise ValueError("Berger finite-weight closure no-go was promoted or removed")
    if (
        berger_all_weight_cartan.get("schema")
        != "quantum-weyl-berger-all-weight-arity-two-cartan-import-v1"
        or berger_all_weight_cartan.get("result_state")
        != "NONZERO_WEIGHT_CARTAN_SOURCE_HAS_EXPLICIT_NONZERO_EXACT_PRIMITIVE"
        or berger_all_weight_cartan.get("cartan_verdict", {}).get("binary_verdict")
        != "ADMISSIBLE_EXACT_PRIMITIVE"
        or berger_all_weight_cartan.get("cartan_verdict", {}).get(
            "source_nonzero_for_generic_nonzero_weights"
        )
        is not True
        or berger_all_weight_cartan.get("cartan_verdict", {}).get("primitive_nonzero")
        is not True
        or berger_all_weight_cartan.get("claim_flags", {}).get(
            "FULL_4D_SUPPORT_LOCAL_Q2"
        )
        is not False
    ):
        raise ValueError("Berger all-weight Cartan verdict was promoted or removed")
    if (
        ppwave_branch_transfer.get("schema")
        != "quantum-weyl-ppwave-branch-transfer-import-v1"
        or ppwave_branch_transfer.get("result_state")
        != "RESTRICTED_SUPPORT_LOCAL_BRANCH_MIXING_ELL2_EXACTLY_ZERO"
        or any(
            ppwave_branch_transfer.get("transferred_bracket", {}).get(entry) != "0"
            for entry in (
                "Einstein_Einstein",
                "Einstein_extraWeyl",
                "extraWeyl_extraWeyl",
            )
        )
        or ppwave_branch_transfer.get("claim_flags", {}).get(
            "ACTUAL_EINSTEIN_EXTRA_WEYL_MIXING_TESTED"
        )
        is not True
        or ppwave_branch_transfer.get("claim_flags", {}).get(
            "FULL_SUPPORT_LOCAL_BV_Q2"
        )
        is not False
    ):
        raise ValueError("pp-wave branch-transfer verdict was promoted or removed")
    if (
        einstein_mhv_fixture.get("schema")
        != "quantum-weyl-einstein-projection-amplitude-fixture-v1"
        or einstein_mhv_fixture.get("result_state")
        != "REFERENCE_MHV_FIXTURE_EXACT_NONLINEAR_EINSTEIN_PROJECTION_INPUT_BLOCKED"
        or einstein_mhv_fixture.get("reference_fixture", {}).get("stripped_value")
        != "1"
        or einstein_mhv_fixture.get("reference_fixture", {}).get("helicities")
        != [-2, -2, 2]
        or einstein_mhv_fixture.get("projection_contract", {}).get(
            "execution_authorized"
        )
        is not False
        or einstein_mhv_fixture.get("generality_assessment", {}).get(
            "promotion_to_G5_authorized"
        )
        is not False
        or einstein_mhv_fixture.get("claim_flags", {}).get(
            "PHYSICAL_TRANSFERRED_Q2_PROJECTED"
        )
        is not False
    ):
        raise ValueError("Einstein-projection MHV fixture was promoted or removed")
    exports = {item["export_id"]: item for item in snapshot["required_exports"]}
    blockers = []
    for export_id in REQUIRED_EXPORTS:
        item = exports[export_id]
        if item["status"] != "AVAILABLE":
            if export_id == "local_classical_bv_differential_q0":
                continue
            if export_id == "local_D_action_on_bv_generators":
                continue
            if export_id in {
                "classical_inclusion_iota_cl",
                "classical_projection_pi_cl",
                "classical_homotopy_s_cl",
                "cyclic_pairing",
            }:
                continue
            blockers.append(
                {
                    "export_id": export_id,
                    "status": item["status"],
                    "reason": item["reason"],
                }
            )

    source_manifest = _source_manifest()
    return {
        "result_id": "NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP",
        "result_state": "ENGINE_READY_HT1_SELECTED_PPWAVE_AND_54_ROW_D_IMPORTED_Q2_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "classical_snapshot_commit": snapshot["classical_commit"],
        "classical_freeze_gate": snapshot["gate_a_status"],
        "convention": "suspended-graded-symmetric-factorial-v1",
        "scope": {
            "established": [
                "exact strong-deformation-retract verification",
                "Koszul-symmetric transferred binary Taylor bracket",
                "contact-plus-exchange transferred ternary Taylor bracket",
                "full and transferred coderivation-square checks through arity three",
                "floating-point rejection",
                "portable nonlinear classical export schema",
                "executable support-local q1/q2 and D-action import preflight",
                "HT1 selected residual cubic bracket including the matter-matter Kuranishi output",
                "HT1b two mode-specialized local quadratic-Bach density seeds matched to residual q2 entries",
                "HT1b direct curvature reevaluation of six forward probes and two reverse slice probes",
                "ND1 exact arity-two D-derivation defect vanishes on all four selected residual HT1 q2 blocks",
                "ND2 canonical exact local-expression consumer and full arity-two Cartan primitive/obstruction engine",
                "ND2 stable physical-run contract with content-addressed evaluator registry and block-sparse exact solving",
                "content-addressed Berger healthy-background, reduced-clock-momentum, and scoped fixed-coupling D_GAUGE import",
                "registered exact 8/34 support-local cyclic Berger clock-sector SDR evidence import",
                "strict portable partial-SDR receiving contract with explicit coefficient-ring, grading, derivative-symbol, coverage, and D-equivariance fields",
                "independently reconstructed exact 26-row retained Berger minimal q1 in the noncommutative invariant-frame PBW algebra",
                "content-addressed arity-one Berger PBW operator backend with validation-only ND2 capability",
                "independently verified exact support-local cyclic contraction of the complete 34-row minimal Berger unary complex onto 26 retained rows",
                "independently imported complete gauge-fixed 54-row Berger unary BV complex, cyclic pairing, and contraction onto 26 retained rows",
                "independently imported complete support-local order-one helical D action on all 54 gauge-fixed Berger rows with unary, contraction, and cyclic equivariance",
                "first action-derived Berger REDUCED-MODE arity-two Cartan verdict with the admissible exact primitive iota_D^(2)=0 on the centered six-row block",
                "exact Berger REDUCED-MODE no-go for every finite pairing-nondegenerate nonzero-D-weight q2-closed block, with normalized first-leakage witness",
                "exact all-integer-weight homogeneous Berger arity-two Cartan contraction with a generically nonzero source and explicit nonzero first-order graded-cyclic primitive",
                "arbitrary-profile aligned Brinkmann pp-wave branch block with genuine Einstein and extra-Weyl representatives, vanishing restricted q2, and homotopy-independent transferred ell2=0",
                "exact complex (--+) Einstein three-graviton MHV reference fixture with pinned solution-locus inclusion and a fail-closed future projection contract",
                "total-D disposition router that permits Cartan contraction only for a certified D_GAUGE result",
                "strict total-D presymplectic audit schema with canonical D_CHARGED vocabulary, sector ledger, and exact verdict signatures",
                "phase-space, boundary-condition, classical-commit, dependency-scope, and source-hash binding before physical execution",
                "opaque verified-manifest token required by the physical Cartan executor",
                "ND3 exact arity-three Cartan recurrence engine with separate direct q3 and exchange sources",
            ],
            "not_established": [
                "the complete conformal-gravity q2 or q3 Taylor tensors",
                "the complete support-local conformal-gravity q2 lift before endpoint projection",
                "closure or centrality of either Weyl-square direction",
                "nonaligned Einstein/extra-Weyl branch mixing outside the Brinkmann pp-wave sector",
                "projection of the physical conformal-gravity cubic tensor onto the Einstein helicity sector or matching to the MHV reference",
                "absence of higher-bracket sector re-entry",
                "the support-local Berger q2 and arity-two nonlinear D-Cartan contraction outside the all-weight homogeneous six-row-per-weight block",
                "the full four-dimensional support-local Berger q2 and complete 54-row arity-two Cartan contraction",
                "an interacting particle or deformation-theory theorem",
                "a quantum correction or residual quantum transfer",
                "any LORENTZIAN-CAUSAL claim",
            ],
        },
        "required_classical_exports": list(REQUIRED_EXPORTS),
        "input_blockers": blockers,
        "question_ledger": [
            {
                "question_id": "transferred_cubic_bracket",
                "status": "COMPUTED_SELECTED_RESIDUAL_MODEL_TWO_DIRECT_LOCAL_SEEDS_AND_RESTRICTED_PPWAVE_BRANCH_BLOCK_FULL_FIELD_DOMAIN_PENDING",
                "next_certificate": "HT1B_COMPLETE_SUPPORT_LOCAL_Q2",
            },
            {
                "question_id": "einstein_extra_weyl_branch_mixing",
                "status": "COMPUTED_RESTRICTED_SUPPORT_LOCAL_ALIGNED_PPWAVE_ELL2_ZERO_NONALIGNED_FULL_BV_PENDING",
                "next_certificate": "HT2_NONALIGNED_BRANCH_MIXING",
            },
            {
                "question_id": "einstein_projection_amplitude_fixture",
                "status": "REFERENCE_MHV_FIXTURE_EXACT_NONLINEAR_PROJECTION_AND_Q2_INPUT_BLOCKED",
                "next_certificate": "N_G5_PROJECT_TRANSFERRED_ELL2_AND_COMPARE_MHV",
            },
            {
                "question_id": "D_quotient_interaction_stability",
                "status": "ALL_INTEGER_WEIGHT_HOMOGENEOUS_NONZERO_SOURCE_CARTAN_EXACT_NONZERO_PRIMITIVE_COMPLETE_FINITE_TRUNCATIONS_OBSTRUCTED_54_ROW_LOCAL_D_IMPORTED_FULL_4D_SUPPORT_LOCAL_Q2_BLOCKED",
                "next_certificate": "ND1_COMPLETE_SUPPORT_LOCAL_D_DERIVATION_AND_IOTA_D2",
            },
            {
                "question_id": "positive_dynamical_direction_closure",
                "status": "NOT_COMPUTED",
                "next_certificate": "HT2_DYNAMICAL_CLOSURE",
            },
            {
                "question_id": "topological_direction_central_or_inert",
                "status": "NOT_COMPUTED",
                "next_certificate": "HT2_TOPOLOGICAL_CENTRALITY",
            },
            {
                "question_id": "higher_bracket_sector_reentry",
                "status": "NOT_COMPUTED",
                "next_certificate": "HT3_HIGHER_ARITY_SECTOR_LEDGER",
            },
            {
                "question_id": "centered_degree_four_one_particle_vanishing",
                "status": "NOT_COMPUTED",
                "next_certificate": "HT3_PARTICLE_FILTRATION_SPECTRAL_SEQUENCE",
            },
            {
                "question_id": "residual_deformation_or_vertex_theory",
                "status": "NOT_COMPUTED",
                "next_certificate": "HT4_MINIMAL_MODULI_INTERPRETATION",
            },
        ],
        "programme_stages": [
            {"stage": "HT0", "deliverable": "exact transfer engine and input contract", "status": "READY"},
            {"stage": "HT1", "deliverable": "import q1/q2/q3 and pi_cl/iota_cl/s_cl; compute ell2", "status": "COMPLETE_54_ROW_UNARY_CONTRACTION_AND_LOCAL_D_ACTION_ALL_WEIGHT_HOMOGENEOUS_NONZERO_CARTAN_PRIMITIVE_AND_RESTRICTED_PPWAVE_BRANCH_ELL2_ZERO_FULL_4D_SUPPORT_LOCAL_Q2_AND_54_ROW_CARTAN_PENDING"},
            {"stage": "HT2", "deliverable": "compute ell3 and dynamical/topological mixing table", "status": "ARITY_THREE_CARTAN_RECURRENCE_ENGINE_READY_PHYSICAL_Q3_INPUT_BLOCKED"},
            {"stage": "HT3", "deliverable": "higher-arity and particle-filtration obstruction ledger", "status": "NOT_COMPUTED"},
            {"stage": "HT4", "deliverable": "cyclic minimal action and formal moduli interpretation", "status": "NOT_COMPUTED"},
            {"stage": "N-G5", "deliverable": "Einstein projection and one helicity/twistor amplitude fixture", "status": "REFERENCE_MHV_FIXTURE_AND_PROJECTION_CONTRACT_READY_PHYSICAL_Q2_PROJECTION_BLOCKED"},
            {"stage": "HTQ", "deliverable": "transfer restored quantum Q corrections", "status": "BLOCKED_PENDING_QME_RESTORED"},
        ],
        "provenance": {
            "classical_snapshot": str(SNAPSHOT_PATH.relative_to(QUANTUM_ROOT.parent)),
            "classical_snapshot_sha256": _sha256(SNAPSHOT_PATH),
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "input_schema": "quantum-weyl/classical_import/schema/support_local_q2_export.schema.json",
            "legacy_finite_tensor_schema": "quantum-weyl/transfer/schema/nonlinear_classical_export.schema.json",
            "support_local_q2_contract": "quantum-weyl/classical_import/certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json",
            "support_local_q2_contract_sha256": _sha256(
                QUANTUM_ROOT
                / "classical_import"
                / "certificates"
                / "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json"
            ),
            "ht1_selected_residual_certificate": "quantum-weyl/transfer/certificates/HT1_RESIDUAL_CUBIC_BLOCK.json",
            "ht1_selected_residual_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "HT1_RESIDUAL_CUBIC_BLOCK.json"
            ),
            "ht1b_local_bach_seed_certificate": "quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json",
            "ht1b_local_bach_seed_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "HT1B_LOCAL_BACH_SEED_LIFT.json"
            ),
            "ht1b_direct_curvature_audit": "quantum-weyl/transfer/certificates/HT1B_DIRECT_CURVATURE_AUDIT.json",
            "ht1b_direct_curvature_audit_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "HT1B_DIRECT_CURVATURE_AUDIT.json"
            ),
            "nd1_selected_residual_D_derivation_certificate": "quantum-weyl/transfer/certificates/ND1_SELECTED_RESIDUAL_D_DERIVATION.json",
            "nd1_selected_residual_D_derivation_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "ND1_SELECTED_RESIDUAL_D_DERIVATION.json"
            ),
            "nd2_arity_two_cartan_engine_certificate": "quantum-weyl/transfer/certificates/ND2_ARITY_TWO_CARTAN_ENGINE.json",
            "nd2_arity_two_cartan_engine_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "ND2_ARITY_TWO_CARTAN_ENGINE.json"
            ),
            "nd2_physical_run_contract_certificate": "quantum-weyl/transfer/certificates/ND2_PHYSICAL_RUN.json",
            "nd2_physical_run_contract_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "ND2_PHYSICAL_RUN.json"
            ),
            "berger_clock_nonlinear_import_certificate": "quantum-weyl/transfer/certificates/BERGER_CLOCK_NONLINEAR_IMPORT.json",
            "berger_clock_nonlinear_import_sha256": _sha256(BERGER_IMPORT_PATH),
            "berger_clock_partial_sdr_import_certificate": "quantum-weyl/transfer/certificates/BERGER_CLOCK_PARTIAL_SDR_IMPORT.json",
            "berger_clock_partial_sdr_import_sha256": _sha256(
                BERGER_PARTIAL_SDR_PATH
            ),
            "berger_retained_minimal_q1_import_certificate": "quantum-weyl/transfer/certificates/BERGER_RETAINED_MINIMAL_Q1_IMPORT.json",
            "berger_retained_minimal_q1_import_sha256": _sha256(
                BERGER_RETAINED_Q1_PATH
            ),
            "berger_pbw_operator_backend_certificate": "quantum-weyl/transfer/certificates/BERGER_PBW_OPERATOR_BACKEND.json",
            "berger_pbw_operator_backend_sha256": _sha256(
                BERGER_PBW_BACKEND_PATH
            ),
            "berger_minimal_34_contraction_import_certificate": "quantum-weyl/transfer/certificates/BERGER_MINIMAL_34_CONTRACTION_IMPORT.json",
            "berger_minimal_34_contraction_import_sha256": _sha256(
                BERGER_MINIMAL_CONTRACTION_PATH
            ),
            "berger_gauge_fixed_nonminimal_import_certificate": "quantum-weyl/transfer/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json",
            "berger_gauge_fixed_nonminimal_import_sha256": _sha256(
                BERGER_GAUGE_FIXED_PATH
            ),
            "berger_54_row_local_D_import_certificate": "quantum-weyl/transfer/certificates/BERGER_54_ROW_LOCAL_D_IMPORT.json",
            "berger_54_row_local_D_import_sha256": _sha256(
                BERGER_54_ROW_LOCAL_D_PATH
            ),
            "berger_first_arity_two_cartan_verdict_certificate": "quantum-weyl/transfer/certificates/BERGER_FIRST_ARITY_TWO_CARTAN_VERDICT.json",
            "berger_first_arity_two_cartan_verdict_sha256": _sha256(
                BERGER_REDUCED_CARTAN_PATH
            ),
            "berger_nonzero_weight_closure_no_go_import_certificate": "quantum-weyl/transfer/certificates/BERGER_NONZERO_WEIGHT_CLOSURE_NO_GO_IMPORT.json",
            "berger_nonzero_weight_closure_no_go_import_sha256": _sha256(
                BERGER_NONZERO_WEIGHT_NO_GO_PATH
            ),
            "berger_all_weight_arity_two_cartan_import_certificate": "quantum-weyl/transfer/certificates/BERGER_ALL_WEIGHT_ARITY_TWO_CARTAN_IMPORT.json",
            "berger_all_weight_arity_two_cartan_import_sha256": _sha256(
                BERGER_ALL_WEIGHT_CARTAN_PATH
            ),
            "ppwave_branch_transfer_import_certificate": "quantum-weyl/transfer/certificates/PPWAVE_BRANCH_TRANSFERRED_ELL2.json",
            "ppwave_branch_transfer_import_sha256": _sha256(
                PPWAVE_BRANCH_TRANSFER_PATH
            ),
            "einstein_projection_MHV_fixture_certificate": "quantum-weyl/transfer/certificates/EINSTEIN_PROJECTION_MHV_FIXTURE.json",
            "einstein_projection_MHV_fixture_sha256": _sha256(
                EINSTEIN_MHV_FIXTURE_PATH
            ),
            "berger_total_D_disposition_certificate": "quantum-weyl/transfer/certificates/BERGER_TOTAL_D_DISPOSITION.json",
            "berger_total_D_disposition_sha256": _sha256(
                TOTAL_D_DISPOSITION_PATH
            ),
            "nd3_arity_three_cartan_engine_certificate": "quantum-weyl/transfer/certificates/ND3_ARITY_THREE_CARTAN_ENGINE.json",
            "nd3_arity_three_cartan_engine_sha256": _sha256(
                TRANSFER_ROOT / "certificates" / "ND3_ARITY_THREE_CARTAN_ENGINE.json"
            ),
        },
        "assumptions": [
            "The low-arity engine uses a finite exact basis and the declared suspended convention.",
            "The engine fixture tests implementation mechanics only and carries no conformal-gravity coefficient claim.",
            "The classical import remains fail-closed until portable tensors and maps are independently verified.",
            "The support-local q2 preflight validates format, completeness declarations, exactness, provenance, and hashes; it does not independently prove an opaque local-expression payload.",
            "The certified endpoint projection computes the residual matter-matter Kuranishi bracket but does not substitute for a portable support-local q2 tensor.",
            "The two local Bach density seeds test selected matrix elements only; they do not substitute for an arbitrary-input bilinear Bach tensor or its BV completions.",
            "The vanishing selected residual D-derivation defect does not construct the full support-local interacting Cartan homotopy.",
            "ND2 fixture primitives and obstruction witnesses certify the exact solver branches only; they contain no conformal-gravity interaction coefficient.",
            "The Berger D_GAUGE theorem is scoped to the smooth fixed-coupling linearized phase space; it does not construct the support-local all-row BV contraction required by ND2.",
            "The earlier Berger clock-SDR receipt contracts exactly 8 of 34 minimal rows and, by itself, carries formulas and fingerprints rather than a portable map payload; D-equivariance remains uncomputed.",
            "The retained Berger minimal-q1 receipt is complete on 26 rows and independently reconstructed from exact PBW entries; by itself it supplies neither the separate clock maps nor nonminimal rows, q2, D action, or a contraction.",
            "The registered Berger backend validates arity-one PBW-operator data only; the Fraction-valued ND2 engine cannot consume it without either a declared PBW-module extension or an exact REDUCED-MODE specialization.",
            "The complete gauge-fixed 54-row unary complex, cyclic pairing, and contraction are independently imported. That unary artifact does not itself supply q2 or D, while the separate complete local-D import now closes unary, contraction, and cyclic D-equivariance.",
            "The complete 54-row local D action is independently imported and unary/contraction/cyclic equivariance is exact. It does not supply q2, so the arity-two D-derivation defect and Cartan source remain input-blocked.",
            "The first action-derived reduced-mode q2/D block has a certified exact zero Cartan source and zero primitive because all six rows have D-weight zero; it cannot rule out an obstruction in omitted nonzero-weight or support-local sectors.",
            "The finite nonzero-weight extension is exactly ruled out at q2 closure, before the Cartan equation: anisotropy and cyclicity force an infinite weight tower. This is not a Cartan-cohomology obstruction and says nothing about the infinite or support-local complexes.",
            "The resulting all-integer-weight homogeneous complex has a generically nonzero Cartan source and an explicit nonzero exact primitive. It remains a three-field REDUCED-MODE theorem and does not promote the full four-dimensional support-local q2 or complete 54-row Cartan contraction.",
            "The pp-wave branch block uses arbitrary smooth aligned Brinkmann profiles and genuine Einstein/non-Einstein metric representatives, but exact linearity on that sector does not determine nonaligned support-local vertices, the centered Weyl-square deformation classes, or the complete BV q2.",
            "The exact (--+) MHV value is a reference fixture, not a conformal-gravity calculation. The pinned Einstein theorem supplies a solution-locus inclusion but no nonlinear tangent projector, observable embedding, or scattering-state map, so G5 remains unpromoted until the complete physical q2 is projected and normalized.",
            "D_CHARGED is the canonical classical verdict; EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT is a route label, not a fifth scientific disposition.",
            "ND3 direct and exchange fixtures certify the arity-three recurrence mechanics only; physical q3 and any support-local or nonzero-weight iota_D^(2) remain absent.",
            "Quantum transfer remains downstream of QME_RESTORED and is not implied by this classical programme.",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"nonlinear transfer certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("NONLINEAR HOMOLOGICAL TRANSFER: 54-ROW UNARY/D AND RESTRICTED HT1 RESULTS READY; FULL SUPPORT-LOCAL Q2 BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
