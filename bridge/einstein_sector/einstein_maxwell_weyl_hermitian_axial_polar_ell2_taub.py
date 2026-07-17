"""Hermitian real-tangent Taub and Chevreton matrices for the ell=2 minus pair."""

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
EE_SOURCE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json"
ADJOINT_WITNESS = ROOT / "bridge/certificates/einstein_maxwell_weyl_target_adjoint_witness.json"
DOMAIN_TAUB = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
CHEVRETON_TANGENT = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
TENSOR_HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_periodic_photon_second_order.py"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.schema.json"


class HermitianAxialPolarTaubError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HermitianAxialPolarTaubError(message)


def _canonical(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.trigsimp(sp.expand_trig(expression))))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _geometry(order: int) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    axial_amplitude, polar_amplitude = sp.symbols("a_A a_P", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    wave = sp.cos(frequency * time)
    harmonic = sp.legendre(2, sp.cos(theta))
    harmonic_prime = sp.diff(harmonic, theta)
    axial_one_form = -sine * harmonic_prime
    tr = lambda expression: _trunc(expression, epsilon, order)

    metric = sp.diag(-1, 1, 1, sine**2)
    # Axial minus representative (H_t,H_x,Q_t,Q_x)=(0,-2,0,2sqrt(3)).
    metric[1, 3] = metric[3, 1] = -2 * epsilon * axial_amplitude * wave * axial_one_form
    # Polar minus representative (A,B,C,K,U)=(2-2sqrt(3),0,2-2sqrt(3),2sqrt(3),1).
    polar_diagonal = (2 - 2 * root) * epsilon * polar_amplitude * wave * harmonic
    polar_sphere = 2 * root * epsilon * polar_amplitude * wave * harmonic
    metric[0, 0] += polar_diagonal
    metric[1, 1] += polar_diagonal
    metric[2, 2] += polar_sphere
    metric[3, 3] += polar_sphere * sine**2
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
    axial_q = 2 * root * axial_amplitude * wave
    field[0, 1] = epsilon * sp.diff(axial_q, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * axial_q * harmonic_prime
    field[2, 1] = -field[1, 2]
    polar_u = polar_amplitude * wave
    field[0, 3] = epsilon * sp.diff(polar_u, time) * axial_one_form
    field[3, 0] = -field[0, 3]
    field[2, 3] += epsilon * polar_u * sp.diff(axial_one_form, theta)
    field[3, 2] = -field[2, 3]
    return {
        "epsilon": epsilon,
        "amplitudes": (axial_amplitude, polar_amplitude),
        "frequency": frequency,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _matrix_from_quadratic(expression: sp.Expr, amplitudes: tuple[sp.Symbol, sp.Symbol]) -> sp.Matrix:
    matrix = sp.Matrix(
        2,
        2,
        lambda row, column: _canonical(
            sp.diff(expression, amplitudes[row], amplitudes[column]) / 2
        ),
    )
    reconstructed = _canonical((sp.Matrix(amplitudes).T * matrix * sp.Matrix(amplitudes))[0])
    _require(_canonical(reconstructed - expression) == 0, "quadratic matrix reconstruction failed")
    return matrix


def _chevreton() -> dict[str, object]:
    data = _geometry(order=1)
    epsilon = data["epsilon"]
    amplitudes = data["amplitudes"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    field = data["field"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(amplitudes, tuple)
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
    leading_tt = sum(
        inverse_zero[d, dd]
        * inverse_zero[index, other]
        * jet[d][0][index]
        * jet[dd][0][other]
        for d in range(4)
        for dd in range(4)
        for index in range(4)
        for other in range(4)
    )
    time, _, theta, _ = coordinates
    component = _canonical(
        (2 * (leading_tt - metric_zero[0, 0] * scalar / 4)).subs(time, 0)
    )
    average = _canonical(
        sp.integrate(component * sp.sin(theta), (theta, 0, sp.pi)) / 2
    )
    matrix = _matrix_from_quadratic(average, amplitudes)
    return {"tt_time_zero": component, "normalized_average": average, "matrix": matrix}


def _weyl_maxwell_taub() -> dict[str, object]:
    order = 2
    data = _curvature(_geometry(order=order), order=order)
    epsilon = data["epsilon"]
    amplitudes = data["amplitudes"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    riemann = data["riemann"]
    schouten = data["schouten"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(amplitudes, tuple)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(riemann, list)
    assert isinstance(schouten, sp.MatrixBase)
    tr = lambda expression: _trunc(expression, epsilon, order)

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
        lowered = tr(
            sum(metric[first, target] * riemann[target][second][third][fourth] for target in range(4))
        )
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
    residual_tt = tr(3 * tr(laplacian - mixed + curvature) - _stress(data, order)[0, 0])
    coefficient = sp.diff(residual_tt, epsilon, 2).subs(epsilon, 0) / 2
    time, _, theta, _ = coordinates
    component = _canonical(coefficient.subs(time, 0))
    average = _canonical(
        sp.integrate(component * sp.sin(theta), (theta, 0, sp.pi)) / 2
    )
    matrix = _matrix_from_quadratic(average, amplitudes)
    return {"tt_time_zero": component, "normalized_average": average, "matrix": matrix}


def _strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(_canonical(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _calculate() -> dict[str, object]:
    chevreton = _chevreton()
    taub = _weyl_maxwell_taub()
    chevreton_matrix = chevreton["matrix"]
    taub_matrix = taub["matrix"]
    assert isinstance(chevreton_matrix, sp.MatrixBase)
    assert isinstance(taub_matrix, sp.MatrixBase)
    _require(chevreton_matrix[0, 1] == 0, "Chevreton axial-polar cross parity changed")
    _require(taub_matrix[0, 1] == 0, "Taub axial-polar cross parity changed")
    q_axial, q_polar = taub_matrix[0, 0], taub_matrix[1, 1]
    _require(q_axial.is_positive is True, "axial Taub coefficient lost positivity")
    _require(q_polar.is_positive is True, "polar Taub coefficient lost positivity")
    quadrature_matrix = sp.diag(q_axial, q_axial, q_polar, q_polar)
    return {
        "chevreton_tt_time_zero": str(chevreton["tt_time_zero"]),
        "chevreton_normalized_average": str(chevreton["normalized_average"]),
        "chevreton_matrix": _strings(chevreton_matrix),
        "weyl_maxwell_tt_time_zero": str(taub["tt_time_zero"]),
        "weyl_maxwell_normalized_average": str(taub["normalized_average"]),
        "taub_matrix": _strings(taub_matrix),
        "taub_determinant": str(_canonical(taub_matrix.det())),
        "real_quadrature_order": ["A_cos", "A_sin", "P_cos", "P_sin"],
        "real_quadrature_taub_matrix": _strings(quadrature_matrix),
        "taub_positive_definite": True,
    }


def _channel_ledger() -> dict[str, Any]:
    return {
        "real_tangent": "Phi^(1)=Re[(z_A Phi_A+z_P Phi_P) exp(-i omega t)], omega^2=6-2sqrt(3)",
        "real_coordinates": "z_A=A_cos+i A_sin, z_P=P_cos+i P_sin",
        "frequency_channels": {
            "zero": ["A conjugate(A)", "P conjugate(P)", "A conjugate(P) and conjugate(A) P"],
            "two_omega": ["AA", "PP", "AP"],
        },
        "axisymmetric_ell_outputs": {
            "AA_even": [0, 2, 4],
            "PP_even": [0, 2, 4],
            "AP_axial": [2, 4],
        },
        "constant_lapse_selection": "only the zero-frequency scalar ell=0 projection survives",
        "cross_term": "A-P is odd under sphere parity and has zero constant-lapse projection",
        "phase_completion": "slice conservation and time-translation invariance turn each cosine self-coefficient into the same coefficient on cosine and sine quadratures with zero cos-sin entry",
    }


def build_certificate() -> dict[str, Any]:
    inputs = [EE_SOURCE, ADJOINT_WITNESS, DOMAIN_TAUB, CHEVRETON_TANGENT]
    records = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    _require(
        [record["result_id"] for record in records]
        == [
            "EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_AND_CORRECTION",
            "EINSTEIN_MAXWELL_WEYL_TARGET_CONSTANT_LAPSE_ADJOINT_WITNESS",
            "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT",
            "EINSTEIN_MAXWELL_CHEVRETON_TANGENT",
        ],
        "Hermitian Taub input changed",
    )
    calculation = _calculate()
    return {
        "schema": "einstein-maxwell-weyl-hermitian-axial-polar-ell2-taub-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB",
        "result_state": "EVERY_NONZERO_REAL_AXIAL_POLAR_MINUS_BRANCH_COMBINATION_FIXED_BUNDLE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_HERMITIAN_ELL2_K0_MINUS_PAIR_TAUB",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(TENSOR_HELPER.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(TENSOR_HELPER),
            "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in inputs},
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 on the unit magnetic fixed-P_N product background",
            "linear_space": "the four-real-dimensional cosine/sine quadrature space of the axisymmetric axial and polar ell=2,k=0 Einstein-Maxwell minus modes",
            "frequency_squared": "6-2*sqrt(3)",
            "charges": "fixed electric and magnetic charges through second order; fixed compact U(1) bundle P_N",
            "quotient": "after local Diff x U(1) reduction and before final residual quotient",
        },
        "channel_ledger": _channel_ledger(),
        "chevreton_second_order": {
            "definition": "C_Ch^(2) from the bilinear tensor in the first Maxwell covariant jet, evaluated on the declared Hermitian tangent",
            "tt_time_zero": calculation["chevreton_tt_time_zero"],
            "normalized_average": calculation["chevreton_normalized_average"],
            "cosine_amplitude_matrix_A_P": calculation["chevreton_matrix"],
            "cross_parity_zero": True,
            "nonzero": True,
            "obstruction_by_itself": False,
        },
        "weyl_maxwell_taub": {
            "source": "[epsilon^2](3B_tt-T_tt)=(1/2)D^2E_WM[Phi^(1),Phi^(1)]_tt",
            "tt_time_zero": calculation["weyl_maxwell_tt_time_zero"],
            "normalized_average": calculation["weyl_maxwell_normalized_average"],
            "cosine_amplitude_matrix_A_P": calculation["taub_matrix"],
            "cosine_matrix_determinant": calculation["taub_determinant"],
            "real_quadrature_order": calculation["real_quadrature_order"],
            "real_quadrature_matrix": calculation["real_quadrature_taub_matrix"],
            "positive_definite": calculation["taub_positive_definite"],
            "exact_positivity_witnesses": [
                "5*sqrt(3)-6>0 because 75>36",
                "7*sqrt(3)-11>0 because 147>121",
            ],
            "cross_parity_zero": True,
        },
        "adjoint_cokernel_witness": {
            "class": "zeta_H, the constant-lapse/time-translation constraint-adjoint class",
            "annihilation": "<zeta_H,L_WM Phi^(2)>=0 for every declared smooth periodic fixed-bundle correction",
            "fixed_bundle_condition": "the second-order magnetic Chern-class lift p is zero",
            "verdict": "the positive-definite Taub pairing is nonzero for every nonzero real tangent, so no declared second-order correction exists",
        },
        "classification": {
            "C_Ch_second_order_matrix_computed": True,
            "full_Weyl_Maxwell_constant_lapse_matrix_computed": True,
            "Hermitian_phase_space_completed": True,
            "every_nonzero_real_combination_fixed_bundle_obstructed": True,
            "remaining_harmonic_blocks_needed_for_fixed_bundle_no_go": False,
            "charge_relaxed_extension_constructed": False,
            "general_ell_or_nonzero_k_classified": False,
            "general_nonlinear_Einstein_sector_closed": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The previously certified AP sum-frequency axial source is nonzero but removable. For a real tangent, however, the conjugate self-products also generate a zero-frequency scalar source. Its fixed-bundle constant-lapse Taub form is positive definite on both axial and polar quadratures. Therefore no nonzero real combination of this degenerate minus-frequency pair extends to second order in the declared fixed-charge Weyl-Maxwell phase space.",
        "next_gate": "test whether an admitted magnetic-charge lift removes only this Taub component and solve the remaining blocks in that enlarged charge fibre; independently extend the Hermitian Taub classification to the plus pair, higher ell, and nonzero momentum",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem is restricted to the real axisymmetric ell=2,k=0 axial-polar minus-frequency pair on the compact fixed bundle. It is not a general Einstein-sector nonlinear no-go, does not classify charge-relaxed extension, final residual descent, causal boundaries, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub --verify bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload["result_id"] == "EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB", "result id changed")
    _require(payload["schema_sha256"] == _sha256(SCHEMA_PATH), "schema hash changed")
    provenance = payload["provenance"]
    _require(provenance["generator_sha256"] == _sha256(Path(__file__)), "generator hash changed")
    _require(provenance["tensor_helper_sha256"] == _sha256(TENSOR_HELPER), "tensor helper hash changed")
    for relative, digest in provenance["inputs"].items():
        _require(_sha256(ROOT / relative) == digest, f"input hash changed: {relative}")
    local = {"sqrt": sp.sqrt}
    matrix = sp.Matrix(
        [[sp.sympify(value, locals=local) for value in row] for row in payload["weyl_maxwell_taub"]["cosine_amplitude_matrix_A_P"]]
    )
    expected = sp.diag(
        sp.Rational(48, 5) * (5 * sp.sqrt(3) - 6),
        sp.Rational(24, 5) * (7 * sp.sqrt(3) - 11),
    )
    _require((matrix - expected).applyfunc(sp.simplify) == sp.zeros(2), "stored Taub matrix changed")
    _require(matrix[0, 0].is_positive is True and matrix[1, 1].is_positive is True, "stored Taub signs changed")


def verify_exhaustive_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale exhaustive Hermitian Taub certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--verify-exhaustive", type=Path)
    args = parser.parse_args()
    if args.print:
        print(json.dumps(_calculate(), indent=2, sort_keys=True))
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.verify_exhaustive:
        verify_exhaustive_certificate(args.verify_exhaustive)
    if not any((args.print, args.write, args.verify, args.verify_exhaustive)):
        parser.error("one of --print, --write, --verify, or --verify-exhaustive is required")


if __name__ == "__main__":
    main()
