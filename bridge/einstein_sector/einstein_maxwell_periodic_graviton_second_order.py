"""Exact second-order obstruction for a periodic l=2 gravitational mode.

The magnetic product flux mixes the odd-parity metric harmonic with a polar
Maxwell harmonic.  The plus normal-mode branch is computed exactly over
Q(sqrt(3))[epsilon]/(epsilon^3).  A single constant-lapse pairing of its
quadratic Weyl--Maxwell source proves the fixed-charge obstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _stress,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
BACKGROUND_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
LINEAR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
PHOTON_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_photon_second_order.json"
TENSOR_HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_periodic_photon_second_order.py"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_periodic_graviton_second_order.schema.json"


class PeriodicGravitonError(RuntimeError):
    """Raised when the periodic gravitational-mode certificate fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PeriodicGravitonError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(sp.sqrtdenest(sp.trigsimp(matrix[row, column])))) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _mode_geometry(order: int) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    root = sp.sqrt(3)
    omega = sp.sqrt(6 + 2 * root)
    metric_amplitude = sp.cos(omega * time)
    maxwell_amplitude = root * metric_amplitude
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    tr = lambda expression: _trunc(expression, epsilon, order)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[1, 3] = metric[3, 1] = epsilon * metric_amplitude * axial_one_form
    inverse = metric.inv().applyfunc(tr)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = tr(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, second], coordinates[first])
                            + sp.diff(metric[index, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )

    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(maxwell_amplitude, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * maxwell_amplitude * sp.diff(harmonic, theta)
    field[2, 1] = -field[1, 2]
    return {
        "epsilon": epsilon,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _linear_checks() -> dict[str, Any]:
    data = _curvature(_mode_geometry(order=1), order=1)
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    field = data["field"]
    ricci = data["ricci"]
    scalar = data["scalar"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(field, sp.MatrixBase)
    assert isinstance(ricci, sp.MatrixBase)
    assert isinstance(scalar, sp.Expr)

    einstein = (ricci - metric * scalar / 2 + metric / 2 - _stress(data, 1)).applyfunc(
        lambda value: sp.factor(
            sp.sqrtdenest(
                sp.trigsimp(sp.diff(value, epsilon).subs(epsilon, 0))
            )
        )
    )
    sine = sp.sin(coordinates[2])
    field_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            field_up[first, second] = _trunc(
                sum(
                    inverse[first, left] * inverse[second, right] * field[left, right]
                    for left in range(4)
                    for right in range(4)
                ),
                epsilon,
                1,
            )
    maxwell = sp.Matrix(
        [
            sp.factor(
                sp.sqrtdenest(
                    sp.trigsimp(
                    sp.diff(
                        sum(
                            sp.diff(sine * field_up[first, second], coordinates[first])
                            for first in range(4)
                        )
                        / sine,
                        epsilon,
                    ).subs(epsilon, 0)
                    )
                )
            )
            for second in range(4)
        ]
    )
    _require(einstein == sp.zeros(4), "l=2 mode failed the linear Einstein equation")
    _require(maxwell == sp.zeros(4, 1), "l=2 mode failed the linear Maxwell equation")

    root = sp.sqrt(3)
    coupling = sp.Matrix([[6, 2], [6, 6]])
    plus_vector = sp.Matrix([1, root])
    minus_vector = sp.Matrix([1, -root])
    _require(
        (coupling * plus_vector - (6 + 2 * root) * plus_vector).applyfunc(sp.simplify)
        == sp.zeros(2, 1),
        "plus frequency changed",
    )
    _require(
        (coupling * minus_vector - (6 - 2 * root) * minus_vector).applyfunc(sp.simplify)
        == sp.zeros(2, 1),
        "minus frequency changed",
    )
    return {
        "reduced_equations": ["H''+6*H+2*q=0", "q''+6*q+6*H=0"],
        "frequency_squared_matrix": [[6, 2], [6, 6]],
        "normal_branches": {
            "plus": {"q_over_H": "sqrt(3)", "omega_squared": "6+2*sqrt(3)"},
            "minus": {"q_over_H": "-sqrt(3)", "omega_squared": "6-2*sqrt(3)"},
        },
        "certified_branch": "plus",
        "linearized_einstein_residual": _matrix_strings(einstein),
        "linearized_maxwell_residual": [str(value) for value in maxwell],
    }


def _chevreton_time_zero() -> sp.Matrix:
    data = _mode_geometry(order=1)
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    field = data["field"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(field, sp.MatrixBase)
    derivative_field = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for derivative in range(4):
        for first in range(4):
            for second in range(4):
                derivative_field[derivative][first][second] = _trunc(
                    sp.diff(field[first, second], coordinates[derivative])
                    - sum(
                        connection[index][derivative][first] * field[index, second]
                        + connection[index][derivative][second] * field[first, index]
                        for index in range(4)
                    ),
                    epsilon,
                    1,
                )
    jet = [
        [
            [sp.diff(derivative_field[d][a][b], epsilon).subs(epsilon, 0) for b in range(4)]
            for a in range(4)
        ]
        for d in range(4)
    ]
    inverse_zero = inverse.subs(epsilon, 0)
    metric_zero = metric.subs(epsilon, 0)
    scalar = sp.simplify(
        sum(
            inverse_zero[d, dd] * inverse_zero[a, aa] * inverse_zero[b, bb]
            * jet[d][a][b] * jet[dd][aa][bb]
            for d in range(4) for dd in range(4)
            for a in range(4) for aa in range(4)
            for b in range(4) for bb in range(4)
        )
    )
    result = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            leading = sum(
                inverse_zero[d, dd] * inverse_zero[index, other]
                * jet[d][first][index] * jet[dd][second][other]
                for d in range(4) for dd in range(4)
                for index in range(4) for other in range(4)
            )
            result[first, second] = sp.factor(
                sp.sqrtdenest(
                    sp.trigsimp(2 * (leading - metric_zero[first, second] * scalar / 4)).subs(coordinates[0], 0)
                )
            )
    expected_tt = -sp.Rational(9, 2) * (
        (33 + 18 * sp.sqrt(3)) * sp.sin(coordinates[2]) ** 4
        - (48 + 24 * sp.sqrt(3)) * sp.sin(coordinates[2]) ** 2
        + 16 + 8 * sp.sqrt(3)
    )
    _require(sp.trigsimp(result[0, 0] - expected_tt) == 0, "Chevreton tt slice changed")
    return result


def _quadratic_source_tt_time_zero() -> sp.Expr:
    data = _curvature(_mode_geometry(order=2), order=2)
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    riemann = data["riemann"]
    schouten = data["schouten"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(riemann, list)
    assert isinstance(schouten, sp.MatrixBase)
    tr = lambda expression: _trunc(expression, epsilon, 2)

    derivative_schouten = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for derivative in range(4):
        for first in range(4):
            for second in range(4):
                derivative_schouten[derivative][first][second] = tr(
                    sp.diff(schouten[first, second], coordinates[derivative])
                    - sum(
                        connection[index][derivative][first] * schouten[index, second]
                        + connection[index][derivative][second] * schouten[first, index]
                        for index in range(4)
                    )
                )

    def second_schouten(outer: int, inner: int, first: int, second: int) -> sp.Expr:
        return tr(
            sp.diff(derivative_schouten[inner][first][second], coordinates[outer])
            - sum(
                connection[index][outer][inner] * derivative_schouten[index][first][second]
                + connection[index][outer][first] * derivative_schouten[inner][index][second]
                + connection[index][outer][second] * derivative_schouten[inner][first][index]
                for index in range(4)
            )
        )

    schouten_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            schouten_up[first, second] = tr(
                sum(
                    inverse[first, left] * inverse[second, right] * schouten[left, right]
                    for left in range(4) for right in range(4)
                )
            )

    def weyl(first: int, second: int, third: int, fourth: int) -> sp.Expr:
        lowered = tr(sum(metric[first, target] * riemann[target][second][third][fourth] for target in range(4)))
        return tr(
            lowered - (
                metric[first, third] * schouten[fourth, second]
                - metric[first, fourth] * schouten[third, second]
                - metric[second, third] * schouten[fourth, first]
                + metric[second, fourth] * schouten[third, first]
            )
        )

    laplacian = sum(
        inverse[outer, inner] * second_schouten(outer, inner, 0, 0)
        for outer in range(4) for inner in range(4)
    )
    mixed = sum(
        inverse[outer, inner] * second_schouten(outer, 0, 0, inner)
        for outer in range(4) for inner in range(4)
    )
    curvature = sum(
        schouten_up[inner, outer] * weyl(0, inner, 0, outer)
        for inner in range(4) for outer in range(4)
    )
    residual_tt = tr(3 * tr(laplacian - mixed + curvature) - _stress(data, 2)[0, 0])
    coefficient = sp.diff(residual_tt, epsilon, 2).subs(epsilon, 0) / 2
    coefficient_at_zero = sp.factor(sp.sqrtdenest(sp.trigsimp(coefficient.subs(coordinates[0], 0))))
    sine_squared = sp.sin(coordinates[2]) ** 2
    expected = sp.Rational(9, 2) * (
        (-101 + 45 * sp.sqrt(3)) * sine_squared**2
        + (109 - 52 * sp.sqrt(3)) * sine_squared
        - 22 + 8 * sp.sqrt(3)
    )
    _require(sp.trigsimp(coefficient_at_zero - expected) == 0, "quadratic tt source slice changed")
    return expected


def build_certificate() -> dict[str, Any]:
    _require(_load(BACKGROUND_CERTIFICATE).get("result_id") == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE", "background gate changed")
    _require(_load(LINEAR_CERTIFICATE).get("result_id") == "EINSTEIN_MAXWELL_CHEVRETON_TANGENT", "linear gate changed")
    _require(_load(PHOTON_CERTIFICATE).get("result_id") == "EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER", "periodic photon gate changed")
    mode = _linear_checks()
    chevreton = _chevreton_time_zero()
    source = _quadratic_source_tt_time_zero()
    theta = sp.symbols("theta", real=True)
    chevreton_average = sp.simplify(sp.integrate(chevreton[0, 0] * sp.sin(theta), (theta, 0, sp.pi)) / 2)
    source_average = sp.simplify(sp.integrate(source * sp.sin(theta), (theta, 0, sp.pi)) / 2)
    _require(chevreton_average == -sp.Rational(36, 5) * (1 + sp.sqrt(3)), "Chevreton average changed")
    _require(source_average == -sp.Rational(12, 5) * (6 + 5 * sp.sqrt(3)), "source average changed")

    return {
        "schema": "einstein-maxwell-periodic-graviton-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER",
        "result_state": "PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(TENSOR_HELPER.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(TENSOR_HELPER),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (BACKGROUND_CERTIFICATE, LINEAR_CERTIFICATE, PHOTON_CERTIFICATE)
            },
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 on the certified unit-radius magnetic product background",
            "charges": "electric and magnetic Maxwell charges fixed through second order",
            "quotient": "before the final residual SO(4,2) quotient",
            "mode_scope": "one smooth axisymmetric odd-parity l=2 gravitational harmonic with its flux-forced Maxwell dressing",
        },
        "first_order_mode": {
            "scalar_harmonic": "Y_20=(3*cos(theta)^2-1)/2",
            "axial_one_form": "X_phi=-sin(theta)*partial_theta(Y_20)=3*sin(theta)^2*cos(theta)",
            "metric": "h1=2*cos(omega*t)*X_phi*dx*dphi",
            "maxwell_potential": "a1=sqrt(3)*cos(omega*t)*Y_20*dx",
            "certified_frequency": "omega^2=6+2*sqrt(3)",
            "electric_charge_variation": "integral_S2 Y_20 dOmega=0",
            "magnetic_charge_variation": "f1_theta_phi=0",
            "not_pure_gauge": "For l=2, Regge--Wheeler gauge h_ij=0 fixes the axial angular diffeomorphism; the gauge-invariant base curl is proportional to H'(t)*X_phi and is not identically zero.",
            "helicity_interpretation": "compact odd-parity l=2 representative of the local metric/helicity-two sector, Maxwell-dressed by the nonzero background flux; not an asymptotic scattering-helicity state",
            **mode,
        },
        "chevreton_second_order_time_zero": {
            "convention": "C_Ch^(2)=2*H^(2)",
            "tensor_matrix": _matrix_strings(chevreton),
            "tt_projection": str(sp.factor(chevreton[0, 0])),
            "normalized_sphere_average_tt": str(chevreton_average),
            "nonzero": True,
        },
        "quadratic_weyl_maxwell_source_time_zero": {
            "equation": "S2_tt|t=0=[epsilon^2](3*B_tt-T_tt)|t=0",
            "tt_projection": str(source),
            "normalized_sphere_average_tt": str(source_average),
            "time_slice_suffices": "a correction would have to satisfy the averaged constraint on every Cauchy slice; failure at t=0 excludes it",
            "full_source_needed_for_no_go": False,
        },
        "adjoint_cokernel_witness": {
            "averaging_group": "S1 x SO(3)",
            "averaged_linear_tt_row": "<L_WM Phi2>_tt=-p after spatial total derivatives integrate to zero",
            "fixed_charge_condition": "p=0; the averaged electric correction has zero linear stress pairing with the magnetic background",
            "normalized_source_pairing_at_t_zero": str(source_average),
            "unnormalized_spatial_pairing_at_t_zero": "-48*pi*L*(6+5*sqrt(3))/5",
            "conclusion": "NO_SMOOTH_PERIODIC_SECOND_ORDER_CORRECTION_FOR_CERTIFIED_L2_BRANCH_AT_FIXED_CHARGES",
        },
        "classification": {
            "periodic_l2_gravitational_tangent_certified": True,
            "flux_forced_maxwell_dressing_included": True,
            "fixed_charge_second_order_extension_exists": False,
            "adjoint_cokernel_obstruction_certified": True,
            "both_normal_branches_classified_at_second_order": False,
            "all_helicity_two_harmonics_obstructed": False,
            "general_nonlinear_closure_certified": False,
        },
        "interpretation": "The compact fixed-charge second-order obstruction now reaches a genuine l=2 gravitational harmonic, not only radion, duality, or photon directions. The linear graviton representative remains present; what fails is its second-order integrability inside the declared compact fixed-charge Weyl--Maxwell solution locus.",
        "next_gate": "write the focused paper theorem combining the exact linear inclusion, removable universal-cover null source, and compact fixed-charge radion, duality, photon, and l=2 gravitational obstructions",
        "claim_boundary": "This LOCAL-ALGEBRAIC and REDUCED-MODE certificate proves a second-order fixed-charge obstruction for the plus branch of one smooth periodic odd-parity l=2 Einstein--Maxwell gravitational harmonic with its required Maxwell dressing. It is a compact gravitational-mode theorem before residual quotient, not a classification of both branches or every helicity-two harmonic, and makes no causal, asymptotically flat, observable, scattering, or quantum claim.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_periodic_graviton_second_order --verify bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_periodic_graviton_second_order --verify-exhaustive bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_periodic_graviton_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_periodic_graviton_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    """Fast provenance and contract rail; does not rebuild fourth-order tensors."""

    payload = _load(path)
    _require(payload.get("result_id") == "EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER", "result id changed")
    _require(_sha256(SCHEMA_PATH) == payload.get("schema_sha256"), "schema hash changed")
    provenance = payload.get("provenance", {})
    _require(_sha256(Path(__file__)) == provenance.get("generator_sha256"), "generator hash changed")
    _require(_sha256(TENSOR_HELPER) == provenance.get("tensor_helper_sha256"), "tensor helper hash changed")
    for relative, digest in provenance.get("inputs", {}).items():
        _require(_sha256(ROOT / relative) == digest, f"input hash changed: {relative}")


def verify_exhaustive_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"periodic graviton certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--verify-exhaustive", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.verify_exhaustive:
        verify_exhaustive_certificate(args.verify_exhaustive)
    if not args.write and not args.verify and not args.verify_exhaustive:
        parser.error("one of --write, --verify, or --verify-exhaustive is required")


if __name__ == "__main__":
    main()
