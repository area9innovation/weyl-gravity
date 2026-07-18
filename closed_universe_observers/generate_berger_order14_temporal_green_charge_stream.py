#!/usr/bin/env python3
"""Stream the common order-14 temporal Maxwell polynomial in charge blocks."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_adaptive_clock_weighted_polarization_stream import (
    POWERS as ADAPTIVE_POWERS,
    _scalar as _adaptive_scalar,
)
from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import (
    POWERS as LOW_POWERS,
    _fast_complex_interval,
    _scalar_interval,
    _supported_pairs,
    _width,
)
from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import (
    charge_block,
    delta_row,
    scalar_eigenvalue,
)
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    CZERO,
    _cadd,
    _cmul,
    _cscale,
    _infinity_norm_upper,
    _mul,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
    laplacian,
)
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    _component_rules,
    axial_scalar_recurrence,
)
from closed_universe_observers.generate_berger_streamable_polarization_sectors import helicity_sectors

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_ORDER14_TEMPORAL_GREEN_CHARGE_STREAM_TWO_J138.json"
SCHEMA = PACKAGE / "schema/berger-order14-temporal-green-charge-stream-v1.schema.json"
REPORT = PACKAGE / "reports/berger-order14-temporal-green-charge-stream.md"
SERIES_ORDER = 14
MAX_TWO_J = 138
PHYSICAL_OFFSET_SCALE = Fraction(1, 48)
POWERS = LOW_POWERS + ADAPTIVE_POWERS

DEPENDENCIES = {
    "low_polarization": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138.json",
    "adaptive_polarization": PACKAGE / "certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_POLARIZATION_STREAM_P12_TO_P28_TWO_J138.json",
    "charge_blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
    "preflight": PACKAGE / "certificates/BERGER_TEMPORAL_GREEN_ORDER_FIVE_HIGH_MODE_PREFLIGHT.json",
    "low_green": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    **{
        f"s{power}": PACKAGE / f"certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json"
        for power in LOW_POWERS
    },
    **{
        f"s{power}": PACKAGE / f"certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json"
        for power in ADAPTIVE_POWERS
    },
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_order14_temporal_green_charge_stream.py",
    PACKAGE / "tests/test_berger_order14_temporal_green_charge_stream.py",
    SCHEMA,
    REPORT,
]

Interval = tuple[Fraction, Fraction]
ComplexInterval = tuple[Interval, Interval]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _encode_integer(value: int) -> bytes:
    body = abs(value).to_bytes(max(1, (abs(value).bit_length() + 7) // 8), "big")
    return bytes((value < 0,)) + len(body).to_bytes(2, "big") + body


def _encode_fraction(value: Fraction) -> bytes:
    return _encode_integer(value.numerator) + _encode_integer(value.denominator)


def _encode_interval(value: ComplexInterval) -> bytes:
    return b"".join(_encode_fraction(endpoint) for axis in value for endpoint in axis)


def _is_zero(value: ComplexInterval) -> bool:
    return value == CZERO


def _combined_polarization(
    streams: dict[int, Any], detector: str, component: int, two_j: int, row: int, column: int
) -> dict[int, ComplexInterval]:
    coordinate, prefactor = _component_rules()[detector][component]
    terms = axial_scalar_recurrence(two_j, row, column, coordinate)
    coefficients = [(term, _fast_complex_interval(prefactor * sp.sympify(term["coefficient"]))) for term in terms]
    answers = {power: CZERO for power in POWERS}
    for term, coefficient in coefficients:
        for power in POWERS:
            if power in LOW_POWERS:
                scalar = _scalar_interval(streams, power, term["next_two_j"], term["diagonal_index"])[0]
            else:
                scalar = _adaptive_scalar(streams, power, term["next_two_j"], term["diagonal_index"])[0]
            answers[power] = _cadd(answers[power], (_mul(coefficient[0], scalar), _mul(coefficient[1], scalar)))
    return answers


@lru_cache(maxsize=None)
def _block_intervals(two_j: int, q: Fraction) -> tuple[list[tuple[int, Fraction]], tuple[tuple[ComplexInterval, ...], ...], tuple[ComplexInterval, ...]]:
    members, block = charge_block(two_j, q)
    delta_members, delta = delta_row(two_j, q)
    if members != delta_members:
        raise AssertionError("charge-block member order drifted")
    block_i = tuple(tuple(_fast_complex_interval(block[row, column]) for column in range(block.cols)) for row in range(block.rows))
    delta_i = tuple(_fast_complex_interval(delta[0, column]) for column in range(delta.cols))
    return members, block_i, delta_i


def _apply_matrix(matrix: tuple[tuple[ComplexInterval, ...], ...], vector: list[ComplexInterval]) -> list[ComplexInterval]:
    answer = []
    for row in matrix:
        total = CZERO
        for column, entry in enumerate(row):
            total = _cadd(total, _cmul(entry, vector[column]))
        answer.append(total)
    return answer


def _dot(row: tuple[ComplexInterval, ...], vector: list[ComplexInterval]) -> ComplexInterval:
    answer = CZERO
    for entry, value in zip(row, vector):
        answer = _cadd(answer, _cmul(entry, value))
    return answer


def _accumulate(target: dict[int, list[ComplexInterval]], power: int, values: list[ComplexInterval]) -> None:
    if power not in target:
        target[power] = [CZERO for _ in values]
    target[power] = [_cadd(old, value) for old, value in zip(target[power], values)]


def block_polynomials(
    two_j: int, q: Fraction, moments: dict[int, list[ComplexInterval]], *, order: int = SERIES_ORDER
) -> tuple[dict[int, list[ComplexInterval]], dict[int, ComplexInterval]]:
    """Return -cos and -sine*delta coefficient intervals for one charge block."""
    members, block, delta = _block_intervals(two_j, q)
    if any(len(moment) != len(members) for moment in moments.values()):
        raise ValueError("moment vector has wrong charge-block dimension")
    spatial: dict[int, list[ComplexInterval]] = {}
    temporal: dict[int, ComplexInterval] = {}
    scalar_lambda = scalar_eigenvalue(two_j, q)
    scalar_lambda_q = Fraction(int(sp.numer(scalar_lambda)), int(sp.denom(scalar_lambda)))
    for moment_power, vector in moments.items():
        block_power_vector = vector
        delta_value = _dot(delta, vector)
        scalar_power = Fraction(1)
        for series_index in range(order + 1):
            if moment_power <= 2 * series_index:
                t_power = 2 * series_index - moment_power
                factor = Fraction((-1) ** (series_index + 1) * comb(2 * series_index, moment_power), factorial(2 * series_index))
                factor *= PHYSICAL_OFFSET_SCALE**moment_power
                _accumulate(spatial, t_power, [_cscale(value, factor) for value in block_power_vector])
            if moment_power <= 2 * series_index + 1:
                t_power = 2 * series_index + 1 - moment_power
                factor = Fraction((-1) ** (series_index + 1) * comb(2 * series_index + 1, moment_power), factorial(2 * series_index + 1))
                factor *= PHYSICAL_OFFSET_SCALE**moment_power * scalar_power
                contribution = _cscale(delta_value, factor)
                if not _is_zero(contribution):
                    temporal[t_power] = _cadd(temporal.get(t_power, CZERO), contribution)
            if series_index != order:
                block_power_vector = _apply_matrix(block, block_power_vector)
                scalar_power *= scalar_lambda_q
    return spatial, temporal


def _helicity_moments(
    streams: dict[int, Any], detector: str, two_j: int, column: int
) -> dict[int, dict[tuple[int, int], ComplexInterval]]:
    dimension = two_j + 1
    real: dict[tuple[int, int], dict[int, ComplexInterval]] = {}
    for component, (coordinate, _) in enumerate(_component_rules()[detector]):
        for row, supported_column in _supported_pairs(dimension, coordinate):
            if supported_column == column:
                real[(component, row)] = _combined_polarization(streams, detector, component, two_j, row, column)
    plus_coefficients = (_fast_complex_interval(1 / sp.sqrt(2)), _fast_complex_interval(-sp.I / sp.sqrt(2)))
    minus_coefficients = (_fast_complex_interval(1 / sp.sqrt(2)), _fast_complex_interval(sp.I / sp.sqrt(2)))
    result = {power: {} for power in POWERS}
    rows = {row for _, row in real}
    for power in POWERS:
        for row in rows:
            v1 = real.get((0, row), {}).get(power, CZERO)
            v2 = real.get((1, row), {}).get(power, CZERO)
            v3 = real.get((2, row), {}).get(power, CZERO)
            plus = _cadd(_cmul(plus_coefficients[0], v1), _cmul(plus_coefficients[1], v2))
            minus = _cadd(_cmul(minus_coefficients[0], v1), _cmul(minus_coefficients[1], v2))
            if not _is_zero(plus):
                result[power][(0, row)] = plus
            if not _is_zero(v3):
                result[power][(1, row)] = v3
            if not _is_zero(minus):
                result[power][(2, row)] = minus
    return result


def _tail(y: Fraction, first_denominator: int, factorial_denominator: int, order: int = SERIES_ORDER) -> Fraction:
    ratio = y / Fraction(first_denominator * (first_denominator + 1))
    if ratio >= 1:
        raise AssertionError("geometric series remainder is not contractive")
    return y ** (order + 1) / factorial(factorial_denominator) / (1 - ratio)


def _cosine_polynomial(y: Fraction, order: int = SERIES_ORDER) -> Fraction:
    return sum(Fraction((-1) ** index) * y**index / factorial(2 * index) for index in range(order + 1))


def remainder_audits() -> list[dict[str, Any]]:
    lambda1 = _infinity_norm_upper(laplacian(MAX_TWO_J, 1))
    lambda0 = _infinity_norm_upper(laplacian(MAX_TWO_J, 0))
    delta_norm = _infinity_norm_upper(d_matrix(MAX_TWO_J, 0).conjugate().T)
    extreme_lambda = Fraction(196000, 9)
    rows = []
    for detector, tau in (("D0", Fraction(1, 8)), ("D1", Fraction(5, 24))):
        y1 = lambda1 * tau**2
        y0 = lambda0 * tau**2
        cosine_tail = _tail(y1, 2 * SERIES_ORDER + 3, 2 * SERIES_ORDER + 2)
        sine_tail = tau * _tail(y0, 2 * SERIES_ORDER + 4, 2 * SERIES_ORDER + 3) * delta_norm
        witness_y = extreme_lambda * tau**2
        witness_polynomial = _cosine_polynomial(witness_y)
        witness_error_lower = abs(witness_polynomial) - 1
        if witness_error_lower <= 1:
            raise AssertionError("extreme-block order-14 obstruction disappeared")
        rows.append({
            "detector_id": detector,
            "tau_max": str(tau),
            "Delta1_infinity_norm_upper": str(lambda1),
            "Delta0_infinity_norm_upper": str(lambda0),
            "spatial_delta_infinity_norm_upper": str(delta_norm),
            "cosine_geometric_ratio": str(y1 / Fraction((2 * SERIES_ORDER + 3) * (2 * SERIES_ORDER + 4))),
            "sine_geometric_ratio": str(y0 / Fraction((2 * SERIES_ORDER + 4) * (2 * SERIES_ORDER + 5))),
            "spatial_cosine_entry_remainder_upper": str(cosine_tail),
            "temporal_sine_entry_remainder_upper": str(sine_tail),
            "uniform_remainders_below_one": cosine_tail < 1 and sine_tail < 1,
            "extreme_charge": "j+1",
            "extreme_block_eigenvalue": str(extreme_lambda),
            "extreme_witness_y": str(witness_y),
            "order14_cosine_polynomial_on_extreme_block": str(witness_polynomial),
            "exact_cosine_error_absolute_lower": str(witness_error_lower),
        })
    return rows


def _stream(values: dict[str, Any]) -> dict[str, Any]:
    streams = {power: values[f"s{power}"]["modes"] for power in POWERS}
    full_hash = hashlib.sha256()
    modes = []
    total_blocks = total_spatial = total_temporal = 0
    maximum_width = Fraction(0)
    for two_j in range(MAX_TWO_J + 1):
        j = Fraction(two_j, 2)
        mode_hash = hashlib.sha256()
        mode_blocks = mode_spatial = mode_temporal = 0
        mode_width = Fraction(0)
        sectors = helicity_sectors(two_j)
        for detector in ("D0", "D1"):
            for column in range(two_j + 1):
                helicity = _helicity_moments(streams, detector, two_j, column)
                for charge, members in sorted(sectors.items()):
                    moments = {
                        power: [helicity[power].get((component, int(m + j)), CZERO) for component, m in members]
                        for power in POWERS
                    }
                    if all(all(_is_zero(value) for value in vector) for vector in moments.values()):
                        continue
                    spatial, temporal = block_polynomials(two_j, charge, moments)
                    mode_blocks += 1
                    prefix = struct.pack(">BBH", int(detector[1]), column, two_j) + _encode_fraction(charge)
                    for t_power, vector in sorted(spatial.items()):
                        for output, value in enumerate(vector):
                            if _is_zero(value):
                                continue
                            encoded = prefix + b"S" + bytes((t_power, output)) + _encode_interval(value)
                            mode_hash.update(encoded); full_hash.update(encoded)
                            mode_spatial += 1; mode_width = max(mode_width, _width(value))
                    for t_power, value in sorted(temporal.items()):
                        if _is_zero(value):
                            continue
                        encoded = prefix + b"T" + bytes((t_power,)) + _encode_interval(value)
                        mode_hash.update(encoded); full_hash.update(encoded)
                        mode_temporal += 1; mode_width = max(mode_width, _width(value))
        total_blocks += mode_blocks; total_spatial += mode_spatial; total_temporal += mode_temporal
        maximum_width = max(maximum_width, mode_width)
        modes.append({
            "two_j": two_j,
            "dimension": two_j + 1,
            "nonzero_detector_column_charge_block_count": mode_blocks,
            "spatial_polynomial_coefficient_interval_count": mode_spatial,
            "temporal_polynomial_coefficient_interval_count": mode_temporal,
            "maximum_interval_width": str(mode_width),
            "canonical_output_stream_sha256": mode_hash.hexdigest(),
        })
    return {
        "nonzero_detector_column_charge_block_count": total_blocks,
        "spatial_polynomial_coefficient_interval_count": total_spatial,
        "temporal_polynomial_coefficient_interval_count": total_temporal,
        "maximum_interval_width": str(maximum_width),
        "canonical_full_output_stream_sha256": full_hash.hexdigest(),
        "mode_summaries": modes,
    }


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "low_polarization": "DETECTOR_PREFACTORED_POLARIZATION_INTERVAL_STREAM_TWO_J0_TO_138_EXPORTED",
        "adaptive_polarization": "COMMON_ORDER14_POLARIZATION_INPUTS_P0_TO_P28_COMPLETE",
        "charge_blocks": "ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    stream = _stream(values)
    remainders = remainder_audits()
    if any(row["uniform_remainders_below_one"] for row in remainders):
        raise AssertionError("order-14 remainder disposition drifted")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result applies every even external-clock moment p=0,2,...,28 to the common order-14 advanced cosine and codifferential/sine polynomials in the exact at-most-three-dimensional Maxwell charge blocks through form two_j=138. The reconstructible output is fail-closed by canonical per-mode and full-stream hashes. Both geometric tails are contractive, but their exported uniform bounds exceed one. More decisively, boundedness of exact cosine on the one-dimensional q=j+1 block gives large positive exact lower bounds on the actual order-14 truncation error for both detector time radii. Therefore the formal polynomial stream is certified but its promotion to a temporal Green image is OBSTRUCTED. A sharper blockwise functional calculus or validated oscillatory method is required before the spatial tail, full Maxwell/massive images, recoil, tangent-cone restriction, Bridge 3 or quantum claims."
    )
    return {
        "schema": "closed-universe-berger-order14-temporal-green-charge-stream-v1",
        "result_id": "BERGER_ORDER14_TEMPORAL_GREEN_CHARGE_STREAM_TWO_J138",
        "setting_id": values["low_polarization"]["setting_id"],
        "claim_status": "ORDER14_CHARGE_BLOCK_POLYNOMIAL_STREAM_CERTIFIED_TEMPORAL_GREEN_PROMOTION_OBSTRUCTED",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "series_convention": {
            "order": SERIES_ORDER,
            "clock_powers": list(POWERS),
            "physical_time_offset": "source_time=t_detector_center+s/48",
            "spatial_polynomial": "-sum_n (-Delta1)^n tau^(2n)/(2n)! after boundary-flat integration by parts",
            "temporal_polynomial": "-sum_n (-Delta0)^n tau^(2n+1)/(2n+1)! delta_Sigma",
            "charge_basis": ["theta_plus", "theta3", "theta_minus"],
            "canonical_stream_order": "two_j,detector,column,charge,spatial-before-temporal,T_power,block-output",
        },
        "coverage": {key: value for key, value in stream.items() if key != "mode_summaries"},
        "mode_summaries": stream["mode_summaries"],
        "remainder_audits": remainders,
        "mutation_results": [{
            "name": "promote_contractive_order14_tail_to_usable_green_image",
            "detected": True,
            "reason": "both uniform remainder bounds exceed one and the exact extreme-block cosine error lower bounds are positive",
        }],
        "flags": {
            "ORDER14_TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED": True,
            "ALL_EVEN_CLOCK_POWERS_P0_TO_P28_APPLIED": True,
            "CANONICAL_RECONSTRUCTIBLE_POLYNOMIAL_OUTPUT_STREAM_EXPORTED": True,
            "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": True,
            "GEOMETRIC_REMAINDER_RATIOS_CONTRACTIVE": True,
            "ORDER14_UNIFORM_REMAINDERS_BELOW_ONE": False,
            "ORDER14_TEMPORAL_GREEN_IMAGE_CERTIFIED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPLACE_GLOBAL_TAYLOR_TRUNCATION_BY_VALIDATED_BLOCKWISE_FUNCTIONAL_CALCULUS_OR_OSCILLATORY_APPROXIMATION",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale order-14 temporal Green charge stream")
    print("BERGER_ORDER14_TEMPORAL_GREEN_CHARGE_STREAM generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
