"""Exact depth-five infinity recurrence for the four additional axial heads.

The metric source has a leading ``z^-2`` coefficient.  Consequently the
coefficient ``A5`` of ``H1`` depends on carrier data through inverse order
eight.  The depth gate below is intentional: using carrier depth seven gives
a plausible but false ``A5``.  This module is the slow producer for the
frozen ``depth5-heads.json`` artifact; ordinary certificate replay reads that
artifact and uses the independent verifier instead of solving it again.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_metric_heads import (
    _parse,
    build_data,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "depth5-heads.json"


def _derivative(value: sp.Expr, rate: sp.Expr, power: sp.Expr,
                z: sp.Symbol) -> sp.Expr:
    return sp.expand(rate*value + power*z*value - z**2*sp.diff(value, z))


def _text(value: sp.Expr) -> str:
    return sp.sstr(sp.cancel(value))


def build_heads(carrier_depth: int = 8) -> dict:
    if carrier_depth < 8:
        raise RuntimeError(
            "carrier depth below eight under-resolves A5 because the metric "
            "source starts at z^-2"
        )
    old = build_data()
    system = build_exact_system()
    r = system["symbols"]["r"]
    omega = system["symbols"]["omega"]
    z = sp.Symbol("z")
    carrier_flow = system["carrier"].subs(r, 1/z)
    full_flow = system["flow6"].subs(r, 1/z)
    answer = {}

    for label, branch in old["branches"].items():
        rate = _parse(branch["rate"], omega)
        carrier_power = _parse(branch["carrier_power"], omega)
        h1_power = _parse(branch["H1"]["power"], omega)
        h0_power = _parse(branch["H0_from_C_equals_zero"]["power"], omega)
        old_pq = [
            [_parse(value, omega) for value in pair]
            for pair in branch["carrier_coefficients_PQ_used_by_H0_check"]
        ]
        unknowns = []
        p_coefficients = []
        q_coefficients = []
        for n in range(carrier_depth + 1):
            if n < len(old_pq):
                p_value, q_value = old_pq[n]
            else:
                p_value, q_value = sp.symbols(f"{label}_p{n} {label}_q{n}")
                unknowns.extend((p_value, q_value))
            p_coefficients.append(p_value)
            q_coefficients.append(q_value)
        p_series = sum(value*z**n for n, value in enumerate(p_coefficients))
        q_series = sum(value*z**n for n, value in enumerate(q_coefficients))
        carrier_state = sp.Matrix([
            p_series,
            _derivative(p_series, rate, carrier_power, z),
            q_series,
            _derivative(q_series, rate, carrier_power, z),
        ])
        carrier_residual = carrier_state.applyfunc(
            lambda value: _derivative(value, rate, carrier_power, z)
        ) - carrier_flow*carrier_state
        equations = []
        unknown_set = set(unknowns)
        for row in (1, 3):
            expanded = sp.series(
                carrier_residual[row], z, 0, carrier_depth + 3
            ).removeO().expand()
            for n in range(carrier_depth + 2):
                coefficient = expanded.coeff(z, n)
                if coefficient != 0 and coefficient.free_symbols & unknown_set:
                    equations.append(coefficient)
        matrix, rhs = sp.linear_eq_to_matrix(equations, unknowns)
        solution, parameters = matrix.gauss_jordan_solve(rhs)
        solution = solution.subs({parameter: 0 for parameter in parameters})
        substitutions = dict(zip(unknowns, solution))
        p_series = sp.expand(p_series.subs(substitutions))
        q_series = sp.expand(q_series.subs(substitutions))
        carrier_state = sp.Matrix([
            p_series,
            _derivative(p_series, rate, carrier_power, z),
            q_series,
            _derivative(q_series, rate, carrier_power, z),
        ])

        source = (full_flow[5, :4]*carrier_state)[0]
        known_h1 = [
            _parse(value, omega)
            for value in branch["H1"]["coefficients_through_inverse_order_3"]
        ]
        a4, a5 = sp.symbols(f"{label}_a4 {label}_a5")
        h1_series = sum(
            value*z**n for n, value in enumerate(known_h1 + [a4, a5])
        )
        f_series = _derivative(h1_series, rate, h1_power, z)
        metric_residual = (
            _derivative(f_series, rate, h1_power, z)
            - full_flow[5, 4]*h1_series
            - full_flow[5, 5]*f_series
            - z**(h1_power - carrier_power)*source
        )
        expanded = sp.series(metric_residual, z, 0, 9).removeO().expand()
        recurrence_equations = []
        for n in range(9):
            coefficient = expanded.coeff(z, n)
            if coefficient != 0 and coefficient.free_symbols & {a4, a5}:
                recurrence_equations.append(coefficient)
        # The recurrence is triangular: the first equation fixes A4 and the
        # second fixes A5.  Later equations need A6,... and are not imposed.
        matrix, rhs = sp.linear_eq_to_matrix(recurrence_equations[:2], [a4, a5])
        solution, parameters = matrix.gauss_jordan_solve(rhs)
        solution = solution.subs({parameter: 0 for parameter in parameters})
        h1_coefficients = known_h1 + list(solution)
        h1_series = sp.expand(sum(
            value*z**n for n, value in enumerate(h1_coefficients)
        ))

        differentiated = sp.expand(
            _derivative(h1_series, rate, h1_power, z)
        )
        f_power = h1_power if rate != 0 else h1_power - 1
        differentiated = sp.expand(z**(f_power - h1_power)*differentiated)
        # For oscillatory heads A6=0 is the canonical truncation, and F6 is
        # retained because differentiation of A5 forces it.
        f_depth = 6 if rate != 0 else 5
        f_coefficients = [
            sp.cancel(differentiated.coeff(z, n)) for n in range(f_depth + 1)
        ]
        f_series = sum(value*z**n for n, value in enumerate(f_coefficients))

        relative_power = z**(h1_power - carrier_power)
        substitutions_h0 = {
            r: 1/z,
            system["states"]["carrier"][0]: relative_power*p_series,
            system["states"]["carrier"][1]: relative_power*_derivative(
                p_series, rate, carrier_power, z
            ),
            system["states"]["carrier"][2]: relative_power*q_series,
            system["states"]["carrier"][3]: relative_power*_derivative(
                q_series, rate, carrier_power, z
            ),
            system["states"]["reduced"][4]: h1_series,
            system["states"]["reduced"][5]: z**(h1_power - f_power)*f_series,
        }
        h0_exact = sp.cancel(system["h0"].subs(substitutions_h0))
        h0_series = sp.series(
            z**(h0_power - h1_power)*h0_exact, z, 0, 6
        ).removeO().expand()
        h0_coefficients = [
            sp.cancel(h0_series.coeff(z, n)) for n in range(6)
        ]

        answer[label] = {
            "rate": _text(rate),
            "carrier_power": _text(carrier_power),
            "H1_power": _text(h1_power),
            "H0_power": _text(h0_power),
            "F_power": _text(f_power),
            "carrier_depth": carrier_depth,
            "carrier_P": [_text(p_series.coeff(z, n)) for n in range(carrier_depth + 1)],
            "carrier_Q": [_text(q_series.coeff(z, n)) for n in range(carrier_depth + 1)],
            "H1": [_text(value) for value in h1_coefficients],
            "F": [_text(value) for value in f_coefficients],
            "H0": [_text(value) for value in h0_coefficients],
            "metric_recurrence_rank": int(matrix.rank()),
            "forced_log_coefficient": "0",
        }
    return answer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--carrier-depth", type=int, default=8)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build_heads(args.carrier_depth)
    if args.check:
        if expected != json.loads(OUTPUT.read_text()):
            raise SystemExit("depth-five head drift")
        print("PASS: exact depth-five recurrence reproduces")
    else:
        OUTPUT.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n")
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
