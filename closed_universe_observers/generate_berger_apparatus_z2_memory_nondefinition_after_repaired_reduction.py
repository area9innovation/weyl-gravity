#!/usr/bin/env python3
"""Certify Z2 and detector-memory nondefinition after failed physical reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION.json"
PAYLOAD = P / "certificates/BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION_PAYLOAD.json"
SCHEMA = P / "schema/berger-apparatus-z2-memory-nondefinition-after-repaired-reduction-v1.schema.json"
REPORT = P / "reports/berger-apparatus-z2-memory-nondefinition-after-repaired-reduction.md"
DEPENDENCIES = {
    "combined_q1": P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112.json",
    "combined_payload": P / "certificates/BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112_PAYLOAD.json",
    "physical_reduction": P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112.json",
    "physical_reduction_payload": P / "certificates/BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112_PAYLOAD.json",
    "abstract_cone_theorem": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "pre_repair_receiver_contract": P / "certificates/BERGER_APPARATUS_SAME_BACKGROUND_Z2_RECEIVER_CONTRACT.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for cert_name, payload_name in (
        ("combined_q1", "combined_payload"),
        ("physical_reduction", "physical_reduction_payload"),
    ):
        if sha256(DEPENDENCIES[payload_name]) != values[cert_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert_name} payload hash mismatch")
    if values["combined_q1"]["atlas_status"] != "CERTIFIED":
        raise AssertionError("terminal combined q1 is not certified")
    if values["physical_reduction"]["atlas_status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("physical-reduction stop condition drifted")
    if set(values["physical_reduction"]["reduction_disposition"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("physical-reduction disposition drifted")

    required_q1 = values["physical_reduction_payload"]["executable_reduction_audit"]["required_operator_fields"]
    combined_q1_keys = sorted(values["combined_payload"]["complete_q1"])
    present_q1 = sorted(set(required_q1) & set(combined_q1_keys))
    if present_q1:
        raise AssertionError("combined payload unexpectedly gained executable reduction fields")
    correction_classes = {
        "bounded_or_quasiperiodic": "NO_CERTIFIED_MAP",
        "smooth_secular": "NO_CERTIFIED_MAP",
        "causal_or_retarded": "NO_CERTIFIED_MAP",
    }
    return {
        "schema": "closed-universe-berger-apparatus-z2-memory-nondefinition-after-repaired-reduction-payload-v1",
        "result_id": "BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION_PAYLOAD",
        "terminal_prerequisite_replay": {
            "combined_q1_atlas_status": values["combined_q1"]["atlas_status"],
            "combined_row_count": values["combined_payload"]["carrier"]["row_count"],
            "physical_reduction_atlas_status": values["physical_reduction"]["atlas_status"],
            "physical_reduction_claim_status": values["physical_reduction"]["claim_status"],
            "required_executable_q1_fields": required_q1,
            "combined_complete_q1_keys": combined_q1_keys,
            "required_fields_present": present_q1,
            "independent_verdict": "NO_EXECUTABLE_Q1_KERNEL_IMAGE_OR_CONTRACTION_DATA",
        },
        "abstract_theorem_scope": {
            "result_state": values["abstract_cone_theorem"]["result_state"],
            "formula": values["abstract_cone_theorem"]["theorem"]["formula"],
            "Berger_carrier_map": "NO_CERTIFIED_MAP",
            "reason": "an abstract image/cokernel criterion does not supply Berger q1 cohomology, a quadratic source, or correction-class receivers",
        },
        "undefined_receiver_chain": {
            "physical_preparation_classes_in_H1": "NO_CERTIFIED_MAP",
            "physical_detector_and_memory_classes": "NO_CERTIFIED_MAP",
            "projection_inclusion_contraction": "NO_CERTIFIED_MAP",
            "action_derived_combined_q2": "NO_CERTIFIED_MAP",
            "quadratic_source_on_preparation_span": "NO_CERTIFIED_MAP",
            "complete_quadratic_output_closure": "NO_CERTIFIED_MAP",
            "stabilizer_moment_and_Taub_maps": "NO_CERTIFIED_MAP",
            "reduced_adjoint_cokernel_and_resonance_pairings": "NO_CERTIFIED_MAP",
            "correction_class_ideals": "NO_CERTIFIED_MAP",
            "Berger_Z2_locus": "NO_CERTIFIED_MAP",
            "detector_response_restricted_to_Z2": "NO_CERTIFIED_MAP",
            "nonlinear_response_rank_and_kernel": "NO_CERTIFIED_MAP",
            "persistent_relational_memory_on_Z2": "NO_CERTIFIED_MAP",
        },
        "correction_class_disposition": correction_classes,
        "operational_disposition": {
            "linearly_detectable_but_nonlinearly_obstructed": "NO_CERTIFIED_MAP",
            "balanced_detectable_combinations": "NO_CERTIFIED_MAP",
            "exceptional_resonant_operational_signature": "NO_CERTIFIED_MAP",
            "observer_coupling_adds_or_removes_source_channel": "NO_CERTIFIED_MAP",
            "memory_survives_gauge_reduction": "NO_CERTIFIED_MAP",
            "leading_coordinate_rank_two": "CERTIFIED_IN_LINEAR_PARENT_SCOPE_ONLY",
        },
        "forbidden_substitutions": {
            "old_108_row_q2": "REJECTED: it is not a coderivation on the replacement 160-row carrier",
            "compact_product_tangent_cone": "REJECTED: no background/carrier crosswalk exists",
            "raw_apparatus_rows_as_observables": "REJECTED: physical q1 classes and contraction are undefined",
            "abstract_theorem_as_receiver": "REJECTED: it supplies a criterion, not Berger source or cokernel data",
            "leading_rank_two_as_nonlinear_rank": "REJECTED: Z2 membership and restriction are undefined",
        },
        "minimal_activation_contract": {
            "first": values["physical_reduction_payload"]["minimal_activation_contract"],
            "then": [
                "export an action-derived combined q2 on the same executable 160-row carrier",
                "construct physical preparation and detector-memory representatives using pi_cl,i,h",
                "construct same-background stabilizer, adjoint-cokernel and correction-class receivers",
                "form each exact Berger Z2 ideal and only then restrict detector response and memory",
            ],
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-apparatus-z2-memory-nondefinition-after-repaired-reduction-v1",
        "result_id": "BERGER_APPARATUS_Z2_MEMORY_NONDEFINITION_AFTER_REPAIRED_REDUCTION",
        "setting_id": values["combined_q1"]["setting_id"],
        "claim_status": "NO_CERTIFIED_MAP_PHYSICAL_REDUCTION_PRECONDITION_FAILED",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "correction_class_disposition": payload["correction_class_disposition"],
        "observer_disposition": payload["operational_disposition"],
        "next_gate": "EXPORT_EXECUTABLE_160_ROW_Q1_AND_PHYSICAL_CONTRACTION_BEFORE_COMBINED_Q2_OR_Z2",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE successor imports by content hash the terminal certified typed 160-row unary pushout, the terminal physical-reduction nondefinition, the abstract correction-class-sensitive finite-harmonic tangent-cone theorem and the earlier same-background receiver contract. It independently replays the first failed prerequisite: none of the coefficient ring, operator schema, bidegree blocks, sparse q1 entries, support-sector chain groups or zero-mode matrices required for exact kernels and images occurs in the combined payload. Consequently no pi_cl, inclusion or homotopy, no physical emitter-preparation class, and no physical detector or persistent-memory class is defined. This stops the requested calculation before a quadratic source may be formed. In particular there is no action-derived combined q2 on physical classes, no exhaustive Berger output closure, no stabilizer moment/Taub receiver, no complementary reduced adjoint cokernel, no resonant pairing and no correction-class ideal. The bounded/quasiperiodic, smooth secular and causal/retarded cones are separately typed and all remain NO_CERTIFIED_MAP; none is inferred from another. The abstract theorem remains certified only as an image/cokernel criterion and supplies no Berger carrier map or Green theorem. Therefore individual or balanced Z2 membership, linearly detectable but nonlinearly obstructed modes, the exceptional resonant operational signature, observer source-channel changes, the detector response restricted to Z2, nonlinear rank/kernel and persistent relational memory on Z2 are undefined. The prior coordinate-level leading rank-two response is retained only in its linear parent scope and is not called a reduced or nonlinear observable. The old 108-row q2, compact-product modes, raw apparatus rows and formal secular inverses are explicitly rejected as substitutions. This result does not establish that any preparation is nonlinearly obstructed, nor does it establish redshift, recoil, positivity, particle or quantum data. Activation first requires the content-addressed executable 160-row q1 and exact physical contraction specified by the terminal reduction certificate; only afterwards may a same-carrier action-derived q2 and Berger receivers be constructed."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_apparatus_z2_memory_nondefinition_after_repaired_reduction --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_apparatus_z2_memory_nondefinition_after_repaired_reduction",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger apparatus Z2 and memory nondefinition after repaired reduction

The repaired typed 160-row unary pushout is certified, but its terminal
physical-reduction gate is `NO_CERTIFIED_MAP`: the machine payload supplies
no executable sectorwise q1, kernel/image bases or contraction.  Therefore
the two preparations and detector-memory rows have no physical classes on
which to evaluate the quadratic source.  All three correction-class Berger
Z2 loci, restricted response ranks and persistent memories remain
`NO_CERTIFIED_MAP`.  This does not classify any mode as nonlinearly
obstructed; it certifies that the required same-background receiver is
undefined until the physical-reduction activation contract is met.
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
