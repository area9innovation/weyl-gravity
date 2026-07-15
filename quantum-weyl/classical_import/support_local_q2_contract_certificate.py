#!/usr/bin/env python3
"""Emit the machine contract for the support-local classical BV q2 handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


IMPORT_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = IMPORT_ROOT / "certificates" / "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json"


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "support_local_q2_contract_certificate.py",
        "verify_support_local_q2_export.py",
        "schema/support_local_q2_export.schema.json",
        "tests/test_support_local_q2_contract_certificate.py",
        "tests/test_verify_support_local_q2_export.py",
    )
    return {
        path: hashlib.sha256((IMPORT_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    source_manifest = _source_manifest()
    required_roles = [
        "metric",
        "diffeomorphism_ghost",
        "weyl_ghost",
        "metric_antifield",
        "diffeomorphism_ghost_antifield",
        "weyl_ghost_antifield",
    ]
    proof_checks = [
        "q1_squared_zero",
        "q1_q2_arity_two_nilpotency",
        "q2_koszul_symmetry",
        "q2_row_completeness",
        "D_q1_commutator_zero",
        "D_q2_derivation",
        "BV_cyclicity_q2",
    ]
    return {
        "result_id": "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT",
        "result_state": "CONTRACT_READY_AWAITING_CLASSICAL_EXPORT",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "schema": "quantum-weyl/classical_import/schema/support_local_q2_export.schema.json",
        "preflight": "quantum-weyl/classical_import/verify_support_local_q2_export.py",
        "required_support_category": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
        "finite_mode_substitution_allowed": False,
        "required_minimal_roles": required_roles,
        "required_taylor_data": {
            "q1": {"arity": 1, "degree": 1},
            "q2": {"arity": 2, "degree": 1},
            "D_action": {"arity": 1, "degree": 0},
            "convention": "suspended-graded-symmetric-factorial-v1",
            "complete_output_row_ledger": True,
        },
        "required_proof_checks": proof_checks,
        "checks": {
            "exact_required_field_sets": "ENFORCED",
            "no_floating_point_payloads": "ENFORCED",
            "minimal_field_ghost_antifield_roles": "ENFORCED",
            "support_locality_not_finite_mode": "ENFORCED",
            "operator_arity_degree_and_parity": "ENFORCED",
            "complete_output_row_ledgers": "ENFORCED",
            "proof_artifact_inventory": "ENFORCED",
            "pinned_proof_artifact_integrity": "ENFORCED_WHEN_REPOSITORY_ROOT_SUPPLIED",
            "canonical_hash_reproduction": "ENFORCED",
            "classical_export_imported": "NOT_AVAILABLE",
            "identities_independently_recomputed": "NOT_COMPUTED",
            "full_D_derivation_defect_computed": "NOT_COMPUTED",
            "iota_D2_solved_or_obstructed": "NOT_COMPUTED",
        },
        "canonical_hashes": {
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "required_roles_sha256": _canonical_hash(required_roles),
            "required_proof_checks_sha256": _canonical_hash(proof_checks),
        },
        "assumptions": [
            "The expression payload is versioned and content-addressed but remains opaque to the format preflight until its declared expression evaluator is imported.",
            "A complete row ledger is a provider completeness declaration; the quantum-side import gate must still independently recompute the identities.",
            "The contract does not convert endpoint, finite-mode, or selected Bach seeds into an arbitrary-support local tensor.",
            "The interacting D-quotient remains INPUT_GATE_BLOCKED until a pinned export and the contraction maps pass their independent checks.",
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
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"support-local q2 export contract is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("SUPPORT-LOCAL Q2 EXPORT CONTRACT: EXACT PREFLIGHT READY, INPUT ABSENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
