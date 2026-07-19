#!/usr/bin/env python3
"""Independent replay of the symmetric-point ghost n=3 simplex integral."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
from scipy.integrate import quad
import sympy as sp

from .generic_background_ghost_n3_symmetric_point_simplex_integration import (
    OUTPUT,
    PROJECTION,
    ROOT,
    SCHEMA,
)


A, B, C = sp.symbols("alpha1 alpha2 alpha0")
E2, E3 = sp.symbols("e2 e3")


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _poly(terms: list[dict[str, Any]], variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * sp.prod(variable ** exponent for variable, exponent in zip(variables, term["exponents"]))
            for term in terms
        )
    )


def _upstream_symmetric_numerator(row: dict[str, Any]) -> sp.Expr:
    base = sum(
        _q(term["coefficient"])
        * A ** term["alpha_exponents"][0]
        * B ** term["alpha_exponents"][1]
        for term in row["terms"]
    )
    average = sp.expand(
        sum(
            base.xreplace({A: permutation[0], B: permutation[1]})
            for permutation in itertools.permutations((A, B, C), 3)
        )
        / 6
    )
    symmetric, remainder, mapping = sp.symmetrize(
        average, [A, B, C], formal=True
    )
    if remainder != 0:
        raise ValueError("upstream symmetric numerator has a noninvariant remainder")
    return sp.expand(
        symmetric.subs(
            {
                mapping[0][0]: 1,
                mapping[1][0]: E2,
                mapping[2][0]: E3,
            }
        )
    )


def _vanishing_order(polynomial: sp.Expr, point: tuple[int, int]) -> int:
    x, y = sp.symbols("x y")
    translated = sp.Poly(
        sp.expand(polynomial.subs({A: point[0] + x, B: point[1] + y})),
        x,
        y,
    )
    return min(sum(exponents) for exponents, coefficient in translated.terms() if coefficient)


def _master_closed_value(row: dict[str, Any], scalar_master: mp.mpf) -> mp.mpf:
    rational = _q(row["value"]["rational"])
    coefficient = _q(row["value"]["scalar_triangle_master_coefficient"])
    return (
        mp.mpf(int(rational.p)) / int(rational.q)
        + mp.mpf(int(coefficient.p)) / int(coefficient.q) * scalar_master
    )


def _verify_scalar_master(stored: dict[str, Any]) -> mp.mpf:
    proof = stored["exact_reduction_certificate"]
    x, y, phi = sp.symbols("x y phi", positive=True)
    denominator = 1 + x + y
    alpha1, alpha2 = x / denominator, y / denominator
    alpha0 = 1 / denominator
    jacobian = sp.det(
        sp.Matrix(
            [
                [sp.diff(alpha1, x), sp.diff(alpha1, y)],
                [sp.diff(alpha2, x), sp.diff(alpha2, y)],
            ]
        )
    )
    e2 = alpha0 * alpha1 + alpha1 * alpha2 + alpha2 * alpha0
    sector_integrand = sp.cancel(jacobian / e2)
    expected_integrand = 1 / ((1 + x + y) * (x + y + x * y))
    if sp.cancel(sector_integrand - expected_integrand) != 0:
        raise ValueError("scalar-master sector map or Jacobian drifted")
    antiderivative = sp.log((x + (1 + x) * y) / (1 + x + y)) / (
        x**2 + x + 1
    )
    if sp.cancel(sp.diff(antiderivative, y) - expected_integrand) != 0:
        raise ValueError("scalar-master y antiderivative drifted")
    x_phi = (sp.sqrt(3) * sp.tan(phi) - 1) / 2
    if sp.trigsimp(
        sp.diff(x_phi, phi) / (x_phi**2 + x_phi + 1) - 2 / sp.sqrt(3)
    ) != 0:
        raise ValueError("scalar-master angle measure drifted")
    expected_intervals = [
        (1, sp.Rational(1, 3), sp.Rational(1, 2)),
        (1, sp.Rational(1, 6), sp.Rational(1, 3)),
        (-1, sp.Rational(0), sp.Rational(1, 6)),
        (-1, sp.Rational(1, 2), sp.Rational(2, 3)),
    ]
    intervals = [
        (
            row["sign"],
            _q(row["lower_pi_units"]),
            _q(row["upper_pi_units"]),
        )
        for row in proof["log_sine_intervals"]
    ]
    if intervals != expected_intervals:
        raise ValueError("scalar-master log-sine interval decomposition drifted")
    # The four interval endpoints give Cl2(pi/3)+Cl2(4*pi/3)/2.
    # The stored Fourier distribution identity then gives 2 Cl2(pi/3)/3;
    # multiplying by 2*sqrt(3) yields 4 Cl2(pi/3)/sqrt(3).
    if sp.simplify(1 + sp.Rational(1, 2) * sp.Rational(-2, 3) - sp.Rational(2, 3)) != 0:
        raise ValueError("scalar-master Clausen distribution arithmetic drifted")

    mp.mp.dps = 60
    clausen = mp.im(mp.polylog(2, mp.e ** (mp.j * mp.pi / 3)))
    closed = 4 * clausen / mp.sqrt(3)

    def integrand(x: float) -> float:
        if x == 0.0:
            return 0.0
        return 3.0 * __import__("math").log(
            ((1.0 + x) * (1.0 + 2.0 * x)) / (x * (x + 2.0))
        ) / (x * x + x + 1.0)

    numeric, error = quad(
        integrand, 0.0, 1.0, points=[0.0, 1.0], epsabs=2e-12, epsrel=2e-12
    )
    if error > 2e-10 or abs(mp.mpf(numeric) - closed) > mp.mpf("2e-11"):
        raise ValueError("scalar triangle Clausen reduction failed numerical replay")
    if abs(mp.mpf(stored["decimal_60"]) - closed) > mp.mpf("1e-58"):
        raise ValueError("stored scalar triangle decimal drifted")
    return closed


def _verify_master_moments(rows: list[dict[str, Any]], scalar_master: mp.mpf) -> dict[tuple[int, int], tuple[sp.Rational, sp.Rational]]:
    a, b = A, B
    c = 1 - a - b
    e2 = sp.expand(a * b + b * c + c * a)
    e3 = sp.expand(a * b * c)
    expected_targets = {
        "M11": 54 * e3 / e2 + 4 / e2 - 22,
        "M12": 3 * e3 / e2**2 - 1 / e2 + 4,
        "M23": 54 * e3**2 / e2**3 - 10 / e2 + 46,
        "M34": 486 * e3**3 / e2**4 - 62 / e2 + 290,
    }
    expected_orders = {
        "M11": [1, 1, 0],
        "M12": [1, 1, 0],
        "M23": [2, 2, 1],
        "M34": [3, 3, 2],
    }
    values: dict[tuple[int, int], tuple[sp.Rational, sp.Rational]] = {
        (0, 0): (sp.Rational(1, 2), sp.S.Zero),
        (0, 1): (sp.S.Zero, sp.S.One),
    }
    for row in rows:
        moment_id = row["moment_id"]
        certificate = row["divergence_certificate"]
        power = certificate["denominator_power"]
        polynomial = _poly(certificate["P_terms"], (a, b))
        swapped = polynomial.xreplace({a: b, b: a})
        vector_a = a * c * polynomial / e2**power
        vector_b = b * c * swapped / e2**power
        divergence = sp.cancel(sp.diff(vector_a, a) + sp.diff(vector_b, b))
        if sp.cancel(divergence - expected_targets[moment_id]) != 0:
            raise ValueError(f"master divergence identity drifted: {moment_id}")
        orders = [
            _vanishing_order(polynomial, point)
            for point in ((0, 0), (1, 0), (0, 1))
        ]
        if orders != expected_orders[moment_id] or orders != certificate[
            "vertex_vanishing_orders"
        ]:
            raise ValueError(f"master corner-flux order drifted: {moment_id}")

        p, q = row["powers"]
        exponent = 2 * q - 3 * p - 3

        def outer(x: float) -> float:
            result, _ = quad(
                lambda t: (
                    6
                    * x ** (2 * p - q + 1)
                    * t**p
                    * (1 + x * (1 + t)) ** exponent
                    / (1 + t + x * t) ** q
                ),
                0.0,
                1.0,
                epsabs=2e-13,
                epsrel=2e-13,
            )
            return result

        numeric, _ = quad(outer, 0.0, 1.0, epsabs=2e-12, epsrel=2e-12)
        if abs(mp.mpf(numeric) - _master_closed_value(row, scalar_master)) > mp.mpf(
            "2e-11"
        ):
            raise ValueError(f"master moment quadrature drifted: {moment_id}")
        values[(p, q)] = (
            _q(row["value"]["rational"]),
            _q(row["value"]["scalar_triangle_master_coefficient"]),
        )
    return values


def _verify_channels(
    stored_rows: list[dict[str, Any]],
    upstream_rows: list[dict[str, Any]],
    moments: dict[tuple[int, int], tuple[sp.Rational, sp.Rational]],
    scalar_master: mp.mpf,
) -> None:
    if [row["channel_id"] for row in stored_rows] != [
        row["channel_id"] for row in upstream_rows
    ]:
        raise ValueError("symmetric-point channel order drifted")
    for stored, upstream in zip(stored_rows, upstream_rows):
        expected_numerator = _upstream_symmetric_numerator(upstream)
        if sp.expand(_poly(stored["symmetric_numerator_terms"], (E2, E3)) - expected_numerator) != 0:
            raise ValueError("symmetric numerator failed upstream reconstruction")
        rational = sp.S.Zero
        master = sp.S.Zero
        for (e2_power, e3_power), coefficient in sp.Poly(
            expected_numerator, E2, E3
        ).terms():
            if coefficient == 0:
                continue
            key = (e3_power, 4 - e2_power)
            if key not in moments:
                raise ValueError(f"unreduced symmetric moment: {key}")
            rational += coefficient * moments[key][0]
            master += coefficient * moments[key][1]
        value = stored["integrated_value"]
        if rational != _q(value["rational"]) or master != _q(
            value["scalar_triangle_master_coefficient"]
        ):
            raise ValueError("integrated channel value failed exact reconstruction")
        numeric = (
            mp.mpf(int(rational.p)) / int(rational.q)
            + mp.mpf(int(master.p)) / int(master.q) * scalar_master
        )
        if abs(mp.mpf(value["decimal_60"]) - numeric) > mp.mpf("1e-58"):
            raise ValueError("integrated channel decimal drifted")


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)

    projection = json.loads(PROJECTION.read_text())
    reference = stored["dependencies"]["five_carrier_projection"]
    if (
        reference["path"] != str(PROJECTION.relative_to(ROOT))
        or reference["result_id"] != projection["result_id"]
        or reference["sha256"] != _sha256(PROJECTION)
    ):
        raise ValueError("symmetric-point projection dependency drifted")

    payload = {
        "masters": stored["master_moments"],
        "channels": stored["channel_rows"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != stored["formula_digest"]:
        raise ValueError("symmetric-point formula digest drifted")

    scalar_master = _verify_scalar_master(stored["scalar_triangle_master"])
    moments = _verify_master_moments(stored["master_moments"], scalar_master)
    _verify_channels(
        stored["channel_rows"], projection["projection_rows"], moments, scalar_master
    )

    flags = stored["claim_flags"]
    if flags["GENERIC_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATED"] is not True or any(
        flag is not False
        for name, flag in flags.items()
        if name != "GENERIC_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATED"
    ):
        raise ValueError("symmetric-point result crossed its claim boundary")
    return stored


def main() -> int:
    verify()
    print("independent generic ghost n=3 symmetric-point simplex integration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
