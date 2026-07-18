#!/usr/bin/env python3
"""Bound clock derivatives of the moving Berger detector profile."""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
import sympy as sp

from closed_universe_observers.generate_berger_clock_integrated_form_profile_coefficients import AMPLITUDE_LOWER
from closed_universe_observers.generate_berger_clock_uniform_profile_sobolev_n1 import _d, _laplacian, _sqrt_upper
from closed_universe_observers.generate_berger_correlated_profile_sobolev_n1 import (
    _canonical_hash, _evaluate_terms, _iv_fraction, _odd_double_factorial,
    _replace_bump_factors, _round_upper,
)
from closed_universe_observers.generate_berger_global_detector_rods import C, X
from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import gershgorin_lower_from_j
from closed_universe_observers.generate_berger_two_j4_profile_tail_obstruction import EPSILON
from closed_universe_observers.generate_berger_validated_flat_bump_moments import _interval_endpoints


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_MOVING_PROFILE_CLOCK_DERIVATIVE_TAIL.json"
SCHEMA = PACKAGE / "schema/berger-moving-profile-clock-derivative-tail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-moving-profile-clock-derivative-tail.md"
DEPENDENCIES = {
    "profile_n1": PACKAGE / "certificates/BERGER_CORRELATED_PROFILE_SOBOLEV_N1.json",
    "clock_envelope": PACKAGE / "certificates/BERGER_CLOCK_MICROPHASE_TAIL_ENVELOPE.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "tail_reduction": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json",
}
SOURCE_FILES = [Path(__file__), PACKAGE / "verify_berger_moving_profile_clock_derivative_tail.py", PACKAGE / "tests/test_berger_moving_profile_clock_derivative_tail.py", SCHEMA, REPORT]
SUBDIVISIONS = 4096
IV_DPS = 50
OUTPUT_DYADIC_BITS = 128
CURRENT_RETAINED_MAX_TWO_J = 1024
BUMP_DERIVATIVE_GLOBAL_BOUNDS = (
    Fraction(1), Fraction(3, 2), Fraction(675, 32),
    Fraction(1633851, 2048), Fraction(3861199773, 65536),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def angular_term_ledger(polarization: str, amplitude_derivative_order: int) -> tuple[tuple[Fraction, tuple[int, ...]], ...]:
    amplitude = sp.symbols("a", positive=True)
    y0 = sp.symbols("Y", positive=True)
    u1, u2, u3, radius = sp.symbols("u1 u2 u3 r", real=True)
    derivatives = sp.symbols("b0:5", real=True)
    sqrt10, pi_symbol = sp.symbols("sqrt10 pi_bound", positive=True)
    bump = sp.Function("B")
    q = 4 * amplitude**2 * 128**2 * (C**2 * X[3] ** 2 + X[1] ** 2 + X[2] ** 2)
    coordinates = {X[0]: y0, X[1]: EPSILON*u2/(2*amplitude), X[2]: EPSILON*u3/(2*amplitude), X[3]: EPSILON*u1/(2*C*amplitude)}
    rod = 2*C*amplitude*X[3] if polarization == "axial" else 2*amplitude*X[1]
    raw = {key: amplitude**3 * X[0] * bump(q) * value for key, value in _d({(): rod}).items()}
    laplacian = _laplacian(raw)
    components = [sp.expand(_replace_bump_factors(sp.diff(laplacian[key], amplitude, amplitude_derivative_order), bump, derivatives).subs(coordinates)) for key in sorted(laplacian)]
    squared_density = sp.expand(sum(value*value for value in components) / (amplitude**3*y0))
    angular = sp.Integer(0)
    parity_zero_count = 0
    for term in sp.Add.make_args(squared_density):
        factors = term.as_powers_dict()
        exponents = [int(factors.pop(variable, 0)) for variable in (u1, u2, u3)]
        if any(exponent % 2 for exponent in exponents):
            parity_zero_count += 1
            continue
        half = [exponent // 2 for exponent in exponents]
        moment = 4 * sp.pi * sp.Rational(
            _odd_double_factorial(2*half[0]-1) * _odd_double_factorial(2*half[1]-1) * _odd_double_factorial(2*half[2]-1),
            _odd_double_factorial(2*sum(half)+1),
        )
        angular += sp.prod(base**power for base, power in factors.items()) * moment * radius**sum(exponents)
    angular = sp.expand(angular).xreplace({sp.sqrt(10): sqrt10, sp.pi: pi_symbol})
    variables = (radius, amplitude, y0, *derivatives, sqrt10, pi_symbol)
    rows = []
    for term in sp.Add.make_args(angular):
        factors = term.as_powers_dict()
        exponents = tuple(int(factors.pop(variable, 0)) for variable in variables)
        coefficient = sp.prod(base**power for base, power in factors.items())
        if coefficient.is_Rational is not True:
            raise AssertionError(f"non-rational angular coefficient {coefficient}")
        rows.append((Fraction(int(sp.numer(coefficient)), int(sp.denom(coefficient))), exponents))
    rows.sort(key=lambda item: (item[1], item[0]))
    angular_term_ledger.audit[(polarization, amplitude_derivative_order)] = {
        "preangular_expanded_term_count": len(sp.Add.make_args(squared_density)),
        "parity_zero_term_count": parity_zero_count,
        "radial_interval_term_count": len(rows),
    }
    return tuple(rows)


angular_term_ledger.audit = {}  # type: ignore[attr-defined]


def _bump_derivatives(radius: Any) -> tuple[Any, ...]:
    q = radius*radius
    t = 1/(1-q)
    bump = mp.iv.exp(1-t)
    return (bump, -t**2*bump, (t**4-2*t**3)*bump, (-t**6+6*t**5-6*t**4)*bump, (t**8-12*t**7+36*t**6-24*t**5)*bump)


def _quadrature_upper(polarization: str, derivative_order: int, subdivisions: int = SUBDIVISIONS) -> tuple[Fraction, dict[str, Any]]:
    mp.iv.dps = IV_DPS
    terms = angular_term_ledger(polarization, derivative_order)
    amplitude = _iv_fraction(AMPLITUDE_LOWER, Fraction(1))
    sqrt10 = _iv_fraction(Fraction(3), Fraction(4))
    pi_bound = _iv_fraction(Fraction(3), Fraction(4))
    width = Fraction(1, subdivisions)
    total = Fraction(0)
    for index in range(subdivisions):
        lower, upper = Fraction(index, subdivisions), Fraction(index+1, subdivisions)
        radius = _iv_fraction(lower, upper)
        if index == subdivisions-1:
            bump_values = tuple(_iv_fraction(-bound, bound) if order else _iv_fraction(0, 1) for order, bound in enumerate(BUMP_DERIVATIVE_GLOBAL_BOUNDS))
        else:
            bump_values = _bump_derivatives(radius)
        y0_lower = 1 - EPSILON**2 * upper**2 * Fraction(10, 9) / AMPLITUDE_LOWER**2
        y0 = _iv_fraction(y0_lower, Fraction(1))
        integrand = _evaluate_terms(terms, (radius, amplitude, y0, *bump_values, sqrt10, pi_bound)) * radius**2
        total += width * _interval_endpoints(integrand)[1]
    return _round_upper(total), {
        "subdivisions": subdivisions,
        "raw_radial_angular_integral_upper": str(_round_upper(total)),
        "angular_reduction": angular_term_ledger.audit[(polarization, derivative_order)],  # type: ignore[attr-defined]
        "canonical_angular_term_ledger_sha256": _canonical_hash([[str(c), list(e)] for c, e in terms]),
    }


@lru_cache(maxsize=1)
def _calculation() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    moment = next(row for row in values["moments"]["raw_radial_integral_enclosures"] if row["power"] == 2)
    cb3_lower = 12 * Fraction(moment["integral"]["lower"])
    by_detector = {row["detector_id"]: row for row in values["profile_n1"]["polarization_bounds"]}
    derivative_rows = []
    for polarization, detector_id in (("axial", "D0"), ("transverse", "D1")):
        row = {"detector_id": detector_id, "polarization": polarization, "amplitude_derivatives": []}
        for order in (1, 2):
            raw_upper, audit = _quadrature_upper(polarization, order)
            norm_squared = raw_upper * EPSILON**-3 / cb3_lower**2
            norm_upper = _sqrt_upper(norm_squared, OUTPUT_DYADIC_BITS)
            row["amplitude_derivatives"].append({"order": order, **audit, "normalized_Delta1_amplitude_derivative_L2_norm_squared_upper": str(norm_squared), "normalized_Delta1_amplitude_derivative_L2_norm_upper": str(norm_upper), "normalized_Delta1_amplitude_derivative_L2_norm_upper_decimal": f"{float(norm_upper):.12e}"})
        derivative_rows.append(row)

    envelope = values["clock_envelope"]["clock_envelope"]
    denominator_lower = Fraction(envelope["clock_bump_denominator"]["lower"])
    denominator_upper = Fraction(envelope["clock_bump_denominator"]["upper"])
    nu = Fraction(envelope["external_clock_frequency_nu"]["upper"])
    max_slope = Fraction(envelope["flat_bump_derivative_audit"]["maximum_abs_slope_upper"])
    rows = []
    for derivative_row in derivative_rows:
        detector_id = derivative_row["detector_id"]
        n0 = Fraction(by_detector[detector_id]["normalized_Delta1_profile_L2_norm_upper"])
        n1, n2 = [Fraction(item["normalized_Delta1_amplitude_derivative_L2_norm_upper"]) for item in derivative_row["amplitude_derivatives"]]
        h_second_l1 = 2*max_slope*n0 + 2*nu*n1 + denominator_upper*nu**2*(n1+n2)
        normalized_h_second = h_second_l1 / denominator_lower
        rows.append({**derivative_row, "clock_derivative_combination": {"Delta1_H_second_derivative_L1_upper": str(_round_upper(h_second_l1)), "normalized_Delta1_H_second_derivative_L1_upper": str(_round_upper(normalized_h_second))}})
    def tail(row: dict[str, Any], retained: int) -> Fraction:
        lam = gershgorin_lower_from_j(Fraction(retained+1, 2))
        return _round_upper(2304 * Fraction(row["clock_derivative_combination"]["normalized_Delta1_H_second_derivative_L1_upper"]) / lam**2)
    for row in rows:
        row["tail_L2_upper_after_two_j1024"] = str(tail(row, CURRENT_RETAINED_MAX_TWO_J))
        row["tail_L2_upper_after_two_j1024_decimal"] = f"{float(tail(row, CURRENT_RETAINED_MAX_TWO_J)):.12e}"
    sufficient = None
    for retained in range(CURRENT_RETAINED_MAX_TWO_J, 100_001):
        if all(tail(row, retained) < 1 for row in rows):
            sufficient = retained
            break
    if sufficient is None:
        raise AssertionError("moving-profile sufficient cutoff search failed")
    return {"cb3_rational_lower": str(cb3_lower), "polarization_bounds": rows, "first_sufficient_moving_profile_retained_max_two_j": sufficient, "sufficient_cutoff_tail_uppers": {row["detector_id"]: str(tail(row, sufficient)) for row in rows}, "previous_cutoff_tail_uppers": {row["detector_id"]: str(tail(row, sufficient-1)) for row in rows}}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {"profile_n1": "VALIDATED_CORRELATED_CLOCK_UNIFORM_DELTA1_NORM_EXPORTED", "clock_envelope": "UNIFORM_FIXED_VECTOR_CLOCK_MICROPHASE_ENVELOPE_EXPORTED", "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED", "tail_reduction": "GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED"}
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    calculation = _calculation()
    boundary = "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result differentiates the actual rod- and Gram-dependent detector profile at fixed Berger spatial point through second order in its clock amplitude, encloses the correlated physical-space norms of Delta1 partial_a F and Delta1 partial_a^2 F, and combines them with the exact flat-bump total-variation identities in an operator-valued two-integration-by-parts estimate. It certifies a physical moving-profile Maxwell tail upper bound and a sufficient cutoff for this bound, but does not construct the complete retained projection, the massive-two-form continuation, detector response or rank, recoil, tangent-cone restriction, active Bridge 3, finite-r/all-orders observer-morphism stability, or a quantum claim."
    return {"schema": "closed-universe-berger-moving-profile-clock-derivative-tail-v1", "result_id": "BERGER_MOVING_PROFILE_CLOCK_DERIVATIVE_TAIL", "setting_id": values["profile_n1"]["setting_id"], "claim_status": "MOVING_PROFILE_CLOCK_DERIVATIVE_AND_MAXWELL_TAIL_BOUND_CERTIFIED_COMPLETE_PROJECTION_OPEN", "atlas_status": "CERTIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"], "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()}, "method": {"moving_profile": "F(a)=rho(a) a^3 y0 dR_I(a), differentiated at fixed Berger spatial point before rod-coordinate substitution", "clock_amplitude": "a(s)=cos(sqrt(58)s/288)", "operator_identity": "integral B(s) cos(s sqrt(Delta1)/48)F(a(s)) ds = -2304 Delta1^(-1) integral cos(...) d_s^2[B(s)F(a(s))] ds", "chain_rule": "H''=B''F+2B'a'F_a+B(a''F_a+(a')^2F_aa)"}, "calculation": calculation, "mutation_results": [{"name": "drop_second_amplitude_derivative_channel", "detected": all(Fraction(row["amplitude_derivatives"][1]["normalized_Delta1_amplitude_derivative_L2_norm_upper"]) > 0 for row in calculation["polarization_bounds"])}], "flags": {"MOVING_DETECTOR_PROFILE_CLOCK_DERIVATIVE_BOUND_EXPORTED": True, "VALIDATED_PHYSICAL_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": True, "CURRENT_TWO_J1024_MOVING_PROFILE_BOUND_CERTIFIES_SMALL_TAIL": all(Fraction(row["tail_L2_upper_after_two_j1024"]) < 1 for row in calculation["polarization_bounds"]), "COMPLETE_LOW_MODE_PROJECTION_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "MASSIVE_TWO_FORM_TAIL_BOUND_EXPORTED": False, "DETECTOR_RESPONSE_EVALUATED": False, "QUANTUM_CLAIM": False}, "next_gate": "BUILD_THE_COMPLETE_RETAINED_PROJECTION_TO_THE_CERTIFIED_MOVING_PROFILE_CUTOFF_THEN_COMPOSE_THE_MASSIVE_TWO_FORM_IMAGE", "claim_boundary": boundary, "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    value = build(); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True)+"\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=rendered): raise SystemExit("stale moving-profile clock-derivative tail certificate")
    print("BERGER_MOVING_PROFILE_CLOCK_DERIVATIVE_TAIL generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
