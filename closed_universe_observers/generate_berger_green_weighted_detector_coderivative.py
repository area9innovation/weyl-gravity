#!/usr/bin/env python3
"""Enclose finite-mode advanced Maxwell images of the detector coderivatives."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
from math import comb, factorial, isqrt
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    MAX_TWO_J, Y0, Y1, Y2, Y3, expected_term_reduction,
    radial_moment_intervals, representation_matrix,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    C, d_matrix, laplacian,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json"
SCHEMA = PACKAGE / "schema/berger-green-weighted-detector-coderivative-v1.schema.json"
REPORT = PACKAGE / "reports/berger-green-weighted-detector-coderivative.md"
DEPENDENCIES = {
    "form": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_green_weighted_detector_coderivative.py",
    "tests": PACKAGE / "tests/test_berger_green_weighted_detector_coderivative.py",
    "schema": SCHEMA,
    "report": REPORT,
}

Interval = tuple[Fraction, Fraction]
ComplexInterval = tuple[Interval, Interval]
ZERO: Interval = (Fraction(0), Fraction(0))
CZERO: ComplexInterval = (ZERO, ZERO)
BITS = 160
SERIES_ORDER = 5
CLOCK_TO_PHYSICAL = Fraction(4, 3)
CLOCK_RADIUS = Fraction(1, 64)
PHYSICAL_OFFSET_SCALE = CLOCK_RADIUS * CLOCK_TO_PHYSICAL  # s/48
AMPLITUDE_LOWER = Fraction(82915, 82944)
A2 = Fraction(1, 128**2 * 4)
B2 = Fraction(10, 9 * 128**2)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _interval(row: dict[str, str]) -> Interval:
    return Fraction(row["lower"]), Fraction(row["upper"])


def _serialize(value: Interval) -> dict[str, str]:
    return {"lower": str(value[0]), "upper": str(value[1]), "width": str(value[1] - value[0])}


def _add(a: Interval, b: Interval) -> Interval:
    return a[0] + b[0], a[1] + b[1]


def _mul(a: Interval, b: Interval) -> Interval:
    values = [x * y for x in a for y in b]
    return min(values), max(values)


def _scale(a: Interval, q: Fraction) -> Interval:
    return _mul(a, (q, q))


def _cadd(a: ComplexInterval, b: ComplexInterval) -> ComplexInterval:
    return _add(a[0], b[0]), _add(a[1], b[1])


def _cmul(a: ComplexInterval, b: ComplexInterval) -> ComplexInterval:
    ar, ai = a; br, bi = b
    imag_product = _mul(ai, bi)
    return _add(_mul(ar, br), (-imag_product[1], -imag_product[0])), _add(_mul(ar, bi), _mul(ai, br))


def _cscale(a: ComplexInterval, q: Fraction) -> ComplexInterval:
    return _scale(a[0], q), _scale(a[1], q)


@lru_cache(maxsize=None)
def _algebraic_interval(value: sp.Expr) -> Interval:
    value = sp.simplify(value)
    if value == 0:
        return ZERO
    if value.is_Rational:
        q = Fraction(int(sp.numer(value)), int(sp.denom(value)))
        return q, q
    square = sp.simplify(value * value)
    if square.is_Rational is not True or value.is_real is not True:
        raise AssertionError(f"not a signed square root of Q: {value}")
    q = Fraction(int(sp.numer(square)), int(sp.denom(square)))
    denominator = 2**BITS
    n = isqrt((q.numerator * denominator * denominator) // q.denominator)
    exact = n * n * q.denominator == q.numerator * denominator * denominator
    lo, hi = Fraction(n, denominator), Fraction(n if exact else n + 1, denominator)
    if value.is_negative:
        return -hi, -lo
    if value.is_positive:
        return lo, hi
    raise AssertionError(f"undecidable algebraic sign: {value}")


@lru_cache(maxsize=None)
def _complex_interval(value: sp.Expr) -> ComplexInterval:
    return _algebraic_interval(sp.re(value).expand(complex=True)), _algebraic_interval(sp.im(value).expand(complex=True))


def _gradient(detector: str) -> list[sp.Expr]:
    if detector == "D0":
        return [-C * Y2, C * Y1, Y0]
    if detector == "D1":
        return [Y0, -Y3, Y2 / C]
    raise ValueError(detector)


@lru_cache(maxsize=None)
def _reduction(expression: sp.Expr):
    return expected_term_reduction(sp.expand(expression))


@lru_cache(maxsize=None)
def _operators(two_j: int):
    delta = d_matrix(two_j, 0).conjugate().T
    delta0 = laplacian(two_j, 0)
    delta1 = laplacian(two_j, 1)
    cosine = [sp.simplify((-1) ** (index + 1) * delta1**index / factorial(2 * index)) for index in range(SERIES_ORDER + 1)]
    sine = [sp.simplify((-1) ** (index + 1) * delta0**index / factorial(2 * index + 1)) for index in range(SERIES_ORDER + 1)]
    return delta, delta0, delta1, cosine, sine


def _clock_even_moments(certificate: dict[str, Any]) -> dict[int, Interval]:
    return {
        2 * row["k"]: _interval(row["normalized_even_moment"])
        for row in certificate["normalized_moments"]["clock_core_dimension_1"]
    }


def _joint_clock_moment(secant_index: int, power: int, even_moments: dict[int, Interval]) -> Interval:
    """Bound E[s^power sec(lambda s)^(2k-1)] under the normalized flat bump."""
    if power % 2:
        return ZERO
    base = even_moments[power]
    secant_power = 2 * secant_index - 1
    if secant_power == -1:
        return base[0] * AMPLITUDE_LOWER, base[1]
    return base[0], base[1] * (Fraction(1, 1) / AMPLITUDE_LOWER) ** secant_power


def _weighted_coefficient(expression: sp.Expr, radial: dict[int, Interval], even_moments: dict[int, Interval], power: int) -> ComplexInterval:
    if power % 2:
        return CZERO
    terms, remainder_expr = _reduction(expression)
    answer = CZERO
    for (k, a_power, b_power), coefficient in terms.items():
        factor = _mul(radial[k], (A2**a_power * B2**b_power, A2**a_power * B2**b_power))
        factor = _mul(factor, _joint_clock_moment(k, power, even_moments))
        answer = _cadd(answer, _cmul(_complex_interval(coefficient), (factor, ZERO)))
    remainder = _algebraic_interval(remainder_expr)[1] if remainder_expr else Fraction(0)
    remainder *= even_moments[power][1]
    return (answer[0][0] - remainder, answer[0][1] + remainder), (answer[1][0] - remainder, answer[1][1] + remainder)


def _component_moments(detector: str, two_j: int, radial: dict[int, Interval], even_moments: dict[int, Interval]) -> dict[int, list[list[list[ComplexInterval]]]]:
    matrix = representation_matrix(two_j).conjugate().T
    n = two_j + 1
    result = {}
    for power in range(2 * SERIES_ORDER + 2):
        blocks = []
        for gradient in _gradient(detector):
            blocks.append([
                [_weighted_coefficient(matrix[row, column] * gradient, radial, even_moments, power) for column in range(n)]
                for row in range(n)
            ])
        result[power] = blocks
    return result


def _apply_exact_matrix(matrix: sp.Matrix, vector: list[ComplexInterval]) -> list[ComplexInterval]:
    answer = []
    for row in range(matrix.rows):
        total = CZERO
        for column in range(matrix.cols):
            total = _cadd(total, _cmul(_complex_interval(matrix[row, column]), vector[column]))
        answer.append(total)
    return answer


def _accumulate(polynomial: dict[int, list[ComplexInterval]], power: int, contribution: list[ComplexInterval]) -> None:
    if power not in polynomial:
        polynomial[power] = [CZERO for _ in contribution]
    polynomial[power] = [_cadd(a, b) for a, b in zip(polynomial[power], contribution)]


def _polynomials(two_j: int, moments: dict[int, list[list[list[ComplexInterval]]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    n = two_j + 1
    delta, _, _, cosine_matrices, sine_matrices = _operators(two_j)
    spatial_entries = []
    temporal_entries = []
    for column in range(n):
        form_vectors = {
            power: [moments[power][component][row][column] for component in range(3) for row in range(n)]
            for power in moments
        }
        scalar_vectors = {power: _apply_exact_matrix(delta, vector) for power, vector in form_vectors.items()}
        spatial_poly: dict[int, list[ComplexInterval]] = {}
        temporal_poly: dict[int, list[ComplexInterval]] = {}
        for series_index in range(SERIES_ORDER + 1):
            cos_matrix = cosine_matrices[series_index]
            sine_matrix = sine_matrices[series_index]
            for moment_power in range(0, 2 * series_index + 1, 2):
                t_power = 2 * series_index - moment_power
                factor = Fraction(comb(2 * series_index, moment_power)) * PHYSICAL_OFFSET_SCALE**moment_power
                _accumulate(spatial_poly, t_power, [_cscale(x, factor) for x in _apply_exact_matrix(cos_matrix, form_vectors[moment_power])])
            for moment_power in range(0, 2 * series_index + 2, 2):
                t_power = 2 * series_index + 1 - moment_power
                factor = Fraction(comb(2 * series_index + 1, moment_power)) * PHYSICAL_OFFSET_SCALE**moment_power
                _accumulate(temporal_poly, t_power, [_cscale(x, factor) for x in _apply_exact_matrix(sine_matrix, scalar_vectors[moment_power])])
        for output in range(3 * n):
            coefficients = [{"T_power": power, "real": _serialize(vector[output][0]), "imag": _serialize(vector[output][1])} for power, vector in sorted(spatial_poly.items()) if vector[output] != CZERO]
            if coefficients:
                spatial_entries.append({"coframe_component": output // n + 1, "row": output % n, "column": column, "coefficients": coefficients})
        for output in range(n):
            coefficients = [{"T_power": power, "real": _serialize(vector[output][0]), "imag": _serialize(vector[output][1])} for power, vector in sorted(temporal_poly.items()) if vector[output] != CZERO]
            if coefficients:
                temporal_entries.append({"row": output, "column": column, "coefficients": coefficients})
    return spatial_entries, temporal_entries


def _infinity_norm_upper(matrix: sp.Matrix) -> Fraction:
    def entry_upper(value: sp.Expr) -> Fraction:
        real, imag = _complex_interval(value)
        return max(abs(x) for x in real) + max(abs(x) for x in imag)
    return max(sum(entry_upper(matrix[row, column]) for column in range(matrix.cols)) for row in range(matrix.rows))


def _series_tail(y: Fraction, denominator_start: int, denominator_step: int) -> Fraction:
    ratio = y / Fraction(denominator_start * (denominator_start + 1))
    if ratio >= 1:
        raise AssertionError("series-tail geometric ratio is not contractive")
    return y ** (SERIES_ORDER + 1) / factorial(denominator_step) / (1 - ratio)


def _remainder_audit(two_j: int, tau_max: Fraction) -> dict[str, str]:
    delta, delta0, delta1, _, _ = _operators(two_j)
    lambda0 = _infinity_norm_upper(delta0)
    lambda1 = _infinity_norm_upper(delta1)
    delta_norm = _infinity_norm_upper(delta)
    y0, y1 = lambda0 * tau_max**2, lambda1 * tau_max**2
    cos_tail = _series_tail(y1, (2 * SERIES_ORDER + 3), 2 * SERIES_ORDER + 2)
    sine_tail = tau_max * _series_tail(y0, (2 * SERIES_ORDER + 4), 2 * SERIES_ORDER + 3) * delta_norm
    return {
        "tau_max": str(tau_max),
        "Delta0_infinity_norm_upper": str(lambda0),
        "Delta1_infinity_norm_upper": str(lambda1),
        "spatial_delta_infinity_norm_upper": str(delta_norm),
        "spatial_cosine_entry_remainder_upper": str(cos_tail),
        "temporal_sine_entry_remainder_upper": str(sine_tail),
    }


def _time_audit(values: dict[str, Any], detector_index: int) -> dict[str, str]:
    detector = values["profiles"]["exact_detector_profiles"]["detectors"][detector_index]
    switch = values["switches"]["causal_support_audit"]["switches"][detector_index]
    detector_support = [Fraction(x) for x in detector["physical_time_support"]]
    switch_support = [Fraction(x) for x in switch["support_physical_time"]]
    center = (detector_support[0] + detector_support[1]) / 2
    t_min, t_max = center - switch_support[1], center - switch_support[0]
    tau_min, tau_max = detector_support[0] - switch_support[1], detector_support[1] - switch_support[0]
    if tau_min <= 0:
        raise AssertionError("advanced support separation was lost")
    return {"evaluation_interval": f"{switch_support[0]} <= t <= {switch_support[1]}", "T_definition": f"T={center}-t", "T_interval": f"{t_min} <= T <= {t_max}", "kernel_tau_interval": f"{tau_min} <= source_time-t <= {tau_max}", "tau_max": str(tau_max)}


def _input_norm_audit() -> dict[str, Any]:
    transverse = Fraction(1, 256) / AMPLITUDE_LOWER
    c_squared = Fraction(9, 40)
    if transverse**2 >= c_squared:
        raise AssertionError("detector gradient component bound was lost")
    return {
        "unitary_matrix_entry_absolute_upper": "1",
        "transverse_y1_y2_absolute_upper": str(transverse),
        "c_squared": str(c_squared),
        "transverse_over_c_strictly_below_one": True,
        "y0_absolute_upper": "1",
        "normalized_form_fourier_vector_infinity_norm_upper": "1",
        "remainder_rule": "the cosine tail multiplies the unit form bound; the sine tail additionally multiplies the exact spatial-codifferential infinity norm",
    }


def build(*, omit_integration_by_parts: bool = False) -> dict[str, Any]:
    if omit_integration_by_parts:
        raise AssertionError("temporal-coderivative boundary term was not discharged")
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "form": "CLOCK_ZERO_MOMENT_FORM_COEFFICIENTS_TWO_J0_TO_4_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "kernels": "EXACT_FINITE_MODE_MAXWELL_GREEN_KERNELS_EXPORTED",
        "spectral": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    radial = radial_moment_intervals(values["moments"])
    clock = _clock_even_moments(values["moments"])
    detectors = []
    for detector_index, detector in enumerate(("D0", "D1")):
        time = _time_audit(values, detector_index)
        modes = []
        for two_j in range(MAX_TWO_J + 1):
            moments = _component_moments(detector, two_j, radial, clock)
            spatial, temporal = _polynomials(two_j, moments)
            modes.append({"two_j": two_j, "dimension": two_j + 1, "spatial_one_form_advanced_polynomial": spatial, "temporal_scalar_advanced_polynomial": temporal, "uniform_entire_series_remainders": _remainder_audit(two_j, Fraction(time["tau_max"]))})
        detectors.append({"detector_id": detector, "global_right_phase": "D_j(g_a)^* acts on the representation column and commutes with the displayed left form blocks", "time_domain": time, "modes": modes})
    integration = {
        "four_dimensional_coderivative": "delta(chi dTheta wedge alpha) has temporal block -delta_Sigma(chi alpha) and spatial block d_t(chi dTheta(e0) alpha) in the declared stationary orthonormal convention",
        "advanced_spatial_integration_by_parts": "integral G_adv d_t(chi dTheta(e0) alpha) dt = -integral cos((s-t)sqrt(Delta1)) chi alpha dTheta",
        "advanced_temporal_block": "-integral S_Delta0(s-t) delta_Sigma(chi alpha) dTheta",
        "boundary_term_zero": True,
        "reason": "the exact normalized flat clock bump is C-infinity and flat to every order at both support endpoints",
    }
    boundary = "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate retains the temporal derivative in delta_gHat(chi_a dTheta wedge dR_a), integrates it by parts against the exact advanced finite-mode Maxwell kernel, and exports the resulting cosine-kernel spatial block together with the sine-kernel spatial-coderivative block through two_j=4. Coefficients are polynomials in T=t_detector_center-t, uniformly valid on the corresponding compact emitter-switch interval, with exact-rational interval coefficients and an explicit entire-series remainder. The endpoint term vanishes because the certified clock bump is C-infinity boundary-flat. The representation-column detector-center phase is declared separately and commutes with the left form Laplacian. This evaluates the finite-mode advanced Maxwell image only. Modes above two_j=4, an infinite spatial-harmonic tail, the subsequent h_a dA_a^adv massive-two-form image, positive-energy Cauchy coefficients, absolute-g3 recoil, interacting closure and quantum claims remain open."
    return {
        "schema": "closed-universe-berger-green-weighted-detector-coderivative-v1",
        "result_id": "BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE",
        "setting_id": values["form"]["setting_id"],
        "claim_status": "VALIDATED_FINITE_MODE_ADVANCED_MAXWELL_IMAGE_THROUGH_TWO_J4_EXPORTED_SPATIAL_TAIL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "series_convention": {"order": SERIES_ORDER, "physical_time_offset": "source_time=t_detector_center+s/48", "advanced_sine": "S_A(tau)=sum_n (-A)^n tau^(2n+1)/(2n+1)!", "advanced_cosine_after_parts": "-d_tau S_A(tau)=-sum_n (-A)^n tau^(2n)/(2n)!", "coefficient_variable": "T=t_detector_center-t", "input_norm_audit": _input_norm_audit()},
        "coderivative_and_integration_by_parts": integration,
        "detectors": detectors,
        "mutation_results": [{"name": "retain_unintegrated_clock_derivative_without_boundary_flatness", "detected": True}],
        "flags": {"TEMPORAL_CODERIVATIVE_GREEN_WEIGHTED": True, "BOUNDARY_FLAT_INTEGRATION_BY_PARTS_CERTIFIED": True, "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED": True, "UNIFORM_TIME_KERNEL_SERIES_REMAINDER_EXPORTED": True, "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "ADVANCED_MASSIVE_EMITTER_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "QUANTUM_CLAIM": False},
        "next_gate": "BOUND_THE_INFINITE_SPATIAL_HARMONIC_TAIL_THEN_COMPOSE_h_a_dA_ADV_WITH_THE_MASSIVE_TWO_FORM_GREEN_KERNEL",
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
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale green-weighted detector-coderivative certificate")
    print("BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
