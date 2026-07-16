"""Exact second-order obstruction for a periodic Einstein--Maxwell photon mode.

The fixture is the smooth axisymmetric l=1 mode on
R_t x S1_x x S2,

    A1 = q(t) cos(theta) dx,
    h1 = 2 H(t) sin(theta)^2 dx dphi.

All tensor operations use exact arithmetic in Q[epsilon]/(epsilon^3).
Only the tt projection of the quadratic Weyl--Maxwell source is needed for
the adjoint-cokernel proof, but the complete Chevreton trace tensor is kept.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
BACKGROUND_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
LINEAR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
SECOND_ORDER_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_second_order_inclusion.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_periodic_photon_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_periodic_photon_second_order.schema.json"


class PeriodicPhotonError(RuntimeError):
    """Raised when the exact periodic photon certificate fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PeriodicPhotonError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trunc(expression: sp.Expr, epsilon: sp.Symbol, order: int = 2) -> sp.Expr:
    expression = sp.sympify(expression)
    result = expression.subs(epsilon, 0)
    if order >= 1:
        result += epsilon * sp.diff(expression, epsilon).subs(epsilon, 0)
    if order >= 2:
        result += epsilon**2 * sp.diff(expression, epsilon, 2).subs(epsilon, 0) / 2
    return sp.simplify(result)


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(sp.trigsimp(value))) for value in matrix.row(row)] for row in range(matrix.rows)]


def _mode_geometry(order: int) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    amplitude = sp.cos(2 * time)
    n = 4
    tr = lambda expression: _trunc(expression, epsilon, order)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[1, 3] = metric[3, 1] = epsilon * amplitude * sine**2
    inverse = metric.inv().applyfunc(tr)

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

    field = sp.zeros(n)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(amplitude, time) * sp.cos(theta)
    field[1, 0] = -field[0, 1]
    field[1, 2] = epsilon * amplitude * sine
    field[2, 1] = -field[1, 2]

    return {
        "epsilon": epsilon,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _curvature(data: dict[str, object], order: int) -> dict[str, object]:
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    tr = lambda expression: _trunc(expression, epsilon, order)
    n = 4

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
                        sp.diff(connection[target][second][vector], coordinates[first])
                        - sp.diff(connection[target][first][vector], coordinates[second])
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
    return {**data, "riemann": riemann, "ricci": ricci, "scalar": scalar, "schouten": schouten}


def _stress(data: dict[str, object], order: int) -> sp.Matrix:
    epsilon = data["epsilon"]
    metric = data["metric"]
    inverse = data["inverse"]
    field = data["field"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(field, sp.MatrixBase)
    tr = lambda expression: _trunc(expression, epsilon, order)
    n = 4
    field_squared = tr(
        sum(
            inverse[a, c] * inverse[b, d] * field[a, b] * field[c, d]
            for a in range(n)
            for b in range(n)
            for c in range(n)
            for d in range(n)
        )
    )
    stress = sp.zeros(n)
    for a in range(n):
        for b in range(n):
            stress[a, b] = tr(
                sum(field[a, c] * inverse[c, d] * field[b, d] for c in range(n) for d in range(n))
                - metric[a, b] * field_squared / 4
            )
    return stress


def _linear_checks() -> dict[str, Any]:
    data = _curvature(_mode_geometry(order=1), order=1)
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    field = data["field"]
    ricci = data["ricci"]
    scalar = data["scalar"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(field, sp.MatrixBase)
    assert isinstance(ricci, sp.MatrixBase)
    assert isinstance(scalar, sp.Expr)
    stress = _stress(data, order=1)
    einstein = (ricci - metric * scalar / 2 + metric / 2 - stress).applyfunc(
        lambda value: sp.simplify(sp.diff(value, epsilon).subs(epsilon, 0))
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
            sp.simplify(
                sp.diff(
                    sum(sp.diff(sine * field_up[first, second], coordinates[first]) for first in range(4)) / sine,
                    epsilon,
                ).subs(epsilon, 0)
            )
            for second in range(4)
        ]
    )
    _require(einstein == sp.zeros(4), "periodic mode failed the linear Einstein equation")
    _require(maxwell == sp.zeros(4, 1), "periodic mode failed the linear Maxwell equation")

    coupling = sp.Matrix([[2, 2], [2, 2]])
    physical_vector = sp.Matrix([1, 1])
    _require(coupling * physical_vector == 4 * physical_vector, "physical frequency changed")
    return {
        "reduced_equations": ["H''+2*H+2*q=0", "q''+2*q+2*H=0"],
        "frequency_squared_matrix": [[2, 2], [2, 2]],
        "physical_eigenvector": [1, 1],
        "physical_frequency_squared": 4,
        "linearized_einstein_residual": _matrix_strings(einstein),
        "linearized_maxwell_residual": [str(value) for value in maxwell],
    }


def _chevreton_second_order() -> sp.Matrix:
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
            inverse_zero[d, dd]
            * inverse_zero[a, aa]
            * inverse_zero[b, bb]
            * jet[d][a][b]
            * jet[dd][aa][bb]
            for d in range(4)
            for dd in range(4)
            for a in range(4)
            for aa in range(4)
            for b in range(4)
            for bb in range(4)
        )
    )
    result = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            leading = sum(
                inverse_zero[d, dd]
                * inverse_zero[index, other]
                * jet[d][first][index]
                * jet[dd][second][other]
                for d in range(4)
                for dd in range(4)
                for index in range(4)
                for other in range(4)
            )
            result[first, second] = sp.factor(sp.trigsimp(2 * (leading - metric_zero[first, second] * scalar / 4)))
    return result


def _quadratic_source_tt() -> sp.Expr:
    """Compute the exact epsilon^2 coefficient of (3 B-T)_tt."""

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
                    for left in range(4)
                    for right in range(4)
                )
            )

    def weyl(first: int, second: int, third: int, fourth: int) -> sp.Expr:
        lowered = tr(sum(metric[first, target] * riemann[target][second][third][fourth] for target in range(4)))
        return tr(
            lowered
            - (
                metric[first, third] * schouten[fourth, second]
                - metric[first, fourth] * schouten[third, second]
                - metric[second, third] * schouten[fourth, first]
                + metric[second, fourth] * schouten[third, first]
            )
        )

    laplacian = sum(
        inverse[outer, inner] * second_schouten(outer, inner, 0, 0)
        for outer in range(4)
        for inner in range(4)
    )
    mixed = sum(
        inverse[outer, inner] * second_schouten(outer, 0, 0, inner)
        for outer in range(4)
        for inner in range(4)
    )
    curvature = sum(
        schouten_up[inner, outer] * weyl(0, inner, 0, outer)
        for inner in range(4)
        for outer in range(4)
    )
    bach_tt = tr(laplacian - mixed + curvature)
    stress_tt = _stress(data, order=2)[0, 0]
    residual_tt = tr(3 * bach_tt - stress_tt)
    coefficient = sp.diff(residual_tt, epsilon, 2).subs(epsilon, 0) / 2
    expected = (
        1
        - sp.Rational(19, 2) * sp.sin(coordinates[2]) ** 2
        + (sp.Rational(63, 2) * sp.sin(coordinates[2]) ** 2 - 21)
        * sp.sin(2 * coordinates[0]) ** 2
    )
    _require(sp.trigsimp(sp.expand_trig(coefficient - expected)) == 0, "quadratic tt source changed")
    return expected


def build_certificate() -> dict[str, Any]:
    background = _load(BACKGROUND_CERTIFICATE)
    linear = _load(LINEAR_CERTIFICATE)
    second_order = _load(SECOND_ORDER_CERTIFICATE)
    _require(background.get("result_id") == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE", "background gate changed")
    _require(linear.get("result_id") == "EINSTEIN_MAXWELL_CHEVRETON_TANGENT", "linear gate changed")
    _require(second_order.get("result_id") == "EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST", "second-order convention gate changed")

    mode = _linear_checks()
    chevreton = _chevreton_second_order()
    source_tt = _quadratic_source_tt()
    time, theta = sp.symbols("t theta", real=True)
    sphere_average_source = sp.simplify(
        sp.integrate(source_tt * sp.sin(theta), (theta, 0, sp.pi)) / 2
    )
    sphere_average_chevreton_tt = sp.simplify(
        sp.integrate(chevreton[0, 0] * sp.sin(theta), (theta, 0, sp.pi)) / 2
    )
    _require(sphere_average_source == -sp.Rational(16, 3), "source pairing changed")
    _require(sphere_average_chevreton_tt == -sp.Rational(8, 3), "Chevreton average changed")

    return {
        "schema": "einstein-maxwell-periodic-photon-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER",
        "result_state": "PERIODIC_NONZERO_FREQUENCY_PHOTON_FIXED_CHARGE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (BACKGROUND_CERTIFICATE, LINEAR_CERTIFICATE, SECOND_ORDER_CERTIFICATE)
            },
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 with the certified unit-radius product metric",
            "smoothness": "cos(theta) is the l=1 scalar harmonic and sin(theta)^2 dphi is the smooth axial Killing one-form",
            "charges": "electric and magnetic Maxwell charges fixed through second order",
            "quotient": "before any final residual SO(4,2) quotient",
        },
        "first_order_mode": {
            "potential": "a1=cos(2*t)*cos(theta)*dx",
            "metric": "h1=2*cos(2*t)*sin(theta)^2*dx*dphi",
            "maxwell_field": "f1=-2*sin(2*t)*cos(theta)*dt wedge dx+cos(2*t)*sin(theta)*dx wedge dtheta",
            "electric_charge_variation": "integral_S2 cos(theta) dOmega=0",
            "magnetic_charge_variation": "f1_theta_phi=0",
            **mode,
        },
        "chevreton_second_order": {
            "convention": "C_Ch^(2)=2*H^(2)",
            "tensor_matrix": _matrix_strings(chevreton),
            "tt_simplified": "8*(sin(theta)^2-1)+(8-12*sin(theta)^2)*sin(2*t)^2",
            "normalized_sphere_average_tt": str(sphere_average_chevreton_tt),
            "nonzero": True,
        },
        "quadratic_weyl_maxwell_source": {
            "equation": "S2_tt=[epsilon^2](3*B_tt-T_tt)",
            "tt_projection": str(source_tt),
            "normalized_sphere_average_tt": str(sphere_average_source),
            "full_source_needed_for_no_go": False,
            "reason": "one nonzero pairing with an adjoint-cokernel element already excludes every correction",
        },
        "adjoint_cokernel_witness": {
            "averaging_group": "S1 x SO(3)",
            "averaged_linear_tt_row": "<L_WM Phi2>_tt=-p because all spatial total derivatives integrate to zero",
            "fixed_charge_condition": "p=0; an averaged electric correction has zero linear stress pairing with the magnetic background",
            "normalized_source_pairing": "-16/3",
            "unnormalized_spatial_pairing": "-(64*pi*L)/3",
            "conclusion": "NO_SMOOTH_PERIODIC_SECOND_ORDER_CORRECTION_AT_FIXED_ELECTRIC_AND_MAGNETIC_CHARGES",
        },
        "classification": {
            "periodic_nonzero_frequency_photon_tangent_certified": True,
            "fixed_charge_second_order_extension_exists": False,
            "adjoint_cokernel_obstruction_certified": True,
            "general_photon_harmonic_no_go_certified": False,
            "periodic_helicity_two_result_certified": False,
            "general_nonlinear_closure_certified": False,
        },
        "interpretation": "The earlier compact obstruction is not confined to zero modes: a genuine l=1 photon--metric normal mode at omega=2 has a non-removable second-order fixed-charge source. This is an integrability obstruction in the compact charge sector, not a loss of the linear photon state.",
        "next_gate": "test one periodic helicity-two harmonic, then state the compact fixed-charge theorem for the declared radion, duality, photon, and graviton sectors",
        "claim_boundary": "This LOCAL-ALGEBRAIC and REDUCED-MODE certificate proves a second-order fixed-electric-and-magnetic-charge obstruction for one smooth periodic nonzero-frequency l=1 Einstein--Maxwell photon--metric tangent on R_t x S1 x S2. It does not prove a no-go for every photon or graviton harmonic, general nonlinear failure, causal or asymptotically flat failure, observable non-embedding, scattering inequivalence, or a quantum statement.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order --verify bridge/certificates/einstein_maxwell_periodic_photon_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_periodic_photon_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_periodic_photon_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"periodic photon certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
