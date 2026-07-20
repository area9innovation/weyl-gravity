#!/usr/bin/env python3
"""Certify the missing base-producer inputs for the executable 160-row unary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL.json"
PAYLOAD = P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-160-executable-unary-export-input-shortfall-v1.schema.json"
REPORT = P / "reports/berger-apparatus-160-executable-unary-export-input-shortfall.md"
DEPENDENCIES = {
    "combined_q1": P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112.json",
    "combined_payload": P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112_PAYLOAD.json",
    "physical_reduction": P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112.json",
    "physical_payload": P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112_PAYLOAD.json",
    "replacement_112": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "replacement_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "material_parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "material_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "old_108_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "old_108_payload": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _missing(container: dict[str, Any], required: list[str]) -> list[str]:
    return sorted(set(required) - set(container))


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for cert_name, payload_name in (
        ("combined_q1", "combined_payload"),
        ("physical_reduction", "physical_payload"),
        ("replacement_112", "replacement_payload"),
        ("material_parent", "material_payload"),
        ("old_108_unary", "old_108_payload"),
    ):
        if sha256(DEPENDENCIES[payload_name]) != values[cert_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert_name} payload hash mismatch")

    required = values["physical_payload"]["executable_reduction_audit"]["required_operator_fields"]
    replacement_required = ["coefficient_ring", "operator_schema", "bidegree_blocks", "sparse_entries", "zero_mode_operator_blocks"]
    material_required = ["row_dictionary", "coefficient_ring", "bidegrees", "q1_sparse_entries", "pairing_sparse_entries", "zero_mode_operator_blocks"]
    replacement_missing = _missing(values["replacement_payload"]["complete_unary"], replacement_required)
    material_missing = _missing(values["material_payload"], material_required)
    if replacement_missing != sorted(replacement_required):
        raise AssertionError("replacement base unexpectedly gained executable coefficients")
    if material_missing != sorted(material_required):
        raise AssertionError("material parent unexpectedly gained executable coefficients")
    if values["old_108_payload"]["block_count"] <= 0:
        raise AssertionError("old executable predecessor drifted")

    return {
        "schema": "closed-universe-berger-apparatus-160-executable-unary-export-input-shortfall-payload-v1",
        "result_id": "BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL_PAYLOAD",
        "required_160_export": {
            "fields_named_by_physical_reduction": required,
            "normalized_matrix_hashes_required": True,
            "independent_byte_equivalent_reconstruction_required": True,
        },
        "base_input_audit": {
            "replacement_112": {
                "row_table": "CERTIFIED",
                "pairing_entries": "CERTIFIED",
                "action_level_unary": "CERTIFIED",
                "required_fields_missing": replacement_missing,
                "first_missing_object": "normalized row-indexed q1 sparse entries for the changed Phi2 background and eight-rod mixed action",
                "status": "NO_CERTIFIED_MAP",
            },
            "material_parent_56": {
                "physical_and_cotangent_row_lists": "CERTIFIED",
                "action_formula_and_principal_transport_pair": "CERTIFIED",
                "pairing_rank": "CERTIFIED",
                "required_fields_missing": material_missing,
                "first_missing_object": "normalized row-indexed q1 and odd-pairing sparse entries on the declared 56-row order",
                "status": "NO_CERTIFIED_MAP",
            },
        },
        "non_substitution_replay": {
            "old_108_block_count": values["old_108_payload"]["block_count"],
            "old_108_blocks_canonical_sha256": values["old_108_payload"]["blocks_canonical_sha256"],
            "verdict": "EXECUTABLE_BUT_FORBIDDEN_AS_REPLACEMENT_INPUT",
            "reason": "the positive-mixed replacement changes Phi2-dependent nonrod rows and adds four rod/cotangent rows; the old operator has neither change",
        },
        "minimal_missing_producer_contracts": {
            "replacement_112_exporter": {
                "must_export": replacement_required + ["row_and_column_degree_table", "real_and_K_actions"],
                "must_recompute": "every changed Phi2-dependent, metric-rod, rod-cotangent and Diff-BV adjoint entry from the positive-mixed action",
            },
            "material_parent_56_exporter": {
                "must_export": material_required + ["real_and_K_actions", "support_sector_blocks"],
                "must_recompute": "the six D_K doublet blocks, their cotangent adjoints and the shared memory unary on one declared row order",
            },
            "then": "reconstruct the rank-eight pushout quotient independently and compare normalized 160-row q1, pairing, embeddings, quotient and detector matrices byte for byte",
        },
        "export_disposition": {
            "canonical_row_dictionary": "NO_CERTIFIED_MAP",
            "complete_sparse_q1": "NO_CERTIFIED_MAP",
            "complete_sparse_pairing": "NO_CERTIFIED_MAP",
            "support_and_zero_mode_chain_groups": "NO_CERTIFIED_MAP",
            "detector_smearing_matrix": "NO_CERTIFIED_MAP",
            "direct_identity_replays": "NO_CERTIFIED_MAP",
            "independent_byte_equivalent_reconstruction": "NO_CERTIFIED_MAP",
            "physical_reduction_and_downstream": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-apparatus-160-executable-unary-export-input-shortfall-v1",
        "result_id": "BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL",
        "setting_id": values["combined_q1"]["setting_id"],
        "claim_status": "SHORTFALL_BASE_PRODUCERS_LACK_SERIALIZED_UNARY_COEFFICIENTS",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "export_disposition": payload["export_disposition"],
        "next_gate": "EXPORT_EXECUTABLE_REPLACEMENT_112_AND_MATERIAL_PARENT_56_UNARY_INPUTS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE input audit imports by content hash the certified typed 160-row pushout, its terminal physical-reduction nondefinition, both immediate base producers and the nearest executable 108-row predecessor. It obeys the work-package stop rule before attempting to synthesize a 160-row matrix. The positive-mixed replacement payload certifies its 112-row table, signed pairing and action-level Hessian identities, but its complete_unary object contains no coefficient ring, operator schema, bidegree blocks, sparse entries or zero-mode operator blocks. In particular its descriptions of changed Phi2-dependent nonrod rows, metric-rod Hessians, rod-cotangent equations and Diff-BV adjoints are prose rather than normalized row-indexed coefficients. Independently, the 56-row material parent payload certifies physical/cotangent row lists, a local action formula, the canonical D_K principal pair and a pairing rank, but exports no row dictionary tying those objects together, no q1 sparse entries, no odd-pairing entries, no bidegrees and no zero-mode blocks. These are two minimal immediate producer contracts, not defects that a pushout consumer may guess around. The older 108-row payload does contain content-addressed executable blocks, but it is explicitly non-substitutable because the positive-mixed background changes Phi2-dependent entries and the replacement adds four rod/cotangent rows. Consequently a canonical executable 160-row q1, complete serialized pairing, support-sector chain groups, zero-mode matrices, detector-smearing matrix, direct identity replays and method-distinct byte-equivalent reconstruction all remain NO_CERTIFIED_MAP. This result preserves the already certified semantic pushout and its action-level identities; it does not retract them. It establishes a serialization/input shortfall, not failure of nilpotency or cyclicity and not a cohomology theorem. No physical reduction, detector rank, q2, q3, Z2, memory, redshift, recoil, particle, positivity or quantum claim is promoted. Activation requires separate content-addressed executable exports from the replacement-112 and material-parent-56 producers, after which the 160-row quotient must be reconstructed and verified from entries rather than ranks or verdict booleans."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_apparatus_160_executable_unary_export_input_shortfall --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_apparatus_160_executable_unary_export_input_shortfall",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger apparatus executable 160-row unary input shortfall

The consumer cannot construct normalized 160-row matrices from the certified
base payloads.  The replacement 112-row producer omits row-indexed q1
coefficients, while the material-parent 56-row producer omits both q1 and
odd-pairing entries.  The executable old 108-row blocks are forbidden because
the positive-mixed Phi2 and four added rod rows change the operator.  Both
immediate producer exports must land before the pushout can be reconstructed.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
