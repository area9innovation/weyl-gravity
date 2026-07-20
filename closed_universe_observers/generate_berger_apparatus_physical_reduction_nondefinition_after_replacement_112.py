#!/usr/bin/env python3
"""Fail closed when the replacement 160-row q1 is not executable by sector."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112.json"
PAYLOAD = P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-physical-reduction-nondefinition-after-replacement-112-v1.schema.json"
REPORT = P / "reports/berger-apparatus-physical-reduction-nondefinition-after-replacement-112.md"
DEPENDENCIES = {
    "combined_q1": P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112.json",
    "combined_payload": P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112_PAYLOAD.json",
    "replacement_q1": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "replacement_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "old_reduction_preflight": P / "certificates/BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if sha256(DEPENDENCIES["combined_payload"]) != values["combined_q1"]["payload_ref"]["sha256"]:
        raise AssertionError("combined q1 payload hash mismatch")
    if sha256(DEPENDENCIES["replacement_payload"]) != values["replacement_q1"]["payload_ref"]["sha256"]:
        raise AssertionError("replacement q1 payload hash mismatch")
    if sha256(DEPENDENCIES["parent_payload"]) != values["parent"]["payload_ref"]["sha256"]:
        raise AssertionError("parent payload hash mismatch")

    combined = values["combined_payload"]
    replacement = values["replacement_payload"]
    required_operator_fields = [
        "coefficient_ring",
        "operator_schema",
        "bidegree_blocks",
        "sparse_entries",
        "chain_groups_by_support_sector",
        "zero_mode_operator_blocks",
    ]
    combined_present = sorted(set(required_operator_fields) & set(combined["complete_q1"]))
    replacement_present = sorted(set(required_operator_fields) & set(replacement["complete_unary"]))
    if combined_present or replacement_present:
        raise AssertionError("the reduction input unexpectedly acquired executable q1 fields")
    if combined["carrier"]["row_count"] != 160 or combined["carrier"]["pairing_rank"] != 160:
        raise AssertionError("typed unary carrier drifted")
    return {
        "schema": "closed-universe-berger-apparatus-physical-reduction-nondefinition-after-replacement-112-payload-v1",
        "result_id": "BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112_PAYLOAD",
        "imported_unary_facts": {
            "combined_row_count": 160,
            "combined_pairing_rank": 160,
            "q1_identity_status": "CERTIFIED_COMPOSITIONALLY",
            "detector_chain_description_status": "CERTIFIED_COMPOSITIONALLY",
            "leading_coordinate_response_rank": 2,
        },
        "executable_reduction_audit": {
            "required_operator_fields": required_operator_fields,
            "combined_operator_fields_present": combined_present,
            "replacement_operator_fields_present": replacement_present,
            "combined_complete_q1_keys": sorted(combined["complete_q1"]),
            "replacement_complete_unary_keys": sorted(replacement["complete_unary"]),
            "row_level_sparse_q1": "NO_CERTIFIED_MAP",
            "support_sector_chain_groups": "NO_CERTIFIED_MAP",
            "zero_mode_matrices": "NO_CERTIFIED_MAP",
            "detector_smearing_matrix_on_chain_groups": "NO_CERTIFIED_MAP",
            "verdict": "EXACT_KERNEL_IMAGE_AND_CONTRACTION_UNDEFINED_FROM_EXPORTED_DATA",
        },
        "forbidden_substitutions": {
            "old_108_q1": "REJECTED: the positive-mixed action and changed Phi2 alter replacement unary rows",
            "raw_160_rows_as_classes": "REJECTED: no kernel/image computation exists",
            "parent_principal_symbol_as_full_q1": "REJECTED: principal symbols omit lower-order and shared-memory blocks",
            "identity_counts_as_operator": "REJECTED: zero defect counts do not reconstruct matrix entries",
        },
        "downstream_nondefinition": {
            "graded_q1_cohomology": "NO_CERTIFIED_MAP",
            "projection_inclusion_contraction": "NO_CERTIFIED_MAP",
            "descended_pairing_radical_signature": "NO_CERTIFIED_MAP",
            "reduced_real_and_K_actions": "NO_CERTIFIED_MAP",
            "canonical_physical_rods_polarizations_emitters": "NO_CERTIFIED_MAP",
            "persistent_memory_classes": "NO_CERTIFIED_MAP",
            "detector_record_classes_and_rank": "NO_CERTIFIED_MAP",
            "Z2_redshift_positivity_quantum": "NO_CERTIFIED_MAP",
        },
        "minimal_activation_contract": {
            "artifact": "content-addressed executable 160-row q1 by support and zero-mode sector",
            "must_export": required_operator_fields + [
                "row_and_column_degree_table",
                "exact_detector_smearing_matrix",
                "independent_q1_squared_replay",
            ],
            "then_compute": "exact canonical kernel/image bases and pi,i,h contraction before any observable promotion",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-apparatus-physical-reduction-nondefinition-after-replacement-112-v1",
        "result_id": "BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112",
        "setting_id": values["combined_q1"]["setting_id"],
        "claim_status": "NO_CERTIFIED_MAP_MISSING_EXECUTABLE_REPLACEMENT_Q1_BY_SECTOR",
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
        "reduction_disposition": payload["downstream_nondefinition"],
        "next_gate": "EXPORT_CONTENT_ADDRESSED_EXECUTABLE_160_ROW_Q1_BY_SUPPORT_AND_ZERO_MODE_SECTOR",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE audit imports the valid "
            "typed 160-row unary pushout, its positive-mixed replacement base "
            "and the material parent by content hash. It does not retract the "
            "compositional action, nilpotency, cyclicity, K-covariance, full-"
            "rank pairing or leading coordinate-level rank-two result. It "
            "does establish that physical reduction is not defined by the "
            "exported machine-readable data. The combined payload describes "
            "q1 as an action pushout and records zero identity defects, but it "
            "exports no coefficient ring, operator schema, bidegree blocks, "
            "sparse entries, chain groups by support category or zero-mode "
            "operator blocks. The replacement payload likewise describes the "
            "changed Hessian compositionally. In particular, its changed Phi2 "
            "affects nonrod unary rows, so the executable old 108-row replay "
            "cannot be imported as replacement cohomology. Principal symbols "
            "and zero defect counts do not determine kernels or images. Hence "
            "no exact graded cohomology, projection, inclusion, contraction, "
            "descended pairing, radical, signature, real/K action, persistent "
            "memory class or reduced detector rank is promoted. The exact "
            "activation contract is a content-addressed executable 160-row q1 "
            "for every declared support and zero-mode sector, with row/column "
            "degrees, detector-smearing matrix and an independent square "
            "replay. Only then may canonical kernel/image bases and pi,i,h be "
            "computed. This nondefinition makes no Z2, redshift, positivity, "
            "q2/q3, particle or quantum claim."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_apparatus_physical_reduction_nondefinition_after_replacement_112 --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_apparatus_physical_reduction_nondefinition_after_replacement_112",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger apparatus physical-reduction nondefinition

The typed 160-row unary carrier exists, but its exported payload contains an
action-level composition and identity counts rather than executable q1 entries
by support and zero-mode sector.  Exact kernels, images and contraction data
therefore cannot be computed without importing the forbidden old 108-row
complex.  Physical classes and reduced detector rank remain NO_CERTIFIED_MAP.
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
