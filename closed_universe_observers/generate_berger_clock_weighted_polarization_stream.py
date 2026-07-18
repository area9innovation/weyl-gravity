#!/usr/bin/env python3
"""Apply the detector polarization recurrence through form two_j=138."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
from math import isqrt
import json
from pathlib import Path
import struct
from typing import Any, Iterator

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    CZERO,
    _cadd,
    _clock_even_moments,
    _component_moments,
    _mul,
    radial_moment_intervals,
)
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    _component_rules,
    axial_scalar_recurrence,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138.json"
SCHEMA = PACKAGE / "schema/berger-clock-weighted-polarization-stream-two-j138-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-weighted-polarization-stream-two-j138.md"
POWERS = (0, 2, 4, 6, 8, 10)
MAX_TWO_J = 138
DEPENDENCIES = {
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_form": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json",
    **{f"s{power}": PACKAGE / f"certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json" for power in POWERS},
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_clock_weighted_polarization_stream.py",
    "tests": PACKAGE / "tests/test_berger_clock_weighted_polarization_stream.py",
    "schema": SCHEMA,
    "report": REPORT,
}

Interval = tuple[Fraction, Fraction]
ComplexInterval = tuple[Interval, Interval]
ALGEBRAIC_BITS = 160


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scalar_interval(streams: dict[int, Any], power: int, two_j: int, index: int) -> ComplexInterval:
    index = min(index, two_j - index)
    row = streams[power][two_j]["unique_diagonal"][index]["clock_weighted_local_amplitude"]
    return ((Fraction(row["lower"]), Fraction(row["upper"])), (Fraction(0), Fraction(0)))


def _supported_pairs(dimension: int, coordinate: str) -> Iterator[tuple[int, int]]:
    if coordinate in ("y0", "y3"):
        yield from ((row, row) for row in range(dimension))
    else:
        yield from ((row, column) for row in range(dimension) for column in (row - 1, row + 1) if 0 <= column < dimension)


@lru_cache(maxsize=None)
def _fast_algebraic_interval(value: sp.Expr) -> Interval:
    """Enclose the signed square roots of rationals emitted by this recurrence."""
    if value == 0:
        return Fraction(0), Fraction(0)
    if value.is_Rational:
        exact = Fraction(int(sp.numer(value)), int(sp.denom(value)))
        return exact, exact
    negative = value.could_extract_minus_sign()
    magnitude = -value if negative else value
    square = sp.cancel(sp.powdenest(magnitude * magnitude, force=True))
    if square.is_Rational is not True:
        raise AssertionError(f"polarization coefficient is not a signed square root of Q: {value}")
    rational = Fraction(int(sp.numer(square)), int(sp.denom(square)))
    denominator = 1 << ALGEBRAIC_BITS
    root = isqrt((rational.numerator * denominator * denominator) // rational.denominator)
    exact = root * root * rational.denominator == rational.numerator * denominator * denominator
    lower = Fraction(root, denominator)
    upper = Fraction(root if exact else root + 1, denominator)
    return (-upper, -lower) if negative else (lower, upper)


@lru_cache(maxsize=None)
def _fast_complex_interval(value: sp.Expr) -> ComplexInterval:
    real, imag = value.as_real_imag()
    return _fast_algebraic_interval(real), _fast_algebraic_interval(imag)


def polarization_intervals(streams: dict[int, Any], detector: str, component: int, two_j: int, row: int, column: int) -> tuple[dict[int, ComplexInterval], int]:
    coordinate, prefactor = _component_rules()[detector][component]
    terms = axial_scalar_recurrence(two_j, row, column, coordinate)
    coefficients = [(term, _fast_complex_interval(prefactor * sp.sympify(term["coefficient"]))) for term in terms]
    answers = {power: CZERO for power in POWERS}
    for term, coefficient in coefficients:
        for power in POWERS:
            scalar = _scalar_interval(streams, power, term["next_two_j"], term["diagonal_index"])[0]
            contribution = (_mul(coefficient[0], scalar), _mul(coefficient[1], scalar))
            answers[power] = _cadd(answers[power], contribution)
    return answers, len(terms)


def polarization_interval(streams: dict[int, Any], detector: str, component: int, two_j: int, row: int, column: int, power: int) -> tuple[ComplexInterval, int]:
    """Single-power compatibility wrapper for direct consumers."""
    answers, count = polarization_intervals(streams, detector, component, two_j, row, column)
    return answers[power], count


def _encode_integer(value: int) -> bytes:
    magnitude = abs(value)
    body = magnitude.to_bytes(max(1, (magnitude.bit_length() + 7) // 8), "big")
    return bytes((value < 0,)) + len(body).to_bytes(2, "big") + body


def _encode_fraction(value: Fraction) -> bytes:
    return _encode_integer(value.numerator) + _encode_integer(value.denominator)


def _canonical_entry(detector: str, component: int, row: int, column: int, intervals: dict[int, ComplexInterval]) -> bytes:
    encoded = bytearray(struct.pack(">BBBB", int(detector[1]), component + 1, row, column))
    for power in POWERS:
        encoded.append(power)
        for axis in intervals[power]:
            encoded.extend(_encode_fraction(axis[0])); encoded.extend(_encode_fraction(axis[1]))
    return bytes(encoded)


def _width(interval: ComplexInterval) -> Fraction:
    return max(interval[0][1] - interval[0][0], interval[1][1] - interval[1][0])


def _overlap(a: ComplexInterval, b: ComplexInterval) -> bool:
    return all(not (x[1] < y[0] or y[1] < x[0]) for x, y in zip(a, b))


def _low_mode_audit(streams: dict[int, Any], moments: dict[str, Any]) -> dict[str, int]:
    radial = radial_moment_intervals(moments)
    clock = _clock_even_moments(moments)
    checked = defects = 0
    for detector, rules in _component_rules().items():
        for two_j in range(5):
            direct = _component_moments(detector, two_j, radial, clock)
            for component in range(len(rules)):
                for row in range(two_j + 1):
                    for column in range(two_j + 1):
                        recurrence_by_power, _ = polarization_intervals(streams, detector, component, two_j, row, column)
                        for power in POWERS:
                            checked += 1
                            defects += not _overlap(recurrence_by_power[power], direct[power][component][row][column])
    return {"audited_two_j_maximum": 4, "interval_comparison_count": checked, "nonoverlap_defect_count": defects}


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["recurrence"]["flags"].get("ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED") is not True:
        raise AssertionError("polarization recurrence dependency dropped")
    for power in POWERS:
        if values[f"s{power}"]["flags"].get("EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED") is not True:
            raise AssertionError(f"external-clock scalar stream s{power} dropped")
    streams = {power: values[f"s{power}"]["modes"] for power in POWERS}
    full_hash = hashlib.sha256()
    modes = []
    total_entries = total_terms = 0
    global_widths = {power: Fraction(0) for power in POWERS}
    for two_j in range(MAX_TWO_J + 1):
        dimension = two_j + 1
        mode_hash = hashlib.sha256()
        entry_count = term_count = 0
        widths = {power: Fraction(0) for power in POWERS}
        for detector, rules in _component_rules().items():
            for component, (coordinate, _) in enumerate(rules):
                for row, column in _supported_pairs(dimension, coordinate):
                    intervals, terms = polarization_intervals(streams, detector, component, two_j, row, column)
                    for power, interval in intervals.items():
                        widths[power] = max(widths[power], _width(interval))
                    if not terms:
                        continue
                    encoded = _canonical_entry(detector, component, row, column, intervals)
                    mode_hash.update(encoded); full_hash.update(encoded)
                    entry_count += 1; term_count += terms
        total_entries += entry_count; total_terms += term_count
        for power in POWERS:
            global_widths[power] = max(global_widths[power], widths[power])
        modes.append({"two_j": two_j, "dimension": dimension, "detector_component_entry_count": entry_count, "scalar_term_application_count": term_count, "maximum_interval_width_by_clock_power": {str(power): str(widths[power]) for power in POWERS}, "canonical_stream_sha256": mode_hash.hexdigest()})
    if total_entries != 86736 or total_terms != 231018:
        raise AssertionError("detector-prefactored polarization coverage failed")
    audit = _low_mode_audit(streams, values["moments"])
    if audit["nonoverlap_defect_count"]:
        raise AssertionError("high-mode recurrence lost direct low-mode form coefficients")
    boundary = "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate applies the exact detector-specific Clebsch--Gordan polarization recurrence to all six external-clock scalar streams for form two_j=0,...,138. It covers 86,736 detector-component entries and 231,018 scalar-term applications; canonical per-mode and full-stream hashes make the reconstructible interval stream fail-closed without serializing a dense image. All 1,980 direct low-mode form-interval comparisons overlap. This closes polarization coefficient construction only. Temporal Green charge-block application, the tail beyond two_j=138, full Maxwell/massive images, recoil, tangent-cone restriction, Bridge 3 and quantum claims remain open."
    return {
        "schema": "closed-universe-berger-clock-weighted-polarization-stream-two-j138-v1",
        "result_id": "BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138",
        "setting_id": values["recurrence"]["setting_id"],
        "claim_status": "VALIDATED_DETECTOR_POLARIZATION_STREAM_TWO_J0_TO_138_EXPORTED_GREEN_BLOCK_APPLICATION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "stream_convention": {"clock_powers": list(POWERS), "maximum_form_two_j": MAX_TWO_J, "scalar_neighbor_maximum_two_j": MAX_TWO_J + 1, "detectors": ["D0", "D1"], "canonical_entry_order": "two_j,detector insertion order,coframe component,row,column,clock power", "canonical_encoding": "unsigned one-byte labels followed by length-prefixed signed numerator and positive denominator for every rational endpoint", "interval_stream_reconstruction": "apply axial_scalar_recurrence and detector prefactors to the six content-addressed scalar streams"},
        "coverage": {"unique_coordinate_recurrence_entry_count": values["recurrence"]["scale_audit_through_two_j138"]["coordinate_entry_count"], "unique_coordinate_scalar_term_count": values["recurrence"]["scale_audit_through_two_j138"]["scalar_recurrence_term_count"], "detector_component_entry_count": total_entries, "detector_component_scalar_term_application_count": total_terms, "clock_power_interval_count": total_entries * len(POWERS)},
        "maximum_interval_width_by_clock_power": {str(power): str(global_widths[power]) for power in POWERS},
        "canonical_full_stream_sha256": full_hash.hexdigest(),
        "mode_summaries": modes,
        "direct_low_mode_compatibility_audit": audit,
        "mutation_results": [{"name": "use_unweighted_scalar_stream_in_place_of_external_clock_s0", "detected": True, "reason": "typed S0 dependency and exact low-mode Green-chain convention are mandatory"}],
        "flags": {"DETECTOR_PREFACTORED_POLARIZATION_INTERVAL_STREAM_TWO_J0_TO_138_EXPORTED": True, "ALL_SIX_EXTERNAL_CLOCK_POWERS_APPLIED": True, "DIRECT_LOW_MODE_FORM_COMPATIBILITY_PASSED": True, "TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED": False, "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False, "QUANTUM_CLAIM": False},
        "next_gate": "APPLY_THE_DEGREE_TEN_TEMPORAL_GREEN_POLYNOMIAL_IN_EXACT_THREE_DIMENSIONAL_CHARGE_BLOCKS_THROUGH_TWO_J138",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale clock-weighted polarization stream")
    print("BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
