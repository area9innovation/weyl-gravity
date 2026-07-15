"""Exact second-order Weyl--Maxwell extension tests on the product fixture.

This module works in the spherically symmetric chart

    g = exp(2 psi(t)) (-dt^2+dx^2) + r(t)^2 dOmega_2^2,
    F = sin(theta) dtheta wedge dphi,

and truncates every tensor operation over Q[epsilon]/(epsilon^3).  It is kept
independent of floating point arithmetic so a removable quadratic source is
distinguished from an actual second-order obstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
LINEAR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
BACKGROUND_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_second_order_inclusion.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_second_order_inclusion.schema.json"


class SecondOrderInclusionError(RuntimeError):
    """Raised when an exact second-order inclusion check fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SecondOrderInclusionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.trigsimp(sp.expand_trig(sp.simplify(expression))))


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(_canonical(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _second_coefficient(
    matrix: sp.MatrixBase, epsilon: sp.Symbol
) -> sp.Matrix:
    return matrix.applyfunc(
        lambda value: _canonical(
            sp.diff(value, epsilon, 2).subs(epsilon, 0) / 2
        )
    )

def _trunc(expression: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    expression = sp.sympify(expression)
    return sp.simplify(
        expression.subs(epsilon, 0)
        + epsilon * sp.diff(expression, epsilon).subs(epsilon, 0)
        + epsilon**2 * sp.diff(expression, epsilon, 2).subs(epsilon, 0) / 2
    )


def _spherical_weyl_maxwell(
    psi: sp.Expr,
    radius: sp.Expr,
    epsilon: sp.Symbol,
    magnetic_amplitude: sp.Expr = sp.S.One,
    electric_amplitude: sp.Expr = sp.S.Zero,
) -> dict[str, object]:
    """Return exact tensors through epsilon squared for the magnetic ansatz."""

    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    n = 4
    tr = lambda expression: _trunc(expression, epsilon)
    base_factor = tr(sp.exp(2 * psi))
    sphere_factor = tr(radius**2)
    sine = sp.sin(theta)
    metric = sp.diag(
        -base_factor,
        base_factor,
        sphere_factor,
        sphere_factor * sine**2,
    )
    inverse = sp.diag(
        -tr(1 / base_factor),
        tr(1 / base_factor),
        tr(1 / sphere_factor),
        tr(1 / (sphere_factor * sine**2)),
    )

    connection = [
        [[sp.S.Zero for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for target in range(n):
        for first in range(n):
            for second in range(n):
                connection[target][first][second] = tr(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, second], coordinates[first])
                            + sp.diff(metric[index, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[index])
                        )
                        for index in range(n)
                    )
                    / 2
                )

    riemann = [
        [
            [[sp.S.Zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for target in range(n):
        for vector in range(n):
            for first in range(n):
                for second in range(n):
                    riemann[target][vector][first][second] = tr(
                        sp.diff(
                            connection[target][second][vector], coordinates[first]
                        )
                        - sp.diff(
                            connection[target][first][vector], coordinates[second]
                        )
                        + sum(
                            connection[target][first][middle]
                            * connection[middle][second][vector]
                            - connection[target][second][middle]
                            * connection[middle][first][vector]
                            for middle in range(n)
                        )
                    )

    ricci = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            ricci[first, second] = tr(
                sum(riemann[index][first][index][second] for index in range(n))
            )
    scalar = tr(
        sum(
            inverse[first, second] * ricci[first, second]
            for first in range(n)
            for second in range(n)
        )
    )
    schouten = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            schouten[first, second] = tr(
                (ricci[first, second] - scalar * metric[first, second] / 6) / 2
            )

    weyl = [
        [
            [[sp.S.Zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for first in range(n):
        for second in range(n):
            for third in range(n):
                for fourth in range(n):
                    lowered_riemann = tr(
                        sum(
                            metric[first, target]
                            * riemann[target][second][third][fourth]
                            for target in range(n)
                        )
                    )
                    weyl[first][second][third][fourth] = tr(
                        lowered_riemann
                        - (
                            metric[first, third] * schouten[fourth, second]
                            - metric[first, fourth] * schouten[third, second]
                            - metric[second, third] * schouten[fourth, first]
                            + metric[second, fourth] * schouten[third, first]
                        )
                    )

    derivative_schouten = [
        [[sp.S.Zero for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for derivative in range(n):
        for first in range(n):
            for second in range(n):
                derivative_schouten[derivative][first][second] = tr(
                    sp.diff(schouten[first, second], coordinates[derivative])
                    - sum(
                        connection[index][derivative][first]
                        * schouten[index, second]
                        + connection[index][derivative][second]
                        * schouten[first, index]
                        for index in range(n)
                    )
                )

    second_schouten = [
        [
            [[sp.S.Zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for outer in range(n):
        for inner in range(n):
            for first in range(n):
                for second in range(n):
                    second_schouten[outer][inner][first][second] = tr(
                        sp.diff(
                            derivative_schouten[inner][first][second],
                            coordinates[outer],
                        )
                        - sum(
                            connection[index][outer][inner]
                            * derivative_schouten[index][first][second]
                            + connection[index][outer][first]
                            * derivative_schouten[inner][index][second]
                            + connection[index][outer][second]
                            * derivative_schouten[inner][first][index]
                            for index in range(n)
                        )
                    )

    schouten_up = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            schouten_up[first, second] = tr(
                sum(
                    inverse[first, left]
                    * inverse[second, right]
                    * schouten[left, right]
                    for left in range(n)
                    for right in range(n)
                )
            )
    bach = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            laplacian = sum(
                inverse[outer, inner]
                * second_schouten[outer][inner][first][second]
                for outer in range(n)
                for inner in range(n)
            )
            mixed = sum(
                inverse[outer, inner]
                * second_schouten[outer][first][second][inner]
                for outer in range(n)
                for inner in range(n)
            )
            curvature = sum(
                schouten_up[inner, outer] * weyl[first][inner][second][outer]
                for inner in range(n)
                for outer in range(n)
            )
            bach[first, second] = tr(laplacian - mixed + curvature)

    field_strength = sp.zeros(n)
    field_strength[0, 1] = tr(electric_amplitude)
    field_strength[1, 0] = -tr(electric_amplitude)
    field_strength[2, 3] = tr(magnetic_amplitude) * sine
    field_strength[3, 2] = -tr(magnetic_amplitude) * sine
    field_squared = tr(
        sum(
            inverse[first, third]
            * inverse[second, fourth]
            * field_strength[first, second]
            * field_strength[third, fourth]
            for first in range(n)
            for second in range(n)
            for third in range(n)
            for fourth in range(n)
        )
    )
    stress = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            stress[first, second] = tr(
                sum(
                    field_strength[first, left]
                    * inverse[left, right]
                    * field_strength[second, right]
                    for left in range(n)
                    for right in range(n)
                )
                - metric[first, second] * field_squared / 4
            )

    derivative_field = [
        [[sp.S.Zero for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for derivative in range(n):
        for first in range(n):
            for second in range(n):
                derivative_field[derivative][first][second] = tr(
                    sp.diff(field_strength[first, second], coordinates[derivative])
                    - sum(
                        connection[index][derivative][first]
                        * field_strength[index, second]
                        + connection[index][derivative][second]
                        * field_strength[first, index]
                        for index in range(n)
                    )
                )

    return {
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "bach": bach,
        "stress": stress,
        "weyl_maxwell_residual": (3 * bach - stress).applyfunc(tr),
        "derivative_field": derivative_field,
    }


def _chevreton_trace_second_order(
    tensors: dict[str, object], epsilon: sp.Symbol
) -> sp.Matrix:
    """Coefficient H_ab^(2) in the primary-literature tensor convention."""

    inverse = tensors["inverse"]
    metric = tensors["metric"]
    derivative_field = tensors["derivative_field"]
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(derivative_field, list)
    inverse_zero = inverse.subs(epsilon, 0)
    metric_zero = metric.subs(epsilon, 0)
    jet = [
        [
            [
                sp.simplify(
                    sp.diff(derivative_field[derivative][first][second], epsilon)
                    .subs(epsilon, 0)
                )
                for second in range(4)
            ]
            for first in range(4)
        ]
        for derivative in range(4)
    ]
    scalar = sp.simplify(
        sum(
            inverse_zero[derivative, other_derivative]
            * inverse_zero[first, other_first]
            * inverse_zero[second, other_second]
            * jet[derivative][first][second]
            * jet[other_derivative][other_first][other_second]
            for derivative in range(4)
            for other_derivative in range(4)
            for first in range(4)
            for other_first in range(4)
            for second in range(4)
            for other_second in range(4)
        )
    )
    result = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            leading = sum(
                inverse_zero[derivative, other_derivative]
                * inverse_zero[index, other_index]
                * jet[derivative][first][index]
                * jet[other_derivative][second][other_index]
                for derivative in range(4)
                for other_derivative in range(4)
                for index in range(4)
                for other_index in range(4)
            )
            result[first, second] = sp.simplify(
                leading - metric_zero[first, second] * scalar / 4
            )
    return result


def _constant_radion_fixture() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    time, theta = sp.symbols("t theta", real=True)
    correction_switch, flux_shift = sp.symbols("z p", real=True)
    base_factor = (
        1
        + 2 * epsilon * time**2
        + epsilon**2 * correction_switch * sp.Rational(8, 3) * time**4
    )
    sphere_factor = 1 + 2 * epsilon
    tensors = _spherical_weyl_maxwell(
        sp.log(base_factor) / 2,
        sp.sqrt(sphere_factor),
        epsilon,
        1 + epsilon**2 * flux_shift,
    )
    residual = tensors["weyl_maxwell_residual"]
    assert isinstance(residual, sp.MatrixBase)
    coefficient = _second_coefficient(residual, epsilon)
    source = coefficient.subs({correction_switch: 0, flux_shift: 0}).applyfunc(
        _canonical
    )
    corrected = coefficient.subs(
        {correction_switch: 1, flux_shift: -2}
    ).applyfunc(_canonical)
    fixed_flux_candidate = coefficient.subs(
        {correction_switch: 1, flux_shift: 0}
    ).applyfunc(_canonical)
    chevreton_h = _chevreton_trace_second_order(tensors, epsilon)
    _require(source[0, 0] == -2, "constant-radion quadratic tt source changed")
    _require(corrected == sp.zeros(4), "flux-shifted radion correction failed")
    _require(fixed_flux_candidate[0, 0] == -2, "fixed-flux radion witness vanished")
    _require(chevreton_h == sp.zeros(4), "constant-radion Chevreton coefficient changed")
    return {
        "first_order_tangent": {
            "metric": "h1=2*t^2*(-dt^2+dx^2)+2*dOmega_2^2",
            "maxwell": "f1=0",
            "magnetic_flux_condition": "delta P=0",
        },
        "chevreton_H_second_order": _matrix_strings(chevreton_h),
        "convention_adjusted_C_Ch_second_order": _matrix_strings(2 * chevreton_h),
        "affine_quadratic_weyl_maxwell_source": _matrix_strings(source),
        "compact_fixed_flux_adjoint_witness": {
            "averaged_linear_tt_row": "<L_WM Phi2>_tt=(1/2L)*integral_S1 partial_x^2(box D) dx=0",
            "source_pairing": "integral_S1 S2_tt dx=-2*L",
            "dual_test": "constant spatial lapse / homogeneous tt row",
            "nonzero_for_L_positive": True,
            "conclusion": "NO_PERIODIC_SECOND_ORDER_CORRECTION_AT_FIXED_MAGNETIC_FLUX",
        },
        "charge_relaxed_extension": {
            "metric_correction": "h2=(8/3)*t^4*(-dt^2+dx^2)",
            "maxwell_correction": "f2=-2*sin(theta)*dtheta wedge dphi",
            "magnetic_flux_shift": "P(epsilon)=1-2*epsilon^2",
            "corrected_residual": _matrix_strings(corrected),
            "fixed_flux_metric_only_residual": _matrix_strings(fixed_flux_candidate),
            "status": "EXPLICIT_SECOND_ORDER_EXTENSION_IF_FLUX_MAY_SHIFT",
        },
    }


def _maxwell_duality_fixture() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    flux_shift = sp.symbols("p", real=True)
    tensors = _spherical_weyl_maxwell(
        sp.S.Zero,
        sp.S.One,
        epsilon,
        1 + epsilon**2 * flux_shift,
        epsilon,
    )
    residual = tensors["weyl_maxwell_residual"]
    assert isinstance(residual, sp.MatrixBase)
    coefficient = _second_coefficient(residual, epsilon)
    source = coefficient.subs(flux_shift, 0).applyfunc(_canonical)
    corrected = coefficient.subs(flux_shift, -sp.Rational(1, 2)).applyfunc(
        _canonical
    )
    chevreton_h = _chevreton_trace_second_order(tensors, epsilon)
    angle = sp.symbols("angle", real=True)
    _require(source[0, 0] == -sp.Rational(1, 2), "duality tt source changed")
    _require(corrected == sp.zeros(4), "duality correction failed")
    _require(chevreton_h == sp.zeros(4), "duality Chevreton coefficient changed")
    _require(sp.trigsimp(sp.cos(angle) ** 2 + sp.sin(angle) ** 2) == 1, "duality norm changed")
    return {
        "first_order_tangent": {
            "metric": "h1=0",
            "maxwell": "f1=dt wedge dx=*Fbar",
            "interpretation": "global Maxwell duality tangent; Maxwell-sector but not a radiative wave packet",
        },
        "chevreton_H_second_order": _matrix_strings(chevreton_h),
        "convention_adjusted_C_Ch_second_order": _matrix_strings(2 * chevreton_h),
        "affine_fixed_magnetic_flux_source": _matrix_strings(source),
        "compact_fixed_flux_adjoint_witness": {
            "source_pairing": "integral_S1 S2_tt dx=-L/2",
            "dual_test": "constant spatial lapse / homogeneous tt row",
            "conclusion": "NO_PERIODIC_SECOND_ORDER_CORRECTION_AT_FIXED_MAGNETIC_FLUX",
        },
        "charge_relaxed_extension": {
            "all_order_family": "F(epsilon)=cos(epsilon)*Fbar+sin(epsilon)*(*Fbar)",
            "second_order_correction": "f2=-(1/2)*Fbar",
            "stress_identity": "cos(epsilon)^2+sin(epsilon)^2=1",
            "corrected_residual": _matrix_strings(corrected),
            "status": "EXACT_ALL_ORDER_DUALITY_EXTENSION_IF_MAGNETIC_FLUX_MAY_SHIFT",
        },
    }


def _null_radiative_fixture() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    time, space = sp.symbols("t x", real=True)
    correction_switch = sp.symbols("z", real=True)
    u = time - space
    v = time + space
    radion = u
    base_conformal = u**2 * v / 4
    correction = u**3 * v * (5 * u * v - 24) / 24
    base_factor = 1 + 2 * epsilon * base_conformal + epsilon**2 * correction_switch * correction
    sphere_factor = 1 + 2 * epsilon * radion
    tensors = _spherical_weyl_maxwell(
        sp.log(base_factor) / 2,
        sp.sqrt(sphere_factor),
        epsilon,
    )
    residual = tensors["weyl_maxwell_residual"]
    assert isinstance(residual, sp.MatrixBase)
    coefficient = _second_coefficient(residual, epsilon)
    source = coefficient.subs(correction_switch, 0).applyfunc(_canonical)
    corrected = coefficient.subs(correction_switch, 1).applyfunc(_canonical)
    chevreton_h = _chevreton_trace_second_order(tensors, epsilon).applyfunc(
        _canonical
    )
    chevreton_c = (2 * chevreton_h).applyfunc(_canonical)
    box_operator = lambda expression: -sp.diff(expression, time, 2) + sp.diff(
        expression, space, 2
    )
    q_value = _canonical(box_operator(correction))
    _require(box_operator(radion) == 0, "null-radion wave equation changed")
    _require(sp.hessian(radion, (time, space)) == sp.zeros(2), "null-radion Hessian changed")
    _require(
        _canonical(box_operator(base_conformal) + 2 * radion) == 0,
        "null-radion Einstein--Maxwell trace equation changed",
    )
    _require(chevreton_c != sp.zeros(4), "radiative Chevreton source vanished")
    _require(corrected == sp.zeros(4), "radiative second-order correction failed")
    return {
        "domain": "universal cover R^(1,1) x S2; polynomial null representative, not periodic on the S1 quotient",
        "first_order_tangent": {
            "u": "t-x",
            "v": "t+x",
            "radion": "phi1=u",
            "base_conformal_mode": "psi1=u^2*v/4",
            "maxwell": "f1=0 with metric-induced nonparallel first Maxwell jet",
            "linearized_einstein_maxwell_checks": [
                "box(phi1)=0",
                "Hessian(phi1)=0",
                "box(psi1)+2*phi1=0",
            ],
        },
        "chevreton_H_second_order": _matrix_strings(chevreton_h),
        "convention_adjusted_C_Ch_second_order": _matrix_strings(chevreton_c),
        "chevreton_type": "pure null: C_Ch^(2)=4*(dt-dx) tensor (dt-dx)",
        "affine_quadratic_weyl_maxwell_source": _matrix_strings(source),
        "explicit_extension": {
            "metric_correction": "h2=D(t,x)*(-dt^2+dx^2)",
            "D": "u^3*v*(5*u*v-24)/24",
            "box_D": str(q_value),
            "maxwell_correction": "f2=0",
            "corrected_residual": _matrix_strings(corrected),
            "status": "EXPLICIT_SECOND_ORDER_EXTENSION_WITH_NONZERO_CHEVRETON_DEFECT",
        },
    }


def build_certificate() -> dict[str, Any]:
    linear = _load(LINEAR_CERTIFICATE)
    background = _load(BACKGROUND_CERTIFICATE)
    _require(
        linear.get("result_id") == "EINSTEIN_MAXWELL_CHEVRETON_TANGENT"
        and linear.get("classification", {}).get(
            "full_lower_order_on_shell_linear_tangent_inclusion"
        )
        is True,
        "linear Chevreton tangent gate changed",
    )
    _require(
        background.get("result_id") == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE"
        and background.get("claim_flags", {}).get(
            "exact_nonlinear_background_incidence_certified"
        )
        is True,
        "product-background gate changed",
    )
    constant_radion = _constant_radion_fixture()
    maxwell_duality = _maxwell_duality_fixture()
    null_radiative = _null_radiative_fixture()
    return {
        "schema": "einstein-maxwell-second-order-inclusion-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST",
        "result_state": "TANGENT_AND_CHARGE_SECTOR_DEPENDENT_SECOND_ORDER_EXTENSION_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                "linear_tangent_theorem": {
                    "path": str(LINEAR_CERTIFICATE.relative_to(ROOT)),
                    "sha256": _sha256(LINEAR_CERTIFICATE),
                },
                "common_background": {
                    "path": str(BACKGROUND_CERTIFICATE.relative_to(ROOT)),
                    "sha256": _sha256(BACKGROUND_CERTIFICATE),
                },
            },
            "primary_identity": {
                "authors": "G. Bergqvist and I. Eriksson",
                "arxiv": "gr-qc/0703073v2",
                "source_equation": "Eq. (66): B_ab=2 H_ab+(2/3) lambda T_ab",
            },
            "chevreton_tensor_formula": {
                "source": "G. Bergqvist, I. Eriksson, and J. M. M. Senovilla, gr-qc/0303036",
                "formula": "H_ab=nabla_c F_ad nabla^c F_b^d-(1/4)g_ab nabla_c F_de nabla^c F^de",
                "repository_fixture_translation": "C_Ch^(2)=2*H^(2) at kappa=1",
            },
        },
        "perturbative_convention": {
            "fields": "Phi(epsilon)=Phibar+epsilon*Phi1+epsilon^2*Phi2+O(epsilon^3)",
            "affine_source": "S2=(1/2)D^2 E[Phi1,Phi1]",
            "extension_equation": "L Phi2=-S2",
            "relation_to_requested_sign": "the requested right-hand source -1/2 D^2E equals -S2",
        },
        "adjoint_cokernel_reduction": {
            "averaging": "The source is invariant under the compact spatial group S1 x SO(3). If any periodic correction exists, averaging it gives an invariant correction because the linearized Weyl--Maxwell operator is equivariant.",
            "gauge_complete_invariant_metric": "After invariant Diff x Weyl gauge fixing, the averaged metric correction is represented by base and sphere factors A(t,x),R(t,x), with D=A-R.",
            "linearized_tt_row": "(L_WM Phi2)_tt=(1/2)*partial_x^2*box(D)-p",
            "maxwell_zero_mode": "p is the epsilon^2 magnetic-flux coefficient; an averaged electric correction has zero linear stress pairing with the purely magnetic background",
            "fixed_flux_condition": "p=0",
            "adjoint_pairing": "Pair with the constant spatial lapse and integrate over S1: derivatives vanish, so <1,L_tt>=0.",
            "scope": "This promotes the invariant calculation to a no-solution result for arbitrary smooth periodic corrections in the declared fixed-magnetic-flux sector.",
        },
        "certified_constant_radion": constant_radion,
        "maxwell_duality_tangent": maxwell_duality,
        "null_radiative_tangent": null_radiative,
        "classification": {
            "constant_radion_compact_fixed_flux_extension_exists": False,
            "constant_radion_compact_fixed_flux_adjoint_obstruction_certified": True,
            "constant_radion_charge_relaxed_extension_constructed": True,
            "maxwell_duality_compact_fixed_flux_extension_exists": False,
            "maxwell_duality_compact_fixed_flux_adjoint_obstruction_certified": True,
            "maxwell_duality_charge_relaxed_exact_extension_constructed": True,
            "nonzero_chevreton_radiative_fixture_extension_constructed": True,
            "nonzero_chevreton_defect_is_by_itself_an_obstruction": False,
            "general_nonlinear_einstein_sector_closure_certified": False,
            "general_second_order_no_go_certified": False,
        },
        "interpretation": {
            "main": "Second-order inclusion is tangent- and charge-sector dependent. The compact fixed-flux constant radion and Maxwell duality directions fail by an averaged constraint, while allowing the required magnetic-charge shift removes both failures. A nonzero pure-null Chevreton defect on the universal cover is explicitly removable by a local Weyl metric correction.",
            "where_the_graviton_went": "No linear graviton or photon class is removed here. The obstruction is a second-order compact fixed-charge integrability condition on two declared zero/charge modes, not a vanishing local radiative spectrum.",
        },
        "next_gate": {
            "status": "OPEN",
            "target": "test periodic nonzero-frequency graviton and photon harmonics at fixed electric and magnetic charges, using their exact adjoint pairings",
            "do_not_infer": [
                "general nonlinear closure from the removable null fixture",
                "a universal nonlinear no-go from the two fixed-flux charge-sector obstructions",
                "asymptotically flat scattering or Lorentzian-causal closure",
            ],
        },
        "claim_flags": {
            "local_algebraic_second_order_classification": True,
            "reduced_mode_fixed_flux_obstruction": True,
            "general_nonlinear_closure_claim": False,
            "general_second_order_no_go_claim": False,
            "lorentzian_causal_claim": False,
            "observable_embedding_claim": False,
            "scattering_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC and REDUCED-MODE certificate classifies three explicit second-order directions at the certified product background. On the compact S1 quotient it proves fixed-magnetic-flux adjoint obstructions for the constant radion and Maxwell duality tangent, and it exhibits their charge-relaxed extensions. On the universal cover it constructs an explicit correction for a null radiative tangent with nonzero Chevreton defect. It proves neither general nonlinear closure nor a general second-order no-go, and makes no causal, observable, scattering, or quantum claim.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_second_order_inclusion --verify bridge/certificates/einstein_maxwell_second_order_inclusion.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_second_order_inclusion.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_second_order_inclusion",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(
        _load(path) == build_certificate(),
        f"second-order inclusion certificate is stale or altered: {path}",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
