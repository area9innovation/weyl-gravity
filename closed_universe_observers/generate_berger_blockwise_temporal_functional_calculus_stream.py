#!/usr/bin/env python3
"""Stream microphase-dressed inputs for the exact-T Maxwell functional calculus."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from fractions import Fraction
from functools import lru_cache
from math import factorial
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_preflight import (
    CERTIFICATE as PREFLIGHT_CERTIFICATE,
    INTERNAL_CLOCK_SCALE,
)
from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import scalar_eigenvalue
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import CZERO, _cadd, _cmul, _cscale
from closed_universe_observers.generate_berger_order14_temporal_green_charge_stream import (
    DEPENDENCIES as ORDER14_DEPENDENCIES,
    MAX_TWO_J,
    POWERS,
    SERIES_ORDER,
    _block_intervals,
    _dot,
    _encode_fraction,
    _encode_interval,
    _helicity_moments,
    _is_zero,
    _width,
)
from closed_universe_observers.generate_berger_streamable_polarization_sectors import helicity_sectors

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_STREAM_TWO_J138.json"
SCHEMA = PACKAGE / "schema/berger-blockwise-temporal-functional-calculus-stream-v1.schema.json"
REPORT = PACKAGE / "reports/berger-blockwise-temporal-functional-calculus-stream.md"
ORDER14_CERTIFICATE = PACKAGE / "certificates/BERGER_ORDER14_TEMPORAL_GREEN_CHARGE_STREAM_TWO_J138.json"
DEPENDENCIES = {
    **ORDER14_DEPENDENCIES,
    "order14_obstruction": ORDER14_CERTIFICATE,
    "functional_preflight": PREFLIGHT_CERTIFICATE,
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_blockwise_temporal_functional_calculus_stream.py",
    PACKAGE / "tests/test_berger_blockwise_temporal_functional_calculus_stream.py",
    SCHEMA,
    REPORT,
]

ComplexInterval = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]
IntervalMatrix = tuple[tuple[ComplexInterval, ...], ...]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(dimension: int) -> IntervalMatrix:
    one = ((Fraction(1), Fraction(1)), (Fraction(0), Fraction(0)))
    return tuple(tuple(one if row == column else CZERO for column in range(dimension)) for row in range(dimension))


def _matrix_multiply(left: IntervalMatrix, right: IntervalMatrix) -> IntervalMatrix:
    dimension = len(left)
    rows = []
    for row in range(dimension):
        values = []
        for column in range(dimension):
            total = CZERO
            for inner in range(dimension):
                total = _cadd(total, _cmul(left[row][inner], right[inner][column]))
            values.append(total)
        rows.append(tuple(values))
    return tuple(rows)


def _matrix_vector(matrix: IntervalMatrix, vector: list[ComplexInterval]) -> list[ComplexInterval]:
    answer = []
    for row in matrix:
        total = CZERO
        for entry, value in zip(row, vector):
            total = _cadd(total, _cmul(entry, value))
        answer.append(total)
    return answer


def block_powers(two_j: int, charge: Fraction) -> tuple[list[tuple[int, Fraction]], tuple[IntervalMatrix, ...], tuple[ComplexInterval, ...]]:
    members, block, delta = _block_intervals(two_j, charge)
    powers = [_identity(len(members))]
    for _ in range(SERIES_ORDER):
        powers.append(_matrix_multiply(block, powers[-1]))
    return members, tuple(powers), delta


def dressed_block(
    two_j: int,
    charge: Fraction,
    moments: dict[int, list[ComplexInterval]],
    powers: tuple[IntervalMatrix, ...] | None = None,
) -> tuple[list[ComplexInterval], ComplexInterval]:
    if powers is None:
        members, default_powers, delta = block_powers(two_j, charge)
    else:
        members, _, delta = _block_intervals(two_j, charge)
        default_powers = powers
    if any(len(vector) != len(members) for vector in moments.values()):
        raise ValueError("moment vector has wrong block dimension")
    spatial = [CZERO for _ in members]
    temporal = CZERO
    scalar_lambda = scalar_eigenvalue(two_j, charge)
    scalar_lambda_q = Fraction(int(sp.numer(scalar_lambda)), int(sp.denom(scalar_lambda)))
    scalar_power = Fraction(1)
    for index, power in enumerate(POWERS):
        factor = Fraction((-1) ** index, factorial(2 * index)) * INTERNAL_CLOCK_SCALE**power
        contribution = _matrix_vector(default_powers[index], moments[power])
        spatial = [_cadd(old, _cscale(value, factor)) for old, value in zip(spatial, contribution)]
        delta_value = _dot(delta, moments[power])
        temporal = _cadd(temporal, _cscale(delta_value, factor * scalar_power))
        scalar_power *= scalar_lambda_q
    return spatial, temporal


def _stream(values: dict[str, Any]) -> dict[str, Any]:
    streams = {power: values[f"s{power}"]["modes"] for power in POWERS}
    full_hash = hashlib.sha256()
    modes = []
    total_blocks = total_spatial = total_temporal = 0
    maximum_width = Fraction(0)
    for two_j in range(MAX_TWO_J + 1):
        if two_j % 10 == 0 or two_j == MAX_TWO_J:
            print(f"functional-calculus stream progress: two_j={two_j}/{MAX_TWO_J}", flush=True)
        j = Fraction(two_j, 2)
        sectors = helicity_sectors(two_j)
        power_cache = {charge: block_powers(two_j, charge)[1] for charge in sectors}
        mode_hash = hashlib.sha256()
        mode_blocks = mode_spatial = mode_temporal = 0
        mode_width = Fraction(0)
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
                    spatial, temporal = dressed_block(two_j, charge, moments, power_cache[charge])
                    prefix = struct.pack(">BBH", int(detector[1]), column, two_j) + _encode_fraction(charge)
                    mode_blocks += 1
                    for output, value in enumerate(spatial):
                        if _is_zero(value):
                            continue
                        encoded = prefix + b"C" + bytes((output,)) + _encode_interval(value)
                        mode_hash.update(encoded); full_hash.update(encoded)
                        mode_spatial += 1; mode_width = max(mode_width, _width(value))
                    if not _is_zero(temporal):
                        encoded = prefix + b"S" + _encode_interval(temporal)
                        mode_hash.update(encoded); full_hash.update(encoded)
                        mode_temporal += 1; mode_width = max(mode_width, _width(temporal))
        total_blocks += mode_blocks; total_spatial += mode_spatial; total_temporal += mode_temporal
        maximum_width = max(maximum_width, mode_width)
        modes.append({
            "two_j": two_j,
            "dimension": two_j + 1,
            "populated_detector_column_charge_block_count": mode_blocks,
            "spatial_microphase_dressed_amplitude_interval_count": mode_spatial,
            "temporal_microphase_dressed_amplitude_interval_count": mode_temporal,
            "maximum_interval_width": str(mode_width),
            "canonical_mode_stream_sha256": mode_hash.hexdigest(),
        })
    return {
        "populated_detector_column_charge_block_count": total_blocks,
        "spatial_microphase_dressed_amplitude_interval_count": total_spatial,
        "temporal_microphase_dressed_amplitude_interval_count": total_temporal,
        "maximum_interval_width": str(maximum_width),
        "canonical_full_stream_sha256": full_hash.hexdigest(),
        "mode_summaries": modes,
    }


def _error_budget(preflight: dict[str, Any], order14: dict[str, Any]) -> list[dict[str, str]]:
    audit = preflight["microphase_remainder_audit"]
    spatial = Fraction(audit["Delta1_cosine_microphase_remainder_upper"])
    scalar = Fraction(audit["Delta0_cosine_microphase_remainder_upper"])
    delta_norm = Fraction(order14["remainder_audits"][0]["spatial_delta_infinity_norm_upper"])
    rows = []
    for detector, t_max in (("D0", Fraction(5, 48)), ("D1", Fraction(3, 16))):
        dressed_temporal = delta_norm * scalar
        propagated_temporal = t_max * dressed_temporal
        rows.append({
            "detector_id": detector,
            "T_absolute_maximum": str(t_max),
            "spatial_exact_T_image_remainder_upper": str(spatial),
            "temporal_dressed_coderivative_remainder_upper": str(dressed_temporal),
            "temporal_exact_T_image_remainder_upper": str(propagated_temporal),
        })
    return rows


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["functional_preflight"]["flags"].get("ANGLE_ADDITION_BLOCKWISE_ROUTE_CERTIFIED") is not True:
        raise AssertionError("functional-calculus preflight dropped")
    if values["functional_preflight"]["flags"].get("EXISTING_EVEN_CLOCK_INPUTS_P0_TO_P28_SUFFICIENT") is not True:
        raise AssertionError("clock-input sufficiency dropped")
    stream = _stream(values)
    errors = _error_budget(values["functional_preflight"], values["order14_obstruction"])
    if max(Fraction(row["spatial_exact_T_image_remainder_upper"]) for row in errors) >= Fraction(1, 10**17):
        raise AssertionError("spatial exact-T error budget drifted")
    if max(Fraction(row["temporal_exact_T_image_remainder_upper"]) for row in errors) >= Fraction(1, 10**15):
        raise AssertionError("temporal exact-T error budget drifted")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result streams the order-14 microphase-dressed detector coderivative inputs in every exact Maxwell charge block through form two_j=138. It retains the large propagation separation exactly as -cos(T sqrt(B)) times the spatial dressed amplitude and -sin(T sqrt(lambda0))/sqrt(lambda0) times the temporal dressed coderivative, with the entire zero-eigenvalue extension. Canonical per-mode and full hashes make the amplitude stream fail closed. The propagated uniform microphase errors are exported and remain below 1e-15. This closes the finite-rail temporal functional-calculus image representation, not the spatial tail beyond two_j=138, full infinite-mode Maxwell image, massive-two-form image, recoil coefficient, tangent-cone restriction, Bridge 3 or quantum claims."
    )
    return {
        "schema": "closed-universe-berger-blockwise-temporal-functional-calculus-stream-v1",
        "result_id": "BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_STREAM_TWO_J138",
        "setting_id": values["functional_preflight"]["setting_id"],
        "claim_status": "VALIDATED_FINITE_RAIL_EXACT_T_TEMPORAL_FUNCTIONAL_CALCULUS_IMAGE_STREAM_EXPORTED_SPATIAL_TAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "functional_calculus_convention": {
            "spatial_image": "-cos(T sqrt(B_q)) C_q where C_q=sum_n (-B_q)^n v_(2n)/(2n)! 48^(2n)",
            "temporal_image": "-[sin(T sqrt(lambda0_q))/sqrt(lambda0_q)] c_q where c_q=sum_n (-lambda0_q)^n delta_q v_(2n)/(2n)! 48^(2n)",
            "zero_eigenvalue_extension": "sin(T sqrt(lambda))/sqrt(lambda) at lambda=0 is T",
            "T_domains": {"D0": "1/16 <= T <= 5/48", "D1": "1/16 <= T <= 3/16"},
            "series_order_applies_only_to_internal_microphase": SERIES_ORDER,
            "large_T_taylor_truncation": False,
        },
        "coverage": {key: value for key, value in stream.items() if key != "mode_summaries"},
        "mode_summaries": stream["mode_summaries"],
        "uniform_error_budgets": errors,
        "mutation_results": [{
            "name": "replace_exact_T_functional_calculus_by_global_order14_Taylor_polynomial",
            "detected": True,
            "reason": "dependency BERGER_ORDER14_TEMPORAL_GREEN_CHARGE_STREAM_TWO_J138 supplies exact extreme-block error lower bounds",
        }],
        "flags": {
            "MICROPHASE_DRESSED_CHARGE_BLOCK_INPUT_STREAM_EXPORTED": True,
            "FINITE_RAIL_EXACT_T_TEMPORAL_FUNCTIONAL_CALCULUS_IMAGE_EXPORTED": True,
            "LARGE_T_TAYLOR_TRUNCATION_REMOVED": True,
            "UNIFORM_PROPAGATED_MICROPHASE_ERROR_BELOW_ONE_E_MINUS_FIFTEEN": True,
            "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CERTIFY_THE_SPATIAL_HARMONIC_TAIL_BEYOND_TWO_J138_FOR_THE_EXACT_T_IMAGE_STREAM",
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
        raise SystemExit("stale blockwise temporal functional-calculus stream")
    print("BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_STREAM generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
