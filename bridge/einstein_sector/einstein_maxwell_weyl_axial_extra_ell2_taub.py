"""Exact fixed-charge Taub test for the two axial extra ell=2 directions.

The two certified generic extra representatives are specialized to k=0 and
lambda=6.  A real Hermitian mode is used, so its quadratic source contains
the zero-frequency singlet seen by the compact constant-lapse adjoint class.
All tensor operations use exact arithmetic in Q(sqrt(3))[epsilon]/(epsilon^3).
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
OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
DETECTOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json"
DOMAIN_TAUB = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
PERIODIC_WITNESS = ROOT / "bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json"
TENSOR_HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_periodic_photon_second_order.py"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_extra_ell2_taub.schema.json"


class AxialExtraEll2TaubError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialExtraEll2TaubError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.trigsimp(sp.expand_trig(expression))))


def _mode_geometry(order: int) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    amplitude_one, amplitude_two = sp.symbols("a_1 a_2", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    frequency = sp.Rational(4) / sp.sqrt(3)
    wave = sp.cos(frequency * time)
    harmonic = sp.legendre(2, sp.cos(theta))
    harmonic_prime = sp.diff(harmonic, theta)
    axial_one_form = -sine * harmonic_prime
    tr = lambda expression: _trunc(expression, epsilon, order)

    # At lambda=6,k=0 the certified extra columns are
    # e1=(-6,0,6,0) and e2=(0,-2/3,0,6).
    h_time = -6 * amplitude_one
    h_space = -sp.Rational(2, 3) * amplitude_two
    q_time = 6 * amplitude_one
    q_space = 6 * amplitude_two

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 3] = metric[3, 0] = epsilon * h_time * wave * axial_one_form
    metric[1, 3] = metric[3, 1] = epsilon * h_space * wave * axial_one_form
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

    potential_time = q_time * wave * harmonic
    potential_space = q_space * wave * harmonic
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(potential_space, time)
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * sp.diff(potential_time, theta)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * sp.diff(potential_space, theta)
    field[2, 1] = -field[1, 2]
    return {
        "epsilon": epsilon,
        "amplitudes": (amplitude_one, amplitude_two),
        "frequency": frequency,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _quadratic_source_tt_time_zero() -> tuple[sp.Expr, sp.Expr, sp.Matrix]:
    data = _curvature(_mode_geometry(order=2), order=2)
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
                        connection[index][derivative][first]
                        * schouten[index, second]
                        + connection[index][derivative][second]
                        * schouten[first, index]
                        for index in range(4)
                    )
                )

    def second_schouten(
        outer: int, inner: int, first: int, second: int
    ) -> sp.Expr:
        return tr(
            sp.diff(
                derivative_schouten[inner][first][second], coordinates[outer]
            )
            - sum(
                connection[index][outer][inner]
                * derivative_schouten[index][first][second]
                + connection[index][outer][first]
                * derivative_schouten[inner][index][second]
                + connection[index][outer][second]
                * derivative_schouten[inner][first][index]
                for index in range(4)
            )
        )

    schouten_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            schouten_up[first, second] = tr(
                sum(
                    inverse[first, left]
                    * inverse[second, right]
                    * schouten[left, right]
                    for left in range(4)
                    for right in range(4)
                )
            )

    def weyl(first: int, second: int, third: int, fourth: int) -> sp.Expr:
        lowered = tr(
            sum(
                metric[first, target]
                * riemann[target][second][third][fourth]
                for target in range(4)
            )
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
    residual_tt = tr(
        3 * tr(laplacian - mixed + curvature) - _stress(data, 2)[0, 0]
    )
    coefficient = sp.diff(residual_tt, epsilon, 2).subs(epsilon, 0) / 2
    time_zero = _canonical(coefficient.subs(coordinates[0], 0))
    theta = coordinates[2]
    normalized_average = _canonical(
        sp.integrate(time_zero * sp.sin(theta), (theta, 0, sp.pi)) / 2
    )
    taub_matrix = sp.Matrix(
        2,
        2,
        lambda row, column: _canonical(
            sp.diff(
                normalized_average, amplitudes[row], amplitudes[column]
            )
            / 2
        ),
    )
    reconstructed = _canonical(
        (sp.Matrix(amplitudes).T * taub_matrix * sp.Matrix(amplitudes))[0]
    )
    _require(
        _canonical(reconstructed - normalized_average) == 0,
        "Taub matrix did not reconstruct the averaged source",
    )
    return time_zero, normalized_average, taub_matrix


def _linear_operator_check(operator: dict[str, Any]) -> dict[str, Any]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    local_symbols = {"lam": eigenvalue, "k": momentum, "omega": frequency, "I": sp.I}
    hessian = sp.Matrix(
        [
            [
                sp.sympify(value.replace("lambda", "lam"), locals=local_symbols)
                for value in row
            ]
            for row in operator["operator_algebra"]["gauge_fixed_Hessian_operator"]
        ]
    )
    basis = sp.Matrix.hstack(
        sp.Matrix([-6, 0, 6, 0]),
        sp.Matrix([0, -sp.Rational(2, 3), 0, 6]),
    )
    image = (hessian * basis).subs(
        {
            eigenvalue: 6,
            momentum: 0,
            frequency: sp.Rational(4) / sp.sqrt(3),
        }
    ).applyfunc(_canonical)
    _require(image == sp.zeros(4, 2), "specialized extra basis left the linear kernel")
    return {
        "shell": "lambda=6, k=0, omega=4/sqrt(3)",
        "operator_image_of_e1_e2": [
            [str(image[row, column]) for column in range(2)]
            for row in range(4)
        ],
        "both_basis_vectors_on_shell": True,
    }


def build_certificate() -> dict[str, Any]:
    inputs = {
        "operator": OPERATOR,
        "detector": DETECTOR,
        "fixed_bundle_taub_domain": DOMAIN_TAUB,
        "constant_lapse_witness": PERIODIC_WITNESS,
    }
    records = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in inputs.items()
    }
    _require(records["operator"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR", "operator input changed")
    _require(records["detector"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR", "detector input changed")
    _require(records["fixed_bundle_taub_domain"]["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT", "fixed-bundle Taub domain changed")
    _require(records["constant_lapse_witness"]["classification"]["adjoint_cokernel_obstruction_certified"], "constant-lapse witness changed")
    source, average, taub_matrix = _quadratic_source_tt_time_zero()
    determinant = _canonical(taub_matrix.det())
    rank = taub_matrix.rank()
    first_principal_minor = _canonical(taub_matrix[0, 0])
    negative_definite = bool(
        first_principal_minor.is_negative and determinant.is_positive
    )
    _require(negative_definite, "extra Taub matrix lost negative definiteness")
    return {
        "schema": "einstein-maxwell-weyl-axial-extra-ell2-taub-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_ELL2_TAUB",
        "result_state": "AXIAL_EXTRA_ELL2_K0_ALL_NONZERO_REAL_COMBINATIONS_FIXED_CHARGE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_AXIAL_EXTRA_ELL2_K0_QUADRATIC_TAUB",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(TENSOR_HELPER.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(TENSOR_HELPER),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in inputs.items()
            },
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 on the unit magnetic product background",
            "charges": "fixed electric and magnetic charges through second order on P_N with N=2",
            "mode": "real axisymmetric ell=2,k=0 extra-primary mode at omega^2=16/3",
            "quotient": "after local Diff x U1 reduction and before final residual SO(4,2) quotient",
        },
        "first_order_extra_basis": {
            "coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
            "e_1": ["-6", "0", "6", "0"],
            "e_2": ["0", "-2/3", "0", "6"],
            "real_mode_rule": "Phi1=(a_1 e_1+a_2 e_2) cos(4 t/sqrt(3)); equivalently the Hermitian e_omega plus conjugate(e_omega) polarization",
            "linear_magnetic_charge_variation": "0",
            "linear_electric_charge_variation": "0 because integral_S2 Y_20 dOmega=0",
            "linear_operator_check": _linear_operator_check(records["operator"]),
        },
        "quadratic_source": {
            "equation": "S2_tt=[epsilon^2](3*B_tt-T_tt)",
            "tt_projection_at_t_zero": str(source),
            "normalized_sphere_average_at_t_zero": str(average),
            "constant_lapse_Taub_matrix": [
                [str(_canonical(taub_matrix[row, column])) for column in range(2)]
                for row in range(2)
            ],
            "matrix_rank": rank,
            "first_principal_minor": str(first_principal_minor),
            "matrix_determinant": str(determinant),
            "signature_positive_negative": [0, 2],
            "negative_definite": negative_definite,
            "real_conjugate_zero_mode_included": True,
        },
        "adjoint_cokernel_witness": {
            "class": "constant spatial lapse / background time translation",
            "averaging_group": "S1 x SO(3)",
            "linear_row": "<L_WM Phi2>_tt=-p after compact spatial total derivatives vanish",
            "fixed_bundle_condition": "p=0 by exact second variation of the Chern number",
            "witness_imported_by_hash": True,
        },
        "classification": {
            "quadratic_Taub_matrix_computed": True,
            "all_nonzero_amplitude_combinations_obstructed": negative_definite,
            "some_nonzero_amplitude_combination_obstructed": bool(taub_matrix != sp.zeros(2)),
            "explicit_second_order_correction_constructed": False,
            "generic_ell_or_nonzero_k_classified": False,
            "EE_and_EX_quadratic_blocks_computed": False,
            "final_residual_or_causal_claim": False,
            "quantum_claim": False,
        },
        "interpretation": "This is the first self-extension test of the classified extra target module. The exact constant-lapse matrix decides the fixed-charge compact ell=2,k=0 combinations recorded above. It does not classify other ell or k, the Einstein-to-extra source block, residual survival, causal boundaries, or particles.",
        "next_gate": "compute the EE normal-source projection and the mixed EX block against the certified extra detector, then extend the XX Taub matrix to symbolic k and generic lambda or exhibit the first unobstructed correction",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE result is a compact fixed-charge quadratic extension test for the declared two-dimensional extra ell=2,k=0 span only. It is not a general nonlinear, causal, asymptotic, particle, or quantum theorem.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_ell2_taub --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_ell2_taub --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_ell2_taub",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload.get("result_id") == "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_ELL2_TAUB", "result id changed")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash changed")
    provenance = payload.get("provenance", {})
    _require(provenance.get("generator_sha256") == _sha256(Path(__file__)), "generator hash changed")
    _require(provenance.get("tensor_helper_sha256") == _sha256(TENSOR_HELPER), "tensor helper hash changed")
    for record in provenance.get("inputs", {}).values():
        _require(_sha256(ROOT / record["path"]) == record["sha256"], f"input hash changed: {record['path']}")


def verify_exhaustive_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(
        json.loads(path.read_text(encoding="utf-8")) == build_certificate(),
        f"stale axial extra ell2 Taub certificate: {path}",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--verify-exhaustive", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if args.verify_exhaustive:
        verify_exhaustive_certificate(args.verify_exhaustive)
    if not args.write and args.verify is None and args.verify_exhaustive is None:
        parser.error("one of --write, --verify, or --verify-exhaustive is required")


if __name__ == "__main__":
    main()
