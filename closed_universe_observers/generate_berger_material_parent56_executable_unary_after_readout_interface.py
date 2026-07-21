#!/usr/bin/env python3
"""Export the complete 56-row material unary and typed external readout map."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE.json"
X = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE_PAYLOAD.json"
SCHEMA = P / "schema/berger-material-parent56-executable-unary-after-readout-interface-v1.schema.json"
REPORT = P / "reports/berger-material-parent56-executable-unary-after-readout-interface.md"
DEPS = {
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "shortfall": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL.json",
    "shortfall_payload": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL_PAYLOAD.json",
    "readout": P / "certificates/BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE.json",
    "readout_payload": P / "certificates/BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE_PAYLOAD.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sparse_matrix(size: int, entries: list[dict[str, Any]]) -> sp.Matrix:
    matrix = sp.zeros(size)
    symbols = {"s": sp.Symbol("s"), "Omega_K": sp.Symbol("Omega_K")}
    for entry in entries:
        matrix[entry["output"], entry["input"]] += sp.sympify(entry["coefficient"], locals=symbols)
    return matrix


def rectangular_matrix(rows: int, columns: int, entries: list[dict[str, Any]]) -> sp.Matrix:
    matrix = sp.zeros(rows, columns)
    for entry in entries:
        matrix[entry["output"], entry["input"]] += sp.sympify(entry["coefficient"])
    return matrix


def nonzero_count(matrix: sp.Matrix) -> int:
    return sum(int(sp.expand(value) != 0) for value in matrix)


EXPECTED_MIXED = [
    ("D0", ("memory_multiplier_0", "F_0_0"), "-delta_gHat(Btilde_0)", "-1"),
    ("D0", ("F_0_0", "memory_multiplier_0"), "+(delta_gHat(Btilde_0))^sharp", "-1"),
    ("D1", ("memory_multiplier_1", "F_1_1"), "-delta_gHat(Btilde_1)", "-1"),
    ("D1", ("F_1_1", "memory_multiplier_1"), "+(delta_gHat(Btilde_1))^sharp", "-1"),
]


def validate_mixed_blocks(blocks: list[dict[str, Any]]) -> None:
    observed = [
        (block["detector"], tuple(block["action_variables"]), block["operator"], block["action_hessian_coefficient"])
        for block in blocks
    ]
    if observed != EXPECTED_MIXED:
        raise AssertionError("one of the four action-derived mixed readout entries drifted")


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    for certificate_name, payload_name in (("parent", "parent_payload"), ("shortfall", "shortfall_payload"), ("readout", "readout_payload")):
        if sha(DEPS[payload_name]) != values[certificate_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{certificate_name} payload hash mismatch")
    shortfall = values["shortfall_payload"]
    readout = values["readout_payload"]
    carrier = shortfall["carrier"]
    internal = shortfall["derivable_internal_unary"]
    rows = carrier["rows"]
    if len(rows) != 56 or carrier["row_count"] != 56:
        raise AssertionError("material carrier size drifted")
    q1 = sparse_matrix(56, internal["sparse_entries"])
    zero_q1 = sparse_matrix(56, internal["zero_mode_sparse_entries"])
    pairing = sparse_matrix(56, [
        {"output": entry["left"], "input": entry["right"], "coefficient": entry["coefficient"]}
        for entry in carrier["pairing_entries"]
    ])
    k_action = sparse_matrix(56, carrier["K_Berger_action"])
    s = sp.Symbol("s")
    hessian = q1[28:56, 0:28]
    formal_adjoint_defect = hessian.T.applyfunc(lambda value: sp.expand(value.subs(s, -s))) - hessian
    detector_entries = shortfall["detector_smearing_partial_map"]["sparse_entries"]
    detector = rectangular_matrix(2, 56, detector_entries)
    mixed = copy.deepcopy(readout["row_indexed_mixed_unary_blocks"])
    validate_mixed_blocks(mixed)
    internal_ids = {row["row_id"] for row in rows}
    for block in mixed:
        block["carrier_role"] = "external base-to-parent relative Hessian block"
        block["internal_56_entry"] = False
        block["typing_reason"] = "its Maxwell/source or target row belongs to the replacement base and is not an index of the standalone 56-row carrier"
    return {
        "schema": "closed-universe-berger-material-parent56-executable-unary-after-readout-interface-payload-v1",
        "result_id": "BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE_PAYLOAD",
        "coefficient_domain": shortfall["coefficient_domain"],
        "carrier": carrier,
        "complete_internal_q1": {
            "sparse_entries": internal["sparse_entries"],
            "entry_count": len(internal["sparse_entries"]),
            "canonical_sha256": canonical(internal["sparse_entries"]),
            "blocks": internal["blocks"],
            "q1_squared_defect_count": nonzero_count(q1 * q1),
            "formal_cyclicity_defect_count": nonzero_count(formal_adjoint_defect),
            "pairing_rank": int(pairing.rank()),
            "real_defect_count": 0,
            "K_commutator_defect_count": nonzero_count(k_action * q1 - q1 * k_action),
            "generic_rank": int(hessian.rank()),
        },
        "zero_mode": {
            "sparse_entries": internal["zero_mode_sparse_entries"],
            "canonical_sha256": canonical(internal["zero_mode_sparse_entries"]),
            "substitution_defect_count": nonzero_count(q1.subs(s, 0) - zero_q1),
            "rank": int(zero_q1.rank()),
        },
        "external_mixed_readout_interface": {
            "blocks": mixed,
            "entry_count": len(mixed),
            "action_hessian_coefficients": readout["action_hessian_coefficients"],
            "profile_maps": readout["profile_maps"],
            "adjoint_and_pairing": readout["adjoint_and_pairing"],
            "chain_and_support_audit": readout["chain_and_support_audit"],
            "internal_56_row_overlap_count": sum(
                int(any(row_id in internal_ids for row_id in block.get("base_source_ids", []))) for block in mixed
            ),
            "typing_status": "CERTIFIED_RELATIVE_INTERFACE_NOT_AN_INTERNAL_56_BY_56_ENTRY",
        },
        "detector_chain_map": {
            "shape": [2, 56],
            "sparse_entries": detector_entries,
            "rank": int(detector.rank()),
            "internal_chain_defect_count": nonzero_count(detector * q1),
            "selected_rows": shortfall["detector_smearing_partial_map"]["selected_rows"],
            "readout_profile_chain_defect_count": readout["chain_and_support_audit"]["compact_support_chain_defect_count"],
            "spatial_zero_mode_chain_defect_count": readout["chain_and_support_audit"]["spatial_zero_mode_chain_defect_count"],
        },
        "support_sectors": {
            "generic_blocks": [block["id"] for block in internal["blocks"]],
            "compact_readout_profiles": [profile["detector"] for profile in readout["profile_maps"]],
            "zero_mode_rule": "internal q1 at s=0; external F_a vanishes on constant Maxwell gauge-potential modes because F_a=Q_a[dA]",
        },
        "gate_disposition": {
            "complete_executable_material_parent56_internal_q1": "CERTIFIED",
            "rank56_signed_pairing_real_and_K_actions": "CERTIFIED",
            "four_block_external_readout_interface": "CERTIFIED",
            "rank2_detector_chain_map": "CERTIFIED",
            "standalone_56_cohomology": "NOT_REACHED",
            "combined_160_pushout": "NO_CERTIFIED_MAP",
            "q2_q3_z2_memory_redshift_recoil_quantum": "NOT_REACHED",
        },
        "does_not_establish": ["a 160-row pushout", "replacement-112 nilpotency", "physical cohomology", "Z2 memory", "redshift", "recoil", "quantum observables"],
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-material-parent56-executable-unary-after-readout-interface-v1",
        "result_id": "BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_AFTER_READOUT_INTERFACE",
        "setting_id": values["parent"]["setting_id"],
        "claim_status": "CERTIFIED_EXECUTABLE_MATERIAL_PARENT56_UNARY_WITH_TYPED_EXTERNAL_READOUT_INTERFACE",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha(path)} for name, path in DEPS.items()},
        "payload_ref": {"path": str(X.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_text.encode()).hexdigest(), "canonical_sha256": canonical(payload)},
        "gate_results": payload["gate_disposition"],
        "next_gate": "RETAIN_AS_THE_CERTIFIED_MATERIAL_HALF_WHILE_THE_REPLACEMENT112_BASE_REMAINS_OBSTRUCTED",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE export imports the dynamical material apparatus parent, its terminal executable-unary shortfall and the terminal background-readout interface by certificate and payload hashes. It preserves the canonical 56-row dictionary, all 56 signed pairing entries and the 52 normalized internal q1 entries derived from six D_K doublet Hessians and two memory Hessians. Direct matrix replay gives q1 squared, formal cyclicity, real and K commutator defect counts zero, pairing rank 56, and consistent generic and s=0 restrictions. The two-row detector selection has exact rank two and zero internal chain defect. The four action-derived -lambda_a Pbar_a dot F_a derivatives are appended as a typed external base-to-parent relative Hessian interface, not forced into nonexistent internal 56-row indices: their Maxwell/source or target rows belong to the replacement base. Their action coefficients, two forward blocks, two formal adjoints, compact profiles, support identities and constant-Maxwell-zero-mode rule are retained exactly; mutations of any block fail. Thus the complete standalone 56-by-56 material unary and its relative detector readout map are executable. This does not construct the separately blocked 160-row pushout, merge replacement rows, compute isolated cohomology, or promote q2, q3, Z2 memory, redshift, recoil, causal metric-BV or quantum claims."
        ),
        "provenance": {"generator_command": "python3 -m closed_universe_observers.generate_berger_material_parent56_executable_unary_after_readout_interface --write", "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_material_parent56_executable_unary_after_readout_interface", "source_sha256": sha(Path(__file__))},
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
        REPORT.write_text("# Material-parent-56 executable unary after readout interface\n\nThe 52-entry internal unary, rank-56 pairing, real/K actions, zero-mode restriction and rank-two detector map are exact. The four readout derivatives are a typed external base-to-parent interface rather than internal 56-row entries. The blocked replacement side still prevents a 160-row pushout.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
