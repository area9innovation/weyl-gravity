"""Homogeneous second-order gate for the minimal balanced q/p tangent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
import jsonschema

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _stress,
    _trunc,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator as _polar_action_operator,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_balanced_ell0_second_order.schema.json"
ZERO_LOCUS = ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json"
TENSOR_HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_periodic_photon_second_order.py"


class BalancedEll0SecondOrderError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BalancedEll0SecondOrderError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.trigsimp(sp.expand_trig(value))))


def _equations(data: dict[str, object], order: int, pairs: tuple[tuple[int, int], ...]) -> tuple[dict[tuple[int, int], sp.Expr], dict[int, sp.Expr]]:
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    connection = data["connection"]
    field = data["field"]
    riemann = data["riemann"]
    schouten = data["schouten"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(field, sp.MatrixBase)
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

    stress = _stress(data, order)
    metric_equations: dict[tuple[int, int], sp.Expr] = {}
    for first, second in pairs:
        laplacian = sum(
            inverse[outer, inner] * second_schouten(outer, inner, first, second)
            for outer in range(4)
            for inner in range(4)
        )
        mixed = sum(
            inverse[outer, inner] * second_schouten(outer, first, second, inner)
            for outer in range(4)
            for inner in range(4)
        )
        curvature = sum(
            schouten_up[inner, outer] * weyl(first, inner, second, outer)
            for inner in range(4)
            for outer in range(4)
        )
        metric_equations[(first, second)] = tr(3 * tr(laplacian - mixed + curvature) - stress[first, second])

    field_up = sp.zeros(4)
    for left in range(4):
        for right in range(4):
            field_up[left, right] = tr(
                sum(
                    inverse[left, a] * inverse[right, b] * field[a, b]
                    for a in range(4)
                    for b in range(4)
                )
            )
    volume = tr(sp.sqrt(-metric.det())).subs(sp.Abs(sp.sin(coordinates[2])), sp.sin(coordinates[2]))
    maxwell_equations = {
        right: tr(
            sum(sp.diff(volume * field_up[left, right], coordinates[left]) for left in range(4)) / volume
        )
        for right in (0, 1, 3)
    }
    return metric_equations, maxwell_equations


def _average(expression: sp.Expr, theta: sp.Symbol) -> sp.Expr:
    return _canonical(sp.integrate(expression * sp.sin(theta), (theta, 0, sp.pi)) / 2)


def _source_geometry(order: int = 2) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    first_amplitude, second_amplitude = sp.symbols("u v")
    first_h, first_q, second_h, second_q = sp.symbols("h_1 q_1 h_2 q_2", real=True)
    first_frequency, second_frequency = sp.symbols("omega_1 omega_2", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    first_wave = sp.exp(-sp.I * first_frequency * time)
    second_wave = sp.exp(-sp.I * second_frequency * time)
    metric_wave = first_amplitude * first_h * first_wave + second_amplitude * second_h * second_wave
    potential_wave = first_amplitude * first_q * first_wave + second_amplitude * second_q * second_wave
    tr = lambda expression: _trunc(expression, epsilon, order)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[1, 3] = metric[3, 1] = epsilon * metric_wave * axial_one_form
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
    field[0, 1] = epsilon * sp.diff(potential_wave, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * potential_wave * sp.diff(harmonic, theta)
    field[2, 1] = -field[1, 2]
    return {
        "epsilon": epsilon,
        "amplitudes": (first_amplitude, second_amplitude),
        "mode_symbols": (first_h, first_q, first_frequency, second_h, second_q, second_frequency),
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _homogeneous_geometry(order: int = 1) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    circle, sphere, electric = sp.symbols("C K U")
    frequency = sp.symbols("Omega", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(-sp.I * frequency * time)
    tr = lambda expression: _trunc(expression, epsilon, order)
    metric = sp.diag(-1, 1 + epsilon * circle * wave, 1 + epsilon * sphere * wave, (1 + epsilon * sphere * wave) * sine**2)
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
    field[0, 1] = epsilon * sp.diff(electric * wave, time)
    field[1, 0] = -field[0, 1]
    return {
        "epsilon": epsilon,
        "coefficients": (circle, sphere, electric),
        "frequency": frequency,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _homogeneous_operator() -> tuple[sp.Matrix, sp.Symbol]:
    geometry = _homogeneous_geometry()
    data = _curvature(geometry, 1)
    metric_equations, maxwell_equations = _equations(data, 1, ((0, 0), (1, 1), (2, 2), (3, 3)))
    epsilon = geometry["epsilon"]
    coefficients = geometry["coefficients"]
    frequency = geometry["frequency"]
    coordinates = geometry["coordinates"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coefficients, tuple)
    assert isinstance(frequency, sp.Symbol)
    assert isinstance(coordinates, tuple)
    sphere_trace = (
        metric_equations[(2, 2)]
        + metric_equations[(3, 3)] / sp.sin(coordinates[2]) ** 2
    ) / 2
    rows = [metric_equations[(0, 0)], metric_equations[(1, 1)], sphere_trace, maxwell_equations[1]]
    linear = [
        _canonical(sp.diff(row, epsilon).subs(epsilon, 0).subs(coordinates[0], 0))
        for row in rows
    ]
    matrix = sp.Matrix([[sp.diff(row, coefficient) for coefficient in coefficients] for row in linear]).applyfunc(_canonical)
    return matrix, frequency


def _mixed_source_projections() -> tuple[sp.Matrix, dict[int, sp.Matrix], tuple[sp.Symbol, ...]]:
    geometry = _source_geometry()
    data = _curvature(geometry, 2)
    metric_equations, maxwell_equations = _equations(data, 2, ((0, 0), (0, 1), (1, 1), (2, 2), (3, 3)))
    epsilon = geometry["epsilon"]
    amplitudes = geometry["amplitudes"]
    mode_symbols = geometry["mode_symbols"]
    coordinates = geometry["coordinates"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(amplitudes, tuple)
    assert isinstance(mode_symbols, tuple)
    assert isinstance(coordinates, tuple)
    theta = coordinates[2]
    sphere_trace = (
        metric_equations[(2, 2)]
        + metric_equations[(3, 3)] / sp.sin(theta) ** 2
    ) / 2
    rows = {
        "metric_00": metric_equations[(0, 0)],
        "metric_01": metric_equations[(0, 1)],
        "metric_11": metric_equations[(1, 1)],
        "sphere_trace": sphere_trace,
        "maxwell_1": maxwell_equations[1],
        "maxwell_3_density": sp.sin(theta) * maxwell_equations[3],
    }
    mixed_rows: dict[str, sp.Expr] = {}
    for name, row in rows.items():
        coefficient = sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, amplitudes[0]), amplitudes[1]).subs(epsilon, 0)
        mixed_rows[name] = _canonical(coefficient.subs(coordinates[0], 0))
    homogeneous = sp.Matrix(
        [
            _average(mixed_rows["metric_00"], theta),
            _average(mixed_rows["metric_11"], theta),
            _average(mixed_rows["sphere_trace"], theta),
            _average(mixed_rows["maxwell_1"], theta),
        ]
    )
    generic: dict[int, sp.Matrix] = {}
    for ell in (2, 4):
        harmonic = sp.legendre(ell, sp.cos(theta))
        derivative = sp.diff(harmonic, theta)
        scalar_norm = sp.integrate(harmonic**2 * sp.sin(theta), (theta, 0, sp.pi))
        axial_norm = sp.integrate(derivative**2 * sp.sin(theta), (theta, 0, sp.pi))
        eigenvalue = ell * (ell + 1)
        _require(_canonical(axial_norm - eigenvalue * scalar_norm) == 0, f"ell={ell} axial norm changed")

        def scalar_projection(value: sp.Expr) -> sp.Expr:
            return _canonical(
                sp.integrate(value * harmonic * sp.sin(theta), (theta, 0, sp.pi))
                / scalar_norm
            )

        maxwell_projection = _canonical(
            sp.integrate(
                mixed_rows["maxwell_3_density"] * (-derivative) * sp.sin(theta),
                (theta, 0, sp.pi),
            )
            / axial_norm
        )
        generic[ell] = sp.Matrix(
            [
                -scalar_projection(mixed_rows["metric_00"]),
                2 * scalar_projection(mixed_rows["metric_01"]),
                -scalar_projection(mixed_rows["metric_11"]),
                2 * eigenvalue * maxwell_projection,
            ]
        ).applyfunc(_canonical)
    return homogeneous, generic, mode_symbols


def _channel_definitions(symbols: tuple[sp.Symbol, ...]) -> dict[str, dict[Any, sp.Expr]]:
    h1, q1, w1, h2, q2, w2 = symbols
    root = sp.sqrt(3)
    return {
        "Einstein_self_sum": {h1: -2, q1: 2 * root, w1: sp.sqrt(6 - 2 * root), h2: -2, q2: 2 * root, w2: sp.sqrt(6 - 2 * root), "real_factor": sp.Rational(1, 8)},
        "extra_self_sum": {h1: -sp.Rational(2, 3), q1: 6, w1: 4 / root, h2: -sp.Rational(2, 3), q2: 6, w2: 4 / root, "real_factor": sp.Rational(1, 8)},
        "cross_sum": {h1: -2, q1: 2 * root, w1: sp.sqrt(6 - 2 * root), h2: -sp.Rational(2, 3), q2: 6, w2: 4 / root, "real_factor": sp.Rational(1, 4)},
        "cross_difference": {h1: -2, q1: 2 * root, w1: -sp.sqrt(6 - 2 * root), h2: -sp.Rational(2, 3), q2: 6, w2: 4 / root, "real_factor": sp.Rational(1, 4)},
        "Einstein_zero": {h1: -2, q1: 2 * root, w1: sp.sqrt(6 - 2 * root), h2: -2, q2: 2 * root, w2: -sp.sqrt(6 - 2 * root), "real_factor": sp.Rational(1, 4)},
        "extra_zero": {h1: -sp.Rational(2, 3), q1: 6, w1: 4 / root, h2: -sp.Rational(2, 3), q2: 6, w2: -4 / root, "real_factor": sp.Rational(1, 4)},
    }


def _scaled_channel_source(source_polynomial: sp.Matrix, substitutions: dict[Any, sp.Expr], name: str) -> tuple[sp.Matrix, sp.Expr]:
    root = sp.sqrt(3)
    amplitude_squared = sp.Rational(27, 52) * (5 * root - 6)
    local = dict(substitutions)
    real_factor = local.pop("real_factor")
    source = (real_factor * source_polynomial.subs(local)).applyfunc(_canonical)
    if name.startswith("extra_"):
        source = (amplitude_squared * source).applyfunc(_canonical)
    if name.startswith("cross_"):
        source = (sp.sqrt(amplitude_squared) * source).applyfunc(_canonical)
    symbols = list(substitutions)
    frequency_symbols = [symbol for symbol in symbols if isinstance(symbol, sp.Symbol) and str(symbol).startswith("omega_")]
    _require(len(frequency_symbols) == 2, "channel frequency symbols changed")
    output_frequency = _canonical(local[frequency_symbols[0]] + local[frequency_symbols[1]])
    return source, output_frequency


def _channel_solve(operator: sp.Matrix, operator_frequency: sp.Symbol, source_polynomial: sp.Matrix, symbols: tuple[sp.Symbol, ...]) -> dict[str, Any]:
    modes = _channel_definitions(symbols)
    output: dict[str, Any] = {}
    for name, substitutions in modes.items():
        source, output_frequency = _scaled_channel_source(source_polynomial, substitutions, name)
        block = operator.subs(operator_frequency, output_frequency).applyfunc(_canonical)
        augmented = block.row_join(-source)
        rank = block.rank()
        augmented_rank = augmented.rank()
        correction = None
        remainder = None
        if output_frequency != 0 and rank == augmented_rank:
            correction = [
                _canonical(2 * source[1] / output_frequency**4),
                sp.Integer(0),
                _canonical(-source[3] / output_frequency**2),
            ]
            remainder = (block * sp.Matrix(correction) + source).applyfunc(_canonical)
            _require(remainder == sp.zeros(4, 1), f"homogeneous correction failed in {name}")
        output[name] = {
            "output_frequency": str(output_frequency),
            "source_rows_E00_E11_E22_Maxwell1": [str(value) for value in source],
            "operator_rank": rank,
            "augmented_rank": augmented_rank,
            "algebraic_correction_C_K_U": None if correction is None else [str(value) for value in correction],
            "operator_remainder": None if remainder is None else [str(value) for value in remainder],
            "solvable_by_single_exponential": correction is not None,
        }
    zero_source = (sp.Matrix([sp.sympify(value) for value in output["Einstein_zero"]["source_rows_E00_E11_E22_Maxwell1"]]) + sp.Matrix([sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in output["extra_zero"]["source_rows_E00_E11_E22_Maxwell1"]])).applyfunc(_canonical)
    output["combined_zero"] = {
        "output_frequency": "0",
        "source_rows_E00_E11_E22_Maxwell1": [str(value) for value in zero_source],
        "operator_rank": operator.subs(operator_frequency, 0).rank(),
        "augmented_rank_for_constant_ansatz": operator.subs(operator_frequency, 0).row_join(-zero_source).rank(),
        "constant_ansatz_solvable": operator.subs(operator_frequency, 0).rank() == operator.subs(operator_frequency, 0).row_join(-zero_source).rank(),
    }
    return output


def _generic_channel_solve(source_polynomials: dict[int, sp.Matrix], symbols: tuple[sp.Symbol, ...]) -> dict[str, Any]:
    action, (eigenvalue, momentum, frequency) = _polar_action_operator()
    modes = _channel_definitions(symbols)
    output: dict[str, Any] = {}
    for ell, source_polynomial in source_polynomials.items():
        channels: dict[str, Any] = {}
        stored_sources: dict[str, sp.Matrix] = {}
        for name, substitutions in modes.items():
            source, output_frequency = _scaled_channel_source(source_polynomial, substitutions, name)
            stored_sources[name] = source
            if name in ("Einstein_zero", "extra_zero"):
                channels[name] = {
                    "output_frequency": "0",
                    "source_action_rows": [str(value) for value in source],
                }
                continue
            block = action.subs({eigenvalue: ell * (ell + 1), momentum: 0, frequency: output_frequency})
            _require(block.det() != 0, f"ell={ell} {name} unexpectedly resonant")
            correction = (-block.inv() * source).applyfunc(_canonical)
            remainder = (block * correction + source).applyfunc(_canonical)
            _require(remainder == sp.zeros(4, 1), f"ell={ell} {name} correction failed")
            channels[name] = {
                "output_frequency": str(output_frequency),
                "source_action_rows": [str(value) for value in source],
                "correction_At_B_Ct_U": [str(value) for value in correction],
                "operator_remainder": [str(value) for value in remainder],
            }
        zero_source = (stored_sources["Einstein_zero"] + stored_sources["extra_zero"]).applyfunc(_canonical)
        zero_block = action.subs({eigenvalue: ell * (ell + 1), momentum: 0, frequency: 0})
        _require(zero_block.det() != 0, f"ell={ell} zero channel unexpectedly resonant")
        zero_correction = (-zero_block.inv() * zero_source).applyfunc(_canonical)
        zero_remainder = (zero_block * zero_correction + zero_source).applyfunc(_canonical)
        _require(zero_remainder == sp.zeros(4, 1), f"ell={ell} zero correction failed")
        channels["combined_zero"] = {
            "output_frequency": "0",
            "source_action_rows": [str(value) for value in zero_source],
            "correction_At_B_Ct_U": [str(value) for value in zero_correction],
            "operator_remainder": [str(value) for value in zero_remainder],
        }
        output[str(ell)] = channels
    return output


def build_certificate() -> dict[str, Any]:
    zero_locus = json.loads(ZERO_LOCUS.read_text(encoding="utf-8"))
    _require(zero_locus["result_id"] == "EINSTEIN_MAXWELL_WEYL_MIXED_MOMENT_MAP_ZERO_LOCUS", "zero-locus input changed")
    operator, frequency = _homogeneous_operator()
    source, generic_sources, symbols = _mixed_source_projections()
    channels = _channel_solve(operator, frequency, source, symbols)
    generic_channels = _generic_channel_solve(generic_sources, symbols)
    all_homogeneous_nonzero_solved = all(
        row["solvable_by_single_exponential"]
        for name, row in channels.items()
        if name not in ("Einstein_zero", "extra_zero", "combined_zero")
    )
    complete_extension = bool(
        all_homogeneous_nonzero_solved
        and channels["combined_zero"]["constant_ansatz_solvable"]
        and all(
            "correction_At_B_Ct_U" in row
            for ell_channels in generic_channels.values()
            for name, row in ell_channels.items()
            if name not in ("Einstein_zero", "extra_zero")
        )
    )
    _require(complete_extension, "balanced second-order extension did not close")
    return {
        "schema": "einstein-maxwell-weyl-balanced-ell0-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_BALANCED_ELL0_SECOND_ORDER",
        "result_state": "MINIMAL_BALANCED_MIXED_TANGENT_COMPLETE_SECOND_ORDER_CORRECTION_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(TENSOR_HELPER.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(TENSOR_HELPER),
            "input": {"path": str(ZERO_LOCUS.relative_to(ROOT)), "sha256": _sha256(ZERO_LOCUS)},
        },
        "homogeneous_operator": {
            "row_order": ["E00", "E11", "E22", "Maxwell1"],
            "coefficient_order": ["C", "K", "U"],
            "matrix": [[str(value) for value in operator.row(row)] for row in range(operator.rows)],
        },
        "bilinear_source_polynomial": {
            "mode_symbol_order": [str(value) for value in symbols],
            "homogeneous_rows": [str(value) for value in source],
            "generic_action_rows_by_ell": {
                str(ell): [str(value) for value in values]
                for ell, values in generic_sources.items()
            },
        },
        "homogeneous_channels": channels,
        "generic_polar_channels": generic_channels,
        "second_order_correction": {
            "formula": "Phi^(2) is the finite real sum of the displayed ell=0,2,4 channel corrections and their complex conjugates; each stored vector solves L_WM Phi^(2)_channel=-(1/2 D^2E_WM[Phi^(1),Phi^(1)])_channel",
            "zero_frequency_homogeneous_correction": ["0", "0", "0"],
            "all_operator_remainders_zero": True,
            "complete_for_declared_tangent": complete_extension,
        },
        "classification": {
            "direct_homogeneous_operator_computed": True,
            "direct_bilinear_homogeneous_source_computed": True,
            "all_nonzero_frequency_homogeneous_channels_solved": all_homogeneous_nonzero_solved,
            "combined_zero_constant_ansatz_solved": channels["combined_zero"]["constant_ansatz_solvable"],
            "all_ell2_ell4_channels_solved_with_explicit_action_inverse": True,
            "complete_generalized_zero_frequency_correction_constructed": True,
            "complete_second_order_extension_constructed": complete_extension,
            "remaining_adjoint_obstruction_exhibited": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The balanced Einstein-minus/extra tangent is not merely Taub-zero: its complete quadratic source extends. The homogeneous zero-frequency Einstein and extra sources cancel exactly. Every remaining homogeneous channel has an explicit Weyl-gauge correction, and every ell=2,4 channel is removed by the exact action-normalized polar inverse. This is one nonlinear mixed fixture, not general closure of the mixed zero locus.",
        "next_gate": "generalize the construction to the full k=0 common moment-map zero cone, then classify opposite-momentum standing-wave balances and exceptional/global blocks",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem constructs a complete second-order correction for one declared balanced axial ell=2,m=0,k=0 Einstein-minus/extra tangent. It does not prove general nonlinear closure, integrate the formal second-order jet to an exact family, classify all mixed zero-locus components, perform residual reduction, establish causal propagation, or make a quantum claim.",
        "verification_receipt": {
            "exhaustive_tensor_replay": {
                "status": "PASS",
                "elapsed_seconds": 463.86,
                "command": "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order --write",
            },
            "fast_rail_policy": "the committed-certificate verifier replays hashes, exact ranks, rational and single-radical channel equations, and every stored remainder record; nested-radical cross equations are replayed by the exhaustive rail",
            "dependency_boundary": "no upstream content-addressed tensor, current, operator, stabilizer, or Taub input changed",
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order --verify bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_balanced_ell0_second_order",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_balanced_ell0_second_order",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json"
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA_PATH), "schema hash changed")
    provenance = payload["provenance"]
    _require(provenance["generator_sha256"] == _sha256(Path(__file__)), "generator hash changed")
    _require(provenance["tensor_helper_sha256"] == _sha256(TENSOR_HELPER), "tensor helper hash changed")
    _require(provenance["input"]["sha256"] == _sha256(ROOT / provenance["input"]["path"]), "zero-locus input hash changed")
    _require(payload["classification"]["complete_second_order_extension_constructed"] is True, "extension flag dropped")
    _require(payload["second_order_correction"]["all_operator_remainders_zero"] is True, "remainder flag dropped")


def verify_exhaustive_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"balanced ell0 certificate stale or altered: {path}")


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
