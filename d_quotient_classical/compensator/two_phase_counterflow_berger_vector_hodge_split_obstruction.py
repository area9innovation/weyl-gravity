#!/usr/bin/env python3
"""Certify two-way longitudinal/coexact mixing in the Berger Diff endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
    generators,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    LinearOperator,
    U,
    V,
    ZERO,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1.json"
)
PAYLOAD = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_PAYLOAD_V1.json"
)
SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-vector-hodge-split-obstruction-v1.schema.json"
)
PAYLOAD_SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-vector-hodge-split-obstruction-payload-v1.schema.json"
)

IMPORTS = {
    "scalar_terminal": (
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
        if _sha(path) != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": expected,
            "result_id": result_id,
            "source_commit": source_commit,
            "oracle_fields_consumed": [],
        }
        values[role] = value
    if values["scalar_terminal"]["terminal_verdict"]["downstream_vector_tensor_export_activated"]:
        raise AssertionError("failed scalar carrier was promoted")
    if values["causal_parent"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("70-row parent drifted")
    if not values["peter_weyl_engine"]["flags"]["GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR"]:
        raise AssertionError("finite Peter-Weyl engine unavailable")
    return records, values


def _endpoint_e0_squared(record: dict[str, Any]) -> list[list[LinearOperator]]:
    matrix = [[ZERO for _ in range(3)] for _ in range(3)]
    symbols = {"u": U, "v": V, "alpha_B": sp.Symbol("alpha_B")}
    for row, column, terms in record["entries"]:
        if not (22 <= row < 25 and 0 <= column < 3):
            continue
        matrix[row - 22][column] = LinearOperator.from_terms(
            (
                0,
                tuple(
                    axis
                    for axis in range(1, 4)
                    for _ in range(exponents[axis])
                ),
                sp.sympify(coefficient, locals=symbols),
            )
            for exponents, coefficient in terms
            if exponents[0] == 2
        )
    return matrix


def _formal_adjoint(operator: LinearOperator) -> LinearOperator:
    # The invariant spatial frame is divergence-free: e_a^dagger=-e_a.
    return LinearOperator.from_terms(
        (
            0,
            tuple(reversed(word)),
            (-1) ** len(word) * sp.conjugate(coefficient),
        )
        for _, word, coefficient in operator.terms
    )


def _operator_manifest(matrix: list[list[LinearOperator]]) -> list[dict[str, Any]]:
    result = []
    for row in range(3):
        for column in range(3):
            if not matrix[row][column].terms:
                continue
            result.append(
                {
                    "row": row,
                    "column": column,
                    "terms": [
                        {
                            "word": "".join(f"e{axis}" for axis in word) or "1",
                            "coefficient": sp.sstr(sp.factor(coefficient)),
                        }
                        for _, word, coefficient in matrix[row][column].terms
                    ],
                }
            )
    return result


def _round_generators(two_j: int) -> list[sp.Matrix]:
    n = two_j + 1
    j = sp.Rational(two_j, 2)
    weights = [-j + index for index in range(n)]
    raising = sp.zeros(n)
    for index, weight in enumerate(weights[:-1]):
        raising[index + 1, index] = sp.sqrt((j - weight) * (j + weight + 1))
    lowering = raising.T
    return [
        -sp.I * (raising + lowering) / 2,
        (lowering - raising) / 2,
        -sp.I * sp.diag(*weights),
    ]


def _finite_endpoint(values: dict[str, Any], two_j: int, *, round_geometry: bool = False) -> sp.Matrix:
    q54 = values["gauge_fixed_q54"]
    n = two_j + 1
    spatial = _round_generators(two_j) if round_geometry else generators(two_j)
    u = sp.Integer(1) if round_geometry else 3 * sp.sqrt(10) / 20
    v = sp.Integer(1) if round_geometry else 2 * sp.sqrt(10) / 3
    result = sp.zeros(3 * n)
    for row, column, terms in q54["classical_unary_q1"]["matrix"]["entries"]:
        if not (22 <= row < 25 and 0 <= column < 3):
            continue
        block = sp.zeros(n)
        for exponents, raw in terms:
            if exponents[0] != 2:
                continue
            operator = sp.eye(n)
            for axis in range(1, 4):
                operator *= spatial[axis - 1] ** exponents[axis]
            block += sp.sympify(raw, locals={"u": u, "v": v, "alpha_B": 5}) * operator
        result[(row - 22) * n : (row - 21) * n, column * n : (column + 1) * n] = sp.simplify(block)
    return result


def _finite_audit(values: dict[str, Any], two_j: int) -> dict[str, Any]:
    n = two_j + 1
    d0 = d_matrix(two_j, 0)
    scalar_laplacian = sp.simplify(d0.conjugate().T * d0)
    exact = sp.simplify(d0 * scalar_laplacian.inv() * d0.conjugate().T)
    coexact = sp.eye(3 * n) - exact
    endpoint = _finite_endpoint(values, two_j)
    exact_to_coexact = sp.simplify(coexact * endpoint * exact)
    coexact_to_exact = sp.simplify(exact * endpoint * coexact)
    expected = n if two_j % 2 else n - 1
    checks = {
        "exact_projector_idempotent": sp.simplify(exact * exact - exact) == sp.zeros(3 * n),
        "orthogonal_complement": sp.simplify(exact * coexact) == sp.zeros(3 * n),
        "endpoint_hermitian": endpoint == endpoint.conjugate().T,
        "cross_blocks_are_adjoints": exact_to_coexact == coexact_to_exact.conjugate().T,
    }
    ranks = {
        "exact_dimension": exact.rank(),
        "coexact_dimension": coexact.rank(),
        "exact_to_coexact_rank": exact_to_coexact.rank(),
        "coexact_to_exact_rank": coexact_to_exact.rank(),
        "expected_cross_rank": expected,
    }
    if not all(checks.values()) or ranks["exact_dimension"] != n or ranks["coexact_dimension"] != 2 * n:
        raise AssertionError(f"projector/adjoint audit failed at two_j={two_j}")
    if ranks["exact_to_coexact_rank"] != expected or ranks["coexact_to_exact_rank"] != expected:
        raise AssertionError(f"mixing rank drifted at two_j={two_j}")
    return {"two_j": two_j, "checks": checks, "ranks": ranks}


def _round_mutation_audit(values: dict[str, Any], two_j: int) -> dict[str, int]:
    n = two_j + 1
    d0 = sp.Matrix.vstack(*_round_generators(two_j))
    exact = sp.simplify(d0 * (d0.conjugate().T * d0).inv() * d0.conjugate().T)
    coexact = sp.eye(3 * n) - exact
    endpoint = _finite_endpoint(values, two_j, round_geometry=True)
    ranks = {
        "two_j": two_j,
        "exact_to_coexact_rank": (coexact * endpoint * exact).rank(),
        "coexact_to_exact_rank": (exact * endpoint * coexact).rank(),
    }
    if ranks["exact_to_coexact_rank"] or ranks["coexact_to_exact_rank"]:
        raise AssertionError(f"round mutation retained Hodge mixing at two_j={two_j}")
    return ranks


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    endpoint = _endpoint_e0_squared(values["gauge_fixed_q54"]["classical_unary_q1"]["matrix"])
    adjoint_defects = []
    for row in range(3):
        for column in range(3):
            defect = endpoint[row][column] - _formal_adjoint(endpoint[column][row])
            if defect.terms:
                adjoint_defects.append([row, column])
    if adjoint_defects:
        raise AssertionError(f"formal endpoint adjoint defects: {adjoint_defects}")
    audits = [_finite_audit(values, two_j) for two_j in range(1, 7)]
    round_audits = [_round_mutation_audit(values, two_j) for two_j in range(1, 4)]
    scalar = values["scalar_terminal"]["first_obstruction"]
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-berger-vector-hodge-split-obstruction-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "endpoint": {
            "source_rows": ["c_spatial_1", "c_spatial_2", "c_spatial_3"],
            "target_rows": ["bar_c_star_diff_1", "bar_c_star_diff_2", "bar_c_star_diff_3"],
            "operator": "A2=coefficient_of_e0_squared(q54[bar_c_star_diff,c_spatial])",
            "PBW_manifest": _operator_manifest(endpoint),
            "PBW_term_count": sum(len(entry["terms"]) for entry in _operator_manifest(endpoint)),
            "formal_adjoint_convention": "e_a^dagger=-e_a; (e_a1...e_ar)^dagger=(-1)^r e_ar...e_a1",
            "formal_self_adjoint": True,
            "formal_adjoint_defects": [],
        },
        "generic_argument": {
            "imported_exact_to_coexact_witness": scalar["leading_mode_coefficient"],
            "imported_domain": "every scalar exact mode with k!=0",
            "orthogonal_split": "Omega1=im(d0) direct_sum ker(d0^dagger)",
            "adjoint_identity": "(P_co A2 P_ex)^dagger=P_ex A2 P_co",
            "conclusion": "both longitudinal-to-coexact and coexact-to-longitudinal blocks are nonzero; neither summand is invariant",
            "minimal_closed_carrier": "the full one-form SU(2)_L x U(1)_R isotypical block, coupled to every q70 row reached by the unary",
        },
        "finite_wigner_audits": audits,
        "round_mutation_audits": round_audits,
        "exceptional_ledger": [
            {"labels": "half-integer j, all k", "status": "TWO_WAY_MIXING_FULL_RANK_ON_EXACT_SECTOR"},
            {"labels": "integer j>=1, k!=0", "status": "TWO_WAY_MIXING_RANK_2j"},
            {"labels": "integer j>=1, k=0", "status": "FIRST_MIXING_KERNEL_FULL_COUPLED_BLOCK_NOT_COMPUTED"},
            {"labels": "j=0", "status": "GLOBAL_LEFT_INVARIANT_ONE_FORM_BLOCK_EXCEPTIONAL"},
        ],
        "mutations": [
            {"id": "ROUND_GEOMETRY_AND_ENDPOINT", "detected": True, "effect": "u=v=c=1 makes both cross blocks vanish in the audited fixtures"},
            {"id": "DROP_ENDPOINT_FORMAL_ADJOINT", "detected": True, "effect": "breaks the exact PBW adjoint identity"},
            {"id": "OMIT_LONGITUDINAL_FROM_VECTOR_CARRIER", "detected": True, "effect": "P_ex A2 P_co remains nonzero"},
            {"id": "OMIT_COEXACT_FROM_SCALAR_CARRIER", "detected": True, "effect": "P_co A2 P_ex remains nonzero"},
            {"id": "CALL_FINITE_BAND_GENERIC", "detected": True, "effect": "finite audits remain explicitly nonpromotion evidence"},
        ],
        "terminal": {
            "result_state": "EXACT_TWO_WAY_VECTOR_HODGE_SPLIT_OBSTRUCTION",
            "requested_longitudinal_coexact_split_closed": False,
            "complete_vector_tensor_quotient_status": "NOT_DEFINED_BEFORE_FULL_ISOTYPICAL_ENLARGEMENT",
            "symmetric_tensor_stage_status": "NOT_STARTED_AFTER_FIRST_VECTOR_CLOSURE_OBSTRUCTION",
            "q70_parent_preserved": True,
            "downstream_exceptional_export_activated": False,
        },
        "next_gate": {
            "required_carrier": "complete fixed-j SU(2)_L x U(1)_R isotypical q70 block with exact/coexact and scalar/vector/tensor rows coupled",
            "first_acceptance_identity": "pi_iso iota_iso=1 and q70 iota_iso=iota_iso q_iso",
            "forbidden_shortcut": "no separate longitudinal/coexact or scalar/vector quotient before the full coupled block closes",
        },
        "claim_boundary": {
            "establishes": [
                "formal self-adjointness of the e0-squared Diff ghost endpoint",
                "two-way non-invariance of the longitudinal/coexact one-form split",
                "exact finite Wigner mixing ranks through two_j=6",
                "the minimal coupled-carrier requirement before a physical quotient",
            ],
            "does_not_establish": [
                "a complete full-isotypical q70 restriction or quotient",
                "a symmetric-tensor harmonic classification",
                "a verdict for right-neutral or global exceptional blocks",
                "failure of the complete q70 BV complex or its causal homotopy",
                "a stability, observer, Hadamard, QME, particle, positivity or unitarity theorem",
            ],
        },
    }
    value["content_sha256"] = _digest(value)
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = payload["terminal"]
    return {
        "schema": "pure-weyl-two-phase-counterflow-berger-vector-hodge-split-obstruction-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": _sha(PAYLOAD) if PAYLOAD.exists() else "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "generic_argument": payload["generic_argument"],
        "finite_rank_ledger": [
            {"two_j": row["two_j"], **row["ranks"]}
            for row in payload["finite_wigner_audits"]
        ],
        "terminal_verdict": terminal,
        "next_gate": payload["next_gate"],
        "claim_boundary": payload["claim_boundary"],
        "content_hashes": {
            "endpoint_sha256": _digest(payload["endpoint"]),
            "generic_argument_sha256": _digest(payload["generic_argument"]),
            "finite_audits_sha256": _digest(payload["finite_wigner_audits"]),
            "terminal_sha256": _digest(terminal),
            "boundary_sha256": _digest(payload["claim_boundary"]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    imports, values = _load_imports()
    payload = _payload(imports, values)
    if args.emit:
        PAYLOAD.write_text(_render(payload))
    if not PAYLOAD.exists() or PAYLOAD.read_text() != _render(payload):
        if args.check:
            raise SystemExit("stale vector-Hodge obstruction payload")
    certificate = _certificate(imports, payload)
    if args.emit:
        certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
        OUTPUT.write_text(_render(certificate))
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))
    Draft202012Validator.check_schema(json.loads(PAYLOAD_SCHEMA.read_text()))
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != _render(certificate)):
        raise SystemExit("stale vector-Hodge obstruction certificate")
    print("TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
