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


REQUIRED_EXPORTS = (
    "field_ghost_antifield_dictionary",
    "field_gradings",
    "local_classical_bv_differential_q0",
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
        "homological_transfer.py",
        "nonlinear_transfer_certificate.py",
        "schema/nonlinear_classical_export.schema.json",
        "tests/test_homological_transfer.py",
        "tests/test_nonlinear_transfer_certificate.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
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
        "result_state": "ENGINE_READY_INPUT_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
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
            ],
            "not_established": [
                "the conformal-gravity q2 or q3 Taylor tensors",
                "the conformal-gravity transferred cubic bracket",
                "closure or centrality of either Weyl-square direction",
                "absence of higher-bracket sector re-entry",
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
                "status": "BLOCKED_MISSING_CLASSICAL_TAYLOR_DATA",
                "next_certificate": "HT1_TRANSFERRED_BINARY_BRACKET",
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
            {"stage": "HT1", "deliverable": "import q1/q2/q3 and pi_cl/iota_cl/s_cl; compute ell2", "status": "BLOCKED"},
            {"stage": "HT2", "deliverable": "compute ell3 and dynamical/topological mixing table", "status": "NOT_COMPUTED"},
            {"stage": "HT3", "deliverable": "higher-arity and particle-filtration obstruction ledger", "status": "NOT_COMPUTED"},
            {"stage": "HT4", "deliverable": "cyclic minimal action and formal moduli interpretation", "status": "NOT_COMPUTED"},
            {"stage": "HTQ", "deliverable": "transfer restored quantum Q corrections", "status": "BLOCKED_PENDING_QME_RESTORED"},
        ],
        "provenance": {
            "classical_snapshot": str(SNAPSHOT_PATH.relative_to(QUANTUM_ROOT.parent)),
            "classical_snapshot_sha256": _sha256(SNAPSHOT_PATH),
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "input_schema": "quantum-weyl/transfer/schema/nonlinear_classical_export.schema.json",
        },
        "assumptions": [
            "The low-arity engine uses a finite exact basis and the declared suspended convention.",
            "The engine fixture tests implementation mechanics only and carries no conformal-gravity coefficient claim.",
            "The classical import remains fail-closed until portable tensors and maps are independently verified.",
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
        print("NONLINEAR HOMOLOGICAL TRANSFER: ENGINE READY, INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
