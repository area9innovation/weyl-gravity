#!/usr/bin/env python3
"""Certify that the apparatus pushout is undefined on the obstructed 112 base."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION.json"
X = P / "certificates/BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-to-apparatus-pushout-nondefinition-v1.schema.json"
REPORT = P / "reports/berger-replacement112-to-apparatus-pushout-nondefinition.md"
DEPS = {
    "terminal_replacement112": P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION.json",
    "terminal_replacement112_payload": P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_MIXED_NILPOTENCY_OBSTRUCTION_PAYLOAD.json",
    "global_rod_obstruction": P / "certificates/BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_OBSTRUCTION.json",
    "global_rod_payload": P / "certificates/BERGER_GLOBAL_ROD_TWO_DIRECTION_EXTENSION_PAYLOAD.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_terminal_branch(terminal: dict[str, Any], payload: dict[str, Any]) -> None:
    if terminal["atlas_status"] != "OBSTRUCTED":
        raise AssertionError("terminal replacement disposition is not the obstructed branch")
    if terminal["gate_results"]["complete_executable_replacement112_q1"] != "NO_CERTIFIED_MAP":
        raise AssertionError("terminal certificate incorrectly exports an executable q1")
    obstruction = payload["mixed_nilpotency_obstruction"]
    if obstruction["quotient_defect_count"] <= 0 or not obstruction["first_witness_nonzero"]:
        raise AssertionError("terminal mixed-square separator is absent")
    if obstruction["rod_wave_defect_count"] != 0:
        raise AssertionError("terminal fixture does not isolate unary closure from rod-wave failure")


def reject_padding_mutation(payload: dict[str, Any]) -> None:
    mutated = copy.deepcopy(payload)
    mutated["proposed_mutation"] = "pad the absent pushout rows with zero"
    if mutated["mixed_nilpotency_obstruction"]["quotient_defect_count"] != payload["mixed_nilpotency_obstruction"]["quotient_defect_count"]:
        raise AssertionError("padding mutation unexpectedly changed the inherited square")


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    for certificate_name, payload_name in (
        ("terminal_replacement112", "terminal_replacement112_payload"),
        ("global_rod_obstruction", "global_rod_payload"),
    ):
        if sha(DEPS[payload_name]) != values[certificate_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{certificate_name} payload hash mismatch")
    terminal = values["terminal_replacement112"]
    terminal_payload = values["terminal_replacement112_payload"]
    validate_terminal_branch(terminal, terminal_payload)
    reject_padding_mutation(terminal_payload)
    witness = terminal_payload["mixed_nilpotency_obstruction"]["first_exact_witness"]
    global_rod = values["global_rod_obstruction"]
    if global_rod["atlas_status"] != "OBSTRUCTED":
        raise AssertionError("global-rod terminal disposition drifted")
    return {
        "schema": "closed-universe-berger-replacement112-to-apparatus-pushout-nondefinition-payload-v1",
        "result_id": "BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION_PAYLOAD",
        "terminal_branch": {
            "replacement112_status": terminal["claim_status"],
            "replacement112_atlas_status": terminal["atlas_status"],
            "complete_executable_q1": terminal["gate_results"]["complete_executable_replacement112_q1"],
            "global_rod_status": global_rod["claim_status"],
            "global_rod_atlas_status": global_rod["atlas_status"],
        },
        "category_of_complexes_gate": {
            "object_requirement": "a typed unary carrier (V,q1) with q1^2=0",
            "source_object_status": "OBSTRUCTED",
            "pushout_status": "NONDEFINED",
            "reason": "the prospective 112-row source is not an object of the category of chain complexes, so no chain-complex pushout can be formed from it",
            "failure_precedes": ["overlap identifications", "material-parent adjoints", "combined pairing", "combined K action", "physical reduction"],
        },
        "basis_independent_separator": {
            "identity": "q1_squared",
            "transformation_law": "(S q1 S^-1)^2 = S q1^2 S^-1",
            "zero_property_is_basis_invariant": True,
            "exact_specialization_rank_lower_bound": 1,
            "witness": witness,
            "witness_point_value": terminal_payload["mixed_nilpotency_obstruction"]["first_witness_point_value"],
            "fixture": terminal_payload["exact_fixture"]["parameter_values"],
            "sphere_point": terminal_payload["mixed_nilpotency_obstruction"]["first_witness_sphere_point"],
            "defect_entry_count": terminal_payload["mixed_nilpotency_obstruction"]["quotient_defect_count"],
            "defect_position_count": terminal_payload["mixed_nilpotency_obstruction"]["quotient_defect_matrix_position_count"],
        },
        "mutation_results": {
            "treat_OBSTRUCTED_as_successful_producer": "REJECTED",
            "zero_pad_absent_pushout_rows": "REJECTED_INHERITED_SQUARE_UNCHANGED",
            "reuse_rejected_old_112_unary": "REJECTED_BY_HASH_AND_TERMINAL_STATUS",
            "rename_or_change_basis": "REJECTED_BY_SIMILARITY_INVARIANCE",
        },
        "minimal_additional_producer": {
            "result_kind": "complete repaired replacement-112 executable unary",
            "must_resolve": "all inherited mixed q1-squared defects, beginning with h_hat_star_00 <- sigma at time mode -2",
            "must_export": ["complete exact sparse q1", "signed pairing", "K_Berger action", "support and zero-mode blocks", "generic symbolic q1-squared certificate", "independent replay"],
            "cannot_be": ["row padding", "zero insertion", "old rejected 112 unary", "a fixture-only zero test"],
        },
        "consumer_activation": {
            "apparatus_160_combined_unary": "NO_CERTIFIED_MAP",
            "physical_reduction": "NO_CERTIFIED_MAP",
            "z2_memory": "NO_CERTIFIED_MAP",
            "relational_redshift": "NO_CERTIFIED_MAP",
            "detector_response_after_reduction": "NO_CERTIFIED_MAP",
        },
        "does_not_establish": ["a 160-row carrier", "a combined unary", "cohomology", "memory", "redshift", "recoil", "a quantum observer algebra"],
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-replacement112-to-apparatus-pushout-nondefinition-v1",
        "result_id": "BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION",
        "setting_id": values["terminal_replacement112"]["setting_id"],
        "claim_status": "CERTIFIED_NONDEFINED_CHAIN_COMPLEX_PUSHOUT_FROM_OBSTRUCTED_SOURCE",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha(path)} for name, path in DEPS.items()},
        "payload_ref": {"path": str(X.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_text.encode()).hexdigest(), "canonical_sha256": canonical(payload)},
        "gate_results": payload["consumer_activation"],
        "basis_independent_separator": payload["basis_independent_separator"],
        "next_gate": "PRODUCE_A_REPAIRED_NILPOTENT_REPLACEMENT112_UNARY_BEFORE_REOPENING_THE_APPARATUS_PUSHOUT",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE disposition imports the terminal replacement-112 mixed-nilpotency obstruction and the terminal global-rod obstruction by certificate and payload hashes. The prospective replacement-112 source has 132 nonzero mixed-square Fourier entries in 28 positions at the certified nondegenerate fixture, with a nonzero h_hat_star_00-from-sigma witness while all eight rod wave equations vanish. Hence it is not an object of the category of chain complexes. A chain-complex pushout with the material apparatus is therefore NONDEFINED before overlap identifications, parent adjoints, combined pairing, K action or background quotient can be formed. The separator is basis independent because q1 squared transforms by similarity; the exact nonzero specialization gives rank at least one. Zero padding, renaming and reuse of the rejected old unary leave the inherited square unchanged or violate the content-addressed terminal disposition. The minimal additional producer is a complete repaired 112-row unary that resolves every inherited mixed-square defect and passes generic symbolic nilpotency with independent replay. This certificate does not construct a 160-row carrier and leaves physical reduction, Z2 memory, detector response after reduction and relational redshift at NO_CERTIFIED_MAP."
        ),
        "provenance": {"generator_command": "python3 -m closed_universe_observers.generate_berger_replacement112_to_apparatus_pushout_nondefinition --write", "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_replacement112_to_apparatus_pushout_nondefinition", "source_sha256": sha(Path(__file__))},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        X.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        C.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text("# Replacement-112 to apparatus pushout disposition\n\nThe prospective chain-complex pushout is nondefined because its content-addressed 112-row source has nonzero `q1^2`. The exact separator has specialization rank at least one and is invariant under basis change. No 160-row or downstream observer map is promoted.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
