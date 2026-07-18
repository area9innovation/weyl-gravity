#!/usr/bin/env python3
"""Independent replay of the repository Euclidean elliptic complex."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json

from spectral.euclidean.elliptic_complex_receiver import (
    PHYSICAL_BLOCKS,
    PHYSICAL_SECTORS,
    validate_euclidean_elliptic_complex,
)
from spectral.euclidean.repository_euclidean_elliptic_complex import (
    ADJOINT_OUTPUT,
    GAUGE_OUTPUT,
    OUTPUT,
    ROOT,
    build,
)


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _matrix(value: dict) -> list[list[Fraction]]:
    rows, columns = value["shape"]
    result = [[Fraction(0) for _ in range(columns)] for _ in range(rows)]
    for entry in value["entries"]:
        q = entry["coefficient"]
        result[entry["row"]][entry["column"]] = Fraction(q["numerator"], q["denominator"])
    return result


def _multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    rows, columns = len(work), len(work[0])
    rank = column = 0
    while rank < rows and column < columns:
        pivot = next((row for row in range(rank, rows) if work[row][column]), None)
        if pivot is None:
            column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][column]:
                scale = work[row][column]
                work[row] = [left - scale * right for left, right in zip(work[row], work[rank])]
        rank += 1
        column += 1
    return rank


def _self_digest(value: dict) -> bool:
    payload = dict(value)
    expected = payload.pop("proof_sha256")
    return expected == _canonical_hash(payload)


def verify() -> dict:
    expected_gauge, expected_adjoint, expected = build()
    gauge = json.loads(GAUGE_OUTPUT.read_text())
    adjoint = json.loads(ADJOINT_OUTPUT.read_text())
    value = json.loads(OUTPUT.read_text())
    if (gauge, adjoint, value) != (expected_gauge, expected_adjoint, expected):
        raise ValueError("repository Euclidean elliptic artifacts do not reproduce")
    if not _self_digest(gauge) or not _self_digest(adjoint):
        raise ValueError("supporting symbol proof digest drifted")

    K = _matrix(gauge["conformal_deformation_symbol"])
    G = _matrix(gauge["gauge_condition_symbol"])
    P = _matrix(gauge["gauge_slice_projection_symbol"])
    FP = _matrix(gauge["faddeev_popov_symbol"])
    if (
        _multiply(G, K) != FP
        or any(entry for row in _multiply(P, K) for entry in row)
        or (_rank(K), _rank(P), _rank(FP)) != (5, 5, 5)
        or gauge["faddeev_popov_determinant"] != {"numerator": 12, "denominator": 1}
    ):
        raise ValueError("independent gauge-symbol replay failed")

    incoming = _matrix(adjoint["incoming_symbol"])
    outgoing = _matrix(adjoint["outgoing_symbol"])
    if (
        any(entry for row in _multiply(outgoing, incoming) for entry in row)
        or (_rank(incoming), _rank(outgoing)) != (5, 5)
        or not adjoint["exact_at_metric_cotangent_middle"]
    ):
        raise ValueError("independent formal-adjoint replay failed")

    receipt = validate_euclidean_elliptic_complex(value, repository_root=ROOT)
    if tuple(row["sector_id"] for row in value["principal_symbol_exactness"]) != PHYSICAL_SECTORS:
        raise ValueError("physical sector ledger drifted")
    observed_blocks = tuple(
        (
            row["block_id"], row["bundle_rank"], row["differential_order"],
            Fraction(row["principal_scalar"]["numerator"], row["principal_scalar"]["denominator"]),
        )
        for row in value["gauge_fixed_kinetic_blocks"]
    )
    if observed_blocks != PHYSICAL_BLOCKS:
        raise ValueError("physical block ledger drifted")
    print("repository Euclidean elliptic complex independent verification: PASS")
    return receipt


if __name__ == "__main__":
    verify()
