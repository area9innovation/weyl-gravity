#!/usr/bin/env python3
"""Validate a correlated squared-norm N=1 Berger detector-profile tail bound."""
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
from closed_universe_observers.generate_berger_global_detector_rods import C, X
from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import gershgorin_lower_from_j
from closed_universe_observers.generate_berger_two_j4_profile_tail_obstruction import EPSILON
from closed_universe_observers.generate_berger_validated_flat_bump_moments import _interval_endpoints


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CORRELATED_PROFILE_SOBOLEV_N1.json"
SCHEMA = PACKAGE / "schema/berger-correlated-profile-sobolev-n1-v1.schema.json"
REPORT = PACKAGE / "reports/berger-correlated-profile-sobolev-n1.md"
DEPENDENCIES = {
    "coarse_n1": PACKAGE / "certificates/BERGER_CLOCK_UNIFORM_PROFILE_SOBOLEV_N1.json",
    "normalization": PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json",
    "tail_reduction": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_correlated_profile_sobolev_n1.py",
    PACKAGE / "tests/test_berger_correlated_profile_sobolev_n1.py",
    SCHEMA,
    REPORT,
]
SUBDIVISIONS = 4096
IV_DPS = 50
OUTPUT_DYADIC_BITS = 128
RETAINED_MAX_TWO_J = 1024


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _odd_double_factorial(value: int) -> int:
    answer = 1
    for factor in range(1, value + 1, 2):
        answer *= factor
    return answer


def _replace_bump_factors(expression: sp.Expr, bump: sp.FunctionClass, derivative_symbols: tuple[sp.Symbol, ...]) -> sp.Expr:
    for substitution in list(expression.atoms(sp.Subs)):
        expression = expression.xreplace({substitution: derivative_symbols[substitution.expr.derivative_count]})
    for application in list(expression.atoms(sp.Function)):
        if getattr(application, "func", None) == bump:
            expression = expression.xreplace({application: derivative_symbols[0]})
    return expression


@lru_cache(maxsize=None)
def angular_term_ledger(polarization: str) -> tuple[tuple[Fraction, tuple[int, ...]], ...]:
    amplitude = sp.symbols("a", positive=True)
    y0 = sp.symbols("Y", positive=True)
    u1, u2, u3, radius = sp.symbols("u1 u2 u3 r", real=True)
    b0, b1, b2 = sp.symbols("b0 b1 b2", real=True)
    sqrt10, pi_symbol = sp.symbols("sqrt10 pi_bound", positive=True)
    bump = sp.Function("B")
    q = 4 * amplitude**2 * 128**2 * (C**2 * X[3] ** 2 + X[1] ** 2 + X[2] ** 2)
    coordinates = {
        X[0]: y0,
        X[1]: EPSILON * u2 / (2 * amplitude),
        X[2]: EPSILON * u3 / (2 * amplitude),
        X[3]: EPSILON * u1 / (2 * C * amplitude),
    }
    if polarization == "axial":
        rod = 2 * C * amplitude * X[3]
    elif polarization == "transverse":
        rod = 2 * amplitude * X[1]
    else:
        raise ValueError(f"unknown polarization {polarization}")
    raw = {key: amplitude**3 * X[0] * bump(q) * value for key, value in _d({(): rod}).items()}
    laplacian = _laplacian(raw)
    components = [
        sp.expand(_replace_bump_factors(laplacian[key], bump, (b0, b1, b2)).subs(coordinates))
        for key in sorted(laplacian)
    ]
    squared_density = sp.expand(sum(value * value for value in components) / (amplitude**3 * y0))
    angular = sp.Integer(0)
    preangular_count = len(sp.Add.make_args(squared_density))
    parity_zero_count = 0
    for term in sp.Add.make_args(squared_density):
        factors = term.as_powers_dict()
        exponents = [int(factors.pop(variable, 0)) for variable in (u1, u2, u3)]
        if any(exponent % 2 for exponent in exponents):
            parity_zero_count += 1
            continue
        half = [exponent // 2 for exponent in exponents]
        moment = 4 * sp.pi * sp.Rational(
            _odd_double_factorial(2 * half[0] - 1)
            * _odd_double_factorial(2 * half[1] - 1)
            * _odd_double_factorial(2 * half[2] - 1),
            _odd_double_factorial(2 * sum(half) + 1),
        )
        angular += sp.prod(base**power for base, power in factors.items()) * moment * radius ** sum(exponents)
    angular = sp.expand(angular).xreplace({sp.sqrt(10): sqrt10, sp.pi: pi_symbol})
    variables = (radius, amplitude, y0, b0, b1, b2, sqrt10, pi_symbol)
    rows: list[tuple[Fraction, tuple[int, ...]]] = []
    for term in sp.Add.make_args(angular):
        factors = term.as_powers_dict()
        exponents = tuple(int(factors.pop(variable, 0)) for variable in variables)
        coefficient = sp.prod(base**power for base, power in factors.items())
        if coefficient.is_Rational is not True:
            raise AssertionError(f"non-rational angular coefficient {coefficient}")
        rows.append((Fraction(int(sp.numer(coefficient)), int(sp.denom(coefficient))), exponents))
    rows.sort(key=lambda item: (item[1], item[0]))
    # Attach structural counts to the cached function for the build-time audit.
    angular_term_ledger.audit[polarization] = {
        "preangular_expanded_term_count": preangular_count,
        "parity_zero_term_count": parity_zero_count,
        "radial_interval_term_count": len(rows),
    }
    return tuple(rows)


angular_term_ledger.audit = {}  # type: ignore[attr-defined]


def _iv_fraction(lower: Fraction, upper: Fraction) -> Any:
    return mp.iv.mpf([mp.mpf(lower.numerator) / lower.denominator, mp.mpf(upper.numerator) / upper.denominator])


def _evaluate_terms(terms: tuple[tuple[Fraction, tuple[int, ...]], ...], inputs: tuple[Any, ...]) -> Any:
    answer = _iv_fraction(Fraction(0), Fraction(0))
    for coefficient, exponents in terms:
        term = _iv_fraction(coefficient, coefficient)
        for value, exponent in zip(inputs, exponents):
            term *= value**exponent
        answer += term
    return answer


def _round_upper(value: Fraction, bits: int = OUTPUT_DYADIC_BITS) -> Fraction:
    denominator = 2**bits
    numerator = -(-value.numerator * denominator // value.denominator)
    return Fraction(numerator, denominator)


def _quadrature_upper(polarization: str, subdivisions: int) -> tuple[Fraction, dict[str, Any]]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    mp.iv.dps = IV_DPS
    terms = angular_term_ledger(polarization)
    width = Fraction(1, subdivisions)
    amplitude = _iv_fraction(AMPLITUDE_LOWER, Fraction(1))
    sqrt10 = _iv_fraction(Fraction(3), Fraction(4))
    pi_bound = _iv_fraction(Fraction(3), Fraction(4))
    total = Fraction(0)
    last_cell_used_global_derivative_bounds = False
    for index in range(subdivisions):
        lower = Fraction(index, subdivisions)
        upper = Fraction(index + 1, subdivisions)
        radius = _iv_fraction(lower, upper)
        if index == subdivisions - 1:
            bump_values = (
                _iv_fraction(Fraction(0), Fraction(1)),
                _iv_fraction(Fraction(-3, 2), Fraction(0)),
                _iv_fraction(Fraction(-675, 32), Fraction(675, 32)),
            )
            last_cell_used_global_derivative_bounds = True
        else:
            q_interval = radius * radius
            reciprocal = 1 / (1 - q_interval)
            bump = mp.iv.exp(1 - reciprocal)
            bump_values = (bump, -reciprocal**2 * bump, (reciprocal**4 - 2 * reciprocal**3) * bump)
        # On the rod ball, 1-y0^2 <= eps^2 r^2/(a_min^2)*max(1/4,1/(4c^2)),
        # and c^2=9/40 makes the maximum 10/9.  sqrt(1-z)>=1-z.
        y0_lower = 1 - EPSILON**2 * upper**2 * Fraction(10, 9) / AMPLITUDE_LOWER**2
        y0 = _iv_fraction(y0_lower, Fraction(1))
        integrand = _evaluate_terms(terms, (radius, amplitude, y0, *bump_values, sqrt10, pi_bound)) * radius**2
        total += width * _interval_endpoints(integrand)[1]
    return _round_upper(total), {
        "subdivisions": subdivisions,
        "interval_decimal_precision": IV_DPS,
        "output_dyadic_bits": OUTPUT_DYADIC_BITS,
        "last_cell_used_global_derivative_bounds": last_cell_used_global_derivative_bounds,
        "raw_radial_angular_integral_upper": str(_round_upper(total)),
    }


@lru_cache(maxsize=1)
def _calculation() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    moment_row = next(row for row in values["moments"]["raw_radial_integral_enclosures"] if row["power"] == 2)
    radial_integral_lower = Fraction(moment_row["integral"]["lower"])
    cb3_lower = 12 * radial_integral_lower
    spectral_lower = gershgorin_lower_from_j(Fraction(RETAINED_MAX_TWO_J + 1, 2))
    prior = {row["polarization"].split(":", 1)[0]: Fraction(row["tail_L2_upper_after_two_j1024"]) for row in values["coarse_n1"]["polarization_bounds"]}
    rows = []
    for polarization, detector_id in (("axial", "D0"), ("transverse", "D1")):
        raw_upper, quadrature = _quadrature_upper(polarization, SUBDIVISIONS)
        norm_squared_upper = raw_upper * EPSILON**-3 / cb3_lower**2
        norm_upper = _sqrt_upper(norm_squared_upper, OUTPUT_DYADIC_BITS)
        tail_upper = norm_upper / spectral_lower
        rows.append({
            "detector_id": detector_id,
            "polarization": polarization,
            "angular_reduction": angular_term_ledger.audit[polarization],  # type: ignore[attr-defined]
            "canonical_angular_term_ledger_sha256": _canonical_hash([[str(c), list(e)] for c, e in angular_term_ledger(polarization)]),
            "quadrature": quadrature,
            "normalized_Delta1_profile_L2_norm_squared_upper": str(norm_squared_upper),
            "normalized_Delta1_profile_L2_norm_upper": str(norm_upper),
            "normalized_Delta1_profile_L2_norm_upper_decimal": f"{float(norm_upper):.12e}",
            "tail_L2_upper_after_two_j1024": str(tail_upper),
            "tail_L2_upper_after_two_j1024_decimal": f"{float(tail_upper):.12e}",
            "prior_triangle_tail_upper": str(prior[detector_id]),
            "strictly_improves_prior_triangle_bound": tail_upper < prior[detector_id],
            "small_tail_certified": tail_upper < 1,
        })
    mutation_upper, _ = _quadrature_upper("axial", SUBDIVISIONS // 2)
    return {
        "radial_integral_lower": str(radial_integral_lower),
        "cb3_rational_lower": str(cb3_lower),
        "first_omitted_delta1_lower": str(spectral_lower),
        "polarization_bounds": rows,
        "mutation_results": [{"name": "halve_radial_subdivisions", "detected": mutation_upper > Fraction(rows[0]["quadrature"]["raw_radial_angular_integral_upper"]), "mutated_raw_upper": str(mutation_upper)}],
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "coarse_n1": "CLOCK_UNIFORM_POLARIZED_DELTA1_PROFILE_NORM_EXPORTED",
        "normalization": "PROFILE_CHANGE_OF_VARIABLES_NORMALIZATION_REPAIRED",
        "tail_reduction": "GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "chart": "EXACT_DETECTOR_RADII_FIXED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    calculation = _calculation()
    rows = calculation["polarization_bounds"]
    if not all(row["strictly_improves_prior_triangle_bound"] for row in rows):
        raise AssertionError("correlated quadrature did not improve the termwise bound")
    if any(row["small_tail_certified"] for row in rows):
        raise AssertionError("current correlated N1 rail unexpectedly certified a small tail")
    if not all(row["angular_reduction"]["radial_interval_term_count"] == 21 for row in rows):
        raise AssertionError("angular reduction term count drifted")
    if not all(row["detected"] for row in calculation["mutation_results"]):
        raise AssertionError("correlated quadrature mutation was not detected")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result replaces the coarse termwise N=1 detector-profile estimate by a correlated squared-norm enclosure. Exact sign parity removes angularly odd monomials and the Berger-sphere moment formula reduces each polarization to 21 radial interval terms. A 4096-cell directed-rounding Darboux sum retains the full component squares, the shared rod amplitude, the repaired y0 Gram factor, and correlated B,B',B'' values away from the boundary-flat final cell. The resulting clock-uniform Delta1 profile norms are below approximately 5.11e8, and the certified first-omitted factor above two_j=1024 gives Maxwell spatial/coderivative tail upper bounds below approximately 1.95e3. This strictly improves the earlier 4.98e4/5.05e4 triangle bounds, but it does not certify a small tail or obstruct the true tail: it only shows that this validated N=1 enclosure is insufficient for full-image promotion. It does not fill the incomplete retained projection, construct full Maxwell or massive-two-form images, evaluate detector response or rank, recoil, tangent-cone restriction, activate Bridge 3, promote nonlinear observer-morphism stability, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-correlated-profile-sobolev-n1-v1",
        "result_id": "BERGER_CORRELATED_PROFILE_SOBOLEV_N1",
        "setting_id": values["coarse_n1"]["setting_id"],
        "claim_status": "VALIDATED_CORRELATED_N1_PROFILE_NORM_AND_FINITE_TAIL_UPPER_BOUND_SMALL_TAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "method": {
            "squared_density": "sum_i |Delta1(rho J dR_I)_i|^2/(a^3 y0) before rod-coordinate integration",
            "rod_ball_coordinates": "R-c=epsilon r n with q=r^2",
            "angular_moment": "integral_S2 n1^(2a)n2^(2b)n3^(2c)=4pi (2a-1)!!(2b-1)!!(2c-1)!!/(2a+2b+2c+1)!!",
            "odd_parity_rule": "all monomials odd in any n_i integrate to zero because y0 depends only on n_i^2",
            "y0_interval": "1-epsilon^2 r_hi^2(10/9)/a_min^2 <= y0 <= 1",
            "algebraic_intervals": ["3<sqrt(10)<4", "3<pi<4"],
            "radial_quadrature": "uniform dyadic Darboux cells with mpmath iv directed rounding",
            "boundary_cell": "use global |B|<=1, |B'|<=3/2, |B''|<=675/32 on the final cell touching r=1",
        },
        "normalization_and_spectral_inputs": {key: calculation[key] for key in ("radial_integral_lower", "cb3_rational_lower", "first_omitted_delta1_lower")},
        "polarization_bounds": rows,
        "mutation_results": calculation["mutation_results"],
        "flags": {
            "CORRELATED_COMPONENT_SQUARES_RETAINED": True,
            "EXACT_ANGULAR_PARITY_REDUCTION_EXPORTED": True,
            "VALIDATED_CORRELATED_CLOCK_UNIFORM_DELTA1_NORM_EXPORTED": True,
            "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_UPPER_BOUND_EXPORTED": True,
            "CURRENT_CORRELATED_N1_BOUND_CERTIFIES_SMALL_TAIL": False,
            "TRUE_TAIL_OBSTRUCTED": False,
            "COMPLETE_LOW_MODE_PROJECTION_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "MASSIVE_TWO_FORM_TAIL_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "WIDEN_A_COMPLETE_RETAINED_RAIL_OR_BUILD_A_DIRECT_CORRELATED_GREEN_TAIL_ESTIMATOR_BEFORE_FULL_IMAGE_PROMOTION",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]},
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
        raise SystemExit("stale correlated profile Sobolev N1 certificate")
    print("BERGER_CORRELATED_PROFILE_SOBOLEV_N1 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
