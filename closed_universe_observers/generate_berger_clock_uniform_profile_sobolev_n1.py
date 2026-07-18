#!/usr/bin/env python3
"""Certify a clock-uniform N=1 Berger detector-profile Sobolev tail bound."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.core.function import AppliedUndef

from closed_universe_observers.generate_berger_clock_integrated_form_profile_coefficients import AMPLITUDE_LOWER
from closed_universe_observers.generate_berger_global_detector_rods import C, X, _frame_derivative
from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import gershgorin_lower_from_j
from closed_universe_observers.generate_berger_two_j4_profile_tail_obstruction import EPSILON, MAX_Y_SQUARED


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CLOCK_UNIFORM_PROFILE_SOBOLEV_N1.json"
SCHEMA = PACKAGE / "schema/berger-clock-uniform-profile-sobolev-n1-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-uniform-profile-sobolev-n1.md"
DEPENDENCIES = {
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "coderivative": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "tail_reduction": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json",
    "normalization_repair": PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_clock_uniform_profile_sobolev_n1.py",
    PACKAGE / "tests/test_berger_clock_uniform_profile_sobolev_n1.py",
    SCHEMA,
    REPORT,
]
RETAINED_MAX_TWO_J = 1024
SQRT_DYADIC_BITS = 128


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _wedge(first: tuple[int, ...], second: tuple[int, ...]) -> tuple[tuple[int, ...] | None, int]:
    sequence = list(first) + list(second)
    if len(set(sequence)) != len(sequence):
        return None, 0
    inversions = sum(sequence[i] > sequence[j] for i in range(len(sequence)) for j in range(i + 1, len(sequence)))
    return tuple(sorted(sequence)), (-1) ** inversions


_D_THETA = [{(1, 2): -1 / C}, {(0, 2): 1 / C}, {(0, 1): -C}]


def _d(form: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    output: dict[tuple[int, ...], sp.Expr] = {}
    for basis, coefficient in form.items():
        for axis in range(3):
            target, sign = _wedge((axis,), basis)
            if target is not None:
                output[target] = output.get(target, 0) + sign * _frame_derivative(coefficient, axis)
        for index, basis_axis in enumerate(basis):
            for pair, structure_coefficient in _D_THETA[basis_axis].items():
                first, sign1 = _wedge(basis[:index], pair)
                if first is None:
                    continue
                target, sign2 = _wedge(first, basis[index + 1 :])
                if target is not None:
                    output[target] = output.get(target, 0) + (-1) ** index * sign1 * sign2 * structure_coefficient * coefficient
    return {key: sp.expand(value) for key, value in output.items() if value != 0}


def _star(form: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    output: dict[tuple[int, ...], sp.Expr] = {}
    for basis, coefficient in form.items():
        complement = tuple(axis for axis in (0, 1, 2) if axis not in basis)
        volume, sign = _wedge(basis, complement)
        if volume != (0, 1, 2):
            raise AssertionError("Hodge-star orientation drifted")
        output[complement] = output.get(complement, 0) + sign * coefficient
    return output


def _delta(form: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    if not form:
        return {}
    degree = len(next(iter(form)))
    return {key: (-1) ** degree * value for key, value in _star(_d(_star(form))).items()}


def _laplacian(form: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    output: dict[tuple[int, ...], sp.Expr] = {}
    for contribution in (_d(_delta(form)), _delta(_d(form))):
        for key, value in contribution.items():
            output[key] = output.get(key, 0) + value
    return {key: sp.expand(value) for key, value in output.items() if value != 0}


def _operator_audit() -> dict[str, Any]:
    scalar_defects = [sp.simplify(_laplacian({(): coordinate})[()] - sp.Rational(29, 18) * coordinate) for coordinate in X]
    rod = 2 * C * X[3]
    d_rod = _d({(): rod})
    lap_d_rod = _laplacian(d_rod)
    commutator_defects = [sp.simplify(lap_d_rod.get(key, 0) - sp.Rational(29, 18) * value) for key, value in d_rod.items()]
    if any(scalar_defects + commutator_defects):
        raise AssertionError("physical-space Hodge Laplacian disagrees with the certified spectral engine")
    return {
        "delta_convention": "delta=(-1)^p star d star on spatial p-forms",
        "scalar_coordinate_eigenvalue": "29/18",
        "scalar_coordinate_defect_count": sum(value != 0 for value in scalar_defects),
        "d_Delta_equals_Delta_d_defect_count": sum(value != 0 for value in commutator_defects),
    }


def _bump_derivative_bounds() -> list[Fraction]:
    """Bounds for B(q)=exp(1-1/(1-q)), q in [0,1], through B''."""
    u = sp.symbols("u", positive=True)
    polynomial = sp.Integer(1)
    rows: list[Fraction] = []
    for _ in range(3):
        bound = Fraction(0)
        for (power,), coefficient in sp.Poly(polynomial, u).terms():
            # exp(1-u) u^p is maximized at u=max(1,p).  For p>1 use
            # exp(1-p)<(3/8)^(p-1), which follows from e>8/3.
            monomial_bound = Fraction(1) if power == 0 else Fraction(power**power) * Fraction(3, 8) ** (power - 1)
            bound += abs(int(coefficient)) * monomial_bound
        rows.append(bound)
        polynomial = sp.expand(u**2 * (sp.diff(polynomial, u) - polynomial))
    if rows != [Fraction(1), Fraction(3, 2), Fraction(675, 32)]:
        raise AssertionError("flat-bump derivative bounds drifted")
    return rows


def _algebraic_coefficient_upper(value: sp.Expr) -> Fraction:
    value = sp.simplify(abs(value)).xreplace({sp.sqrt(10): sp.Integer(4)})
    if value.is_Rational is not True:
        raise AssertionError(f"unexpected coefficient in Sobolev expression: {value}")
    return Fraction(int(sp.numer(value)), int(sp.denom(value)))


def _component_bound(expression: sp.Expr, bump: sp.FunctionClass, amplitude: sp.Symbol, derivative_bounds: list[Fraction]) -> Fraction:
    coordinate_bounds = {
        X[0]: Fraction(1),
        X[1]: EPSILON / (2 * AMPLITUDE_LOWER),
        X[2]: EPSILON / (2 * AMPLITUDE_LOWER),
        X[3]: EPSILON / (2 * Fraction(9, 20) * AMPLITUDE_LOWER),
    }
    total = Fraction(0)
    for term in sp.Add.make_args(sp.expand(expression)):
        substitutions = list(term.atoms(sp.Subs))
        applications = [item for item in term.atoms(AppliedUndef) if item.func == bump]
        if substitutions:
            if len(substitutions) != 1:
                raise AssertionError("term contains multiple bump derivatives")
            bump_factor = substitutions[0]
            derivative_order = bump_factor.expr.derivative_count
        else:
            if len(applications) != 1:
                raise AssertionError("term contains no unique bump factor")
            bump_factor = applications[0]
            derivative_order = 0
        factors = sp.cancel(term / bump_factor).as_powers_dict()
        bound = Fraction(1)
        for variable in (amplitude, *X):
            power = int(factors.pop(variable, 0))
            if variable == amplitude:
                if power < 0:
                    bound *= AMPLITUDE_LOWER**power
            else:
                bound *= coordinate_bounds[variable] ** power
        bound *= _algebraic_coefficient_upper(sp.prod(base**power for base, power in factors.items()))
        bound *= derivative_bounds[derivative_order]
        total += bound
    return total


def _sqrt_upper(value: Fraction, bits: int = SQRT_DYADIC_BITS) -> Fraction:
    scaled = (value.numerator * 2 ** (2 * bits) + value.denominator - 1) // value.denominator
    root = math.isqrt(scaled)
    if root * root < scaled:
        root += 1
    return Fraction(root, 2**bits)


def _polarization_row(name: str, rod: sp.Expr, amplitude: sp.Symbol, q: sp.Expr, bump: sp.FunctionClass, normalization_upper: Fraction, sqrt_volume_upper: Fraction, spectral_lower: Fraction) -> dict[str, Any]:
    raw = {key: sp.expand(amplitude**3 * X[0] * bump(q) * value) for key, value in _d({(): rod}).items()}
    laplacian = _laplacian(raw)
    derivative_bounds = _bump_derivative_bounds()
    components = [_component_bound(laplacian[key], bump, amplitude, derivative_bounds) for key in sorted(laplacian)]
    pointwise_upper = sum(components, Fraction(0)) * normalization_upper
    sobolev_upper = pointwise_upper * sqrt_volume_upper
    tail_upper = sobolev_upper / spectral_lower
    return {
        "polarization": name,
        "coframe_component_term_counts": [len(sp.Add.make_args(laplacian[key])) for key in sorted(laplacian)],
        "unnormalized_component_absolute_upper_bounds": [str(value) for value in components],
        "normalized_Delta1_profile_pointwise_norm_upper": str(pointwise_upper),
        "clock_uniform_Delta1_profile_L2_norm_upper": str(sobolev_upper),
        "clock_uniform_Delta1_profile_L2_norm_upper_decimal": f"{float(sobolev_upper):.12e}",
        "tail_L2_upper_after_two_j1024": str(tail_upper),
        "tail_L2_upper_after_two_j1024_decimal": f"{float(tail_upper):.12e}",
        "small_tail_certified": False,
    }


def _mutation_audit(rod: sp.Expr, amplitude: sp.Symbol, q: sp.Expr, bump: sp.FunctionClass, correct_row: dict[str, Any]) -> list[dict[str, Any]]:
    d_rod = _d({(): rod})
    correct_components = [Fraction(value) for value in correct_row["unnormalized_component_absolute_upper_bounds"]]
    without_gram = _laplacian({key: sp.expand(bump(q) * value) for key, value in d_rod.items()})
    without_gram_components = [_component_bound(without_gram[key], bump, amplitude, _bump_derivative_bounds()) for key in sorted(without_gram)]
    correct_raw = {key: sp.expand(amplitude**3 * X[0] * bump(q) * value) for key, value in d_rod.items()}
    correct_laplacian = _laplacian(correct_raw)
    wrong_derivatives = [Fraction(1), Fraction(3, 2), Fraction(3, 2)]
    wrong_derivative_components = [_component_bound(correct_laplacian[key], bump, amplitude, wrong_derivatives) for key in sorted(correct_laplacian)]
    return [
        {"name": "drop_gram_factor_a3_y0_from_profile", "detected": without_gram_components != correct_components},
        {"name": "replace_flat_bump_second_derivative_bound_by_first_derivative_bound", "detected": wrong_derivative_components != correct_components},
    ]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "chart": "EXACT_DETECTOR_RADII_FIXED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "rods": "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "coderivative": "BOUNDARY_FLAT_INTEGRATION_BY_PARTS_CERTIFIED",
        "tail_reduction": "GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED",
        "normalization_repair": "PROFILE_CHANGE_OF_VARIABLES_NORMALIZATION_REPAIRED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if values["chart"]["selected_profiles"]["epsilon_0"] != "1/128" or values["chart"]["selected_profiles"]["epsilon_1"] != "1/128":
        raise AssertionError("detector radius drifted")

    moment_row = next(row for row in values["moments"]["raw_radial_integral_enclosures"] if row["power"] == 2)
    radial_integral_lower = Fraction(moment_row["integral"]["lower"])
    normalization_upper = EPSILON**-3 / (12 * radial_integral_lower)
    gram_lower = AMPLITUDE_LOWER**3 * (1 - MAX_Y_SQUARED)
    support_volume_upper = Fraction(16, 3) * EPSILON**3 / gram_lower
    sqrt_volume_upper = _sqrt_upper(support_volume_upper)
    spectral_lower = gershgorin_lower_from_j(Fraction(RETAINED_MAX_TWO_J + 1, 2))

    amplitude = sp.symbols("a", positive=True)
    q = 4 * amplitude**2 * 128**2 * (C**2 * X[3] ** 2 + X[1] ** 2 + X[2] ** 2)
    bump = sp.Function("B")
    polarizations = [
        _polarization_row("D0:dR0_1 axial", 2 * C * amplitude * X[3], amplitude, q, bump, normalization_upper, sqrt_volume_upper, spectral_lower),
        _polarization_row("D1:dR1_2 transverse", 2 * amplitude * X[1], amplitude, q, bump, normalization_upper, sqrt_volume_upper, spectral_lower),
    ]
    if not all(Fraction(row["tail_L2_upper_after_two_j1024"]) > 1 for row in polarizations):
        raise AssertionError("coarse N=1 rail unexpectedly certified a small tail")
    mutations = _mutation_audit(2 * C * amplitude * X[3], amplitude, q, bump, polarizations[0])
    if not all(row["detected"] for row in mutations):
        raise AssertionError("profile Sobolev mutation rail failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result applies the physical-space Berger Hodge Laplacian once to each normalized detector form F_a(t)=rho_a J_a dR_aI, with J_a=a(t)^3 y0 and dSigma=d^3R/J_a. The differential operator exactly reproduces Delta0 x_mu=(29/18)x_mu and Delta1 dR=d Delta0 R. Rational support, flat-bump derivative, normalization and volume bounds give clock-uniform L2 enclosures for ||Delta1 F_a(t)||. Combining them with the certified first-omitted spectral lower bound above two_j=1024 gives finite Maxwell spatial and coderivative tail upper bounds of about 4.98e4 and 5.05e4. The nonnegative unit clock bump makes the same bound valid after clock integration, and the exact-T Maxwell multipliers add no amplification. This is a rigorous but deliberately coarse N=1 triangle/Darboux enclosure: it does not certify a small tail, convergence of the current working rail, a complete low-mode projection, a full Maxwell or massive-two-form image, detector response or rank, recoil, tangent-cone restriction, active Bridge 3, nonlinear observer-morphism stability or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-clock-uniform-profile-sobolev-n1-v1",
        "result_id": "BERGER_CLOCK_UNIFORM_PROFILE_SOBOLEV_N1",
        "setting_id": values["profiles"]["setting_id"],
        "claim_status": "CERTIFIED_CLOCK_UNIFORM_N1_PROFILE_SOBOLEV_AND_FINITE_TAIL_UPPER_BOUND_SMALL_TAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "operator_audit": _operator_audit(),
        "profile_convention": {
            "detector_center_phase_disposition": "the Hopf U(1) right phase is an isometry of the Berger metric and commutes with the left form Laplacian",
            "amplitude_interval": [str(AMPLITUDE_LOWER), "1"],
            "local_rod_coordinates": ["R1-c1=2 c a y3", "R2-c2=2 a y1", "R3-c3=2 a y2"],
            "bump_argument": "q=|R-c|^2/epsilon^2, B(q)=exp(1-1/(1-q)) for 0<=q<1",
            "spatial_form": "F_a(t)=B(q)/(epsilon^3 C_B3) a^3 y0 dR_aI",
            "normalization": "C_B3=4 pi integral_0^1 r^2 B(r^2) dr; the imported radial bump uses the equivalent B(radius)",
        },
        "rational_bound_ledger": {
            "sqrt10_lower_for_c": "sqrt(10)>3, hence c>9/20",
            "sqrt10_upper_for_coefficients": "sqrt(10)<4",
            "pi_bounds": "3<pi<4",
            "e_lower_for_bump_derivatives": "e>8/3",
            "bump_derivative_absolute_uppers_orders_0_1_2": [str(value) for value in _bump_derivative_bounds()],
            "radial_normalization_integral_lower": str(radial_integral_lower),
            "inverse_profile_normalization_upper": str(normalization_upper),
            "gram_jacobian_lower_on_support": str(gram_lower),
            "support_berger_volume_upper": str(support_volume_upper),
            "support_berger_volume_sqrt_upper": str(sqrt_volume_upper),
            "retained_max_two_j": RETAINED_MAX_TWO_J,
            "first_omitted_delta1_lower": str(spectral_lower),
        },
        "polarization_bounds": polarizations,
        "clock_and_green_transfer": {
            "clock_profile_nonnegative_unit_integral": True,
            "spatial_exact_T_multiplier_norm_upper": "1",
            "coderivative_sine_exact_T_multiplier_norm_upper": "1",
            "same_uniform_tail_bound_after_clock_integration": True,
        },
        "mutation_results": mutations,
        "flags": {
            "PHYSICAL_SPACE_HODGE_LAPLACIAN_MATCHES_SPECTRAL_ENGINE": True,
            "CLOCK_UNIFORM_POLARIZED_DELTA1_PROFILE_NORM_EXPORTED": True,
            "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_UPPER_BOUND_EXPORTED": True,
            "CURRENT_N1_BOUND_CERTIFIES_SMALL_TAIL": False,
            "COMPLETE_LOW_MODE_PROJECTION_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "MASSIVE_TWO_FORM_TAIL_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPLACE_THE_COARSE_N1_TRIANGLE_BOUND_BY_A_CORRELATED_SQUARED_NORM_QUADRATURE_OR_WIDEN_THE_COMPLETE_RETAINED_RAIL_BEFORE_FULL_IMAGE_PROMOTION",
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
        raise SystemExit("stale clock-uniform profile Sobolev N1 certificate")
    print("BERGER_CLOCK_UNIFORM_PROFILE_SOBOLEV_N1 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
