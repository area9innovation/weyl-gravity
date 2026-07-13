#!/usr/bin/env python3
"""Exact scalar-quotient quadratic Weyl Hessians for P4 exchange.

This certificate computes the actual two-wave coefficient of

    sqrt(-g) (R_mn R^mn - R^2/3)

on ``R x S^3`` in the three scalar-type internal blocks isolated by
``verify_conformal_quartic_exchange.py``.  The component basis, field Gram,
diffeomorphism/Weyl generators, and two bordered gauges are inherited from
that staging rail.

Each gauge quotient is one-dimensional.  If ``p_+`` and ``p_-`` span the two
gauge slices and ``q_+``, ``q_-`` span the Ward covectors, the exact action
Hessian has the form

    K(omega) = kappa q_+ q_-^T,

and one curved-cylinder two-wave calculation fixes ``kappa``.

The output is a covariant stationary-mode *action* Hessian.  It is not by
itself a time-ordered Born denominator or a cylinder effective-Hamiltonian
matrix element.  The latter identification remains an explicit acceptance
rail for the complete exchange calculation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import sympy as sp

try:
    from symbolic.verify_conformal_quartic_contact import (
        _inverse_metric_by_subsets,
        _load_verified_kernel,
        _sqrtg_by_subsets,
    )
    from symbolic.verify_conformal_quartic_exchange import (
        BLOCKS,
        EXCHANGE_SPECS,
        DirectionData,
        evaluate_direction,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_quartic_contact import (
        _inverse_metric_by_subsets,
        _load_verified_kernel,
        _sqrtg_by_subsets,
    )
    from verify_conformal_quartic_exchange import (
        BLOCKS,
        EXCHANGE_SPECS,
        DirectionData,
        evaluate_direction,
    )


I = sp.I
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def spatial_christoffel(kernel: dict[str, object]) -> list[list[list[sp.Expr]]]:
    coordinates = (kernel["alpha"], kernel["beta"], kernel["gamma"])
    metric = kernel["background_metric_expression"][1:4, 1:4]
    inverse = sp.simplify(metric.inv())
    output = [[[sp.Integer(0) for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for upper in range(3):
        for first in range(3):
            for second in range(3):
                output[upper][first][second] = sp.simplify(
                    sum(
                        inverse[upper, lower]
                        * (
                            sp.diff(metric[lower, second], coordinates[first])
                            + sp.diff(metric[lower, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[lower])
                        )
                        / 2
                        for lower in range(3)
                    )
                )
    return output


@dataclass(frozen=True)
class ScalarHarmonicGeometry:
    harmonic: sp.Expr
    gradient: sp.Matrix
    trace_tensor: sp.Matrix
    traceless_hessian: sp.Matrix | None


def scalar_geometry(
    kernel: dict[str, object],
    ell: int,
    magnetic_left: sp.Rational | None = None,
    magnetic_right: sp.Rational | None = None,
) -> ScalarHarmonicGeometry:
    spin = R(ell, 2)
    left = spin if magnetic_left is None else magnetic_left
    right = spin if magnetic_right is None else magnetic_right
    harmonic = kernel["scalar_harmonic"](spin, left, right)
    spatial_coordinates = (kernel["alpha"], kernel["beta"], kernel["gamma"])
    gradient = sp.Matrix([sp.diff(harmonic, coordinate) for coordinate in spatial_coordinates])
    metric = kernel["background_metric_expression"][1:4, 1:4]
    connection = spatial_christoffel(kernel)
    hessian = sp.zeros(3)
    for first in range(3):
        for second in range(3):
            hessian[first, second] = sp.simplify(
                sp.diff(harmonic, spatial_coordinates[first], spatial_coordinates[second])
                - sum(
                    connection[upper][first][second] * gradient[upper]
                    for upper in range(3)
                )
            )
    lam = sp.Integer(ell * (ell + 2))
    traceless = sp.simplify(hessian + lam * metric * harmonic / 3)
    if ell == 1:
        origin = {kernel["alpha"]: 0, kernel["gamma"]: 0}
        check(
            "P4-Hessian: ell=1 scalar traceless Hessian vanishes identically",
            all(
                kernel["beta_to_tangent"](
                    sp.trigsimp(entry.subs(origin))
                )
                == 0
                for entry in traceless
            ),
        )
        traceless_output = None
    else:
        traceless_output = traceless
    return ScalarHarmonicGeometry(harmonic, gradient, metric * harmonic, traceless_output)


def scalar_metric_wave(
    kernel: dict[str, object],
    geometry: ScalarHarmonicGeometry,
    coefficients: sp.Matrix,
    omega: int,
    *,
    bra: bool,
) -> sp.Matrix:
    """Metric perturbation in the exact unnormalized scalar component basis."""

    expected_dimension = 3 if geometry.traceless_hessian is None else 4
    if coefficients.shape != (expected_dimension, 1):
        raise ValueError("scalar component coefficient shape mismatch")
    phase = sp.exp((I if bra else -I) * omega * kernel["time"])

    def orient(value: sp.Expr | sp.Matrix) -> sp.Expr | sp.Matrix:
        return sp.conjugate(value) if bra else value

    wave = sp.zeros(4)
    scalar = phase * orient(geometry.harmonic)
    wave[0, 0] = coefficients[0] * scalar
    gradient = phase * orient(geometry.gradient)
    for spatial in range(3):
        value = coefficients[1] * gradient[spatial]
        wave[0, spatial + 1] = value
        wave[spatial + 1, 0] = value
    trace_tensor = phase * orient(geometry.trace_tensor)
    for first in range(3):
        for second in range(3):
            wave[first + 1, second + 1] = coefficients[2] * trace_tensor[first, second]
    if geometry.traceless_hessian is not None:
        traceless = phase * orient(geometry.traceless_hessian)
        for first in range(3):
            for second in range(3):
                wave[first + 1, second + 1] += coefficients[3] * traceless[first, second]
    return wave


@dataclass(frozen=True)
class ActionCoefficient:
    density: sp.Expr
    measured_integrand: sp.Expr
    coefficient: sp.Expr
    inverse_verified: bool


def multilinear_reduced_weyl(
    kernel: dict[str, object], waves: list[sp.Matrix]
) -> ActionCoefficient:
    """Exact n-wave reduced-Weyl action coefficient for n=2 or n=3."""

    if len(waves) not in (2, 3):
        raise ValueError("quadratic/cubic engine accepts two or three waves")
    jets = [kernel["jet_matrix_from_expressions"](wave) for wave in waves]
    inverse = _inverse_metric_by_subsets(kernel, jets)
    g_lower = {
        frozenset(): kernel["matrix_to_components"](kernel["background_metric"])
    }
    for number, matrix in enumerate(jets):
        g_lower[frozenset({number})] = kernel["matrix_to_components"](matrix)
    g_upper = {
        key: kernel["matrix_to_components"](matrix) for key, matrix in inverse.items()
    }
    inverse_product = kernel["wt_contract"](g_lower, g_upper, ((1, 0),))
    inverse_verified = all(
        kernel["jet_equal"](
            kernel["wt_component"](inverse_product, key, (row, column)),
            kernel["Jet"].constant(1 if (not key and row == column) else 0),
        )
        for key in inverse
        for row in range(4)
        for column in range(4)
    )
    ricci = kernel["curvature"](g_lower, g_upper)
    scalar = kernel["wt_contract"](g_upper, ricci, ((0, 0), (1, 1)))
    one_up = kernel["wt_contract"](g_upper, ricci, ((1, 0),))
    two_up = kernel["wt_contract"](g_upper, one_up, ((1, 1),))
    ricci2 = kernel["wt_contract"](two_up, ricci, ((0, 0), (1, 1)))
    density_tensor = kernel["wt_mul"](
        _sqrtg_by_subsets(kernel, jets),
        kernel["wt_add"](
            ricci2,
            kernel["wt_scale"](
                kernel["wt_mul"](scalar, scalar), -R(1, 3)
            ),
        ),
    )
    key = frozenset(range(len(waves)))
    density = kernel["canonical_jet_coefficient"](
        kernel["wt_component"](density_tensor, key, ()).value()
    )
    tangent = kernel["radial_tangent"]
    measured = sp.cancel(2 * density / (1 + tangent**2))
    coefficient = sp.simplify(
        8 * sp.pi**2 * sp.integrate(measured, (tangent, 0, sp.oo))
    )
    return ActionCoefficient(density, measured, coefficient, inverse_verified)


def harmonic_checks(
    kernel: dict[str, object], geometry: ScalarHarmonicGeometry, ell: int
) -> None:
    beta = kernel["beta"]
    alpha = kernel["alpha"]
    gamma = kernel["gamma"]
    metric = kernel["background_metric_expression"][1:4, 1:4]
    inverse = sp.simplify(metric.inv())
    origin = {alpha: 0, gamma: 0}
    scalar_density = sp.trigsimp(
        sp.conjugate(geometry.harmonic) * geometry.harmonic
    ).subs(origin)
    scalar_norm = sp.simplify(
        sp.pi**2 * sp.integrate(sp.sin(beta) * scalar_density, (beta, 0, sp.pi))
    )
    gradient_density = sp.trigsimp(
        (sp.conjugate(geometry.gradient).T * inverse * geometry.gradient)[0]
    ).subs(origin)
    gradient_norm = sp.simplify(
        sp.pi**2 * sp.integrate(sp.sin(beta) * gradient_density, (beta, 0, sp.pi))
    )
    lam = ell * (ell + 2)
    check(
        f"P4-Hessian: ell={ell} scalar and gradient normalizations are exact",
        scalar_norm == 1 and gradient_norm == lam,
    )
    if geometry.traceless_hessian is not None:
        Q = geometry.traceless_hessian
        trace = sp.simplify(sum(inverse[i, j] * Q[i, j] for i in range(3) for j in range(3)))
        Q2 = sum(
            sp.conjugate(Q[i, j])
            * inverse[i, k]
            * inverse[j, l]
            * Q[k, l]
            for i in range(3)
            for j in range(3)
            for k in range(3)
            for l in range(3)
        ).subs(origin)
        # The direct trigonometric heuristic integrator is needlessly costly
        # for high ell.  Move to the same exact stereographic rational field
        # as the perturbiner: sin(beta) d beta = 4t dt/(1+t^2)^2.
        Q2_tangent = kernel["beta_to_tangent"](Q2)
        tangent = kernel["radial_tangent"]
        Qnorm = sp.simplify(
            sp.pi**2
            * sp.integrate(
                4 * tangent * Q2_tangent / (1 + tangent**2) ** 2,
                (tangent, 0, sp.oo),
            )
        )
        check(
            f"P4-Hessian: ell={ell} Q is traceless with the exact Gram norm",
            kernel["beta_to_tangent"](
                sp.trigsimp(trace.subs(origin))
            )
            == 0
            and Qnorm == R(2, 3) * lam * (lam - 3),
        )


@dataclass(frozen=True)
class HessianResult:
    label: str
    slice_minus: sp.Matrix
    slice_plus: sp.Matrix
    slice_coefficient: sp.Expr
    kappa: sp.Expr
    hessian: sp.Matrix
    density: sp.Expr
    bordered_verified: bool


EXPECTED_HESSIAN_DATA = {
    "s": {
        "density": lambda t: (54720 * t**5 - 2400 * t)
        / (sp.pi**2 * (1 + t**2) ** 5),
        "slice": sp.Integer(10752),
        "kappa": sp.Integer(131712),
    },
    "t": {
        "density": lambda t: (-12 * t**3 + 12 * t)
        / (sp.pi**2 * (1 + t**2) ** 2),
        "slice": sp.Integer(0),
        "kappa": sp.Integer(0),
    },
    "u": {
        "density": lambda t: (
            10944 * t**5 - 24480 * t**3 + 52512 * t
        )
        / (sp.pi**2 * (1 + t**2) ** 4),
        "slice": sp.Integer(96000),
        "kappa": sp.Integer(960),
    },
}


def calculate_block(
    kernel: dict[str, object], label: str
) -> HessianResult:
    block = BLOCKS[label]
    geometry = scalar_geometry(kernel, block.ell)
    harmonic_checks(kernel, geometry, block.ell)
    p_plus_space = block.C_plus.nullspace()
    p_minus_space = block.C_minus.nullspace()
    if len(p_plus_space) != 1 or len(p_minus_space) != 1:
        raise ValueError("gauge slice quotient is not one-dimensional")
    p_plus = p_plus_space[0]
    p_minus = p_minus_space[0]
    plus_wave = scalar_metric_wave(
        kernel, geometry, p_plus, block.omega, bra=False
    )
    minus_wave = scalar_metric_wave(
        kernel, geometry, p_minus, block.omega, bra=True
    )
    print(f"[RUN] {label}: exact two-wave curved-cylinder Hessian", flush=True)
    action = multilinear_reduced_weyl(kernel, [minus_wave, plus_wave])
    check(
        f"P4-Hessian: {label} inverse metric is exact on all four subsets",
        action.inverse_verified,
    )
    q_minus = block.current_minus_basis
    q_plus = block.current_plus_basis
    denominator = sp.simplify(
        (p_minus.T * q_plus)[0] * (q_minus.T * p_plus)[0]
    )
    if denominator == 0:
        raise ValueError("slice vectors do not pair with Ward covectors")
    kappa = sp.simplify(action.coefficient / denominator)
    hessian = sp.simplify(kappa * q_plus * q_minus.T)
    print(f"[DATA] {label}: slice coefficient = {action.coefficient}", flush=True)
    print(f"[DATA] {label}: covariant kappa = {kappa}", flush=True)
    expected = EXPECTED_HESSIAN_DATA[label]
    tangent = kernel["radial_tangent"]
    check(
        f"P4-Hessian: {label} density, slice coefficient, and kappa are regression-fixed",
        sp.cancel(action.density - expected["density"](tangent)) == 0
        and action.coefficient == expected["slice"]
        and kappa == expected["kappa"],
    )

    # Unit Ward currents make the bordered exchange equal 1/kappa.  The
    # evaluator independently solves conformal-de-Donder and Gram-orthogonal
    # bordered systems and rejects disagreement.
    if kappa == 0:
        bordered_verified = False
        check(
            f"P4-Hessian: {label} scalar quotient is exactly Hessian-null",
            action.coefficient == 0 and hessian == sp.zeros(block.dimension),
        )
        print(
            f"[BLOCKED] {label}: both bordered Hessians are singular; "
            "a constraint/BRST reduction is required before any exchange inverse",
            flush=True,
        )
    else:
        unit_direction = DirectionData(q_minus, q_plus)
        bordered = evaluate_direction(block, hessian, unit_direction)
        check(
            f"P4-Hessian: {label} both bordered gauges reproduce 1/kappa",
            sp.simplify(bordered.subtraction - 1 / kappa) == 0
            and bordered.bordered_subtraction == bordered.subtraction
            and bordered.alternate_bordered_subtraction == bordered.subtraction,
        )
        bordered_verified = True
    check(
        f"P4-Hessian: {label} reconstructed K has exact diffeo/Weyl kernels",
        hessian * block.B_plus == sp.zeros(block.dimension, block.B_plus.cols)
        and block.B_minus.T * hessian
        == sp.zeros(block.B_minus.cols, block.dimension),
    )
    return HessianResult(
        label,
        p_minus,
        p_plus,
        action.coefficient,
        kappa,
        hessian,
        action.density,
        bordered_verified,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "labels",
        nargs="*",
        choices=tuple(BLOCKS),
        default=list(BLOCKS),
        help="exchange blocks to evaluate (default: s t u)",
    )
    parser.add_argument(
        "--require-born-map",
        action="store_true",
        help="fail closed: the stationary action-to-Born map is not certified here",
    )
    args = parser.parse_args()
    kernel = _load_verified_kernel()
    results = [calculate_block(kernel, label) for label in args.labels]
    for result in results:
        print(f"{result.label} gauge-slice p(-):", result.slice_minus.T)
        print(f"{result.label} gauge-slice p(+):", result.slice_plus.T)
        print(f"{result.label} slice action coefficient:", result.slice_coefficient)
        print(f"{result.label} exact covariant kappa:", result.kappa)
        print(f"{result.label} reconstructed covariant Hessian:", result.hessian)
        print(f"{result.label} local radial density:", result.density)
    print(
        "P4 HESSIAN STATUS: EXACT COVARIANT ACTION DATA. Stationary Born/time-ordering "
        "normalization is not inferred from these coefficients."
    )
    if args.require_born_map:
        raise SystemExit(
            "stationary covariant-action to effective-Hamiltonian/Born mapping remains required"
        )


if __name__ == "__main__":
    main()
