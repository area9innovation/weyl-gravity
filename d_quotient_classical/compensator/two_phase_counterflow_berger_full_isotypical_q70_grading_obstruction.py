#!/usr/bin/env python3
"""Audit the graded q70 interface before constructing Berger isotypical quotients.

The fixed-j Peter--Weyl carrier is finite and invariant under every PBW word
appearing in q54.  The imported 16-component diagonal-U(1) table, however,
uses the opposite chain orientation from q54.  This producer records that
first exact obstruction and the convention-derived transpose repair without
silently changing the pinned causal parent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1.json"
SCHEMA = HERE / "schema/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-payload-v1.schema.json"

IMPORTS = {
    "scalar_obstruction": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1.json",
        "0d462cab26aead0409b8da64c13770b6eae61cdd4d5cfc6cf6efdf538f1d535e",
        "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1",
        "1fcfca7c599781721ce8256ddf41b8d5cc692885",
    ),
    "causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "causal_parent_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
        "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "gauge_fixed_q54": (
        "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
        "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
        "445e26663d06764bc858ff0a004ba6178acce75f",
    ),
    "peter_weyl_engine": (
        "closed_universe_observers/certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
        "e24c860b338188254c4388a7ca660ac454ba7b70c13659ffc36a98bf39250120",
        "BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE",
        "0b8fe045411de64008f55bb551ab3799aa85e77a",
    ),
}

U1_NAMES = (
    "chi",
    "c_U1",
    "A_star",
    "B=A-dchi",
    "c_U1_star",
    "H=chi_star+delta_A_star",
    "bar_c",
    "b",
    "b_star",
    "bar_c_star",
)
U1_GHOST_NUMBERS = (0, 1, -1, 0, -2, -1, -1, 0, -1, 0)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id, source_commit) in IMPORTS.items():
        path = ROOT / relative
        value = json.loads(path.read_text())
        actual = _sha(path)
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "source_commit": source_commit,
            "oracle_fields_consumed": [],
        }
        values[role] = value
    if values["causal_parent"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("q70 parent rank drifted")
    if values["gauge_fixed_q54"]["row_layout"]["total_rows"] != 54:
        raise AssertionError("q54 row ledger drifted")
    return records, values


def _q54_degree_audit(q54: dict[str, Any]) -> dict[str, Any]:
    degrees = {
        row["index"]: row["degree"] for row in q54["row_layout"]["component_rows"]
    }
    entries = q54["classical_unary_q1"]["matrix"]["entries"]
    shifts: dict[int, int] = {}
    defects = []
    for row, column, _ in entries:
        shift = degrees[row] - degrees[column]
        shifts[shift] = shifts.get(shift, 0) + 1
        if shift != 1:
            defects.append([row, column, shift])
    if shifts != {1: 309} or defects:
        raise AssertionError("q54 is not homogeneous of compact degree +1")
    return {
        "degree_convention": "compact_degree=-ghost_number on the linear BV chain",
        "component_degree_ranks": q54["row_layout"]["degree_ranks"],
        "nonzero_operator_blocks": len(entries),
        "degree_shift_histogram": {"+1": 309},
        "homogeneous_degree_plus_one": True,
    }


def _u1_degree_audit(parent_payload: dict[str, Any]) -> dict[str, Any]:
    extension = parent_payload["u1_minimal_nonminimal_extension"]
    if tuple(extension["changed_basis_order"]) != U1_NAMES:
        raise AssertionError("U1 changed-basis order drifted")
    ranks = tuple(extension["changed_basis_component_ranks"])
    if ranks != (1, 1, 4, 4, 1, 1, 1, 1, 1, 1):
        raise AssertionError("U1 component ranks drifted")
    degree = tuple(-number for number in U1_GHOST_NUMBERS)
    entries = extension["Q_changed_basis"]["entries"]
    rows = []
    serialized_histogram: dict[int, int] = {}
    repaired_histogram: dict[int, int] = {}
    expanded_count = 0
    for entry in entries:
        row = entry["row"]
        column = entry["column"]
        if ranks[row] != ranks[column]:
            raise AssertionError("U1 arrow has incompatible component ranks")
        multiplicity = ranks[row]
        expanded_count += multiplicity
        shift = degree[row] - degree[column]
        repaired_shift = -shift
        serialized_histogram[shift] = serialized_histogram.get(shift, 0) + multiplicity
        repaired_histogram[repaired_shift] = repaired_histogram.get(repaired_shift, 0) + multiplicity
        rows.append(
            {
                "serialized_arrow": f"{U1_NAMES[column]} -> {U1_NAMES[row]}",
                "component_multiplicity": multiplicity,
                "source_ghost_number": U1_GHOST_NUMBERS[column],
                "target_ghost_number": U1_GHOST_NUMBERS[row],
                "compact_degree_shift": shift,
                "transpose_repair_arrow": f"{U1_NAMES[row]} -> {U1_NAMES[column]}",
                "transpose_repair_shift": repaired_shift,
            }
        )
    if serialized_histogram != {-1: 8} or repaired_histogram != {1: 8}:
        raise AssertionError("U1 orientation audit drifted")
    return {
        "changed_basis_order": list(U1_NAMES),
        "component_ranks": list(ranks),
        "ghost_numbers": list(U1_GHOST_NUMBERS),
        "compact_degrees": list(degree),
        "serialized_multiplet_arrows": len(entries),
        "serialized_component_arrows": expanded_count,
        "serialized_degree_shift_histogram": {"-1": 8},
        "transpose_repair_degree_shift_histogram": {"+1": 8},
        "arrow_ledger": rows,
        "homogeneous_degree_plus_one": False,
        "exact_repair_candidate": "transpose Q_changed_basis and S_changed_basis before direct sum with q54",
    }


def _carrier() -> dict[str, Any]:
    return {
        "group": "SU(2)_L x U(1)_R on the biaxial Berger sphere",
        "label_domain": "two_j in Z_>=0, j=two_j/2, fixed m in {-j,...,j}; k is an internal weight, not a block label",
        "normalized_scalar_basis": "Y_jmk=sqrt((2*j+1)/Vol_Berger)*D^j_mk",
        "row_basis": "e_row tensor Y_jmk for row=0,...,69 and k=-j,...,j",
        "complex_dimension": "70*(2*j+1)",
        "inclusion": "iota_jm(e_row tensor e_k)=e_row Y_jmk",
        "projection": "pi_jm extracts the Y_jmk coefficient by the normalized L2 pairing",
        "pi_iota": "I_(70*(2*j+1))",
        "closure_proof": "every q54 coefficient is a finite PBW polynomial in e0,e1,e2,e3; e1,e2,e3 preserve the irreducible fixed-j Peter-Weyl space, e0 preserves it, and the U1 block is algebraic",
        "minimal_weight_closure": "for j>0 the e1/e2 ladder graph on k=-j,...,j is connected, so no nonempty proper k truncation is invariant",
        "right_neutral_warning": "for integer j>0, k=0 is an internal weight coupled to k=+/-1; it is not a standalone q70 subcomplex",
        "conjugation": "conjugate(Y_jmk)=(-1)^(m-k)Y_j,-m,-k; reality pairs the m and -m blocks",
        "ungraded_closure_status": "FINITE_COMPLETE",
        "graded_BV_subcomplex_status": "OBSTRUCTED_BY_IMPORTED_U1_ORIENTATION",
    }


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    q54 = _q54_degree_audit(values["gauge_fixed_q54"])
    u1 = _u1_degree_audit(values["causal_parent_payload"])
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "full_isotypical_carrier": _carrier(),
        "q54_grading_audit": q54,
        "u1_grading_audit": u1,
        "direct_sum_obstruction": {
            "equation": "q70_serialized=q54 direct_sum qU1_serialized",
            "degree_shift_histogram": {"+1": 309, "-1": 8},
            "single_homogeneous_BV_degree_exists": False,
            "nilpotency_is_not_sufficient": "q70_serialized^2=0 only defines an ungraded/Z2 complex; it does not supply the declared Z-graded BV chain or H^degree quotient",
            "first_failed_gate": "graded q70 import before cohomology, descended pairing, characteristics or Jordan data",
        },
        "cyclic_pairing_interface": {
            "q54_pairing": "explicit 54x54 cyclic pairing imported and homogeneous",
            "parent_u1_text": values["causal_parent_payload"]["u1_minimal_nonminimal_extension"]["cyclic_pairing"],
            "canonical_nonminimal_pairs_required_by_row_names": ["bar_c-bar_c_star", "b-b_star"],
            "parent_text_nonminimal_pairs": ["bar_c-b_star", "b-bar_c_star"],
            "status": "PAIRING_TEXT_ROW_MISMATCH_REQUIRES_REPAIR_EXPORT",
        },
        "repair_candidate": {
            "formula": "qU1_repaired=(qU1_serialized)^T; SU1_repaired=(SU1_serialized)^T",
            "degree_shift": "+1 on all 8 expanded component arrows",
            "algebraic_identities": ["qU1_repaired^2=0", "qU1_repaired SU1_repaired+SU1_repaired qU1_repaired=I16"],
            "support": "algebraic and support-local",
            "promotion_status": "NOT_APPLIED_TO_PINNED_PARENT",
            "required_follow_up": "regenerate the 70-row parent, explicit 16-row cyclic pairing, causal direct sum, receiver hashes and independent consumer from the corrected chain convention",
        },
        "mutation_ledger": {
            "anisotropy": "the imported nonzero scalar Hodge defect remains; the grading obstruction is geometry-independent",
            "round_limit": "u=v removes Hodge mixing but does not change the U1 degree shift",
            "omitted_row": "54+16=70 is required; deleting a row fails the complete parent inventory",
            "truncation_boundary": "deleting any k weight from a j>0 irrep leaves a nonzero e1/e2 boundary coupling",
            "transpose": "the transpose mutation changes every U1 component shift from -1 to +1 and is therefore the unique table-orientation repair",
        },
        "downstream_disposition": {
            "cohomology_quotient": "NOT_DEFINED_ON_SERIALIZED_Z_GRADED_PARENT",
            "descended_pairing_radical_inertia": "NOT_DEFINED_BEFORE_GRADED_CYCLIC_REPAIR",
            "characteristics_and_Jordan": "NOT_DEFINED_BEFORE_GRADED_CYCLIC_REPAIR",
            "spatial_principal_and_gradient": "NOT_DEFINED_BEFORE_GRADED_CYCLIC_REPAIR",
            "causal_parent_revoked": False,
            "scope": "the 54-row causal theorem and the algebraic contractibility of the U1 table remain valid separately; only their claimed graded q70 direct-sum interface is obstructed",
        },
    }
    value["content_sha256"] = _digest(value)
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    boundary = {
        "establishes": [
            "finite complete fixed-j all-k 70-row ungraded isotypical closure",
            "exact q54 plus-one versus serialized U1 minus-one grading mismatch",
            "convention-derived transpose repair candidate",
            "first exact obstruction to the requested graded q70 quotient",
        ],
        "does_not_establish": [
            "a repaired 70-row parent or receiver",
            "q70 cohomology, physical modes, pairing inertia, characteristics or stability",
            "an obstruction to the separately certified q54 causal complex",
            "Hadamard, observer, nonlinear, anomaly, QME, particle or unitarity claims",
        ],
    }
    terminal = {
        "result_state": "OBSTRUCTED_IMPORTED_Q70_GRADING_CONVENTION_REPAIR_REQUIRED",
        "ungraded_isotypical_closure": "CERTIFIED_FINITE_COMPLETE",
        "graded_q70_import": "OBSTRUCTED",
        "first_failed_gate": payload["direct_sum_obstruction"]["first_failed_gate"],
        "next_gate": "REPAIR_AND_REISSUE_DIAGONAL_U1_CHAIN_ORIENTATION_AND_CYCLIC_PAIRING",
    }
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1",
        "result_state": terminal["result_state"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "full_isotypical_carrier": payload["full_isotypical_carrier"],
        "grading_obstruction": payload["direct_sum_obstruction"],
        "repair_candidate": payload["repair_candidate"],
        "terminal_verdict": terminal,
        "claim_boundary": boundary,
    }
    value["content_hashes"] = {
        "carrier_sha256": _digest(value["full_isotypical_carrier"]),
        "obstruction_sha256": _digest(value["grading_obstruction"]),
        "repair_sha256": _digest(value["repair_candidate"]),
        "terminal_sha256": _digest(value["terminal_verdict"]),
        "boundary_sha256": _digest(value["claim_boundary"]),
    }
    return value


def _validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    if payload["content_sha256"] != _digest(
        {key: value for key, value in payload.items() if key != "content_sha256"}
    ):
        raise AssertionError("payload content hash mismatch")
    if certificate["grading_obstruction"]["single_homogeneous_BV_degree_exists"]:
        raise AssertionError("mixed-degree parent was promoted")
    if certificate["terminal_verdict"]["graded_q70_import"] != "OBSTRUCTED":
        raise AssertionError("graded import obstruction dropped")
    if certificate["repair_candidate"]["promotion_status"] != "NOT_APPLIED_TO_PINNED_PARENT":
        raise AssertionError("repair was silently promoted")
    if certificate["content_hashes"] != {
        "carrier_sha256": _digest(certificate["full_isotypical_carrier"]),
        "obstruction_sha256": _digest(certificate["grading_obstruction"]),
        "repair_sha256": _digest(certificate["repair_candidate"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "boundary_sha256": _digest(certificate["claim_boundary"]),
    }:
        raise AssertionError("certificate content hashes drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, values = _load_imports()
    payload = _payload(imports, values)
    certificate = _certificate(imports, payload)
    _validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    _validate(certificate, payload)
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    Draft202012Validator.check_schema(json.loads(PAYLOAD_SCHEMA.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if json.loads(OUTPUT.read_text()) != certificate:
        raise AssertionError("stored certificate drifted")
    if json.loads(PAYLOAD.read_text()) != payload:
        raise AssertionError("stored payload drifted")
    print("TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
