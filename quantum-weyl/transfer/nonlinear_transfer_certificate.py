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
    if (
        berger_import.get("result_state")
        != "BACKGROUND_AND_REDUCED_CHARGE_IMPORTED_TOTAL_D_OPEN"
        or berger_import.get("D_disposition", {}).get("status") != "OPEN"
    ):
        raise ValueError("Berger nonlinear import is absent or has crossed its certified boundary")
    exports = {item["export_id"]: item for item in snapshot["required_exports"]}
    blockers = []
    for export_id in REQUIRED_EXPORTS:
        item = exports[export_id]
        if item["status"] != "AVAILABLE":
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
        "result_state": "ENGINE_READY_HT1_RESIDUAL_AND_LOCAL_SEEDS_COMPUTED_INPUT_BLOCKED",
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
                "content-addressed Berger healthy-background and reduced-clock-momentum import with total D explicitly open",
                "total-D disposition router that permits Cartan contraction only for a certified D_GAUGE result",
                "ND3 exact arity-three Cartan recurrence engine with separate direct q3 and exchange sources",
            ],
            "not_established": [
                "the complete conformal-gravity q2 or q3 Taylor tensors",
                "the complete support-local conformal-gravity q2 lift before endpoint projection",
                "closure or centrality of either Weyl-square direction",
                "absence of higher-bracket sector re-entry",
                "the total gravitational-plus-matter D disposition on the Berger clock branch",
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
                "status": "COMPUTED_SELECTED_RESIDUAL_MODEL_TWO_DIRECT_LOCAL_SEEDS_FULL_FIELD_DOMAIN_PENDING",
                "next_certificate": "HT1B_COMPLETE_SUPPORT_LOCAL_Q2",
            },
            {
                "question_id": "D_quotient_interaction_stability",
                "status": "SELECTED_RESIDUAL_Q2_D_DERIVATION_VERIFIED_BERGER_HEALTHY_CLOCK_AND_REDUCED_MOMENTUM_IMPORTED_TOTAL_D_OPEN_ND2_DISPOSITION_ROUTER_AND_ND3_CARTAN_SOLVER_READY_FULL_LOCAL_VERDICT_INPUT_GATE_BLOCKED",
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
            {"stage": "HT1", "deliverable": "import q1/q2/q3 and pi_cl/iota_cl/s_cl; compute ell2", "status": "RESIDUAL_CUBIC_LOCAL_SEEDS_AND_SELECTED_D_DERIVATION_COMPUTED_FULL_LOCAL_EXPORT_PENDING"},
            {"stage": "HT2", "deliverable": "compute ell3 and dynamical/topological mixing table", "status": "ARITY_THREE_CARTAN_RECURRENCE_ENGINE_READY_PHYSICAL_Q3_INPUT_BLOCKED"},
            {"stage": "HT3", "deliverable": "higher-arity and particle-filtration obstruction ledger", "status": "NOT_COMPUTED"},
            {"stage": "HT4", "deliverable": "cyclic minimal action and formal moduli interpretation", "status": "NOT_COMPUTED"},
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
            "The Berger import certifies a healthy background and nonzero reduced O(2) momentum, not the total D charge; OPEN and non-gauge dispositions never enter Cartan contraction.",
            "ND3 direct and exchange fixtures certify the arity-three recurrence mechanics only; physical q3 and iota_D^(2) remain absent.",
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
        print("NONLINEAR HOMOLOGICAL TRANSFER: HT1/ND1 RESULTS, ND2 PHYSICAL CONTRACT, AND ND3 CARTAN SOLVER READY; INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
