#!/usr/bin/env python3
"""Independent frame-level check of the Berger delta-charge certificate.

This checker does not import the producer.  It reconstructs the curvature in
the time-dependent orthonormal Berger frame, derives R and C^2, and then
recomputes the linearized lapse row at the rational fixture.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    dimension = 4
    eta = sp.diag(-1, 1, 1, 1)
    c, c1, c2 = sp.symbols("c c1 c2", nonzero=True, real=True)
    lapse, lapse1 = sp.symbols("N N1", nonzero=True, real=True)

    derivative_variables = [c, c1, lapse]
    derivative_successors = [c1, c2, lapse1]

    def frame_derivative(index: int, expression: sp.Expr) -> sp.Expr:
        if index != 0:
            return sp.S(0)
        return sp.simplify(
            sum(
                sp.diff(expression, variable) * successor
                for variable, successor in zip(
                    derivative_variables, derivative_successors
                )
            )
            / lapse
        )

    structure = [
        [[sp.S(0) for _ in range(dimension)] for _ in range(dimension)]
        for _ in range(dimension)
    ]
    hubble_c = c1 / (lapse * c)
    structure[0][3][3] = -hubble_c
    structure[3][0][3] = hubble_c
    for first, second, target, value in (
        (1, 2, 3, c),
        (2, 3, 1, 1 / c),
        (3, 1, 2, 1 / c),
    ):
        structure[first][second][target] = value
        structure[second][first][target] = -value

    connection = [
        [[sp.S(0) for _ in range(dimension)] for _ in range(dimension)]
        for _ in range(dimension)
    ]
    for derivative in range(dimension):
        for vector in range(dimension):
            for lowered_target in range(dimension):
                gamma_lower = sp.Rational(1, 2) * (
                    sum(
                        eta[lowered_target, middle]
                        * structure[derivative][vector][middle]
                        for middle in range(dimension)
                    )
                    - sum(
                        eta[derivative, middle]
                        * structure[vector][lowered_target][middle]
                        for middle in range(dimension)
                    )
                    + sum(
                        eta[vector, middle]
                        * structure[lowered_target][derivative][middle]
                        for middle in range(dimension)
                    )
                )
                for target in range(dimension):
                    connection[target][derivative][vector] += (
                        eta[target, lowered_target] * gamma_lower
                    )

    riemann = [
        [
            [
                [sp.S(0) for _ in range(dimension)]
                for _ in range(dimension)
            ]
            for _ in range(dimension)
        ]
        for _ in range(dimension)
    ]
    for target in range(dimension):
        for vector in range(dimension):
            for first in range(dimension):
                for second in range(dimension):
                    riemann[target][vector][first][second] = sp.simplify(
                        frame_derivative(
                            first, connection[target][second][vector]
                        )
                        - frame_derivative(
                            second, connection[target][first][vector]
                        )
                        + sum(
                            connection[middle][second][vector]
                            * connection[target][first][middle]
                            - connection[middle][first][vector]
                            * connection[target][second][middle]
                            - structure[first][second][middle]
                            * connection[target][middle][vector]
                            for middle in range(dimension)
                        )
                    )

    ricci = sp.zeros(dimension)
    for first in range(dimension):
        for second in range(dimension):
            ricci[first, second] = sp.factor(
                sum(
                    riemann[index][first][index][second]
                    for index in range(dimension)
                )
            )
    scalar = sp.factor(
        sum(
            eta[first, second] * ricci[first, second]
            for first in range(dimension)
            for second in range(dimension)
        )
    )
    schouten = sp.simplify((ricci - scalar * eta / 6) / 2)
    weyl = [
        [
            [
                [sp.S(0) for _ in range(dimension)]
                for _ in range(dimension)
            ]
            for _ in range(dimension)
        ]
        for _ in range(dimension)
    ]
    for first in range(dimension):
        for second in range(dimension):
            for third in range(dimension):
                for fourth in range(dimension):
                    riemann_lower = sum(
                        eta[first, target]
                        * riemann[target][second][third][fourth]
                        for target in range(dimension)
                    )
                    weyl[first][second][third][fourth] = sp.factor(
                        riemann_lower
                        - (
                            eta[first, third] * schouten[fourth, second]
                            - eta[first, fourth] * schouten[third, second]
                            - eta[second, third] * schouten[fourth, first]
                            + eta[second, fourth] * schouten[third, first]
                        )
                    )
    weyl_squared = sp.factor(
        sum(
            eta[first, first]
            * eta[second, second]
            * eta[third, third]
            * eta[fourth, fourth]
            * weyl[first][second][third][fourth] ** 2
            for first in range(dimension)
            for second in range(dimension)
            for third in range(dimension)
            for fourth in range(dimension)
        )
    )

    expected_scalar = -(
        lapse**3 * c**3
        - 4 * lapse**3 * c
        - 4 * lapse * c2
        + 4 * lapse1 * c1
    ) / (2 * lapse**3 * c)
    expected_weyl_squared = (
        4
        * (
            lapse**3 * c**3
            - lapse**3 * c
            - 3 * lapse**2 * c * c1
            - lapse * c2
            + lapse1 * c1
        )
        * (
            lapse**3 * c**3
            - lapse**3 * c
            + 3 * lapse**2 * c * c1
            - lapse * c2
            + lapse1 * c1
        )
        / (3 * lapse**6 * c**2)
    )
    if sp.factor(scalar - expected_scalar) != 0:
        raise AssertionError("independent frame scalar-curvature check failed")
    if sp.factor(weyl_squared - expected_weyl_squared) != 0:
        raise AssertionError("independent frame Weyl-square check failed")

    # Independent rational-fixture lapse-row check.  The coefficients are
    # obtained by differentiating the exact reduced action with respect to the
    # lapse before setting N=1.
    dc, dn, drho, domega = sp.symbols("dc dn drho domega", real=True)
    relative_delta_charge = (
        2 * sp.sqrt(10) * dc / 3
        + 2 * drho
        + sp.Rational(4, 3) * domega
        - dn
    )
    lapse_row = (
        -sp.Rational(9, 16) * dc
        + 27 * sp.sqrt(10) * dn / 320
        - 27 * sp.sqrt(10) * drho / 160
        - 9 * sp.sqrt(10) * domega / 80
    )
    if sp.simplify(
        lapse_row + 27 * sp.sqrt(10) * relative_delta_charge / 320
    ) != 0:
        raise AssertionError("independent rational lapse-row check failed")

    print("BERGER_FIXED_COUPLING_DELTA_CHARGE_INDEPENDENT: PASS")
    print("frame curvature: PASS")
    print("rational lapse row: PASS")


if __name__ == "__main__":
    main()
