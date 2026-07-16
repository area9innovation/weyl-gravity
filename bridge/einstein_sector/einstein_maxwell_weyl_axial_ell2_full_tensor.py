"""Independent full-tensor ell=2 replay for the axial Weyl--Maxwell block.

This module deliberately does not use the arbitrary-lambda harmonic reduction.
It inserts Y_20=P_2(cos(theta)) into the four-dimensional metric and Maxwell
field, linearizes the Bach--Maxwell equations in coordinates, and extracts the
off-shell Fourier coefficient rows.  It is the independent fixture required by
the generic axial operator-module preflight.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _stress,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_full_tensor.schema.json"


class AxialEll2FullTensorError(RuntimeError):
    """Raised when the independent full-tensor replay fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialEll2FullTensorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _linear_coefficient(expression: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    return sp.expand(sp.diff(expression, epsilon).subs(epsilon, 0))


def _separate(expression: sp.Expr, theta: sp.Symbol | None = None) -> sp.Expr:
    """Reduce explicit ell=2 trigonometry after division by its harmonic."""

    reduced = sp.trigsimp(expression, method="fu")
    if theta is not None:
        sine_squared = 1 - sp.cos(theta) ** 2
        numerator, denominator = sp.together(reduced).as_numer_denom()
        for power in (8, 6, 4, 2):
            replacement = sine_squared ** (power // 2)
            numerator = sp.expand(numerator).subs(sp.sin(theta) ** power, replacement)
            denominator = sp.expand(denominator).subs(sp.sin(theta) ** power, replacement)
        reduced = numerator / denominator
    return sp.factor(sp.cancel(reduced))


def _full_tensor_rows(ell: int = 2) -> dict[str, object]:
    _require(ell >= 2, "the axial tensor fixture requires ell>=2")
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency, momentum = sp.symbols("omega k", real=True)
    h_time, h_space, q_time, q_space = sp.symbols("h_t h_x q_t q_x")
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    eigenvalue = ell * (ell + 1)
    harmonic = sp.legendre(ell, sp.cos(theta))
    harmonic_prime = sp.diff(harmonic, theta)
    axial_one_form = -sine * harmonic_prime

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 3] = metric[3, 0] = epsilon * h_time * wave * axial_one_form
    metric[1, 3] = metric[3, 1] = epsilon * h_space * wave * axial_one_form
    inverse = sp.diag(-1, 1, 1, sine ** -2)
    inverse[0, 3] = inverse[3, 0] = epsilon * h_time * wave * axial_one_form / sine**2
    inverse[1, 3] = inverse[3, 1] = -epsilon * h_space * wave * axial_one_form / sine**2

    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = _trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2,
                    epsilon,
                    1,
                )

    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.I * (-frequency * q_space - momentum * q_time) * wave * harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * q_time * wave * harmonic_prime
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * q_space * wave * harmonic_prime
    field[2, 1] = -field[1, 2]

    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        1,
    )
    schouten = data["schouten"]
    riemann = data["riemann"]
    assert isinstance(schouten, sp.MatrixBase)
    assert isinstance(riemann, list)

    background_metric = metric.subs(epsilon, 0)
    background_inverse = inverse.subs(epsilon, 0)
    background_schouten = schouten.subs(epsilon, 0)
    delta_schouten = schouten.applyfunc(lambda value: _linear_coefficient(value, epsilon))
    background_connection = [
        [[connection[a][b][c].subs(epsilon, 0) for c in range(4)] for b in range(4)]
        for a in range(4)
    ]
    delta_connection = [
        [[_linear_coefficient(connection[a][b][c], epsilon) for c in range(4)] for b in range(4)]
        for a in range(4)
    ]

    # The product background has covariantly constant Schouten tensor.  Thus
    # the first derivative below is precisely delta(nabla P), and the second
    # needs only the background connection acting on this rank-three tensor.
    derivative_schouten = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for derivative in range(4):
        for first in range(4):
            for second in range(4):
                derivative_schouten[derivative][first][second] = sp.expand(
                    sp.diff(delta_schouten[first, second], coordinates[derivative])
                    - sum(
                        background_connection[index][derivative][first]
                        * delta_schouten[index, second]
                        + background_connection[index][derivative][second]
                        * delta_schouten[first, index]
                        + delta_connection[index][derivative][first]
                        * background_schouten[index, second]
                        + delta_connection[index][derivative][second]
                        * background_schouten[first, index]
                        for index in range(4)
                    )
                )

    second_schouten = [
        [
            [[sp.S.Zero for _ in range(4)] for _ in range(4)]
            for _ in range(4)
        ]
        for _ in range(4)
    ]
    for outer in range(4):
        for inner in range(4):
            for first in range(4):
                for second in range(4):
                    second_schouten[outer][inner][first][second] = sp.expand(
                        sp.diff(
                            derivative_schouten[inner][first][second],
                            coordinates[outer],
                        )
                        - sum(
                            background_connection[index][outer][inner]
                            * derivative_schouten[index][first][second]
                            + background_connection[index][outer][first]
                            * derivative_schouten[inner][index][second]
                            + background_connection[index][outer][second]
                            * derivative_schouten[inner][first][index]
                            for index in range(4)
                        )
                    )

    weyl_background = [
        [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
        for _ in range(4)
    ]
    weyl_delta = [
        [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
        for _ in range(4)
    ]
    for first in range(4):
        for second in range(4):
            for third in range(4):
                for fourth in range(4):
                    lowered_riemann = sum(
                        metric[first, target] * riemann[target][second][third][fourth]
                        for target in range(4)
                    )
                    weyl = _trunc(
                        lowered_riemann
                        - (
                            metric[first, third] * schouten[fourth, second]
                            - metric[first, fourth] * schouten[third, second]
                            - metric[second, third] * schouten[fourth, first]
                            + metric[second, fourth] * schouten[third, first]
                        ),
                        epsilon,
                        1,
                    )
                    weyl_background[first][second][third][fourth] = weyl.subs(epsilon, 0)
                    weyl_delta[first][second][third][fourth] = _linear_coefficient(weyl, epsilon)

    schouten_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            schouten_up[first, second] = _trunc(
                sum(
                    inverse[first, left]
                    * inverse[second, right]
                    * schouten[left, right]
                    for left in range(4)
                    for right in range(4)
                ),
                epsilon,
                1,
            )
    background_schouten_up = schouten_up.subs(epsilon, 0)
    delta_schouten_up = schouten_up.applyfunc(lambda value: _linear_coefficient(value, epsilon))

    delta_bach = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            laplacian = sum(
                background_inverse[outer, inner]
                * second_schouten[outer][inner][first][second]
                for outer in range(4)
                for inner in range(4)
            )
            mixed = sum(
                background_inverse[outer, inner]
                * second_schouten[outer][first][second][inner]
                for outer in range(4)
                for inner in range(4)
            )
            curvature = sum(
                delta_schouten_up[inner, outer]
                * weyl_background[first][inner][second][outer]
                + background_schouten_up[inner, outer]
                * weyl_delta[first][inner][second][outer]
                for inner in range(4)
                for outer in range(4)
            )
            delta_bach[first, second] = sp.expand(laplacian - mixed + curvature)

    stress = _stress(data, 1)
    delta_stress = stress.applyfunc(lambda value: _linear_coefficient(value, epsilon))
    target_metric = (3 * delta_bach - delta_stress).applyfunc(sp.expand)

    field_up = sp.zeros(4)
    for left in range(4):
        for right in range(4):
            field_up[left, right] = _trunc(
                sum(
                    inverse[left, first]
                    * inverse[right, second]
                    * field[first, second]
                    for first in range(4)
                    for second in range(4)
                ),
                epsilon,
                1,
            )
    maxwell = sp.Matrix(
        [
            _linear_coefficient(
                sum(
                    sp.diff(sine * field_up[left, right], coordinates[left])
                    for left in range(4)
                )
                / sine,
                epsilon,
            )
            for right in range(4)
        ]
    )

    tensor_factor = sp.Rational(eigenvalue, 2) * harmonic * sine + sp.cos(theta) * harmonic_prime
    normalizers = {
        "metric_t": wave * axial_one_form,
        "metric_x": wave * axial_one_form,
        "metric_angular": sp.I * wave * tensor_factor,
        "maxwell_t": wave * harmonic,
        "maxwell_x": wave * harmonic,
        "maxwell_angular": -sp.I * wave * harmonic_prime,
    }
    rows = {
        "metric_t": _separate(target_metric[0, 3] / normalizers["metric_t"], theta),
        "metric_x": _separate(target_metric[1, 3] / normalizers["metric_x"], theta),
        "metric_angular": _separate(target_metric[2, 3] / normalizers["metric_angular"], theta),
        "maxwell_t": _separate(maxwell[0] / normalizers["maxwell_t"], theta),
        "maxwell_x": _separate(maxwell[1] / normalizers["maxwell_x"], theta),
        "maxwell_angular": _separate(maxwell[2] / normalizers["maxwell_angular"], theta),
    }
    for name, row in rows.items():
        _require(not row.has(theta), f"{name} failed harmonic separation: {row}")

    return {
        "symbols": {
            "ell": ell,
            "eigenvalue": eigenvalue,
            "frequency": frequency,
            "momentum": momentum,
            "coefficients": (h_time, h_space, q_time, q_space),
        },
        "rows": rows,
        "all_unlisted_metric_rows": [
            (first, second, _separate(target_metric[first, second] / wave, theta))
            for first in range(4)
            for second in range(first, 4)
            if (first, second) not in {(0, 3), (1, 3), (2, 3)}
            and target_metric[first, second] != 0
        ],
        "all_unlisted_maxwell_rows": [
            (index, _separate(maxwell[index] / wave, theta))
            for index in range(4)
            if index not in {0, 1, 2} and maxwell[index] != 0
        ],
    }


def _ell2_full_tensor_rows() -> dict[str, object]:
    return _full_tensor_rows(2)


def _row_strings(rows: dict[str, sp.Expr]) -> dict[str, str]:
    return {name: str(sp.factor(value)) for name, value in rows.items()}


def build_certificate() -> dict[str, object]:
    samples = {}
    for ell in (2, 3, 4):
        result = _full_tensor_rows(ell)
        _require(result["all_unlisted_metric_rows"] == [], f"ell={ell} has extra metric rows")
        _require(result["all_unlisted_maxwell_rows"] == [], f"ell={ell} has extra Maxwell rows")
        samples[str(ell)] = {
            "lambda": ell * (ell + 1),
            "rows": _row_strings(result["rows"]),
            "all_unlisted_metric_rows_zero": True,
            "all_unlisted_maxwell_rows_zero": True,
        }
    return {
        "schema": "einstein-maxwell-weyl-axial-ell2-full-tensor-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_FULL_TENSOR",
        "result_state": "ELL2_INDEPENDENT_REPLAY_WITH_ELL3_ELL4_SPECTRAL_RECONSTRUCTION_SAMPLES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_AXIAL_FULL_TENSOR_SAMPLES",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "method": "direct coordinate linearization of 3*B_ab-T_ab and div(F)^b on R_t x S1 x S2 with explicit Legendre harmonics",
        },
        "normalization": {
            "harmonic": "Y_ell0=P_ell(cos(theta))",
            "metric_t": "delta(3B-T)_(t,phi)/(exp(i(kx-omega t))*X_phi)",
            "metric_x": "delta(3B-T)_(x,phi)/(exp(i(kx-omega t))*X_phi)",
            "metric_angular": "delta(3B-T)_(theta,phi)/(i*exp(i(kx-omega t))*X_(theta,phi))",
            "maxwell_rows": "coordinate Maxwell divergence divided by the matching scalar/vector harmonic",
        },
        "samples": samples,
        "classification": {
            "ell2_full_tensor_replay_passed": True,
            "off_shell_frequency_and_momentum_retained": True,
            "no_branch_substitution": True,
            "all_unlisted_rows_zero": True,
            "ell3_ell4_reconstruction_samples_passed": True,
            "generic_lambda_operator_inferred_here": False,
            "Green_identity_or_particle_claim": False,
        },
        "interpretation": "The required Y_20 replay is now independent of the arbitrary-lambda harmonic reduction and exposes the complete off-shell fourth-order metric rows together with the unchanged Maxwell rows. Ell=3 and ell=4 are retained as exact spectral-polynomial reconstruction samples; this fixture alone does not infer or interpret a generic extra branch.",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE certificate is a direct coordinate tensor fixture. It does not by itself prove the generic-lambda operator, a covariant Green identity, a causal phase space, a norm, or a particle spectrum.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_ell2_full_tensor.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ell2_full_tensor",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale full-tensor fixture: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--ell", type=int)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.ell is not None:
        result = _full_tensor_rows(args.ell)
        for key, value in result["rows"].items():
            print(f"{key}: {value}")
        print(f"unlisted metric rows: {result['all_unlisted_metric_rows']}")
        print(f"unlisted Maxwell rows: {result['all_unlisted_maxwell_rows']}")
    if not args.write and args.verify is None and args.ell is None:
        parser.error("one of --write, --verify, or --ell is required")
