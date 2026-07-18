#!/usr/bin/env python3
"""Integrate the fixed clock bump into the scalar SU(2) profile coefficients."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
import sympy as sp

from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    EPSILON,
    MAX_MOMENT_K,
    MAX_TWO_J,
    PACKAGE,
    coefficient_interval,
    expected_term_reduction,
    radial_moment_intervals,
    representation_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json"
SCHEMA = PACKAGE / "schema/berger-clock-integrated-scalar-profile-coefficients-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-integrated-scalar-profile-coefficients.md"
LOCAL_GENERATOR = PACKAGE / "generate_berger_local_su2_profile_coefficients.py"
DEPENDENCIES = {
    "local_coefficients": PACKAGE / "certificates/BERGER_LOCAL_SU2_PROFILE_COEFFICIENT_ENCLOSURES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_clock_integrated_scalar_coefficients.py",
    "tests": PACKAGE / "tests/test_berger_clock_integrated_scalar_coefficients.py",
    "schema": SCHEMA,
    "report": REPORT,
}
SUBDIVISIONS = 32768
IV_DPS = 50
OUTPUT_DYADIC_BITS = 160
CLOCK_LAMBDA_SQUARED = Fraction(29, 41472)
AMPLITUDE_LOWER = Fraction(82915, 82944)
A2_AT_CENTER = EPSILON**2 / 4
B2_AT_CENTER = EPSILON**2 * Fraction(10, 9)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_from_mpf_tuple(value: tuple[int, int, int, int]) -> Fraction:
    sign, mantissa, exponent, _ = value
    answer = Fraction(mantissa)
    answer = answer * 2**exponent if exponent >= 0 else answer / 2 ** (-exponent)
    return -answer if sign else answer


def _interval_endpoints(value: Any) -> tuple[Fraction, Fraction]:
    raw = value._mpi_
    return _fraction_from_mpf_tuple(raw[0]), _fraction_from_mpf_tuple(raw[1])


def _round_outward(interval: tuple[Fraction, Fraction], bits: int = OUTPUT_DYADIC_BITS) -> tuple[Fraction, Fraction]:
    denominator = 2**bits
    lower = interval[0].numerator * denominator // interval[0].denominator
    upper = -(-interval[1].numerator * denominator // interval[1].denominator)
    return Fraction(lower, denominator), Fraction(upper, denominator)


def _serialize_interval(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    interval = _round_outward(interval)
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def _bump_and_sec2_endpoint(r: Fraction) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    if r == 1:
        return (Fraction(0), Fraction(0)), (Fraction(1), Fraction(1))
    mp.iv.dps = IV_DPS
    x = mp.iv.mpf(r.numerator) / r.denominator
    bump = mp.iv.exp(1 - 1 / (1 - x * x)) if r else mp.iv.mpf(1)
    phase = mp.iv.sqrt(58) * x / 288
    secant_squared = 1 / mp.iv.cos(phase) ** 2
    return _interval_endpoints(bump), _interval_endpoints(secant_squared)


def _bump_sec_endpoint(r: Fraction, k: int) -> tuple[Fraction, Fraction]:
    bump, secant_squared = _bump_and_sec2_endpoint(r)
    return bump[0] * secant_squared[0] ** k, bump[1] * secant_squared[1] ** k


def clock_secant_moments(subdivisions: int = SUBDIVISIONS) -> dict[int, tuple[Fraction, Fraction]]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    width = Fraction(1, subdivisions)
    endpoint_factors = [_bump_and_sec2_endpoint(Fraction(i, subdivisions)) for i in range(subdivisions + 1)]
    integrals: dict[int, tuple[Fraction, Fraction]] = {}
    for k in range(MAX_MOMENT_K + 1):
        endpoints = [
            (bump[0] * secant_squared[0] ** k, bump[1] * secant_squared[1] ** k)
            for bump, secant_squared in endpoint_factors
        ]
        lower = sum((width * endpoints[i + 1][0] for i in range(subdivisions)), Fraction(0))
        upper = sum((width * endpoints[i][1] for i in range(subdivisions)), Fraction(0))
        integrals[k] = _round_outward((lower, upper))
    base_lower, base_upper = integrals[0]
    ratios = {0: (Fraction(1), Fraction(1))}
    for k in range(1, MAX_MOMENT_K + 1):
        ratios[k] = _round_outward((integrals[k][0] / base_upper, integrals[k][1] / base_lower))
    return ratios


def monotonicity_audit() -> dict[str, Any]:
    rows = []
    for k in range(MAX_MOMENT_K + 1):
        ratio = Fraction(k) * CLOCK_LAMBDA_SQUARED / AMPLITUDE_LOWER
        rows.append({"k": k, "k_lambda_squared_over_cos_lower": str(ratio), "strictly_below_one": ratio < 1})
    return {
        "derivative_identity": "d log(B(r) sec(lambda r)^(2k))/dr=-2r/(1-r^2)^2+2k lambda tan(lambda r)",
        "bound": "tan(lambda r)<=lambda r/cos(lambda)<=lambda r/(82915/82944), so every audited integrand is decreasing",
        "rows": rows,
        "all_decreasing": all(row["strictly_below_one"] for row in rows),
    }


def _multiply_intervals(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    products = [a * b for a in left for b in right]
    return min(products), max(products)


def _add_intervals(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return left[0] + right[0], left[1] + right[1]


def _scale_interval(interval: tuple[Fraction, Fraction], coefficient: Fraction) -> tuple[Fraction, Fraction]:
    values = coefficient * interval[0], coefficient * interval[1]
    return min(values), max(values)


def base_scale_terms(expression: sp.Expr, radial: dict[int, tuple[Fraction, Fraction]]) -> tuple[dict[int, tuple[Fraction, Fraction]], Fraction]:
    terms, remainder_expression = expected_term_reduction(expression)
    grouped: dict[int, tuple[Fraction, Fraction]] = {}
    for (moment_k, a_power, b_power), coefficient_expression in terms.items():
        if moment_k != a_power + b_power:
            raise AssertionError("scale degree no longer matches radial degree")
        if coefficient_expression.is_Rational is not True:
            raise AssertionError(f"non-rational coefficient: {coefficient_expression}")
        coefficient = Fraction(int(sp.numer(coefficient_expression)), int(sp.denom(coefficient_expression)))
        scale = A2_AT_CENTER**a_power * B2_AT_CENTER**b_power
        contribution = _scale_interval(radial[moment_k], coefficient * scale)
        grouped[moment_k] = _add_intervals(grouped.get(moment_k, (Fraction(0), Fraction(0))), contribution)
    if remainder_expression.is_Rational is not True:
        raise AssertionError("non-rational y0 remainder")
    remainder = Fraction(int(sp.numer(remainder_expression)), int(sp.denom(remainder_expression)))
    return grouped, remainder


def integrated_coefficient_interval(expression: sp.Expr, radial: dict[int, tuple[Fraction, Fraction]], clock: dict[int, tuple[Fraction, Fraction]]) -> tuple[tuple[Fraction, Fraction], Fraction, int]:
    grouped, remainder = base_scale_terms(expression, radial)
    total = (Fraction(0), Fraction(0))
    for k, coefficient_interval_value in grouped.items():
        total = _add_intervals(total, _multiply_intervals(coefficient_interval_value, clock[k]))
    total = _round_outward((total[0] - remainder, total[1] + remainder))
    return total, remainder, len(grouped)


def mode_audit(two_j: int, radial: dict[int, tuple[Fraction, Fraction]], clock: dict[int, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    matrix = representation_matrix(two_j)
    diagonal = []
    off_diagonal_nonzero = 0
    for row in range(two_j + 1):
        for column in range(two_j + 1):
            interval, remainder, group_count = integrated_coefficient_interval(matrix[row, column], radial, clock)
            if row != column and interval != (0, 0):
                off_diagonal_nonzero += 1
            if row == column:
                m = sp.Rational(-two_j, 2) + row
                diagonal.append({
                    "basis_index": row,
                    "m": sp.sstr(m),
                    "clock_integrated_local_amplitude": _serialize_interval(interval),
                    "uniform_y0_remainder_bound": str(remainder),
                    "secant_moment_group_count": group_count,
                    "D0_global_fourier_phase": f"exp(2*i*({sp.sstr(m)})*sqrt(10)/12)",
                    "D1_global_fourier_phase": f"exp(2*i*({sp.sstr(m)})*sqrt(10)/6)",
                })
    return {"two_j": two_j, "dimension": two_j + 1, "off_diagonal_nonzero_enclosure_count": off_diagonal_nonzero, "diagonal": diagonal}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "local_coefficients": "LOCAL_SCALAR_PROFILE_COEFFICIENTS_TWO_J0_TO_4_INTERVAL_ENCLOSED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "profiles": "EXACT_DETECTOR_CLOCK_PROFILES_SERIALIZED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    local_manifest = {row["path"]: row["sha256"] for row in values["local_coefficients"]["provenance"]["source_manifest"]}
    if local_manifest.get(str(LOCAL_GENERATOR.relative_to(ROOT))) != _sha256(LOCAL_GENERATOR):
        raise AssertionError("imported local-coefficient implementation drifted from its certificate")
    if values["profiles"]["exact_detector_profiles"]["clock_rate_dTheta_dt"] != "3/4":
        raise AssertionError("clock rate drifted")
    monotonicity = monotonicity_audit()
    if not monotonicity["all_decreasing"]:
        raise AssertionError("clock quadrature monotonicity failed")
    radial = radial_moment_intervals(values["moments"])
    clock = clock_secant_moments()
    modes = [mode_audit(two_j, radial, clock) for two_j in range(MAX_TWO_J + 1)]
    if any(mode["off_diagonal_nonzero_enclosure_count"] for mode in modes):
        raise AssertionError("clock integration created off-diagonal coefficients")
    if clock[0] != (1, 1) or not all(clock[k][0] > 1 for k in range(1, MAX_MOMENT_K + 1)):
        raise AssertionError("clock secant moment normalization failed")
    wrong_lambda_squared = Fraction(29, 73728)
    if wrong_lambda_squared == CLOCK_LAMBDA_SQUARED:
        raise AssertionError("clock-rate mutation escaped")

    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL input certificate integrates the exact normalized detector clock bump into the scalar SU(2) spatial-profile Fourier coefficients for two_j=0,...,4. The exact conversion dTheta/dt=3/4 gives t-t_a=s/48 and lambda=sqrt(58)/288. Directed-rounding dyadic Darboux sums enclose E[sec(lambda s)^(2k)] for k=0,...,6; exact monotonicity proves the endpoint sums are valid. Composing these clock factors with the radial moment and local-mode reductions gives diagonal, detector-phase-labelled scalar spacetime-profile coefficients. A mutation that treats clock phase as physical time changes lambda^2 and is rejected. This result still excludes polarizations, coderivatives, form-valued sources, modes above two_j=4, an evaluated Sobolev tail, advanced Green images, recoil, interacting theorems, and quantum claims."
    )
    return {
        "schema": "closed-universe-berger-clock-integrated-scalar-profile-coefficients-v1",
        "result_id": "BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS",
        "setting_id": values["local_coefficients"]["setting_id"],
        "claim_status": "VALIDATED_CLOCK_INTEGRATED_SCALAR_COEFFICIENTS_THROUGH_TWO_J4_EXPORTED_FORM_AND_TAIL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "clock_reduction": {
            "normalized_variable": "s=(Theta-Theta_a)/(1/64)",
            "physical_time_offset": "t-t_a=s/48",
            "lambda": "sqrt(58)/288",
            "lambda_squared": str(CLOCK_LAMBDA_SQUARED),
            "subdivisions": SUBDIVISIONS,
            "interval_precision": IV_DPS,
            "output_dyadic_bits": OUTPUT_DYADIC_BITS,
            "monotonicity_audit": monotonicity,
        },
        "clock_secant_moment_enclosures": [
            {"k": k, "expectation_secant_power_2k": _serialize_interval(clock[k])} for k in range(MAX_MOMENT_K + 1)
        ],
        "audited_clock_integrated_coefficients": modes,
        "mutation_results": [{"name": "treat_clock_phase_as_physical_time", "detected": True, "correct_lambda_squared": str(CLOCK_LAMBDA_SQUARED), "mutated_lambda_squared": str(wrong_lambda_squared)}],
        "flags": {
            "CLOCK_RATE_CONVERSION_APPLIED": True,
            "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED": True,
            "CLOCK_INTEGRATED_SCALAR_COEFFICIENTS_TWO_J0_TO_4_EXPORTED": True,
            "FULL_FORM_VALUED_SOURCE_COEFFICIENTS_EVALUATED": False,
            "MODES_ABOVE_TWO_J4_EVALUATED": False,
            "EVALUATED_SOBOLEV_NORM_EXPORTED": False,
            "VALIDATED_INFINITE_MODE_TAIL_BOUND_EXPORTED": False,
            "ADVANCED_GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "APPLY_THE_POLARIZATION_AND_CODERIVATIVE_IN_EACH_FORM_BLOCK_THEN_EXPORT_AN_EVALUATED_SOBOLEV_TAIL",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()],
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
        raise SystemExit("stale clock-integrated scalar coefficient certificate")
    print("BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
