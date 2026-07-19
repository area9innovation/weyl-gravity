"""Exact candidate blocks for the Berger nonlinear clock second jet.

The radial block is obtained by differentiating the rod action after the
quadratic Weyl change of metric variables.  The remaining two blocks are a
fail-closed homological reconstruction on the certified clock doublets.  They
are useful diagnostics, but are not by themselves an independent derivation
of the full nonlinear canonical transformation.
"""

from __future__ import annotations

from fractions import Fraction

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers import (
    generate_berger_108_row_local_rod_hessian_pbw_overlay as local_rod,
)


MINUS = (Fraction(-1), Fraction(0))
TWO = (Fraction(2), Fraction(0))
MINUS_SIX = (Fraction(-6), Fraction(0))


def _rod_metric_source(component: int) -> replay.Polynomial:
    """Return delta S_rod/d H_component at the flat metric fixture."""

    matrix = local_rod.component_matrix(component)
    result: replay.Polynomial = {}
    for name in local_rod.RODS:
        gradient = [
            local_rod.derivative(local_rod.background(name), axis)
            for axis in range(4)
        ]
        for first in range(4):
            for second in range(4):
                coefficient = Fraction(
                    matrix[first][second]
                    * local_rod.ETA[first]
                    * local_rod.ETA[second],
                    2,
                )
                if coefficient:
                    result = local_rod.add(
                        result,
                        local_rod.scale(
                            local_rod.multiply(gradient[first], gradient[second]),
                            local_rod.rational(coefficient),
                        ),
                    )
        trace = sum(
            local_rod.ETA[axis] * matrix[axis][axis] for axis in range(4)
        )
        for axis in range(4):
            coefficient = Fraction(-trace * local_rod.ETA[axis], 4)
            if coefficient:
                result = local_rod.add(
                    result,
                    local_rod.scale(
                        local_rod.multiply(gradient[axis], gradient[axis]),
                        local_rod.rational(coefficient),
                    ),
                )
    return result


def radial_rod_action_hessian() -> replay.Operator:
    """Hessian induced by H_true=H+2 R H-3 R^2 eta+O(3)."""

    result: replay.Operator = {}
    sources = [_rod_metric_source(component) for component in range(10)]
    for component, source in enumerate(sources):
        replay.add_operator_term(result, (27 + component, 15, ()), replay.scale(source, TWO))
        replay.add_operator_term(result, (37, 5 + component, ()), replay.scale(source, TWO))

    trace_source: replay.Polynomial = {}
    for component, (first, second) in enumerate(local_rod.METRIC_COMPONENTS):
        if first == second:
            trace_source = replay.add(
                trace_source,
                replay.scale(
                    sources[component],
                    (Fraction(local_rod.ETA[first]), Fraction(0)),
                ),
            )
    replay.add_operator_term(
        result,
        (37, 15, ()),
        replay.scale(trace_source, MINUS_SIX),
    )
    return result


def square_coefficient(q00: replay.Operator, q10: replay.Operator) -> replay.Operator:
    return replay.add_operators(
        replay.compose(q00, q10),
        replay.compose(q10, q00),
    )


def weyl_clock_doublet_completion(
    q00: replay.Operator, q10: replay.Operator
) -> replay.Operator:
    """Minimal cyclic R--Theta block fixed by q00(sigma)=-R.

    This removes the Theta-antifield/Weyl-ghost residual and installs its
    frozen-pairing cotangent mate.
    """

    residual = square_coefficient(q00, q10)
    entry = {
        word: coefficient
        for (row, column, word), coefficient in residual.items()
        if row == 38 and column == 4
    }
    result: replay.Operator = {}
    for word, coefficient in entry.items():
        replay.add_operator_term(result, (38, 15, word), coefficient)
    for word, coefficient in replay.formal_adjoint_entry(entry).items():
        replay.add_operator_term(result, (37, 16, word), coefficient)
    return result


def temporal_clock_doublet_completion(
    q00: replay.Operator, q10: replay.Operator
) -> replay.Operator:
    """Minimal cyclic block fixed by q00(tau)=Theta.

    Only the metric-antifield and Theta-antifield output rows are used.  Their
    cotangent mates are derived from the certified signed-permutation pairing.
    """

    residual = square_coefficient(q00, q10)
    pairing = replay.pairing_map()
    inverse_pairing = {
        partner: (row, coefficient)
        for row, (partner, coefficient) in pairing.items()
    }
    result: replay.Operator = {}
    for output in (*range(27, 37), 38):
        entry = {
            word: replay.scale(coefficient, MINUS)
            for (row, column, word), coefficient in residual.items()
            if row == output and column == 3
        }
        for word, coefficient in entry.items():
            replay.add_operator_term(result, (output, 16, word), coefficient)
        if output == 38:
            continue

        paired_row, paired_coefficient = inverse_pairing[output]
        paired_entry = {
            word: replay.scale(coefficient, paired_coefficient)
            for word, coefficient in entry.items()
        }
        partner, partner_coefficient = pairing[16]
        if partner_coefficient[1] or not partner_coefficient[0]:
            raise AssertionError("Theta pairing coefficient ceased to be rational invertible")
        reciprocal = (Fraction(1, 1) / partner_coefficient[0], Fraction(0))
        for word, coefficient in replay.formal_adjoint_entry(paired_entry).items():
            replay.add_operator_term(
                result,
                (partner, paired_row, word),
                replay.scale(coefficient, reciprocal),
            )
    return result


def candidate_completion(
    q00: replay.Operator, q10: replay.Operator
) -> tuple[replay.Operator, dict[str, replay.Operator]]:
    radial = radial_rod_action_hessian()
    after_radial = replay.add_operators(q10, radial)
    weyl = weyl_clock_doublet_completion(q00, after_radial)
    after_weyl = replay.add_operators(after_radial, weyl)
    temporal = temporal_clock_doublet_completion(q00, after_weyl)
    complete = replay.add_operators(radial, weyl, temporal)
    return complete, {"radial": radial, "weyl": weyl, "temporal": temporal}
