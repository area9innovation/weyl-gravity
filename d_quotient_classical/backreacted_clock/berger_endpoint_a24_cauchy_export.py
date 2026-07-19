"""Export the certified Berger endpoint factors and their two Cauchy blocks.

The causal-witness theorem already constructs the spatial Faddeev--Popov and
rough-wave factors coefficientwise but historically serialized only their
fourth-order products.  This module exposes those existing factors and forms
the canonical two-factor graph companions required by the quantum A104
consumer.  No factor is reconstructed inside ``quantum-weyl``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from . import berger_causal_witness_preflight as witness


HERE = Path(__file__).resolve().parent
DROOT = HERE.parent
ROOT = HERE.parents[1]
OUTPUT = DROOT / "certificates/BERGER_ENDPOINT_A24_CAUCHY_EXPORT.json"
REPORT = DROOT / "reports/berger-endpoint-a24-cauchy-export.md"
CONSUMER_SCHEMA = ROOT / "quantum-weyl/lorentzian/schema/berger-endpoint-a24-cauchy-export-v1.schema.json"
CAUSAL_WITNESS = DROOT / "certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json"
CAUSAL_CHAIN = DROOT / "certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"

PRIMARY = [f"c_spatial_{index}" for index in range(1, 4)]
AUXILIARY = [f"aux[c_spatial_{index}]" for index in range(1, 4)]
IDENTITY_PRIMARY = [f"c_spatial_star_{index}" for index in range(1, 4)]
IDENTITY_AUXILIARY = [f"aux[c_spatial_star_{index}]" for index in range(1, 4)]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(body: object) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _entries(matrix: list[list[witness.LinearOperator]]) -> list[list[Any]]:
    result: list[list[Any]] = []
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            if not operator.terms:
                continue
            terms = []
            for _, word, coefficient in operator.terms:
                exponents = [word.count(axis) for axis in range(4)]
                terms.append([exponents, str(sp.factor(coefficient))])
            result.append([row, column, terms])
    return result


def _factor_record(
    factor_record_id: str,
    matrix: list[list[witness.LinearOperator]],
    row_ids: list[str],
    column_ids: list[str],
    source_commit: str,
) -> dict[str, Any]:
    body = {
        "factor_record_id": factor_record_id,
        "shape": [len(matrix), len(matrix[0])],
        "row_ids": row_ids,
        "column_ids": column_ids,
        "entries": _entries(matrix),
        "source_commit": source_commit,
    }
    return {**body, "sha256": _digest(body)}


def _block_record(
    block_id: str,
    matrix: list[list[witness.LinearOperator]],
    local_ordering: list[str],
) -> dict[str, Any]:
    body = {
        "block_id": block_id,
        "shape": [len(matrix), len(matrix[0])],
        "local_ordering": local_ordering,
        "entries": _entries(matrix),
    }
    return {**body, "sha256": _digest(body)}


def _zero(rank: int) -> list[list[witness.LinearOperator]]:
    return [[witness.ZERO for _ in range(rank)] for _ in range(rank)]


def _graph_companion(
    first: list[list[witness.LinearOperator]],
    second: list[list[witness.LinearOperator]],
) -> list[list[witness.LinearOperator]]:
    """Return [[first,-I],[0,second]], whose elimination is second o first."""

    rank = len(first)
    if rank != len(second) or any(len(row) != rank for row in first + second):
        raise ValueError("endpoint factor ranks do not match")
    result = _zero(2 * rank)
    identity = witness._identity_matrix(rank)
    for row in range(rank):
        for column in range(rank):
            result[row][column] = first[row][column]
            result[row + rank][column + rank] = second[row][column]
            result[row][column + rank] = identity[row][column].scale(-1)
    return result


def _split_temporal(matrix: list[list[witness.LinearOperator]]):
    pieces = [_zero(len(matrix)) for _ in range(3)]
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            accumulators: list[list[tuple[int, tuple[int, ...], sp.Expr]]] = [
                [], [], []
            ]
            for _, word, coefficient in operator.terms:
                temporal_order = word.count(0)
                if temporal_order > 2:
                    raise ValueError("factor graph has temporal order above two")
                spatial_word = tuple(axis for axis in word if axis != 0)
                accumulators[temporal_order].append(
                    (0, spatial_word, coefficient)
                )
            for order, terms in enumerate(accumulators):
                pieces[order][row][column] = witness.LinearOperator.from_terms(
                    tuple(terms)
                )
    return tuple(pieces)


def _restore_temporal(pieces):
    rank = len(pieces[0])
    result = _zero(rank)
    for order, matrix in enumerate(pieces):
        for row, values in enumerate(matrix):
            for column, operator in enumerate(values):
                terms = list(result[row][column].terms)
                terms.extend(
                    (0, (0,) * order + word, coefficient)
                    for _, word, coefficient in operator.terms
                )
                result[row][column] = witness.LinearOperator.from_terms(
                    tuple(terms)
                )
    return result


def _constant_matrix(matrix) -> sp.Matrix:
    result = sp.zeros(len(matrix))
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            for _, word, coefficient in operator.terms:
                if word:
                    raise ValueError("temporal leading coefficient is not algebraic")
                result[row, column] += coefficient
    return result


def _left_constant_multiply(coefficients: sp.Matrix, matrix):
    rank = coefficients.rows
    result = _zero(rank)
    for row in range(rank):
        for column in range(rank):
            result[row][column] = witness._sum_ops(
                matrix[middle][column].scale(coefficients[row, middle])
                for middle in range(rank)
            )
    return result


def _cauchy_generator(graph):
    K0, K1, K2 = _split_temporal(graph)
    leading = _constant_matrix(K2)
    inverse = sp.simplify(leading.inv())
    rank = len(graph)
    result = _zero(2 * rank)
    identity = witness._identity_matrix(rank)
    lower_left = _left_constant_multiply(-inverse, K0)
    lower_right = _left_constant_multiply(-inverse, K1)
    for row in range(rank):
        for column in range(rank):
            result[row][column + rank] = identity[row][column]
            result[row + rank][column] = lower_left[row][column]
            result[row + rank][column + rank] = lower_right[row][column]
    return result, (K0, K1, K2), leading, inverse


def _maximum_spatial_order(matrix) -> int:
    return max(
        (
            len(word)
            for row in matrix
            for operator in row
            for _, word, _ in operator.terms
        ),
        default=-1,
    )


def _scaled(matrix, coefficient):
    return [[entry.scale(coefficient) for entry in row] for row in matrix]


def _verify_internal_hash(record: dict[str, Any]) -> bool:
    return record["sha256"] == _digest(
        {key: value for key, value in record.items() if key != "sha256"}
    )


def build() -> dict[str, Any]:
    source = json.loads(CAUSAL_WITNESS.read_text())
    causal_chain = json.loads(CAUSAL_CHAIN.read_text())
    if source.get("exact_checks", {}).get("ghost_factorization_exact") is not True:
        raise ValueError("causal endpoint factor theorem drifted")
    if causal_chain.get("classical_commit") is None:
        raise ValueError("causal chain classical commit missing")
    classical_commit = causal_chain["classical_commit"]

    gauge = witness._split_operator_vector(witness._spatial_gauge_operator(), 3)
    de_donder = witness._spatial_de_donder()
    fp = witness._compose_matrices(de_donder, gauge)
    wave = witness._rough_wave_spatial_covector(witness._identity_matrix(3))
    fp_adjoint = witness._adjoint_matrix(fp, sign=-1)
    wave_adjoint = witness._adjoint_matrix(wave, sign=-1)

    factors = {
        "F_spatial_K_spatial": _factor_record(
            "F_spatial_K_spatial", fp, AUXILIARY, PRIMARY, classical_commit
        ),
        "Box_1_spatial_covector": _factor_record(
            "Box_1_spatial_covector", wave, PRIMARY, AUXILIARY, classical_commit
        ),
        "F_spatial_K_spatial_formal_adjoint": _factor_record(
            "F_spatial_K_spatial_formal_adjoint",
            fp_adjoint,
            IDENTITY_PRIMARY,
            IDENTITY_AUXILIARY,
            classical_commit,
        ),
        "Box_1_spatial_covector_formal_adjoint": _factor_record(
            "Box_1_spatial_covector_formal_adjoint",
            wave_adjoint,
            IDENTITY_AUXILIARY,
            IDENTITY_PRIMARY,
            classical_commit,
        ),
    }

    ghost_graph = _graph_companion(fp, wave)
    identity_graph = _graph_companion(wave_adjoint, fp_adjoint)
    ghost_A12, ghost_pieces, ghost_leading, ghost_inverse = _cauchy_generator(
        ghost_graph
    )
    identity_A12, identity_pieces, identity_leading, identity_inverse = (
        _cauchy_generator(identity_graph)
    )

    ghost_endpoint = witness._compose_matrices(wave, fp)
    identity_endpoint = witness._compose_matrices(fp_adjoint, wave_adjoint)
    expected_ghost = witness._matrix_from_record(
        source["degreewise_P_blocks"]["ghost"]
    )
    expected_identity = witness._matrix_from_record(
        source["degreewise_P_blocks"]["identity"]
    )

    checks = {
        "factor_record_internal_hashes": all(
            _verify_internal_hash(record) for record in factors.values()
        ),
        "factor_row_and_column_orderings_match_retained_layout": (
            factors["F_spatial_K_spatial"]["column_ids"] == PRIMARY
            and factors["F_spatial_K_spatial"]["row_ids"] == AUXILIARY
            and factors["Box_1_spatial_covector"]["column_ids"] == AUXILIARY
            and factors["Box_1_spatial_covector"]["row_ids"] == PRIMARY
            and factors["Box_1_spatial_covector_formal_adjoint"]["column_ids"]
            == IDENTITY_PRIMARY
            and factors["Box_1_spatial_covector_formal_adjoint"]["row_ids"]
            == IDENTITY_AUXILIARY
            and factors["F_spatial_K_spatial_formal_adjoint"]["column_ids"]
            == IDENTITY_AUXILIARY
            and factors["F_spatial_K_spatial_formal_adjoint"]["row_ids"]
            == IDENTITY_PRIMARY
        ),
        "ghost_factor_composition_reconstructs_retained_endpoint": (
            _scaled(ghost_endpoint, witness.ALPHA_B) == expected_ghost
        ),
        "identity_factor_composition_reconstructs_retained_endpoint": (
            _scaled(identity_endpoint, witness.ALPHA_B) == expected_identity
        ),
        "formal_adjoint_factor_relations": (
            fp_adjoint == witness._adjoint_matrix(fp, sign=-1)
            and wave_adjoint == witness._adjoint_matrix(wave, sign=-1)
        ),
        "second_order_graph_companions_reconstruct_factor_products": (
            witness._compose_matrices(wave, fp) == ghost_endpoint
            and witness._compose_matrices(fp_adjoint, wave_adjoint)
            == identity_endpoint
            and _restore_temporal(ghost_pieces) == ghost_graph
            and _restore_temporal(identity_pieces) == identity_graph
        ),
        "temporal_leading_matrices_are_two_sided_invertible": (
            sp.simplify(ghost_leading * ghost_inverse) == sp.eye(6)
            and sp.simplify(ghost_inverse * ghost_leading) == sp.eye(6)
            and sp.simplify(identity_leading * identity_inverse) == sp.eye(6)
            and sp.simplify(identity_inverse * identity_leading) == sp.eye(6)
        ),
        "derived_A12_blocks_have_spatial_order_at_most_two": (
            _maximum_spatial_order(ghost_A12) <= 2
            and _maximum_spatial_order(identity_A12) <= 2
        ),
    }
    if not all(checks.values()):
        raise ValueError(f"endpoint A24 exact check failed: {checks}")

    result = {
        "schema": "quantum-weyl-berger-endpoint-a24-cauchy-export-v1",
        "result_id": "BERGER_ENDPOINT_A24_CAUCHY_EXPORT",
        "result_state": "ENDPOINT_FACTORS_AND_DERIVED_A24_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": classical_commit,
        "setting_id": source["setting_id"],
        "coefficient_ring": "Q(U,V,alpha_B) with exact SymPy rational expressions",
        "differential_axis_order": [
            "t",
            "berger_frame_1",
            "berger_frame_2",
            "berger_frame_3",
        ],
        "factor_records": factors,
        "derived_A12_blocks": {
            "ghost_A12": _block_record(
                "ghost_A12",
                ghost_A12,
                PRIMARY
                + AUXILIARY
                + [f"partial_t[{row}]" for row in PRIMARY + AUXILIARY],
            ),
            "identity_A12": _block_record(
                "identity_A12",
                identity_A12,
                IDENTITY_PRIMARY
                + IDENTITY_AUXILIARY
                + [
                    f"partial_t[{row}]"
                    for row in IDENTITY_PRIMARY + IDENTITY_AUXILIARY
                ],
            ),
        },
        "exact_checks": checks,
        "claim_boundary": (
            "This classical LOCAL-ALGEBRAIC plus LORENTZIAN-CAUSAL export exposes the four "
            "already-certified Berger ghost/identity endpoint factors and derives their exact "
            "rank-12 first-order Cauchy graph blocks. It does not assemble the global A104, "
            "construct q_Cauchy or the Cauchy/Krein form, prove closedness or spectral isolation, "
            "construct a covariance or Hadamard state, restore a QME or make a quantum claim."
        ),
    }
    verify(result)
    Draft202012Validator(json.loads(CONSUMER_SCHEMA.read_text())).validate(result)
    return result


def verify(result: dict[str, Any]) -> None:
    if result.get("result_state") != "ENDPOINT_FACTORS_AND_DERIVED_A24_EXACT":
        raise ValueError("endpoint export state drifted")
    if not all(result.get("exact_checks", {}).values()):
        raise ValueError("endpoint export exact check dropped")
    for record in result.get("factor_records", {}).values():
        if not _verify_internal_hash(record):
            raise ValueError("endpoint factor internal hash drifted")
    for record in result.get("derived_A12_blocks", {}).values():
        if not _verify_internal_hash(record):
            raise ValueError("derived A12 internal hash drifted")
    if result.get("derived_A12_blocks", {}).get("ghost_A12", {}).get("shape") != [
        12,
        12,
    ]:
        raise ValueError("ghost A12 shape drifted")
    if result.get("derived_A12_blocks", {}).get("identity_A12", {}).get(
        "shape"
    ) != [12, 12]:
        raise ValueError("identity A12 shape drifted")


def report_text(result: dict[str, Any]) -> str:
    ghost = result["derived_A12_blocks"]["ghost_A12"]
    identity = result["derived_A12_blocks"]["identity_A12"]
    return f"""# Berger endpoint A24 Cauchy export

The four endpoint factors already used by the classical causal theorem are now
serialized in the quantum consumer contract. Their two canonical factor-graph
companions give exact `12 x 12` first-order Cauchy blocks:

| block | sparse entries | sha256 |
| --- | ---: | --- |
| `ghost_A12` | {len(ghost['entries'])} | `{ghost['sha256']}` |
| `identity_A12` | {len(identity['entries'])} | `{identity['sha256']}` |

The factor products reconstruct the certified fourth-order ghost and identity
endpoints, both formal-adjoint relations hold, both temporal leading matrices
are two-sided invertible, and the derived generators have spatial order at
most two.

This artifact closes only the 24-component classical endpoint export.  Its
quantum consumer now assembles the global `A104` independently.  The Cauchy
BRST operator, Krein form, closed spectral realization, zero-frequency ledger
and Hadamard covariance remain downstream.
"""


def emit(*, check: bool) -> None:
    result = build()
    certificate = json.dumps(result, indent=2, sort_keys=True) + "\n"
    report = report_text(result)
    if check:
        if OUTPUT.read_text() != certificate:
            raise SystemExit("stale Berger endpoint A24 export")
        if REPORT.read_text() != report:
            raise SystemExit("stale Berger endpoint A24 report")
    else:
        OUTPUT.write_text(certificate)
        REPORT.write_text(report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit(check=False)
    if args.check:
        emit(check=True)
    if not args.emit and not args.check:
        print(json.dumps(build(), indent=2, sort_keys=True))
    print("BERGER ENDPOINT A24 CAUCHY EXPORT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
