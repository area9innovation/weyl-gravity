"""Natural support-local Einstein--Maxwell to Weyl--Maxwell chain map.

The equation map is derived in the complete parallel invariant operator
algebra of the compact magnetic 2+2 product.  Direct action-derived source
rows and independently frozen target rows are replayed in both parities; the
identity-row map is then solved on arbitrary equation tensors.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _stress,
    _trunc,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _generic_rows as _polar_generic_rows,
)
from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor import (
    _linear_coefficient,
    _separate,
)
from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import (
    _generic_rows as _axial_generic_rows,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json"
PROOF = ROOT / "bridge/einstein_sector/proofs/einstein-weyl-compact-product-covariant-chain-map-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-product-covariant-chain-map-v1.schema.json"
REPORT = ROOT / "bridge/einstein_sector/reports/einstein-weyl-compact-product-covariant-chain-map.md"
INPUTS = {
    "background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
    "principal_preflight": ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json",
    "source_axial": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "source_polar": ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json",
    "target_axial_tensor": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json",
    "target_polar_tensor": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "exceptional_maps": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
}


class CovariantChainMapError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CovariantChainMapError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _covariant_one_covector(
    value: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    connection: list[list[list[sp.Expr]]],
) -> list[list[sp.Expr]]:
    return [
        [
            sp.expand(
                sp.diff(value[b], coordinates[a])
                - sum(connection[c][a][b] * value[c] for c in range(4))
            )
            for b in range(4)
        ]
        for a in range(4)
    ]


def _covariant_one_cov2(
    value: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    connection: list[list[list[sp.Expr]]],
) -> list[list[list[sp.Expr]]]:
    return [
        [
            [
                sp.expand(
                    sp.diff(value[a, b], coordinates[d])
                    - sum(
                        connection[c][d][a] * value[c, b]
                        + connection[c][d][b] * value[a, c]
                        for c in range(4)
                    )
                )
                for b in range(4)
            ]
            for a in range(4)
        ]
        for d in range(4)
    ]


def _covariant_two_cov2(
    first: list[list[list[sp.Expr]]],
    coordinates: tuple[sp.Symbol, ...],
    connection: list[list[list[sp.Expr]]],
) -> list[list[list[list[sp.Expr]]]]:
    return [
        [
            [
                [
                    sp.expand(
                        sp.diff(first[d][a][b], coordinates[c])
                        - sum(
                            connection[r][c][d] * first[r][a][b]
                            + connection[r][c][a] * first[d][r][b]
                            + connection[r][c][b] * first[d][a][r]
                            for r in range(4)
                        )
                    )
                    for b in range(4)
                ]
                for a in range(4)
            ]
            for d in range(4)
        ]
        for c in range(4)
    ]


def _tracefree(value: sp.Matrix, metric: sp.Matrix, inverse: sp.Matrix) -> sp.Matrix:
    trace = sp.expand(
        sum(inverse[a, b] * value[a, b] for a in range(4) for b in range(4))
    )
    return (value - metric * trace / 4).applyfunc(sp.expand)


def _background_connection(theta: sp.Symbol) -> list[list[list[sp.Expr]]]:
    sine = sp.sin(theta)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    connection[2][3][3] = -sine * sp.cos(theta)
    connection[3][2][3] = connection[3][3][2] = sp.cot(theta)
    return connection


def _source_rows(
    *,
    metric: sp.Matrix,
    inverse: sp.Matrix,
    connection: list[list[list[sp.Expr]]],
    field: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    epsilon: sp.Symbol,
) -> tuple[sp.Matrix, sp.Matrix]:
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
    ricci = data["ricci"]
    scalar = data["scalar"]
    assert isinstance(ricci, sp.MatrixBase) and isinstance(scalar, sp.Expr)
    stress = _stress(data, 1)
    source_metric = (
        ricci - metric * scalar / 2 + metric / 2 - stress
    ).applyfunc(lambda value: _linear_coefficient(value, epsilon))
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
    theta = coordinates[2]
    sine = sp.sin(theta)
    volume = _trunc(sp.sqrt(-metric.det()), epsilon, 1).subs(
        sp.Abs(sine), sine
    )
    source_maxwell = sp.Matrix(
        [
            _linear_coefficient(
                sum(
                    sp.diff(volume * field_up[left, right], coordinates[left])
                    for left in range(4)
                )
                / sine,
                epsilon,
            )
            for right in range(4)
        ]
    )
    return source_metric, source_maxwell


def _polar_data(ell: int) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency, momentum = sp.symbols("omega k", real=True)
    source_a, mixed, source_c, sphere_trace_field, maxwell = sp.symbols("A B C K U")
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    harmonic = sp.legendre(ell, sp.cos(theta))
    first = sp.diff(harmonic, theta)
    axial_one_form = -sine * first
    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 0] += epsilon * source_a * wave * harmonic
    metric[0, 1] = metric[1, 0] = epsilon * mixed * wave * harmonic
    metric[1, 1] += epsilon * source_c * wave * harmonic
    metric[2, 2] += epsilon * sphere_trace_field * wave * harmonic
    metric[3, 3] += epsilon * sphere_trace_field * wave * harmonic * sine**2
    inverse = metric.inv().applyfunc(lambda value: _trunc(value, epsilon, 1))
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
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
    field[0, 3] = -sp.I * frequency * epsilon * maxwell * wave * axial_one_form
    field[3, 0] = -field[0, 3]
    field[1, 3] = sp.I * momentum * epsilon * maxwell * wave * axial_one_form
    field[3, 1] = -field[1, 3]
    field[2, 3] += epsilon * maxwell * wave * sp.diff(axial_one_form, theta)
    field[3, 2] = -field[2, 3]
    source_metric, source_maxwell = _source_rows(
        metric=metric,
        inverse=inverse,
        connection=connection,
        field=field,
        coordinates=coordinates,
        epsilon=epsilon,
    )
    rows, symbols = _polar_generic_rows()
    eigenvalue = symbols[0]
    target_a, target_mixed, target_c, target_maxwell = symbols[3:]
    target_substitution = {
        eigenvalue: ell * (ell + 1),
        target_a: source_a + sphere_trace_field,
        target_mixed: mixed,
        target_c: source_c - sphere_trace_field,
        target_maxwell: maxwell,
    }
    rows = {name: value.subs(target_substitution) for name, value in rows.items()}
    tracefree = (sp.diff(harmonic, theta, 2) - sp.cot(theta) * first) / 2
    target_metric = sp.zeros(4)
    target_metric[0, 0] = rows["metric_00"] * wave * harmonic
    target_metric[0, 1] = target_metric[1, 0] = rows["metric_01"] * wave * harmonic
    target_metric[1, 1] = rows["metric_11"] * wave * harmonic
    target_metric[0, 2] = target_metric[2, 0] = rows["metric_0a"] * wave * first
    target_metric[1, 2] = target_metric[2, 1] = rows["metric_1a"] * wave * first
    target_metric[2, 2] = wave * (
        rows["sphere_trace"] * harmonic + rows["sphere_tracefree"] * tracefree
    )
    target_metric[3, 3] = sine**2 * wave * (
        rows["sphere_trace"] * harmonic - rows["sphere_tracefree"] * tracefree
    )
    return {
        "symbols": {
            "omega": frequency,
            "k": momentum,
            "coefficients": (source_a, mixed, source_c, sphere_trace_field, maxwell),
        },
        "raw": {
            "coordinates": coordinates,
            "background_metric": metric.subs(epsilon, 0),
            "background_inverse": inverse.subs(epsilon, 0),
            "background_connection": _background_connection(theta),
            "source_metric": source_metric,
            "source_maxwell": source_maxwell,
            "target_metric": target_metric,
            "wave": wave,
        },
    }


def _axial_data(ell: int) -> dict[str, object]:
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
    inverse = sp.diag(-1, 1, 1, sine**-2)
    inverse[0, 3] = inverse[3, 0] = epsilon * h_time * wave * axial_one_form / sine**2
    inverse[1, 3] = inverse[3, 1] = -epsilon * h_space * wave * axial_one_form / sine**2
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
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
    source_metric, source_maxwell = _source_rows(
        metric=metric,
        inverse=inverse,
        connection=connection,
        field=field,
        coordinates=coordinates,
        epsilon=epsilon,
    )
    rows, symbols = _axial_generic_rows()
    lam = symbols["lambda"]
    rows = {name: value.subs(lam, eigenvalue) for name, value in rows.items()}
    tensor_factor = sp.Rational(eigenvalue, 2) * harmonic * sine + sp.cos(theta) * harmonic_prime
    target_metric = sp.zeros(4)
    target_metric[0, 3] = target_metric[3, 0] = rows["metric_t"] * wave * axial_one_form
    target_metric[1, 3] = target_metric[3, 1] = rows["metric_x"] * wave * axial_one_form
    target_metric[2, 3] = target_metric[3, 2] = rows["metric_angular"] * sp.I * wave * tensor_factor
    return {
        "symbols": {
            "frequency": frequency,
            "momentum": momentum,
            "coefficients": (h_time, h_space, q_time, q_space),
        },
        "raw": {
            "coordinates": coordinates,
            "background_metric": metric.subs(epsilon, 0),
            "background_inverse": inverse.subs(epsilon, 0),
            "background_connection": _background_connection(theta),
            "source_metric": source_metric,
            "source_maxwell": source_maxwell,
            "target_metric": target_metric,
            "wave": wave,
        },
    }


def _basis_from_data(data: dict[str, object]) -> dict[str, object]:
    raw = data["raw"]
    assert isinstance(raw, dict)
    coordinates = raw["coordinates"]
    metric = raw["background_metric"]
    inverse = raw["background_inverse"]
    connection = raw["background_connection"]
    source = raw["source_metric"]
    source_maxwell = raw["source_maxwell"]
    target = raw["target_metric"]
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(source, sp.MatrixBase)
    assert isinstance(source_maxwell, sp.MatrixBase)
    assert isinstance(target, sp.MatrixBase)

    first = _covariant_one_cov2(source, coordinates, connection)
    second = _covariant_two_cov2(first, coordinates, connection)
    box_source = sp.Matrix(
        4,
        4,
        lambda a, b: sp.expand(
            sum(inverse[c, d] * second[c][d][a][b] for c in range(4) for d in range(4))
        ),
    )
    trace_source = sp.expand(
        sum(inverse[a, b] * source[a, b] for a in range(4) for b in range(4))
    )
    scalar_first = [sp.diff(trace_source, coordinate) for coordinate in coordinates]
    scalar_second = sp.Matrix(
        4,
        4,
        lambda a, b: sp.expand(
            sp.diff(scalar_first[b], coordinates[a])
            - sum(connection[c][a][b] * scalar_first[c] for c in range(4))
        ),
    )
    box_trace = sp.expand(
        sum(inverse[a, b] * scalar_second[a, b] for a in range(4) for b in range(4))
    )
    principal = (
        box_source / 2 - (metric * box_trace - scalar_second) / 6
    ).applyfunc(sp.expand)

    sine = sp.sin(coordinates[2])
    projector_s = sp.diag(0, 0, 1, 1)
    projector_l = sp.eye(4) - projector_s
    sphere_metric = metric * projector_s
    invariant_tf = _tracefree(sphere_metric, metric, inverse)
    trace_s = sp.expand(
        sum(
            inverse[a, b] * projector_s[b, c] * source[a, c]
            for a in range(4)
            for b in range(4)
            for c in range(4)
        )
    )

    def left_right(left: sp.Matrix, right: sp.Matrix, value: sp.Matrix) -> sp.Matrix:
        return sp.Matrix(
            4,
            4,
            lambda a, b: sp.expand(
                sum(
                    (
                        left[a, c] * right[b, d]
                        + left[b, c] * right[a, d]
                    )
                    * value[c, d]
                    / 2
                    for c in range(4)
                    for d in range(4)
                )
            ),
        )

    epsilon_l = sp.Matrix(
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    )
    epsilon_s = sp.Matrix(
        [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1 / sine], [0, 0, -sine, 0]]
    )
    endomorphisms = [projector_l, projector_s, epsilon_l, epsilon_s]
    algebraic: list[sp.Matrix] = []
    for left, right in itertools.product(endomorphisms, repeat=2):
        algebraic.append(
            _tracefree(left_right(left, right, source), metric, inverse)
        )
    algebraic_scalars = [
        sp.expand(
            sum(
                inverse[a, c] * endomorphism[c, b] * source[a, b]
                for a in range(4)
                for b in range(4)
                for c in range(4)
            )
        )
        for endomorphism in endomorphisms
    ]
    algebraic.extend(
        [(invariant_tf * scalar).applyfunc(sp.expand) for scalar in algebraic_scalars]
    )

    maxwell_lower = metric * source_maxwell
    derivative_m = _covariant_one_covector(maxwell_lower, coordinates, connection)
    derivative_matrix = sp.Matrix(4, 4, lambda a, b: derivative_m[a][b])
    differential: list[sp.Matrix] = []
    for left, right in itertools.product(endomorphisms, repeat=2):
        differential.append(
            _tracefree(left_right(left, right, derivative_matrix), metric, inverse)
        )
    scalars = [
        sp.expand(
            sum(
                inverse[a, c] * endomorphism[c, b] * derivative_matrix[a, b]
                for a in range(4)
                for b in range(4)
                for c in range(4)
            )
        )
        for endomorphism in endomorphisms
    ]
    differential.extend(
        [(invariant_tf * scalar).applyfunc(sp.expand) for scalar in scalars]
    )
    return {
        "data": data,
        "principal": principal,
        "algebraic": algebraic,
        "differential": differential,
        "target": target,
    }


def _basis(ell: int = 2) -> dict[str, object]:
    return _basis_from_data(_polar_data(ell))


def _axial_basis(ell: int = 2) -> dict[str, object]:
    return _basis_from_data(_axial_data(ell))


def _simple_coefficients() -> list[sp.Expr]:
    return [
        3,
        sp.Rational(3, 2), -1, 0, 0,
        0, sp.Rational(-5, 2), 0, 0,
        0, 0, sp.Rational(-1, 2), 0,
        0, 0, 0, sp.Rational(5, 2),
        0, 0, 0, 0,
        0, 0, 0, 3,
        0, 0, 0, 3,
        0, 0, 0, 0,
        -3, -3, 0, 0,
        0, 0, 0, 0,
    ]


def _candidate_output(payload: dict[str, object]) -> sp.Matrix:
    candidates = [payload["principal"], *payload["algebraic"], *payload["differential"]]
    coefficients = _simple_coefficients()
    assert len(candidates) == len(coefficients) == 41
    return sum(
        (coefficient * candidate for coefficient, candidate in zip(coefficients, candidates)),
        sp.zeros(4),
    ).applyfunc(sp.expand)


def _axial_check(ell: int = 2) -> None:
    payload = _axial_basis(ell)
    data = payload["data"]
    raw = data["raw"]
    symbols = data["symbols"]
    assert isinstance(raw, dict) and isinstance(symbols, dict)
    target = payload["target"]
    assert isinstance(target, sp.MatrixBase)
    defect = (_candidate_output(payload) - target).applyfunc(sp.expand)
    wave = raw["wave"]
    coordinates = raw["coordinates"]
    coefficients = symbols["coefficients"]
    frequency = symbols["frequency"]
    momentum = symbols["momentum"]
    assert isinstance(wave, sp.Expr) and isinstance(coordinates, tuple)
    assert isinstance(coefficients, tuple)
    theta = coordinates[2]
    samples = [
        {momentum: 1, frequency: 2, theta: sp.pi / 3},
        {momentum: 2, frequency: 3, theta: sp.pi / 4},
    ]
    failures: list[tuple[int, int, int, sp.Expr]] = []
    for sample_index, sample in enumerate(samples):
        for coefficient in coefficients:
            substitution = {
                **sample,
                **{item: int(item == coefficient) for item in coefficients},
            }
            for a in range(4):
                for b in range(a, 4):
                    value = sp.factor(sp.cancel(defect[a, b] / wave).subs(substitution))
                    if value != 0:
                        failures.append((sample_index, a, b, value))
    print(f"axial ell={ell} failures={len(failures)}")
    if failures:
        print(failures[:20])


def _axial_linear_system(ell: int = 2) -> tuple[sp.Matrix, sp.Matrix]:
    payload = _axial_basis(ell)
    data = payload["data"]
    raw = data["raw"]
    symbols = data["symbols"]
    assert isinstance(raw, dict) and isinstance(symbols, dict)
    candidates = [payload["principal"], *payload["algebraic"], *payload["differential"]]
    target = payload["target"]
    assert isinstance(target, sp.MatrixBase)
    wave = raw["wave"]
    coordinates = raw["coordinates"]
    coefficients = symbols["coefficients"]
    frequency = symbols["frequency"]
    momentum = symbols["momentum"]
    assert isinstance(wave, sp.Expr) and isinstance(coordinates, tuple)
    assert isinstance(coefficients, tuple)
    theta = coordinates[2]
    rows: list[list[sp.Expr]] = []
    values: list[sp.Expr] = []
    samples = [
        {momentum: 1, frequency: 2, theta: sp.pi / 3},
        {momentum: 2, frequency: 3, theta: sp.pi / 4},
    ]
    for sample in samples:
        for coefficient in coefficients:
            substitution = {
                **sample,
                **{item: int(item == coefficient) for item in coefficients},
            }
            for a in range(4):
                for b in range(a, 4):
                    row = [
                        sp.factor(sp.cancel(candidate[a, b] / wave).subs(substitution))
                        for candidate in candidates
                    ]
                    value = sp.factor(sp.cancel(target[a, b] / wave).subs(substitution))
                    if any(item != 0 for item in row) or value != 0:
                        rows.append(row)
                        values.append(value)
    return sp.Matrix(rows), sp.Matrix(values)


def _symbolic_defect(ell: int, *, axial: bool) -> list[tuple[int, int, sp.Expr]]:
    payload = _axial_basis(ell) if axial else _basis(ell)
    data = payload["data"]
    raw = data["raw"]
    assert isinstance(raw, dict)
    target = payload["target"]
    assert isinstance(target, sp.MatrixBase)
    defect = (_candidate_output(payload) - target).applyfunc(sp.expand)
    wave = raw["wave"]
    coordinates = raw["coordinates"]
    assert isinstance(wave, sp.Expr) and isinstance(coordinates, tuple)
    theta = coordinates[2]
    failures: list[tuple[int, int, sp.Expr]] = []
    for a in range(4):
        for b in range(a, 4):
            value = _separate(
                sp.trigsimp(sp.expand_trig(defect[a, b] / wave), method="fu"),
                theta,
            )
            value = sp.factor(
                sp.trigsimp(sp.expand_trig(value), method="fu")
            )
            if value != 0:
                failures.append((a, b, value))
    return failures


def _identity_fit(ell: int = 2) -> tuple[sp.Matrix, sp.Matrix, list[sp.Expr]]:
    t, x, theta, phi = sp.symbols("t x theta phi", real=True)
    coordinates = (t, x, theta, phi)
    omega, momentum = sp.symbols("omega k", real=True)
    wave = sp.exp(sp.I * (momentum * x - omega * t))
    harmonic = sp.legendre(ell, sp.cos(theta))
    first_harmonic = sp.diff(harmonic, theta)
    sine = sp.sin(theta)
    metric = sp.diag(-1, 1, 1, sine**2)
    inverse = sp.diag(-1, 1, 1, sine**-2)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    connection[2][3][3] = -sine * sp.cos(theta)
    connection[3][2][3] = connection[3][3][2] = sp.cot(theta)

    coefficients = sp.symbols("e00 e01 e11 ep0 ea0 ep1 ea1 et esf esa m0 m1 mp ma")
    e00, e01, e11, ep0, ea0, ep1, ea1, et, esf, esa, m0, m1, mp, ma = coefficients
    source = sp.zeros(4)
    source[0, 0] = e00 * wave * harmonic
    source[0, 1] = source[1, 0] = e01 * wave * harmonic
    source[1, 1] = e11 * wave * harmonic
    source[0, 2] = source[2, 0] = ep0 * wave * first_harmonic
    source[0, 3] = source[3, 0] = ea0 * wave * (-sine * first_harmonic)
    source[1, 2] = source[2, 1] = ep1 * wave * first_harmonic
    source[1, 3] = source[3, 1] = ea1 * wave * (-sine * first_harmonic)
    source[2, 2] = wave * (
        et * harmonic
        + esf * (sp.diff(harmonic, theta, 2) + ell * (ell + 1) * harmonic / 2)
    )
    source[3, 3] = wave * (
        et * sine**2 * harmonic
        + esf * (-sine * sp.cos(theta) * first_harmonic + ell * (ell + 1) * sine**2 * harmonic / 2)
    )
    axial_sphere = sp.diff(-sine * first_harmonic, theta) - sp.cot(theta) * (-sine * first_harmonic)
    source[2, 3] = source[3, 2] = esa * wave * axial_sphere / 2

    maxwell_lower = sp.Matrix([
        m0 * wave * harmonic,
        m1 * wave * harmonic,
        mp * wave * first_harmonic,
        ma * wave * (-sine * first_harmonic),
    ])
    source_maxwell = inverse * maxwell_lower
    data = {
        "raw": {
            "coordinates": coordinates,
            "background_metric": metric,
            "background_inverse": inverse,
            "background_connection": connection,
            "source_metric": source,
            "source_maxwell": source_maxwell,
            "target_metric": sp.zeros(4),
        }
    }
    payload = _basis_from_data(data)
    output = _candidate_output(payload)

    def divergence_cov2(value: sp.Matrix) -> sp.Matrix:
        derivative = _covariant_one_cov2(value, coordinates, connection)
        return sp.Matrix([
            sp.expand(
                sum(inverse[a, c] * derivative[c][a][b] for a in range(4) for c in range(4))
            )
            for b in range(4)
        ])

    derivative_m = _covariant_one_covector(maxwell_lower, coordinates, connection)
    divergence_m = sp.expand(
        sum(inverse[a, b] * derivative_m[a][b] for a in range(4) for b in range(4))
    )
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    lorentz_force = field * source_maxwell
    source_identity = (divergence_cov2(source) + lorentz_force).applyfunc(sp.expand)
    target_identity = (divergence_cov2(output) + lorentz_force).applyfunc(sp.expand)

    identity_first = _covariant_one_covector(source_identity, coordinates, connection)
    # Compute the rough covector Laplacian directly.
    second_identity = [
        [
            [
                sp.expand(
                    sp.diff(identity_first[d][b], coordinates[c])
                    - sum(
                        connection[r][c][d] * identity_first[r][b]
                        + connection[r][c][b] * identity_first[d][r]
                        for r in range(4)
                    )
                )
                for b in range(4)
            ]
            for d in range(4)
        ]
        for c in range(4)
    ]
    box_identity = sp.Matrix([
        sp.expand(
            sum(inverse[c, d] * second_identity[c][d][b] for c in range(4) for d in range(4))
        )
        for b in range(4)
    ])
    projector_s = sp.diag(0, 0, 1, 1)
    projector_l = sp.eye(4) - projector_s
    epsilon_l = sp.Matrix([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    epsilon_s = sp.Matrix([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1 / sine], [0, 0, -sine, 0]])
    endomorphisms = [projector_l, projector_s, epsilon_l, epsilon_s]
    gradient_divergence_m = sp.Matrix([sp.diff(divergence_m, coordinate) for coordinate in coordinates])
    candidates = [box_identity]
    candidates.extend((endomorphism * source_identity).applyfunc(sp.expand) for endomorphism in endomorphisms)
    candidates.extend((endomorphism * gradient_divergence_m).applyfunc(sp.expand) for endomorphism in endomorphisms)

    rows: list[list[sp.Expr]] = []
    values: list[sp.Expr] = []
    samples = [
        {momentum: 1, omega: 2, theta: sp.pi / 3},
        {momentum: 2, omega: 3, theta: sp.pi / 4},
    ]
    for sample in samples:
        for coefficient in coefficients:
            substitution = {**sample, **{item: int(item == coefficient) for item in coefficients}}
            for b in range(4):
                row = [sp.factor(sp.cancel(item[b] / wave).subs(substitution)) for item in candidates]
                value = sp.factor(sp.cancel(target_identity[b] / wave).subs(substitution))
                if any(item != 0 for item in row) or value != 0:
                    rows.append(row)
                    values.append(value)
    return sp.Matrix(rows), sp.Matrix(values), candidates


def _linear_system(ell: int = 2) -> tuple[sp.Matrix, sp.Matrix]:
    payload = _basis(ell)
    data = payload["data"]
    assert isinstance(data, dict)
    raw = data["raw"]
    assert isinstance(raw, dict)
    symbols = data["symbols"]
    assert isinstance(symbols, dict)
    omega, momentum = symbols["omega"], symbols["k"]
    coefficients = symbols["coefficients"]
    wave = raw["wave"]
    coordinates = raw["coordinates"]
    assert isinstance(coefficients, tuple)
    assert isinstance(wave, sp.Expr)
    assert isinstance(coordinates, tuple)
    theta = coordinates[2]
    candidates = [payload["principal"], *payload["algebraic"], *payload["differential"]]
    target = payload["target"]
    assert isinstance(target, sp.MatrixBase)
    unknown_count = len(candidates)
    equations: list[list[sp.Expr]] = []
    values: list[sp.Expr] = []
    substitutions = [
        {momentum: 1, omega: 2, theta: sp.pi / 6},
        {momentum: 2, omega: 3, theta: sp.pi / 3},
        {momentum: 3, omega: 1, theta: sp.pi / 4},
    ]
    for substitution in substitutions:
        for coefficient in coefficients:
            field_substitution = {item: int(item == coefficient) for item in coefficients}
            combined = {**substitution, **field_substitution}
            for a in range(4):
                for b in range(a, 4):
                    row = [
                        sp.factor(sp.cancel(candidate[a, b] / wave).subs(combined))
                        for candidate in candidates
                    ]
                    value = sp.factor(sp.cancel(target[a, b] / wave).subs(combined))
                    if any(item != 0 for item in row) or value != 0:
                        equations.append(row)
                        values.append(value)
    matrix = sp.Matrix(equations)
    vector = sp.Matrix(values)
    print(f"ell={ell} equations={matrix.rows} unknowns={unknown_count}")
    return matrix, vector


def _operator_formula() -> dict[str, Any]:
    return {
        "parallel_tensors": {
            "L": "orthogonal projector onto the Lorentzian M2 factor",
            "S": "orthogonal projector onto the spherical S2 factor; L+S=I",
            "J_L": "mixed-index oriented Lorentzian volume form",
            "J_S": "mixed-index oriented spherical volume form, equal to the background magnetic F_a^b",
        },
        "symmetrized_action": "B(A,B;X)_ab=(A_a^c B_b^d+A_b^c B_a^d)X_cd/2",
        "tracefree_projection": "TF(X)_ab=X_ab-g_ab tr(X)/4",
        "source_rows": {
            "E_ab": "delta(G_ab+Lambda g_ab-T_ab)",
            "M^a": "delta(nabla_b F^{ba})",
        },
        "principal": "P(E)_ab=(Box E_ab)/2-(g_ab Box-nabla_a nabla_b)tr(E)/6",
        "metric_equation_map": (
            "W_ab=3 P(E)_ab+TF[3 B(L,L;E)/2-B(L,S;E)-5 B(S,S;E)/2"
            "-B(J_L,J_L;E)/2+5 B(J_S,J_S;E)/2"
            "+3 B(I,J_S;nabla M)-3 B(J_S,I;nabla M)]_ab"
        ),
        "maxwell_equation_map": "M^a maps identically",
        "source_identities": {
            "I_b": "nabla^a E_ab+F_bar_bc M^c",
            "J": "nabla_a M^a",
        },
        "identity_map": {
            "diff": "I'_b=3 Box I_b/2+(L_b^c-S_b^c/2)I_c-3 (J_S)_b^c nabla_c J/2",
            "u1": "J'=J",
            "weyl_trace": "0",
        },
        "ghost_map": "identity on Diff x U(1), followed by zero in the new Weyl-ghost component",
        "field_map": "identity on the common metric and fixed-bundle Maxwell potential",
        "operator_orders": {"metric_from_E": 2, "metric_from_M": 1, "maxwell": 0, "diff_identity": 2},
        "support_local": True,
        "uses_inverse_laplacian_curl_frequency_or_momentum": False,
    }


def build_heavy_proof() -> dict[str, Any]:
    polar_matrix, polar_vector = _linear_system(2)
    axial_matrix, axial_vector = _axial_linear_system(2)
    combined_matrix = polar_matrix.col_join(axial_matrix)
    combined_vector = polar_vector.col_join(axial_vector)
    coefficients = sp.Matrix(_simple_coefficients())
    _require(
        combined_matrix * coefficients == combined_vector,
        "simple covariant coefficient representative failed the combined fit",
    )
    polar_rank = polar_matrix.rank()
    axial_rank = axial_matrix.rank()
    combined_rank = combined_matrix.rank()
    _require(polar_rank == polar_matrix.row_join(polar_vector).rank(), "polar fit inconsistent")
    _require(axial_rank == axial_matrix.row_join(axial_vector).rank(), "axial fit inconsistent")
    _require(combined_rank == combined_matrix.row_join(combined_vector).rank(), "combined fit inconsistent")
    _require(combined_rank == 26, "combined invariant-fit rank changed")

    identity_matrix, identity_vector, _ = _identity_fit(2)
    identity_coefficients = sp.Matrix(
        [sp.Rational(3, 2), 1, sp.Rational(-1, 2), 0, 0, 0, 0, 0, sp.Rational(-3, 2)]
    )
    _require(identity_matrix * identity_coefficients == identity_vector, "identity-map coefficients failed")
    identity_rank = identity_matrix.rank()
    _require(identity_rank == identity_matrix.row_join(identity_vector).rank() == 9, "identity fit lost uniqueness")

    replays: dict[str, Any] = {}
    for ell in (2, 3, 4):
        for axial in (True, False):
            failures = _symbolic_defect(ell, axial=axial)
            _require(not failures, f"symbolic {'axial' if axial else 'polar'} ell={ell} defect survived: {failures[:2]}")
            replays[f"{'axial' if axial else 'polar'}_ell{ell}"] = {
                "all_ten_symmetric_tensor_components": "0",
                "off_shell_frequency_momentum_retained": True,
            }
    return {
        "schema": "einstein-weyl-compact-product-covariant-chain-map-proof-v1",
        "result_id": "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_PROOF_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "producer": {
            "path": str(Path(__file__).relative_to(ROOT)),
            "sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "invariant_ansatz": {
            "candidate_count": 41,
            "principal_candidates": 1,
            "parallel_algebraic_candidates": 20,
            "first_derivative_Maxwell_candidates": 20,
            "endomorphism_basis": ["L", "S", "J_L", "J_S"],
            "polar_rank": polar_rank,
            "polar_augmented_rank": polar_rank,
            "axial_rank": axial_rank,
            "axial_augmented_rank": axial_rank,
            "combined_rank": combined_rank,
            "combined_augmented_rank": combined_rank,
            "coefficient_vector": [str(value) for value in coefficients],
            "chosen_representative_exact": True,
        },
        "identity_fit": {
            "candidate_count": 9,
            "rank": identity_rank,
            "augmented_rank": identity_rank,
            "coefficient_vector": [str(value) for value in identity_coefficients],
            "unique": True,
        },
        "symbolic_action_replays": replays,
        "spectral_globalization": {
            "degree_bound_in_lambda": 2,
            "nodes": [6, 12, 20],
            "argument": "both sides are natural order-four product-equivariant tensor operators and hence each harmonic coefficient is polynomial of degree at most two in lambda; exact ell=2,3,4 equality globalizes to every spherical harmonic",
            "all_m": "SO(3) equivariance",
            "all_compact_k_and_off_shell_omega": True,
        },
        "formula": _operator_formula(),
    }


def build_certificate() -> dict[str, Any]:
    proof = _load(PROOF)
    _require(
        proof.get("result_id") == "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_PROOF_V1",
        "heavy proof changed",
    )
    _require(proof["invariant_ansatz"]["combined_rank"] == proof["invariant_ansatz"]["combined_augmented_rank"] == 26, "fit proof changed")
    _require(proof["identity_fit"]["rank"] == proof["identity_fit"]["augmented_rank"] == 9, "identity proof changed")
    _require(len(proof["symbolic_action_replays"]) == 6, "symbolic replay coverage changed")
    inputs = {name: _load(path) for name, path in INPUTS.items()}
    expected_ids = {
        "background": "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
        "principal_preflight": "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT",
        "source_axial": "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "source_polar": "COMPACT_EM_POLAR_MASTER_COMPLEX",
        "target_axial_tensor": "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_FULL_TENSOR",
        "target_polar_tensor": "EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR",
        "exceptional_maps": "EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1",
    }
    for name, expected in expected_ids.items():
        _require(inputs[name].get("result_id") == expected, f"{name} input changed")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "einstein-weyl-compact-product-covariant-chain-map-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1",
        "result_state": "NATURAL_SUPPORT_LOCAL_ALL_ROW_MINIMAL_CHAIN_MAP_CERTIFIED_NONCYCLIC_TRIANGLE_ENDPOINTS_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact magnetic Plebanski-Hacyan product R_t x S1 x S2 at the rational common fixture",
            "boundaries": "smooth fixed magnetic bundle; identity-component local gauge complex",
            "carrier": "four-dimensional minimal Diff x U(1) equation complex into minimal Diff x U(1) x Weyl equation complex",
            "harmonics": "all ell,m and compact k by naturality and exact polynomial globalization",
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "heavy_proof": {"path": str(PROOF.relative_to(ROOT)), "sha256": _sha256(PROOF)},
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "chain_map": _operator_formula(),
        "exact_identities": {
            "ghost_field": "K_WM i_ghost=i_field K_EM",
            "field_equation": "H_WM i_field=Q_equation H_EM",
            "equation_identity": "N_WM Q_equation=Q_identity N_EM",
            "target_trace": "tr(W)=0",
            "maxwell_row": "identity",
            "all_symbolic_defects": "0",
        },
        "coverage": {
            "generic_axial_and_polar": "CERTIFIED_BY_NATURAL_TENSOR_FORMULA",
            "exceptional_ell1": "CERTIFIED_BY_POLYNOMIAL_GLOBALIZATION_AND_IMPORTED_DIRECT_TABLES",
            "homogeneous_ell0": "CERTIFIED_AT_LOCAL_TENSOR_LEVEL; finite residual/large-gauge endpoint rows remain separate",
            "spectral_projector_used": False,
            "support_local": True,
        },
        "classification": {
            "single_covariant_support_local_map_reconstructed": True,
            "full_curved_minimal_local_chain_map_certified": True,
            "harmonic_row_selection_eliminated": True,
            "noncyclic_three_form_triangle_completed": False,
            "standard_pairing_cyclic_map_exists": False,
            "standard_pairing_cyclic_map_obstructed_by_imported_inertia": True,
            "finite_large_gauge_and_residual_endpoints_included": False,
            "causal_nonlinear_observational_or_quantum_claim": False,
        },
        "next_gate": "add the finite residual/large-gauge endpoint rows and export the Einstein, pulled-back Weyl and relative forms separately as the noncyclic three-form triangle",
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem constructs one natural finite-order support-local chain morphism on the common compact-product tensor bundles and proves all local ghost, field, equation and identity squares. It does not make the map cyclic for the standard action pairings, include finite large-gauge/residual endpoint rows, construct a causal Green map, or imply nonlinear, observational, particle or quantum equivalence.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_compact_product_covariant_chain_map --verify-proof",
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_compact_product_covariant_chain_map --verify bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_weyl_compact_product_covariant_chain_map.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_compact_product_covariant_chain_map -v",
        ],
    }


def verify_proof() -> None:
    _require(_load(PROOF) == build_heavy_proof(), "heavy proof is stale")


def verify_certificate(path: Path = OUTPUT) -> None:
    value = _load(path)
    Draft202012Validator.check_schema(_load(SCHEMA))
    errors = sorted(Draft202012Validator(_load(SCHEMA)).iter_errors(value), key=lambda error: list(error.path))
    _require(not errors, f"schema validation failed: {errors[0].message if errors else ''}")
    _require(value == build_certificate(), f"stale covariant chain-map certificate: {path}")


def _write_report(value: dict[str, Any]) -> None:
    REPORT.write_text(
        """# Compact-product covariant Einstein--Weyl chain map

The formerly separate harmonic coefficient maps are the reductions of one
natural support-local four-dimensional chain morphism.  Its equation row is
the universal Bach-from-Einstein operator plus a parallel algebraic product
correction and a first-order Maxwell commutator.  The induced identity map is
unique in the declared invariant class.  No inverse Laplacian, curl,
frequency, momentum or harmonic projector is used.

The exact symbolic replay covers both parities at three independent spherical
eigenvalues, retains arbitrary off-shell frequency and compact momentum, and
globalizes by the degree-two natural-operator bound and SO(3) equivariance.

This closes the local covariant-glue gate, not the entire relative triangle.
The standard action pairings remain noncyclic by the separately certified
inertia obstruction.  Finite residual and large-gauge endpoint rows and the
three distinct Einstein/pulled-back-Weyl/relative forms remain the next gate.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--heavy-write", action="store_true")
    parser.add_argument("--verify-proof", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.heavy_write:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(build_heavy_proof(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify_proof:
        verify_proof()
    if args.write:
        value = build_certificate()
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write_report(value)
    if args.verify:
        verify_certificate(args.verify)
    if not any((args.heavy_write, args.verify_proof, args.write, args.verify)):
        parser.error("one of --heavy-write, --verify-proof, --write, or --verify is required")


if __name__ == "__main__":
    main()
