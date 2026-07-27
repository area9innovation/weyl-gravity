#!/usr/bin/env python3
"""Independently verify the massive axial Jost crosswalk certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import acb, arb
import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
R, W, M, K, SIGMA, EPS = sp.symbols(
    "r omega m k sigma eps", nonzero=True
)
LAMBDA, N = sp.symbols("lam n")
F = (R - 2) / R


def exact(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def parse(value: str) -> sp.Expr:
    return sp.sympify(
        value,
        locals={
            "r": R,
            "omega": W,
            "m": M,
            "k": K,
            "sigma": SIGMA,
            "eps": EPS,
            "lam": LAMBDA,
            "n": N,
            "I": sp.I,
        },
    )


def dstar(value: sp.Expr) -> sp.Expr:
    return exact(F * sp.diff(value, R))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parsed_matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(entry) for entry in row] for row in rows])


def verify(data: dict | None = None) -> None:
    if data is None:
        data = json.loads(CERTIFICATE.read_text())
    jsonschema.validate(data, json.loads(SCHEMA.read_text()))
    assert data["status"] == (
        "ANALYTIC_COMPLETE_MASSIVE_JOST_CROSSWALK_AND_NONZERO_QNM_VELOCITY"
    )
    flags = data["claim_flags"]
    for name in (
        "parameter_analytic_horizon_jost_plane",
        "parameter_analytic_infinity_jost_plane",
        "opposite_jost_admixture_excluded",
        "complete_massive_jost_crosswalk",
        "physical_squared_mass_qnm_velocity_identified",
        "physical_squared_mass_qnm_velocity_nonzero",
    ):
        assert flags[name] is True
    assert flags["global_causal_resolvent_certified"] is False

    coupling = sp.Matrix(
        [
            [
                -F * (10 / R**2 - 16 / R**3),
                -8 * F * (R - 3) / R**3,
            ],
            [-2 * F / R**2, -F * (4 / R**2 + 2 / R**3)],
        ]
    ).applyfunc(exact)
    infinity = data["infinity_jost"]
    assert (
        parsed_matrix(infinity["coupling_matrix_B"]) - coupling
    ).applyfunc(exact) == sp.zeros(2)
    assert parsed_matrix(infinity["r_squared_coupling_limit"]) == sp.Matrix(
        [[-10, -8], [-2, -4]]
    )

    p = SIGMA * sp.I * (K + M * F / (K * R))
    residual = exact(
        dstar(p) + p**2 + K**2 + M - M * F
    ).subs(SIGMA**2, 1)
    assert exact(parse(infinity["phase_log_derivative"]) - p) == 0
    assert exact(parse(infinity["phase_residual"]) - residual) == 0
    assert exact(
        sp.limit(R**2 * residual, R, sp.oo)
        - parse(infinity["r_squared_phase_residual_limit"])
    ) == 0
    assert parse(infinity["coulomb_exponent_mass_derivative_at_zero"]) == 0
    assert parse(infinity["binomial_parameter_abs_upper"]) < 1
    assert parse(infinity["decay_at_m_zero_lower"]) > sp.Rational(1, 5)
    assert parse(
        infinity["decay_on_declared_mass_disk_lower"]
    ) > sp.Rational(1, 5)

    horizon = data["horizon_jost"]
    assert sp.simplify(
        parse(horizon["indicial_polynomial"])
        - (W**2 + LAMBDA**2 / 4)
    ) == 0
    assert sp.factor(parse(horizon["plus_recursion_denominator"])) == (
        N * (N + 4 * sp.I * W) / 4
    )
    assert sp.factor(parse(horizon["minus_recursion_denominator"])) == (
        N * (N - 4 * sp.I * W) / 4
    )
    assert parse(horizon["qnm_disk_real_axis_margin"]) > 0
    assert parsed_matrix(horizon["coupling_over_f_at_horizon"]) == sp.Matrix(
        [[-sp.Rational(1, 2), 1], [-sp.Rational(1, 2), -sp.Rational(5, 4)]]
    )

    schur = data["schur_reduction"]
    a, g, a1, b1, c1, g1 = sp.symbols(
        "a g a1 b1 c1 g1", nonzero=True
    )
    expected = sp.Matrix(
        [[a + EPS * a1, EPS * b1], [EPS * c1, g + EPS * g1]]
    )
    # Reparse with the symbols used in the stored expression.
    stored = sp.Matrix(
        [
            [
                sp.sympify(
                    v,
                    locals={
                        "eps": EPS,
                        "a": a,
                        "g": g,
                        "a1": a1,
                        "b1": b1,
                        "c1": c1,
                        "g1": g1,
                    },
                )
                for v in row
            ]
            for row in schur["connection_model"]
        ]
    )
    assert (stored - expected).applyfunc(exact) == sp.zeros(2)
    reduced = exact(stored[0, 0] - stored[0, 1] / stored[1, 1] * stored[1, 0])
    assert exact(sp.diff(reduced, EPS).subs(EPS, 0) - a1) == 0
    assert exact(
        sp.diff(stored.det(), EPS).subs({EPS: 0, a: 0}) - a1 * g
    ) == 0

    # Recompute the certified velocity enclosure from the imported balls.
    scope = data["scope"]["qnm_center"]
    center_re = sp.Rational(scope["re"])
    center_im = sp.Rational(scope["im"])
    radius = sp.Rational(scope["radius"])
    kappa = acb(arb("0 +/- 0.0468"), arb("0.1 +/- 0.0371"))
    omega = acb(
        arb(f"{float(center_re)} +/- {float(radius)}"),
        arb(f"{float(center_im)} +/- {float(radius)}"),
    )
    velocity = 2 * acb(0, 1) * kappa / (3 * omega)
    enclosure = data["mass_velocity"]["certified_outer_enclosure"]
    re_lo, re_hi = map(sp.Rational, enclosure["re"])
    im_lo, im_hi = map(sp.Rational, enclosure["im"])
    re_outer = arb(
        f"{float((re_lo + re_hi) / 2)} +/- "
        f"{float((re_hi - re_lo) / 2)}"
    )
    im_outer = arb(
        f"{float((im_lo + im_hi) / 2)} +/- "
        f"{float((im_hi - im_lo) / 2)}"
    )
    assert re_outer.contains(velocity.real)
    assert im_outer.contains(velocity.imag)
    assert not re_outer.contains(0)
    assert data["mass_velocity"]["excludes_zero"] is True

    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        assert path.is_file()
        assert sha256(path) == imported["sha256"]
    selector_path = ROOT / data["imports"]["intrinsic_qnm_selector"]["path"]
    selector = json.loads(selector_path.read_text())
    assert selector["result"]["kappa_beta_over_alpha_enclosure"] == (
        "[+/- 0.0468] + [0.1 +/- 0.0371]j"
    )

    exclusions = set(data["does_not_establish"])
    assert "a global weighted exterior Fredholm domain" in exclusions
    assert "a retarded inverse-Laplace contour deformation" in exclusions


if __name__ == "__main__":
    verify()
    print("PASS complete massive axial Jost crosswalk")
