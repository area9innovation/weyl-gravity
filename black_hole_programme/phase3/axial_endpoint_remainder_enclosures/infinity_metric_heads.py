"""Exact formal infinity metric heads for the four axial carrier branches.

This is a deliberately small downstream consumer of the complete six-state
reconstruction.  It records the canonical particular lifts (both Einstein
kernel constants set to zero) and checks the displayed coefficients directly
against the exact rational flow.  No convergence, endpoint matching, flux,
or scattering statement is made here.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "infinity-metric-heads.json"
I = sp.I


class MetricHeadError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MetricHeadError(message)


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(value))


def strings(values: list[sp.Expr]) -> list[str]:
    return [sp.sstr(clean(value)) for value in values]


def metric_coefficients(omega: sp.Symbol) -> dict[str, dict]:
    w = omega
    common = 4*w**2 - I*w - 2

    xi0_a = [
        (w - 6*I)/(2*w**3),
        I*(w - 18*I)/(4*w**4),
        5*I*(5*w - 18*I)/(12*w**4),
        5*(5*w + 6*I)/(8*w**5),
    ]
    xi1_a = [
        I*(w + 6*I)/(4*w**2),
        (7*w - 30*I)/(8*w**3),
        -5*(5*w + 6*I)/(24*w**3),
        5*I*(17*w - 42*I)/(16*w**4),
    ]
    xi2_a = [
        2*common,
        sp.Integer(0),
        (
            256*w**6 - 128*I*w**5 - 304*w**4 + 116*I*w**3
            + 99*w**2 - 24*I*w - 6
        )/w**2,
        2*I*(
            2048*w**8 - 2048*I*w**7 - 3584*w**6 + 2272*I*w**5
            + 1832*w**4 - 726*I*w**3 - 306*w**2 + 63*I*w + 9
        )/(3*w**3),
    ]
    xi3_a = [
        -I*w/2,
        sp.Integer(0),
        -I*(64*w**4 - 16*I*w**3 - 40*w**2 + 11*I*w + 2)/(4*w),
        (
            256*w**5 - 192*I*w**4 - 272*w**3 + 120*I*w**2
            + 63*w - 15*I
        )/(3*w),
    ]

    raw = {
        "XI0": {
            "rate": sp.Integer(0),
            "carrier_power": sp.Integer(0),
            "H1_power": sp.Integer(-1),
            "H1": xi0_a,
            "H0_power": sp.Integer(2),
            "H0": [
                sp.Rational(1, 2),
                sp.Integer(0),
                -I*(w + 6*I)/(4*w**2),
                -(w - 18*I)/(4*w**3),
            ],
            "metric_pivot": "-2*I*omega*(n+1)",
            "carrier_determinant": "-4*omega**2*n*(n-1)",
            "source_first_power": 2,
            "source": [
                -I*(w - 6*I)/w**2,
                -I*(w + 2*I)*(4*w - 27*I)/(2*w**3),
                -I*(8*w**3 - 29*I*w**2 + 84*w + 156*I)/(2*w**4),
                -I*(32*w**4 - 116*I*w**3 + 373*w**2 + 390*I*w - 624)/(4*w**5),
            ],
            "carrier": [
                [1, 0],
                [3*I/w, 0],
                [(-I*w - 3)/w**2, -3/w**2],
                [-1/w**2, (w - 6*I)/w**3],
                [(5*w - 15*I)/(4*w**3), -5*I/w**3],
            ],
        },
        "XI1": {
            "rate": sp.Integer(0),
            "carrier_power": sp.Integer(-1),
            "H1_power": sp.Integer(-1),
            "H1": xi1_a,
            "H0_power": sp.Integer(2),
            "H0": [
                I*w/4,
                sp.Integer(-1),
                (w - 18*I)/(8*w),
                I*(7*w - 30*I)/(8*w**2),
            ],
            "metric_pivot": "-2*I*omega*(n+1)",
            "carrier_determinant": "-4*omega**2*n*(n+1)",
            "source_first_power": 1,
            "source": [
                (w + 6*I)/(2*w),
                (4*w**2 + 13*I*w - 78)/(4*w**2),
                (8*w**3 + 35*I*w**2 - 76*w - 204*I)/(4*w**3),
                (32*w**4 + 140*I*w**3 - 267*w**2 - 658*I*w + 816)/(8*w**4),
            ],
            "carrier": [
                [0, 1],
                [sp.Rational(1, 2), 3*I/w],
                [I/w, (I*w - 6)/(2*w**2)],
                [5*I/(8*w), -5/w**2],
                [-sp.Rational(17, 8)/w**2, (-15*w - 30*I)/(8*w**3)],
            ],
        },
        "XI2": {
            "rate": -2*I*w,
            "carrier_power": -4*I*w,
            "H1_power": 2 - 4*I*w,
            "H1": xi2_a,
            "H0_power": 2 - 4*I*w,
            "H0": [
                -common,
                2*common,
                -(
                    256*w**5 - 128*I*w**4 - 272*w**3 + 100*I*w**2
                    + 65*w - 16*I
                )/(2*w),
                -I*(
                    4096*w**7 - 2560*I*w**6 - 5632*w**5 + 2528*I*w**4
                    + 2248*w**3 - 858*I*w**2 - 297*w + 102*I
                )/(6*w**2),
            ],
            "metric_pivot": "2*I*omega*(n-1)",
            "carrier_determinant": "-4*omega**2*n*(n-1)",
            "source_first_power": -1,
            "source": [
                -4*I*w*(4*w**2 - I*w - 2),
                8*(4*w**2 - 2*I*w - 1)*(4*w**2 - I*w - 2),
                2*I*(256*w**6 - 384*I*w**5 - 432*w**4 + 284*I*w**3
                     + 137*w**2 - 36*I*w - 6)/w,
                -4*(4*w**2 - I*w - 2)*(
                    256*w**5 - 576*I*w**4 - 608*w**3 + 348*I*w**2
                    + 102*w - 21*I
                )/(3*w),
            ],
            "carrier": [
                [1, -2],
                [(8*I*w**2 - 3*I)/w, 0],
                [
                    (-32*w**4 + 22*w**2 + 4*I*w - 3)/w**2,
                    (-64*w**4 + 44*w**2 - 8*I*w - 9)/w**2,
                ],
                [
                    (-256*I*w**5 + 272*I*w**3 - 72*w**2 - 60*I*w + 15)/(3*w**2),
                    (-1024*I*w**6 - 384*w**5 + 1088*I*w**4 + 288*w**3
                     - 366*I*w**2 - 42*w + 36*I)/(3*w**3),
                ],
                [
                    (2048*w**7 - 2944*w**5 - 768*I*w**4 + 648*w**3
                     + 222*I*w**2 + 60*w + 45*I)/(12*w**3),
                    (2048*w**7 - 2048*I*w**6 - 3456*w**5 + 1792*I*w**4
                     + 1640*w**3 - 538*I*w**2 - 244*w + 35*I)/(2*w**3),
                ],
            ],
        },
        "XI3": {
            "rate": -2*I*w,
            "carrier_power": -1 - 4*I*w,
            "H1_power": 2 - 4*I*w,
            "H1": xi3_a,
            "H0_power": 2 - 4*I*w,
            "H0": [
                I*w/4,
                -I*w/2,
                I*(64*w**4 - 16*I*w**3 - 32*w**2 + 9*I*w - 2)/(8*w),
                -(
                    1024*w**6 - 384*I*w**5 - 800*w**4 + 240*I*w**3
                    + 102*w**2 - 69*I*w + 18
                )/(24*w**2),
            ],
            "metric_pivot": "2*I*omega*(n-1)",
            "carrier_determinant": "-4*omega**2*n*(n+1)",
            "source_first_power": -2,
            "source": [
                -w**2,
                -2*I*w*(4*w**2 - 2*I*w - 1),
                (64*w**4 - 80*I*w**3 - 56*w**2 + 17*I*w + 2)/2,
                I*(256*w**6 - 576*I*w**5 - 608*w**4 + 348*I*w**3
                   + 102*w**2 - 21*I*w + 6)/(3*w),
            ],
            "carrier": [
                [0, 1],
                [-sp.Rational(1, 2), (8*I*w**2 + w - 3*I)/w],
                [
                    (-4*I*w**2 + I)/w,
                    (-64*w**4 + 32*I*w**3 + 52*w**2 - 5*I*w - 6)/(2*w**2),
                ],
                [
                    (128*w**3 - 32*I*w**2 - 64*w + 5*I)/(8*w),
                    (-1024*I*w**5 - 1152*w**4 + 1568*I*w**3 + 576*w**2
                     - 351*I*w - 60)/(12*w**2),
                ],
                [
                    (1024*I*w**5 + 768*w**4 - 896*I*w**3 - 312*w**2 + 51)/(24*w**2),
                    (4096*w**7 - 8192*I*w**6 - 12032*w**5 + 8320*I*w**4
                     + 4752*w**3 - 1788*I*w**2 - 147*w + 90*I)/(24*w**3),
                ],
            ],
        },
    }

    result = {}
    for label, branch in raw.items():
        rate = branch["rate"]
        h1_power = branch["H1_power"]
        h1 = branch["H1"]
        if rate == 0:
            f_power = h1_power - 1
            f_coefficients = [(h1_power - n)*value for n, value in enumerate(h1)]
        else:
            f_power = h1_power
            f_coefficients = [rate*h1[0]]
            f_coefficients.extend(
                rate*h1[n] + (h1_power - n + 1)*h1[n - 1]
                for n in range(1, len(h1))
            )
            # H1 is canonically truncated with A4=0, but differentiating its
            # A3/r^3 term produces one further F coefficient.  Keeping this
            # derivative-forced term removes the marginal cross-rate
            # Volterra residual without requiring a new carrier recurrence.
            f_coefficients.append((h1_power - 3)*h1[3])
        result[label] = {
            "rate": sp.sstr(rate),
            "carrier_power": sp.sstr(branch["carrier_power"]),
            "H1": {
                "power": sp.sstr(h1_power),
                "coefficients_through_inverse_order_3": strings(h1),
            },
            "F_equals_dH1_dr": {
                "power": sp.sstr(f_power),
                "coefficients_through_inverse_order_3": strings(f_coefficients),
                "highest_inverse_order": len(f_coefficients) - 1,
                "H1_inverse_order_4_convention": (
                    "A4=0; the oscillatory F4 is derivative-forced from A3"
                    if rate != 0 else "NOT_APPLICABLE"
                ),
            },
            "H0_from_C_equals_zero": {
                "power": sp.sstr(branch["H0_power"]),
                "coefficients_through_inverse_order_3": strings(branch["H0"]),
            },
            "recurrence": {
                "metric_pivot": branch["metric_pivot"],
                "metric_pivots_n_0_to_3": strings([
                    (-2*I*w*(n + 1) if rate == 0 else 2*I*w*(n - 1))
                    for n in range(4)
                ]),
                "carrier_determinant": branch["carrier_determinant"],
                "oscillatory_n1_obstruction": "0" if rate != 0 else "NOT_APPLICABLE",
                "free_EI2_coefficient": "0 (canonical particular lift)" if rate != 0 else "NOT_APPLICABLE",
                "forced_log_coefficient": "0",
            },
            "normalized_metric_source": {
                "definition": "B(P,P_prime,Q,Q_prime)=sum(s_k*r^(-k)) after factoring exp(rate*r)*r^carrier_power",
                "first_inverse_power": branch["source_first_power"],
                "coefficients_used_by_displayed_metric_recurrence": strings(branch["source"]),
            },
            "carrier_coefficients_PQ_used_by_H0_check": [
                strings(pair) for pair in branch["carrier"]
            ],
        }
    return result


def _parse(value: str, omega: sp.Symbol) -> sp.Expr:
    return sp.sympify(value, locals={"omega": omega})


def _truncate(value: sp.Expr, z: sp.Symbol, order: int) -> sp.Expr:
    return sp.series(value, z, 0, order).removeO().expand()


def verify_symbolically(data: dict, labels: tuple[str, ...] | None = None) -> None:
    """Check every displayed coefficient against the exact six-state flow."""
    system = build_exact_system()
    r = system["symbols"]["r"]
    omega = system["symbols"]["omega"]
    z = sp.Symbol("z")

    k21 = _truncate(system["kernel"][1, 0].subs(r, 1/z), z, 9)
    k22 = _truncate(system["kernel"][1, 1].subs(r, 1/z), z, 9)

    def derivative(series: sp.Expr, rate: sp.Expr, power: sp.Expr) -> sp.Expr:
        return sp.expand(rate*series + power*z*series - z**2*sp.diff(series, z))

    def metric_operator(series: sp.Expr, rate: sp.Expr, power: sp.Expr) -> sp.Expr:
        first = derivative(series, rate, power)
        second = derivative(first, rate, power)
        return _truncate(second - k22*first - k21*series, z, 7)

    selected = labels or tuple(data["branches"])
    for label in selected:
        branch = data["branches"][label]
        rate = _parse(branch["rate"], omega)
        carrier_power = _parse(branch["carrier_power"], omega)
        h1_power = _parse(branch["H1"]["power"], omega)
        h0_power = _parse(branch["H0_from_C_equals_zero"]["power"], omega)
        f_power = _parse(branch["F_equals_dH1_dr"]["power"], omega)

        pq = [
            [_parse(entry, omega) for entry in row]
            for row in branch["carrier_coefficients_PQ_used_by_H0_check"]
        ]
        p_series = sum(row[0]*z**n for n, row in enumerate(pq))
        q_series = sum(row[1]*z**n for n, row in enumerate(pq))
        pp_series = derivative(p_series, rate, carrier_power)
        qp_series = derivative(q_series, rate, carrier_power)
        source_record = branch["normalized_metric_source"]
        source_first = source_record["first_inverse_power"]
        source = sum(
            _parse(value, omega)*z**(source_first + index)
            for index, value in enumerate(
                source_record["coefficients_used_by_displayed_metric_recurrence"]
            )
        )

        h1_coefficients = [
            _parse(entry, omega)
            for entry in branch["H1"]["coefficients_through_inverse_order_3"]
        ]
        h1_series = sum(value*z**n for n, value in enumerate(h1_coefficients))
        residual = _truncate(
            metric_operator(h1_series, rate, h1_power)
            - z**(h1_power - carrier_power)*source,
            z,
            6,
        )
        for order in range(1, 5):
            require(clean(residual.coeff(z, order)) == 0,
                    f"{label} H1 residual at recurrence order {order}")

        if rate != 0:
            require(branch["recurrence"]["metric_pivots_n_0_to_3"][1] == "0",
                    f"{label} missing resonant zero pivot")
            require(branch["recurrence"]["oscillatory_n1_obstruction"] == "0",
                    f"{label} resonance obstruction is not zero")
            require(branch["recurrence"]["forced_log_coefficient"] == "0",
                    f"{label} unexpectedly forces a logarithm")

        f_exact = derivative(h1_series, rate, h1_power)
        f_coefficients = [
            _parse(entry, omega)
            for entry in branch["F_equals_dH1_dr"]["coefficients_through_inverse_order_3"]
        ]
        f_recorded = z**(h1_power - f_power)*sum(
            value*z**n for n, value in enumerate(f_coefficients)
        )
        f_difference = _truncate(f_exact - f_recorded, z, 5)
        start = int(h1_power - f_power)
        for order in range(start, start + len(f_coefficients)):
            require(clean(f_difference.coeff(z, order)) == 0,
                    f"{label} F coefficient {order - start}")

        relative_carrier = z**(h1_power - carrier_power)
        substitutions = {
            r: 1/z,
            system["states"]["carrier"][0]: relative_carrier*p_series,
            system["states"]["carrier"][1]: relative_carrier*pp_series,
            system["states"]["carrier"][2]: relative_carrier*q_series,
            system["states"]["carrier"][3]: relative_carrier*qp_series,
            system["states"]["reduced"][4]: h1_series,
            system["states"]["reduced"][5]: f_exact,
        }
        h0_exact = _truncate(system["h0"].subs(substitutions), z, 7)
        h0_coefficients = [
            _parse(entry, omega)
            for entry in branch["H0_from_C_equals_zero"]["coefficients_through_inverse_order_3"]
        ]
        h0_recorded = z**(h1_power - h0_power)*sum(
            value*z**n for n, value in enumerate(h0_coefficients)
        )
        h0_difference = _truncate(h0_exact - h0_recorded, z, 7)
        start = int(sp.re(h1_power - h0_power))
        for order in range(start, start + 4):
            require(clean(h0_difference.coeff(z, order)) == 0,
                    f"{label} H0 coefficient {order - start}")


def build_data() -> dict:
    omega = sp.Symbol("omega", nonzero=True, real=True)
    return {
        "schema": "phase3-axial-infinity-metric-heads-v1",
        "scope": {
            "background": "Schwarzschild M=1 in ingoing EF coordinates",
            "sector": "axial ell=2 with exp(+i*omega*v)",
            "frequency": "real omega in [1/2,3/4]",
            "radial_class": "formal polyhomogeneous infinity module",
            "normalization": "canonical particular lift; both Einstein-kernel constants zero",
        },
        "series_convention": (
            "X=e^(rate*r)*r^power*sum(coefficients[n]*r^(-n)); H1/H0 end at n=3, oscillatory F includes derivative-forced n=4"
        ),
        "branches": metric_coefficients(omega),
        "claim": {
            "statement": (
                "All four imported carrier heads have exact log-free metric lifts "
                "through inverse-radius order three.  The XI2/XI3 n=1 metric "
                "resonance is compatible and has zero forced-log coefficient."
            ),
            "does_not_establish": [
                "convergence of the formal series",
                "endpoint remainder bounds",
                "horizon-to-infinity matching",
                "finite Lee-Wald flux",
                "scattering channels or stability",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-branch", choices=("XI0", "XI1", "XI2", "XI3"))
    parser.add_argument("--verify-sequence-index", type=int)
    args = parser.parse_args()
    data = build_data()
    if args.verify_sequence_index is not None:
        labels = ("XI0", "XI1", "XI2", "XI3")
        require(0 <= args.verify_sequence_index < len(labels), "invalid sequence index")
        label = labels[args.verify_sequence_index]
        verify_symbolically(data, (label,))
        print("PASS exact infinity metric residual", label, flush=True)
        next_index = args.verify_sequence_index + 1
        if next_index < len(labels):
            os.execv(
                sys.executable,
                [sys.executable, str(Path(__file__).resolve()),
                 "--verify-sequence-index", str(next_index)],
            )
        encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
        require(OUTPUT.exists(), f"missing {OUTPUT}")
        require(OUTPUT.read_text() == encoded, "infinity metric-head JSON drift")
        print("PASS all exact XI0..XI3 infinity metric heads")
        return
    if args.verify_branch:
        verify_symbolically(data, (args.verify_branch,))
        print("PASS exact infinity metric residual", args.verify_branch)
        return

    encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.check:
        require(OUTPUT.exists(), f"missing {OUTPUT}")
        require(OUTPUT.read_text() == encoded, "infinity metric-head JSON drift")
        print("PASS infinity metric-head JSON reproduces")
    else:
        OUTPUT.write_text(encoded)
        print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
