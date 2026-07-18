#!/usr/bin/env python3
"""Action-derived leading variation of the Nariai Bach Hessian.

The full first variation of the action Hessian has differential order at most
two in the moving orthonormal covariant-PBW frame.  This module derives its
order-two part directly from the covariant Bach formula.  It deliberately
freezes derivatives of the varied curvature: coefficient derivatives can
only lower the number of derivatives left on the input field, so this
freezing is authoritative at order two and nowhere below it.

The lower-order completion is handled in the certificate producer below by
the complete Noether solve.  Keeping these two arguments separate makes the
action input independent of the parent lower-order target.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from typing import Iterable

import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
    _clean,
    _scale,
)
from d_quotient_classical.causal_transfer.first_variation_pbw import (
    LinearizedOperator,
    lin_add,
    lin_scale,
    zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    _h_basis,
)
from d_quotient_classical.causal_transfer.nariai_transverse_curvature_incidence_variation import (
    _variation_riemann,
)
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import (
    _pbw_layers,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
)


Expr = dict[tuple[int, ...], sp.Matrix]
LinExpr = tuple[Expr, Expr]


def _lin_sum(values: Iterable[LinExpr]) -> LinExpr:
    values = tuple(values)
    return lin_add(*values) if values else ({}, {})


def _lin_derivative(value: LinExpr, axis: int, pbw) -> LinExpr:
    return pbw.compose(zero_variation({(axis,): sp.eye(1)}), value)


def _background_pair(base: sp.Expr, delta: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    return sp.expand(base), sp.expand(delta)


def _lin_scalar_multiply(value: LinExpr, coefficient: tuple[sp.Expr, sp.Expr]) -> LinExpr:
    base_coefficient, delta_coefficient = coefficient
    return lin_add(
        lin_scale(value, base_coefficient),
        ({}, _scale(value[0], delta_coefficient)) if delta_coefficient != 0 else ({}, {}),
    )


def _weyl_pair(a: int, b: int, c: int, d: int) -> tuple[sp.Expr, sp.Expr]:
    # The fixed-Lambda Einstein tangent has dot(P)=dot(Ric)=0 in the moving
    # orthonormal frame, hence dot(C)=dot(Riemann) with all indices lowered.
    return _background_pair(
        NariaiBackground.riemann(a, b, c, d)
        - sp.Rational(1, 6)
        * (
            NariaiBackground.metric[a, c] * NariaiBackground.metric[d, b]
            - NariaiBackground.metric[a, d] * NariaiBackground.metric[c, b]
            - NariaiBackground.metric[b, c] * NariaiBackground.metric[d, a]
            + NariaiBackground.metric[b, d] * NariaiBackground.metric[c, a]
        ),
        _variation_riemann()[a, b, c, d],
    )


def _connection_variation(h: list[list[LinExpr]], pbw):
    eta = NariaiBackground.metric
    output = [[[({}, {}) for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for rho in range(4):
        sign = eta[rho, rho]
        for mu in range(4):
            for nu in range(4):
                output[rho][mu][nu] = lin_scale(
                    lin_add(
                        _lin_derivative(h[nu][rho], mu, pbw),
                        _lin_derivative(h[mu][rho], nu, pbw),
                        lin_scale(_lin_derivative(h[mu][nu], rho, pbw), -1),
                    ),
                    sp.Rational(1, 2) * sign,
                )
    return output


def _linearized_curvatures(h: list[list[LinExpr]], pbw):
    eta = NariaiBackground.metric
    delta_r = _variation_riemann()
    gamma = _connection_variation(h, pbw)
    riemann_mixed = [[[[({}, {}) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    riemann_mixed[rho][sigma][mu][nu] = lin_add(
                        _lin_derivative(gamma[rho][nu][sigma], mu, pbw),
                        lin_scale(_lin_derivative(gamma[rho][mu][sigma], nu, pbw), -1),
                    )

    riemann_lower = [[[[({}, {}) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    riemann_lower[a][b][c][d] = lin_add(
                        *(
                            _lin_scalar_multiply(
                                h[a][rho],
                                (
                                    eta[rho, rho] * NariaiBackground.riemann(rho, b, c, d),
                                    eta[rho, rho] * delta_r[rho, b, c, d],
                                ),
                            )
                            for rho in range(4)
                        ),
                        lin_scale(riemann_mixed[a][b][c][d], eta[a, a]),
                    )

    ricci = [[({}, {}) for _ in range(4)] for _ in range(4)]
    for b in range(4):
        for d in range(4):
            ricci[b][d] = _lin_sum(
                riemann_mixed[rho][b][rho][d] for rho in range(4)
            )
    scalar = _lin_sum(
        lin_scale(ricci[a][a], eta[a, a]) for a in range(4)
    )
    schouten = [[({}, {}) for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            schouten[a][b] = lin_scale(
                lin_add(
                    ricci[a][b],
                    lin_scale(scalar, -sp.Rational(1, 6) * eta[a, b]),
                    lin_scale(h[a][b], -sp.Rational(2, 3)),
                ),
                sp.Rational(1, 2),
            )

    background_schouten = sp.Rational(1, 6) * eta
    weyl = [[[[({}, {}) for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    variation_wedge = lin_add(
                        lin_scale(h[a][c], background_schouten[d, b]),
                        lin_scale(schouten[d][b], eta[a, c]),
                        lin_scale(h[a][d], -background_schouten[c, b]),
                        lin_scale(schouten[c][b], -eta[a, d]),
                        lin_scale(h[b][c], -background_schouten[d, a]),
                        lin_scale(schouten[d][a], -eta[b, c]),
                        lin_scale(h[b][d], background_schouten[c, a]),
                        lin_scale(schouten[c][a], eta[b, d]),
                    )
                    weyl[a][b][c][d] = lin_add(
                        riemann_lower[a][b][c][d],
                        lin_scale(variation_wedge, -1),
                    )
    return gamma, ricci, weyl


def _linearized_bach_tensor(h: list[list[LinExpr]], pbw):
    eta = NariaiBackground.metric
    gamma, ricci, weyl_one = _linearized_curvatures(h, pbw)

    def u(f: int, a: int, c: int, b: int, d: int) -> LinExpr:
        return lin_add(
            _lin_derivative(weyl_one[a][c][b][d], f, pbw),
            *(
                lin_scale(
                    _lin_scalar_multiply(gamma[p][f][a], _weyl_pair(p, c, b, d)),
                    -1,
                )
                for p in range(4)
            ),
            *(
                lin_scale(
                    _lin_scalar_multiply(gamma[p][f][c], _weyl_pair(a, p, b, d)),
                    -1,
                )
                for p in range(4)
            ),
            *(
                lin_scale(
                    _lin_scalar_multiply(gamma[p][f][b], _weyl_pair(a, c, p, d)),
                    -1,
                )
                for p in range(4)
            ),
            *(
                lin_scale(
                    _lin_scalar_multiply(gamma[p][f][d], _weyl_pair(a, c, b, p)),
                    -1,
                )
                for p in range(4)
            ),
        )

    output = [[({}, {}) for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            double_divergence = _lin_sum(
                lin_scale(
                    _lin_derivative(u(d, a, c, b, d), c, pbw),
                    eta[c, c] * eta[d, d],
                )
                for c in range(4)
                for d in range(4)
            )
            ricci_variation_term = _lin_sum(
                lin_scale(
                    _lin_scalar_multiply(
                        lin_add(ricci[c][d], lin_scale(h[c][d], -2)),
                        _weyl_pair(a, c, b, d),
                    ),
                    sp.Rational(1, 2) * eta[c, c] * eta[d, d],
                )
                for c in range(4)
                for d in range(4)
            )
            background_ricci_term = _lin_sum(
                lin_scale(
                    weyl_one[a][c][b][d],
                    sp.Rational(1, 2) * eta[c, d],
                )
                for c in range(4)
                for d in range(4)
            )
            output[a][b] = lin_add(
                double_divergence,
                ricci_variation_term,
                background_ricci_term,
            )
    return output


@lru_cache(maxsize=1)
def action_variation_frozen() -> dict[str, Expr]:
    middle = middle_fixture()
    algebraic = middle["algebraic"]
    pbw = _pbw_layers()["H1"]
    raw_h, _, gram, left_inverse = _h_basis(algebraic)
    h: list[list[LinExpr]] = [
        [zero_variation(raw_h[a][b]) for b in range(4)] for a in range(4)
    ]
    bach = _linearized_bach_tensor(h, pbw)
    coordinates: list[dict[tuple[int, ...], sp.Matrix]] = [
        defaultdict(lambda: sp.zeros(9)) for _ in range(2)
    ]
    for output_coordinate in range(9):
        for a in range(4):
            for b in range(4):
                coefficient = left_inverse[output_coordinate, 4 * a + b]
                if coefficient == 0:
                    continue
                for layer in range(2):
                    for word, row in bach[a][b][layer].items():
                        coordinates[layer][word][output_coordinate, :] += coefficient * row
    coordinate_pair = tuple(_clean(value) for value in coordinates)
    covector_pair = tuple(
        _clean({word: gram * matrix for word, matrix in value.items()})
        for value in coordinate_pair
    )
    action_pair = tuple(_scale(value, -2) for value in covector_pair)
    return {
        "base": action_pair[0],
        "frozen_variation": action_pair[1],
        "order_two": {
            word: matrix
            for word, matrix in action_pair[1].items()
            if len(word) == 2
        },
    }


if __name__ == "__main__":
    data = action_variation_frozen()
    for name, table in data.items():
        print(
            name,
            sorted({len(word) for word in table}),
            sum(value != 0 for matrix in table.values() for value in matrix),
        )
