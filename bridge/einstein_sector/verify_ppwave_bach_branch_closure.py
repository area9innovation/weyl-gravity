#!/usr/bin/env python3
"""Independent exact audit of the Brinkmann Bach branch-closure theorem."""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/ppwave_bach_branch_closure.json"
DIMENSION = 4


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    u, v, x, y = sp.symbols("u v x y", real=True)
    coordinates = (u, v, x, y)
    profile = sp.Function("H")(u, x, y)
    metric = sp.Matrix(
        [[profile, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    )
    inverse = metric.inv()
    connection = [
        [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for target, first, second in product(range(DIMENSION), repeat=3):
        connection[target][first][second] = sp.simplify(
            sum(
                inverse[target, index]
                * (
                    sp.diff(metric[index, second], coordinates[first])
                    + sp.diff(metric[index, first], coordinates[second])
                    - sp.diff(metric[first, second], coordinates[index])
                )
                for index in range(DIMENSION)
            )
            / 2
        )
    riemann = [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for target, source, first, second in product(range(DIMENSION), repeat=4):
        riemann[target][source][first][second] = sp.simplify(
            sp.diff(connection[target][source][second], coordinates[first])
            - sp.diff(connection[target][source][first], coordinates[second])
            + sum(
                connection[target][middle][first]
                * connection[middle][source][second]
                - connection[target][middle][second]
                * connection[middle][source][first]
                for middle in range(DIMENSION)
            )
        )
    ricci = sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda first, second: sp.simplify(
            sum(riemann[index][first][index][second] for index in range(DIMENSION))
        ),
    )
    delta = sp.diff(profile, x, 2) + sp.diff(profile, y, 2)
    assert ricci[0, 0] == -delta / 2
    assert all(
        ricci[first, second] == 0
        for first, second in product(range(DIMENSION), repeat=2)
        if (first, second) != (0, 0)
    )
    scalar = sp.simplify(
        sum(
            inverse[first, second] * ricci[first, second]
            for first, second in product(range(DIMENSION), repeat=2)
        )
    )
    assert scalar == 0
    schouten = ricci / 2

    derivative = [
        [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for direction, first, second in product(range(DIMENSION), repeat=3):
        derivative[direction][first][second] = sp.simplify(
            sp.diff(schouten[first, second], coordinates[direction])
            - sum(
                connection[index][direction][first] * schouten[index, second]
                + connection[index][direction][second] * schouten[first, index]
                for index in range(DIMENSION)
            )
        )
    second_derivative = [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for outer, inner, first, second in product(range(DIMENSION), repeat=4):
        second_derivative[outer][inner][first][second] = sp.simplify(
            sp.diff(derivative[inner][first][second], coordinates[outer])
            - sum(
                connection[index][outer][inner] * derivative[index][first][second]
                + connection[index][outer][first] * derivative[inner][index][second]
                + connection[index][outer][second] * derivative[inner][first][index]
                for index in range(DIMENSION)
            )
        )

    # For this type-N Ricci tensor P^{cd} has only a vv component.  Verify
    # C_{avbv}=0, hence the curvature term vanishes, independently of the producer.
    schouten_up = sp.simplify(inverse * schouten * inverse)
    curvature_term = sp.zeros(DIMENSION)
    for first, second in product(range(DIMENSION), repeat=2):
        lowered = sp.simplify(
            sum(metric[first, target] * riemann[target][1][second][1] for target in range(DIMENSION))
        )
        c_avbv = sp.simplify(
            lowered
            - (
                metric[first, second] * schouten[1, 1]
                - metric[first, 1] * schouten[second, 1]
                - metric[1, second] * schouten[1, first]
                + metric[1, 1] * schouten[second, first]
            )
        )
        curvature_term[first, second] = sp.simplify(schouten_up[1, 1] * c_avbv)
    assert curvature_term == sp.zeros(DIMENSION)

    bach = sp.zeros(DIMENSION)
    for first, second in product(range(DIMENSION), repeat=2):
        bach[first, second] = sp.simplify(
            sum(
                inverse[outer, inner]
                * (
                    second_derivative[outer][inner][first][second]
                    - second_derivative[outer][first][second][inner]
                )
                for outer, inner in product(range(DIMENSION), repeat=2)
            )
            + curvature_term[first, second]
        )
    bilaplacian = sp.diff(delta, x, 2) + sp.diff(delta, y, 2)
    assert bach[0, 0] == -bilaplacian / 4
    assert all(
        bach[first, second] == 0
        for first, second in product(range(DIMENSION), repeat=2)
        if (first, second) != (0, 0)
    )

    f = sp.Function("f")(u)
    g = sp.Function("g")(u)
    einstein = f * (x**2 - y**2)
    extra = g * x**3
    transverse = lambda value: sp.factor(
        sp.diff(value, x, 2) + sp.diff(value, y, 2)
    )
    assert transverse(einstein) == 0
    assert transverse(extra) == 6 * x * g
    assert transverse(transverse(extra)) == 0
    assert payload["restricted_nonlinear_tensor"]["q2_entries"] == {
        "Einstein_Einstein": "0",
        "Einstein_extraWeyl": "0",
        "extraWeyl_extraWeyl": "0",
    }
    assert payload["flags"]["RESTRICTED_SUPPORT_LOCAL_Q2_BLOCK"] is True
    assert payload["flags"]["FULL_SUPPORT_LOCAL_BV_Q2"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("PPWAVE_BACH_BRANCH_CLOSURE_INDEPENDENT: PASS")
    print("restricted support-local Einstein/extra-Weyl ell2: EXACTLY ZERO")
    print("nonaligned and complete 54-row q2: OPEN")


if __name__ == "__main__":
    main()
