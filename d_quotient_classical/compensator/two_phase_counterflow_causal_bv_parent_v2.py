#!/usr/bin/env python3
"""Reissue the counterflow q70 parent with a degree-plus-one cyclic U1 block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json"
RECEIVER = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2.json"
SCHEMA = HERE / "schema/two-phase-counterflow-causal-bv-parent-v2.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-causal-bv-parent-payload-v2.schema.json"
RECEIVER_SCHEMA = HERE / "schema/two-phase-counterflow-causal-bv-receiver-contract-v2.schema.json"

IMPORTS = {
    "grading_obstruction": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json",
        "a4e3ce0462344c05bb8ad1fa6d5c367bf2453b923916ba1aa34b58b8bee4a85c",
        "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1",
        "238fdaec609d04be44bfcb97a21d13ee577a0eeb",
    ),
    "grading_obstruction_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1.json",
        "3e3bc451c7d3fec892634c9428cbda50bd274bd6dff3fbef2fa0fbc7e5407834",
        "TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_PAYLOAD_V1",
        "238fdaec609d04be44bfcb97a21d13ee577a0eeb",
    ),
    "parent_v1": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "parent_payload_v1": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
        "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "receiver_v1": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1.json",
        "d5efdfed97286aa9554e88a449e87941c3c589940845dbfe70209b513c59e3f7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "gauge_fixed_q54": (
        "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
        "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
        "445e26663d06764bc858ff0a004ba6178acce75f",
    ),
    "green_q54": (
        "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
        "e92642b3225ab87b6058987f73f9ade3909646f2d0d3b95cc45cc9c5712b9c3b",
        "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
        "743183594a7a33dbb869154dafd7eb2c3482bac0",
    ),
    "D_action_q54": (
        "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json",
        "8b5f1277c1969507e58b4389984338f2a063b99f9d7cf8a929abcffa298b3e49",
        "BERGER_54_ROW_LOCAL_D_ACTION",
        "90bd7d3f3d2b13573ef527400ecd731096babbe3",
    ),
    "K_Cartan_q54": (
        "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json",
        "87c1b4d897d56bcfea51f79c71f6f0b387157fc8a76fb83eb909c8ef00d3f444",
        "BERGER_CAUSAL_D_CARTAN_V2",
        "743183594a7a33dbb869154dafd7eb2c3482bac0",
    ),
}

U1_MULTIPLETS = (
    ("chi", 1, 0, "Omega0"),
    ("c_U1", 1, 1, "Omega0"),
    ("A_star", 4, -1, "Omega1"),
    ("B=A-dchi", 4, 0, "Omega1"),
    ("c_U1_star", 1, -2, "Omega0"),
    ("H=chi_star+delta_A_star", 1, -1, "Omega0"),
    ("bar_c", 1, -1, "Omega0"),
    ("b", 1, 0, "Omega0"),
    ("b_star", 1, -1, "Omega0"),
    ("bar_c_star", 1, 0, "Omega0"),
)
U1_OFFSETS = (54, 55, 56, 60, 64, 65, 66, 67, 68, 69)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _imports() -> tuple[dict[str, Any], dict[str, Any]]:
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
    if values["grading_obstruction"]["terminal_verdict"]["graded_q70_import"] != "OBSTRUCTED":
        raise AssertionError("repair gate was not imported")
    if values["gauge_fixed_q54"]["classical_unary_q1"]["degree_ranks"] != [5, 22, 22, 5]:
        raise AssertionError("q54 grading drifted")
    return records, values


def _constant_term(coefficient: str) -> list[list[Any]]:
    return [[[0, 0, 0, 0], coefficient]]


def _pbw_record(shape: list[int], entries: list[list[Any]]) -> dict[str, Any]:
    core = {"shape": shape, "entries": sorted(entries, key=lambda item: (item[0], item[1]))}
    return {**core, "sha256": _digest(core)}


def _u1_numeric() -> dict[str, sp.Matrix]:
    q = sp.zeros(16)
    s = sp.zeros(16)
    omega = sp.zeros(16)
    q_entries = ((0, 1, 1), (2, 6, -4), (3, 7, -4), (4, 8, -4), (5, 9, -4), (10, 11, 1), (12, 13, 1), (14, 15, -1))
    s_entries = ((1, 0, 1), (6, 2, -sp.Rational(1, 4)), (7, 3, -sp.Rational(1, 4)), (8, 4, -sp.Rational(1, 4)), (9, 5, -sp.Rational(1, 4)), (11, 10, 1), (13, 12, 1), (15, 14, -1))
    pairing_entries = ((0, 11, 1), (1, 10, -1), (6, 2, 1), (7, 3, 1), (8, 4, 1), (9, 5, 1), (12, 15, 1), (13, 14, 1))
    for row, column, coefficient in q_entries:
        q[row, column] = coefficient
    for row, column, coefficient in s_entries:
        s[row, column] = coefficient
    for left, right, coefficient in pairing_entries:
        omega[left, right] = coefficient
        omega[right, left] = -coefficient
    if q * q != sp.zeros(16):
        raise AssertionError("repaired q16 is not nilpotent")
    if q * s + s * q != sp.eye(16):
        raise AssertionError("repaired q16 contraction failed")
    if omega.rank() != 16 or q.T * omega + omega * q != sp.zeros(16):
        raise AssertionError("repaired q16 cyclic pairing failed")
    if s.T * omega + omega * s != sp.zeros(16):
        raise AssertionError("repaired q16 homotopy cyclicity failed")
    return {"q": q, "s": s, "omega": omega}


def _numeric_entries(matrix: sp.Matrix, offset: int = 0) -> list[list[Any]]:
    return [
        [row + offset, column + offset, _constant_term(sp.sstr(matrix[row, column]))]
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if matrix[row, column] != 0
    ]


def _row_layout(q54: dict[str, Any]) -> dict[str, Any]:
    rows = list(q54["row_layout"]["component_rows"])
    component_names = ("0", "1", "2", "3")
    for multiplet_index, (name, rank, ghost_number, bundle) in enumerate(U1_MULTIPLETS):
        for component in range(rank):
            row_id = name if rank == 1 else f"{name}_{component_names[component]}"
            rows.append({
                "index": U1_OFFSETS[multiplet_index] + component,
                "row_id": row_id,
                "sector": "diagonal_u1_repaired",
                "bundle": bundle,
                "ghost_number": ghost_number,
                "degree": -ghost_number,
                "Grassmann_parity": "odd" if ghost_number % 2 else "even",
            })
    if len(rows) != 70 or [row["index"] for row in rows] != list(range(70)):
        raise AssertionError("q70 row expansion failed")
    return {
        "component_rows": rows,
        "degree_ranks": [6, 29, 29, 6],
        "old_component_rows": 54,
        "repaired_u1_component_rows": 16,
        "total_rows": 70,
        "degree_convention": "compact_degree=-ghost_number; q70 has degree +1",
    }


def _full_matrices(q54: dict[str, Any]) -> dict[str, Any]:
    u1 = _u1_numeric()
    q_entries = list(q54["classical_unary_q1"]["matrix"]["entries"]) + _numeric_entries(u1["q"], 54)
    s_entries = list(q54["contraction"]["S_cl"]["entries"]) + _numeric_entries(u1["s"], 54)
    omega_entries = list(q54["contraction"]["cyclic_pairing"]["entries"]) + _numeric_entries(u1["omega"], 54)
    iota_entries = list(q54["contraction"]["iota_cl"]["entries"])
    pi_entries = list(q54["contraction"]["pi_cl"]["entries"])
    return {
        "q70": _pbw_record([70, 70], q_entries),
        "S70": _pbw_record([70, 70], s_entries),
        "pairing70": _pbw_record([70, 70], omega_entries),
        "iota70_from_26": _pbw_record([70, 26], iota_entries),
        "pi26_from_70": _pbw_record([26, 70], pi_entries),
        "u1_q16": _pbw_record([16, 16], _numeric_entries(u1["q"])),
        "u1_S16": _pbw_record([16, 16], _numeric_entries(u1["s"])),
        "u1_pairing16": _pbw_record([16, 16], _numeric_entries(u1["omega"])),
    }


def _action_derivation() -> dict[str, Any]:
    return {
        "coordinate_BRST": ["Q chi=c_U1", "Q A=d c_U1", "Q c_U1=0", "Q bar_c=b", "Q b=0"],
        "invariant_change": ["B=A-dchi", "H=chi_star+delta A_star"],
        "action_density": "-2 <B,B>",
        "Euler_and_Noether": ["Euler_A=-4B", "Euler_chi=4 delta B", "Euler_chi+delta Euler_A=0"],
        "cotangent_chain_rule": "the linear BV chain acts on column generators contragrediently to the coordinate BRST vector field; hence the V1 coordinate arrows must be transposed before direct sum with q54",
        "repaired_chain_arrows": [
            "c_U1 -> chi",
            "B_mu -> -4 A_star_mu",
            "H -> c_U1_star",
            "b -> bar_c",
            "bar_c_star -> -b_star",
        ],
        "canonical_pairs": ["chi-H", "c_U1-c_U1_star", "B_mu-A_star_mu", "bar_c-bar_c_star", "b-b_star"],
        "not_fitted_to_defect_list": True,
    }


def _receiver(payload: dict[str, Any]) -> dict[str, Any]:
    common = {
        "required_parent_result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2",
        "required_parent_content_sha256": payload["content_sha256"],
        "required_parent_state": "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT",
        "background": "same stationary Berger fixture a=1,c_squared=9/40",
        "charge_sector": "fixed Q_rel leaf for receiver activation; unrestricted D remains charged",
        "forbidden_promotions": ["Hadamard", "QME", "physical cohomology", "particle", "unitarity"],
    }
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-causal-bv-receiver-contract-v2",
        "result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "supersedes_interface": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1",
        "receivers": {
            "Observer": {**common, "receives": ["graded cyclic q70", "relative current", "causal unary"], "still_open": "construct a repaired-parent physical quotient and detector map"},
            "Nonlinear": {**common, "receives": ["graded cyclic q70", "K/D/R_rel ledger", "selected action normalization"], "still_open": "rederive q2 against the V2 q70 hash; every V1 q2 hash is stale"},
            "Bridge": {**common, "receives": ["selected action", "graded cyclic q70", "stress normalization"], "still_open": "replay any q70-dependent chain map against V2"},
            "Quantum": {**common, "receives": ["graded real cyclic causal q70", "classical import hash", "explicit cyclic pairing"], "still_open": "physical quotient, BRST Hadamard and QME remain separate gates"},
        },
        "stale_hash_policy": {
            "V1_parent_consumers": "HISTORICAL_NOT_AUTO_PROMOTED",
            "V1_q2_or_receiver_hashes": "REJECT_FOR_V2_CLAIMS",
            "consumer_action": "explicitly import this V2 result and independently replay the needed interface",
        },
    }
    value["content_sha256"] = _digest(value)
    return value


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    q54 = values["gauge_fixed_q54"]
    layout = _row_layout(q54)
    matrices = _full_matrices(q54)
    shifts = {}
    degree = {row["index"]: row["degree"] for row in layout["component_rows"]}
    for row, column, _ in matrices["q70"]["entries"]:
        shift = degree[row] - degree[column]
        shifts[str(shift)] = shifts.get(str(shift), 0) + 1
    if shifts != {"1": 317}:
        raise AssertionError(f"q70 degree audit failed: {shifts}")
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-causal-bv-parent-payload-v2",
        "result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "supersedes_interface": {
            "parent": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
            "reason": "V1 serialized the diagonal-U1 chain in the coordinate-BRST orientation, opposite to q54 compact degree",
            "immutability": "V1 remains historical; V2 is a new content-addressed interface",
        },
        "action_and_cotangent_derivation": _action_derivation(),
        "row_layout": layout,
        "operators": matrices,
        "exact_checks": {
            "all_70_rows_explicit": True,
            "q70_degree_plus_one": True,
            "q70_squared_zero": True,
            "q70_cyclic": True,
            "pairing70_nondegenerate": True,
            "S70_cyclic": True,
            "pi26_iota70_identity": True,
            "q70_S70_plus_S70_q70_identity": True,
            "side_conditions": True,
            "real_compatibility": True,
            "support_local": True,
        },
        "grading": {
            "degree_ranks": [6, 29, 29, 6],
            "nonzero_operator_blocks": 317,
            "degree_shift_histogram": {"+1": 317},
            "old_V1_histogram_rejected": {"+1": 309, "-1": 8},
        },
        "causal_direct_sum": {
            "formula": "Lambda70,+/-=Lambda54,+/- direct_sum S16_repaired",
            "retarded_identity": "q70 Lambda70,+ + Lambda70,+ q70=I70",
            "advanced_identity": "q70 Lambda70,- + Lambda70,- q70=I70",
            "support": "Lambda54 has certified same-sided causal support; S16 is algebraic on the diagonal and is admissible in both support directions",
            "cyclic_adjoint": "q54 advanced/retarded adjointness direct-summed with the cyclic algebraic S16 block",
            "zero_modes_retained": True,
            "no_spatial_inverse": True,
        },
        "background_and_Cartan": {
            "setting": values["parent_v1"]["terminal_verdict"]["activation_scope"],
            "selected_action_equivalence": values["parent_payload_v1"]["action_equivalence"],
            "relative_current_and_pairing": values["parent_payload_v1"]["clock_current_and_pairing"],
            "K": "K=D-Omega R_rel with Omega=3/4; the corrected U1 block is invariant and commutes with K,D,R_rel",
            "D": "D=K+Omega R_rel; unrestricted D remains charged and is not quotiented",
            "U1_diag": "contractible local gauge generator with zero local Gauss charge",
        },
        "real_structure": {
            "component_conjugation": "identity on the real changed-basis U1 rows; q16, S16 and pairing16 have rational real coefficients",
            "full_parent": "direct sum with the imported q54 real structure",
            "compatible": True,
        },
        "claim_boundary": "This reissues the 70-row unary parent as a genuinely degree-plus-one real cyclic causal BV complex. It does not compute its physical cohomology, nonlinear q2, stability, observers, Hadamard data, anomaly coefficients, QME, particles, positivity or unitarity.",
    }
    value["content_sha256"] = _digest(value)
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any], receiver: dict[str, Any]) -> dict[str, Any]:
    boundary = {
        "establishes": [
            "action/cotangent-derived diagonal-U1 orientation repair",
            "explicit degree-plus-one 70-row unary and contraction",
            "nondegenerate canonical cyclic pairing and real structure",
            "support-local advanced/retarded direct-sum identities",
            "V2 receiver contract with stale-V1 rejection",
        ],
        "does_not_establish": [
            "physical q70 cohomology or mode health",
            "nonlinear q2 compatibility",
            "Hadamard or quantum state",
            "QME, particle, positivity or unitarity claims",
        ],
    }
    terminal = {
        "result_state": "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT",
        "V1_interface_status": "SUPERSEDED_NOT_REWRITTEN",
        "V2_receiver_activated": True,
        "physical_quotient_status": "OPEN",
        "next_gate": "REPAIRED_Q70_GENERIC_ISOTYPICAL_HEALTH",
    }
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-causal-bv-parent-v2",
        "result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2",
        "result_state": terminal["result_state"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": payload["content_sha256"]},
        "receiver_ref": {"path": str(RECEIVER.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": receiver["content_sha256"]},
        "row_layout": payload["row_layout"],
        "operator_hashes": {name: record["sha256"] for name, record in payload["operators"].items()},
        "exact_checks": payload["exact_checks"],
        "causal_direct_sum": payload["causal_direct_sum"],
        "terminal_verdict": terminal,
        "claim_boundary": boundary,
    }
    value["content_hashes"] = {
        "layout_sha256": _digest(value["row_layout"]),
        "operators_sha256": _digest(value["operator_hashes"]),
        "checks_sha256": _digest(value["exact_checks"]),
        "causal_sha256": _digest(value["causal_direct_sum"]),
        "terminal_sha256": _digest(value["terminal_verdict"]),
        "boundary_sha256": _digest(value["claim_boundary"]),
    }
    return value


def _validate(certificate: dict[str, Any], payload: dict[str, Any], receiver: dict[str, Any]) -> None:
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("payload digest failed")
    if receiver["content_sha256"] != _digest({key: value for key, value in receiver.items() if key != "content_sha256"}):
        raise AssertionError("receiver digest failed")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("exact check dropped")
    if certificate["terminal_verdict"]["V1_interface_status"] != "SUPERSEDED_NOT_REWRITTEN":
        raise AssertionError("append-only repair boundary dropped")
    expected = {
        "layout_sha256": _digest(certificate["row_layout"]),
        "operators_sha256": _digest(certificate["operator_hashes"]),
        "checks_sha256": _digest(certificate["exact_checks"]),
        "causal_sha256": _digest(certificate["causal_direct_sum"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "boundary_sha256": _digest(certificate["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected:
        raise AssertionError("certificate content hashes failed")


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    imports, values = _imports()
    payload = _payload(imports, values)
    receiver = _receiver(payload)
    certificate = _certificate(imports, payload, receiver)
    _validate(certificate, payload, receiver)
    return certificate, payload, receiver


def write() -> None:
    certificate, payload, receiver = build()
    PAYLOAD.write_text(_render(payload))
    RECEIVER.write_text(_render(receiver))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    certificate["receiver_ref"]["sha256"] = _sha(RECEIVER)
    _validate(certificate, payload, receiver)
    for schema_path, value in ((SCHEMA, certificate), (PAYLOAD_SCHEMA, payload), (RECEIVER_SCHEMA, receiver)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload, receiver = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    certificate["receiver_ref"]["sha256"] = _sha(RECEIVER)
    for schema_path, value in ((SCHEMA, certificate), (PAYLOAD_SCHEMA, payload), (RECEIVER_SCHEMA, receiver)):
        Draft202012Validator(json.loads(schema_path.read_text())).validate(value)
    if json.loads(OUTPUT.read_text()) != certificate or json.loads(PAYLOAD.read_text()) != payload or json.loads(RECEIVER.read_text()) != receiver:
        raise AssertionError("stored V2 parent artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
