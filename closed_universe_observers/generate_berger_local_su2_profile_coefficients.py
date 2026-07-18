#!/usr/bin/env python3
"""Enclose low Berger Peter-Weyl coefficients of the fixed spatial bumps."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import C, generators


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_LOCAL_SU2_PROFILE_COEFFICIENT_ENCLOSURES.json"
SCHEMA = PACKAGE / "schema/berger-local-su2-profile-coefficient-enclosures-v1.schema.json"
REPORT = PACKAGE / "reports/berger-local-su2-profile-coefficient-enclosures.md"
DEPENDENCIES = {
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_local_su2_profile_coefficients.py",
    "tests": PACKAGE / "tests/test_berger_local_su2_profile_coefficients.py",
    "schema": SCHEMA,
    "report": REPORT,
}

Y0, Y1, Y2, Y3 = sp.symbols("y0 y1 y2 y3", real=True)
SQUARED_RADIUS = Y1**2 + Y2**2 + Y3**2
EPSILON = Fraction(1, 128)
AMPLITUDE_MIN = Fraction(82915, 82944)
A2_INTERVAL = (EPSILON**2 / 4, EPSILON**2 / (4 * AMPLITUDE_MIN**2))
B2_INTERVAL = (EPSILON**2 * Fraction(10, 9), EPSILON**2 * Fraction(10, 9) / AMPLITUDE_MIN**2)
MAX_Y2 = Fraction(93312, 1374979445)
MAX_TWO_J = 4
MAX_MOMENT_K = 6
OUTPUT_DYADIC_BITS = 160


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fundamental_matrix(*, flip_y1_sign: bool = False) -> sp.Matrix:
    y1 = -Y1 if flip_y1_sign else Y1
    return sp.Matrix([
        [Y0 + sp.I * Y3, Y2 - sp.I * y1],
        [-Y2 - sp.I * y1, Y0 - sp.I * Y3],
    ])


def representation_matrix(two_j: int, *, flip_y1_sign: bool = False) -> sp.Matrix:
    """Normalized symmetric-power representation in ascending m basis."""
    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    u = fundamental_matrix(flip_y1_sign=flip_y1_sign)
    answer = sp.zeros(two_j + 1)
    for column in range(two_j + 1):
        for from_first in range(two_j - column + 1):
            for from_second in range(column + 1):
                row = from_first + from_second
                coefficient = (
                    sp.sqrt(sp.binomial(two_j, column) / sp.binomial(two_j, row))
                    * sp.binomial(two_j - column, from_first)
                    * sp.binomial(column, from_second)
                )
                answer[row, column] += coefficient * (
                    u[0, 0] ** (two_j - column - from_first)
                    * u[1, 0] ** from_first
                    * u[0, 1] ** (column - from_second)
                    * u[1, 1] ** from_second
                )
    return sp.expand(answer)


def generator_defect_count(two_j: int, *, flip_y1_sign: bool = False) -> int:
    matrix = representation_matrix(two_j, flip_y1_sign=flip_y1_sign)
    identity = {Y0: 1, Y1: 0, Y2: 0, Y3: 0}
    derivatives = [sp.simplify(sp.diff(matrix, y).subs(identity) / 2) for y in (Y1, Y2, Y3)]
    expected = generators(two_j)
    expected[2] = sp.simplify(C * expected[2])
    return sum(sp.simplify(derivatives[a][i, j] - expected[a][i, j]) != 0 for a in range(3) for i in range(two_j + 1) for j in range(two_j + 1))


def _odd_double_factorial(value: int) -> int:
    return int(sp.factorial2(value)) if value > 0 else 1


def _canonical_surviving_terms(expression: sp.Expr) -> dict[tuple[int, int, int, int], sp.Expr]:
    """Apply sign parity and exact y1/y2 exchange symmetry before bounding."""
    groups: dict[tuple[int, int, int, int], sp.Expr] = {}
    polynomial = sp.Poly(sp.expand(expression), Y0, Y1, Y2, Y3)
    for (q, e1, e2, e3), coefficient in polynomial.terms():
        if any(exponent % 2 for exponent in (e1, e2, e3)):
            continue
        first, second = sorted((e1, e2))
        key = (q, first, second, e3)
        groups[key] = sp.simplify(groups.get(key, 0) + coefficient)
    return {key: value for key, value in groups.items() if value != 0}


def _polynomial_moment_terms(expression: sp.Expr) -> dict[tuple[int, int, int], sp.Expr]:
    """Reduce even Cartesian monomials to radial moments and A^2,B^2 scales."""
    groups: dict[tuple[int, int, int], sp.Expr] = {}
    polynomial = sp.Poly(sp.expand(expression), Y1, Y2, Y3)
    for (e1, e2, e3), coefficient in polynomial.terms():
        if any(exponent % 2 for exponent in (e1, e2, e3)):
            continue
        a, b, c = e1 // 2, e2 // 2, e3 // 2
        moment_k = a + b + c
        angular = sp.Rational(
            _odd_double_factorial(2 * a - 1) * _odd_double_factorial(2 * b - 1) * _odd_double_factorial(2 * c - 1),
            _odd_double_factorial(2 * moment_k + 1),
        )
        key = (moment_k, a + b, c)
        groups[key] = sp.simplify(groups.get(key, 0) + coefficient * angular)
    return {key: value for key, value in groups.items() if value != 0}


def expected_term_reduction(expression: sp.Expr) -> tuple[dict[tuple[int, int, int], sp.Expr], sp.Expr]:
    """Taylor-reduce odd powers of y0 with a rigorous uniform remainder."""
    reduced: dict[tuple[int, int, int], sp.Expr] = {}
    remainder = sp.Rational(0)
    for (q, e1, e2, e3), coefficient in _canonical_surviving_terms(expression).items():
        degree = e1 + e2 + e3
        vector_monomial = Y1**e1 * Y2**e2 * Y3**e3
        if q % 2 == 0:
            polynomial = coefficient * vector_monomial * (1 - SQUARED_RADIUS) ** (q // 2)
        else:
            order = (2 * MAX_MOMENT_K - degree) // 2
            alpha = sp.Rational(q, 2)
            polynomial = coefficient * vector_monomial * sum(
                sp.binomial(alpha, r) * (-SQUARED_RADIUS) ** r for r in range(order + 1)
            )
            falling = sp.prod(alpha - j for j in range(order + 1))
            denominator_power = int(sp.ceiling(order + 1 - alpha))
            remainder += (
                sp.Abs(coefficient)
                * sp.Abs(falling)
                / sp.factorial(order + 1)
                * sp.Rational(MAX_Y2.numerator, MAX_Y2.denominator) ** (order + 1 + degree // 2)
                / (1 - sp.Rational(MAX_Y2.numerator, MAX_Y2.denominator)) ** denominator_power
            )
        for key, value in _polynomial_moment_terms(polynomial).items():
            reduced[key] = sp.simplify(reduced.get(key, 0) + value)
    return {key: value for key, value in reduced.items() if value != 0}, sp.simplify(remainder)


def _multiply_nonnegative(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return left[0] * right[0], left[1] * right[1]


def _power_nonnegative(interval: tuple[Fraction, Fraction], exponent: int) -> tuple[Fraction, Fraction]:
    return interval[0] ** exponent, interval[1] ** exponent


def _add_scaled(interval: tuple[Fraction, Fraction], coefficient: Fraction, total: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    if coefficient >= 0:
        return total[0] + coefficient * interval[0], total[1] + coefficient * interval[1]
    return total[0] + coefficient * interval[1], total[1] + coefficient * interval[0]


def _serialize_interval(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def _round_outward(interval: tuple[Fraction, Fraction], bits: int = OUTPUT_DYADIC_BITS) -> tuple[Fraction, Fraction]:
    denominator = 2**bits
    lower_numerator = interval[0].numerator * denominator // interval[0].denominator
    upper_numerator = -(-interval[1].numerator * denominator // interval[1].denominator)
    return Fraction(lower_numerator, denominator), Fraction(upper_numerator, denominator)


def radial_moment_intervals(moment_certificate: dict[str, Any]) -> dict[int, tuple[Fraction, Fraction]]:
    return {
        row["k"]: (
            Fraction(row["normalized_even_moment"]["lower"]),
            Fraction(row["normalized_even_moment"]["upper"]),
        )
        for row in moment_certificate["normalized_moments"]["radial_core_dimension_3"]
    }


def coefficient_interval(expression: sp.Expr, moments: dict[int, tuple[Fraction, Fraction]]) -> tuple[tuple[Fraction, Fraction], Fraction, int]:
    terms, remainder_expression = expected_term_reduction(expression)
    total = (Fraction(0), Fraction(0))
    for (moment_k, a_power, b_power), coefficient_expression in terms.items():
        if coefficient_expression.is_Rational is not True or sp.im(coefficient_expression) != 0:
            raise AssertionError(f"non-rational surviving coefficient: {coefficient_expression}")
        coefficient = Fraction(int(sp.numer(coefficient_expression)), int(sp.denom(coefficient_expression)))
        factor = moments[moment_k]
        factor = _multiply_nonnegative(factor, _power_nonnegative(A2_INTERVAL, a_power))
        factor = _multiply_nonnegative(factor, _power_nonnegative(B2_INTERVAL, b_power))
        total = _add_scaled(factor, coefficient, total)
    if remainder_expression.is_Rational is not True:
        raise AssertionError(f"non-rational remainder: {remainder_expression}")
    remainder = Fraction(int(sp.numer(remainder_expression)), int(sp.denom(remainder_expression)))
    return _round_outward((total[0] - remainder, total[1] + remainder)), remainder, len(terms)


def mode_audit(two_j: int, moments: dict[int, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    matrix = representation_matrix(two_j)
    diagonal = []
    off_diagonal_nonzero = 0
    for row in range(two_j + 1):
        for column in range(two_j + 1):
            interval, remainder, term_count = coefficient_interval(matrix[row, column], moments)
            if row != column and interval != (0, 0):
                off_diagonal_nonzero += 1
            if row == column:
                m = sp.Rational(-two_j, 2) + row
                diagonal.append({
                    "basis_index": row,
                    "m": sp.sstr(m),
                    "local_fourier_amplitude": _serialize_interval(interval),
                    "y0_remainder_bound": str(remainder),
                    "reduced_term_count": term_count,
                    "D0_global_fourier_phase": f"exp(2*i*({sp.sstr(m)})*sqrt(10)/12)",
                    "D1_global_fourier_phase": f"exp(2*i*({sp.sstr(m)})*sqrt(10)/6)",
                })
    return {
        "two_j": two_j,
        "dimension": two_j + 1,
        "generator_convention_defect_count": generator_defect_count(two_j),
        "off_diagonal_nonzero_enclosure_count": off_diagonal_nonzero,
        "diagonal": diagonal,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "chart": "EXACT_DETECTOR_RADII_FIXED",
        "spectral": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "rods": "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    moments = radial_moment_intervals(values["moments"])
    modes = [mode_audit(two_j, moments) for two_j in range(MAX_TWO_J + 1)]
    if any(mode["generator_convention_defect_count"] or mode["off_diagonal_nonzero_enclosure_count"] for mode in modes):
        raise AssertionError("local SU(2) coefficient audit failed")
    mutation_defects = generator_defect_count(1, flip_y1_sign=True)
    if mutation_defects == 0:
        raise AssertionError("quaternion-sign mutation escaped")
    odd_remainders = [Fraction(row["y0_remainder_bound"]) for mode in modes if mode["two_j"] % 2 for row in mode["diagonal"]]
    if not odd_remainders or not all(0 < value < Fraction(1, 10**24) for value in odd_remainders):
        raise AssertionError("odd-mode y0 remainder rail failed")

    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL input certificate computes uniform interval enclosures for the normalized scalar spatial-bump SU(2) Fourier matrices in the exact Berger representation convention for two_j=0,...,4. Differentiating the declared quaternion matrix reproduces all certified spin generators. Sign parity, y1-y2 exchange symmetry, and isotropic moment identities make every local Fourier matrix diagonal. Odd powers of y0=sqrt(1-|y|^2) use moments through order twelve and a rigorous Taylor remainder below 10^-24 on the fixed detector support. The exact detector-center phases convert local diagonal entries to the two global Hopf-centered Fourier matrices, uniformly over both clock windows. These are scalar spatial-profile coefficients only: clock integration, polarizations, coderivatives, form-valued sources, modes above two_j=4, an evaluated infinite spectral tail, advanced Green images, recoil, interacting theorems, and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-local-su2-profile-coefficient-enclosures-v1",
        "result_id": "BERGER_LOCAL_SU2_PROFILE_COEFFICIENT_ENCLOSURES",
        "setting_id": values["moments"]["setting_id"],
        "claim_status": "VALIDATED_LOCAL_SCALAR_PROFILE_COEFFICIENTS_THROUGH_TWO_J4_EXPORTED_FULL_SOURCE_AND_TAIL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "representation_convention": {
            "fundamental_matrix": "[[y0+i*y3,y2-i*y1],[-y2-i*y1,y0-i*y3]]",
            "basis": "normalized Sym^(two_j)(C^2), ordered by m=-j,-j+1,...,j",
            "infinitesimal_curve": "y_a=s/2 at identity",
            "global_fourier_convention": "hat(rho)(j)=integral rho(g) D_j(g)^* dSigma; for g=g_a h, hat(rho)=hat(rho_local) D_j(g_a)^*",
        },
        "uniform_window_geometry": {
            "rod_radius": "1/128",
            "rod_amplitude_interval": [str(AMPLITUDE_MIN), "1"],
            "A_squared_interval_for_y1_y2": [str(A2_INTERVAL[0]), str(A2_INTERVAL[1])],
            "B_squared_interval_for_y3": [str(B2_INTERVAL[0]), str(B2_INTERVAL[1])],
            "maximum_y_squared": str(MAX_Y2),
            "output_dyadic_bits": OUTPUT_DYADIC_BITS,
            "detector_center_phases": {"D0": "sqrt(10)/12", "D1": "sqrt(10)/6"},
        },
        "audited_mode_coefficients": modes,
        "mutation_results": [{"name": "flip_fundamental_y1_sign", "detected": True, "generator_defect_count": mutation_defects}],
        "flags": {
            "REPRESENTATION_CONVENTION_MATCHES_CERTIFIED_GENERATORS": True,
            "LOCAL_SCALAR_PROFILE_COEFFICIENTS_TWO_J0_TO_4_INTERVAL_ENCLOSED": True,
            "Y0_BINOMIAL_REMAINDER_VALIDATED": True,
            "DETECTOR_CENTER_PHASES_EXPORTED": True,
            "FULL_FORM_VALUED_SOURCE_COEFFICIENTS_EVALUATED": False,
            "MODES_ABOVE_TWO_J4_EVALUATED": False,
            "EVALUATED_SOBOLEV_NORM_EXPORTED": False,
            "VALIDATED_INFINITE_MODE_TAIL_BOUND_EXPORTED": False,
            "ADVANCED_GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "INTEGRATE_THE_CLOCK_FACTOR_AND_FORM_POLARIZATION_THEN_EXPORT_AN_EVALUATED_SOBOLEV_TAIL_CONSTANT",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()
            ],
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
        raise SystemExit("stale local SU(2) profile coefficient certificate")
    print("BERGER_LOCAL_SU2_PROFILE_COEFFICIENT_ENCLOSURES generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
