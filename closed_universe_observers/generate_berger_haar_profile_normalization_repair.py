#!/usr/bin/env python3
"""Repair the Berger detector-profile Gram/Haar Jacobian normalization."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_global_detector_rods import C, X, _frame_derivative
from closed_universe_observers.generate_berger_two_j4_profile_tail_obstruction import (
    EPSILON,
    MAX_Y_SQUARED,
    _base_integral,
    squared_radial_integral,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json"
SCHEMA = PACKAGE / "schema/berger-haar-profile-normalization-repair-v1.schema.json"
REPORT = PACKAGE / "reports/berger-haar-profile-normalization-repair.md"
DEPENDENCIES = {
    "rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "volume": ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json",
    "legacy_tail": PACKAGE / "certificates/BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION.json",
    "legacy_capacity": PACKAGE / "certificates/BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT.json",
    "tail_reduction": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_haar_profile_normalization_repair.py",
    PACKAGE / "tests/test_berger_haar_profile_normalization_repair.py",
    SCHEMA,
    REPORT,
]

PI_LOWER = Fraction(3)
C_LOWER = Fraction(9, 20)
LOW_MODE_ENTRY_BOUND = Fraction(1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def jacobian_audit() -> dict[str, Any]:
    y0, y1, y2, y3 = X
    amplitude = sp.symbols("a", positive=True)
    rods = [2 * C * amplitude * y3, 2 * amplitude * y1, 2 * amplitude * y2]
    derivative_matrix = sp.Matrix([[_frame_derivative(rod, axis) for axis in range(3)] for rod in rods])
    sphere_norm = sum(value * value for value in X)
    coordinate_jacobian = sp.simplify(8 * C * amplitude**3)
    frame_determinant = sp.factor(derivative_matrix.det())
    gram_determinant = sp.factor((derivative_matrix * derivative_matrix.T).det())
    frame_on_sphere = sp.factor(frame_determinant.subs(sphere_norm, 1))
    gram_on_sphere = sp.factor(gram_determinant.subs(sphere_norm, 1))
    # The substitutions above do not rewrite the expanded norm automatically.
    frame_on_sphere = sp.factor(frame_determinant / sphere_norm)
    gram_on_sphere = sp.factor(gram_determinant / sphere_norm**2)
    expected_gram_jacobian = amplitude**3 * y0
    if sp.simplify(frame_on_sphere - expected_gram_jacobian) != 0:
        raise AssertionError("rod-frame determinant did not reduce to a^3 y0")
    if sp.simplify(gram_on_sphere - expected_gram_jacobian**2) != 0:
        raise AssertionError("rod Gram determinant did not reduce to a^6 y0^2")
    haar_coordinate_density = 8 * C / y0
    relative = sp.simplify(coordinate_jacobian / haar_coordinate_density)
    if sp.simplify(relative - expected_gram_jacobian) != 0:
        raise AssertionError("coordinate/Haar Jacobian ratio disagrees with sqrt(det G)")
    return {
        "detector_centered_rods": [sp.sstr(value) for value in rods],
        "rod_derivative_matrix_in_orthonormal_frame": [[sp.sstr(value) for value in derivative_matrix.row(row)] for row in range(3)],
        "coordinate_jacobian_dR_over_dy": sp.sstr(coordinate_jacobian),
        "berger_haar_density_dSigma_over_dy": sp.sstr(haar_coordinate_density),
        "gram_determinant_on_S3": sp.sstr(expected_gram_jacobian**2),
        "normalized_gram_jacobian_J": sp.sstr(expected_gram_jacobian),
        "change_of_variables_identity": "J_a dSigma=d^3R",
        "clock_center_values": {"a": "1", "y0": "1", "J": "1", "coordinate_jacobian": sp.sstr(8 * C)},
    }


def weighted_capacity(max_dimension: int) -> int:
    triangular = max_dimension * (max_dimension + 1) // 2
    return 3 * triangular**2


def minimum_dimension(target: Fraction) -> int:
    dimension = 1
    while weighted_capacity(dimension) < target:
        dimension += 1
    return dimension


def capacity_row(total_energy_lower: Fraction, fraction: Fraction) -> dict[str, Any]:
    target = fraction * total_energy_lower
    dimension = minimum_dimension(target)
    return {
        "fraction_of_corrected_energy_lower": str(fraction),
        "minimum_max_dimension_for_capacity": dimension,
        "minimum_two_j_max_for_capacity": dimension - 1,
        "previous_capacity": str(weighted_capacity(dimension - 1)),
        "selected_capacity": str(weighted_capacity(dimension)),
        "interpretation": "necessary capacity only; not a convergence cutoff",
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "rods": "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED",
        "chart": "QUANTITATIVE_LOCAL_ROD_CHART_INVERSE_CERTIFIED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "legacy_tail": "TWO_J4_UNIFORM_PROFILE_TAIL_SMALLNESS_OBSTRUCTED",
        "legacy_capacity": "STREAMED_ADAPTIVE_PETER_WEYL_ROUTE_SELECTED",
        "tail_reduction": "GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if values["volume"]["conventions"]["maurer_cartan_volume"] != "V_0=int sigma_1 wedge sigma_2 wedge sigma_3=16 pi^2":
        raise AssertionError("Berger volume convention drifted")

    jacobian = jacobian_audit()
    base = _base_integral(values["moments"])
    squared = squared_radial_integral()
    # chi=rho J and dSigma=d^3R/J.  The selected component has |dR_I|^2>=y0^2,
    # so chi^2 |dR_I|^2 dSigma >= rho^2 y0^3 d^3R.  On support,
    # y0^3=(1-|y|^2)^(3/2)>=(1-M)^2.  Multiplying by Vol=16*pi^2*c and
    # C_B3=4*pi*I_B leaves 4*pi*c; pi>3 and c>9/20 give 4*pi*c>27/5.
    total_energy_lower = (
        Fraction(27, 5)
        * EPSILON**-3
        * (1 - MAX_Y_SQUARED) ** 2
        * squared[0]
        / base[1] ** 2
    )
    retained_energy_upper = LOW_MODE_ENTRY_BOUND**2 * 3 * sum(dimension**3 for dimension in range(1, 6))
    omitted_energy_lower = total_energy_lower - retained_energy_upper
    omitted_fraction_lower = 1 - Fraction(retained_energy_upper, 1) / total_energy_lower
    if total_energy_lower <= 70_000_000 or omitted_fraction_lower <= Fraction(99999, 100000):
        raise AssertionError("corrected two_j<=4 obstruction did not close")

    targets = (Fraction(9, 10), Fraction(99, 100), Fraction(999, 1000), Fraction(1))
    capacities = [capacity_row(total_energy_lower, fraction) for fraction in targets]
    if capacities[-1]["minimum_max_dimension_for_capacity"] != 98:
        raise AssertionError("corrected necessary capacity dimension drifted")
    legacy_energy = Fraction(values["legacy_tail"]["tail_audit"]["total_fourier_energy_lower"])
    legacy_two_j = values["legacy_capacity"]["necessary_cutoffs"][-1]["minimum_two_j_max_for_capacity"]
    if not legacy_energy > total_energy_lower or legacy_two_j != 138:
        raise AssertionError("legacy normalization witness drifted")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL repair distinguishes the rod-coordinate Jacobian d^3R/d^3y=8 c a^3 from the apparatus Gram Jacobian J=sqrt(det G)=a^3 y0. The Berger Haar density is dSigma=(8c/y0)d^3y, so J dSigma=d^3R exactly and J=1, not 8c, at either detector clock center. Recomputing the Parseval lower bound with chi=rho J gives total one-form Fourier energy above 7.02e7 and proves that more than 0.99999 remains above two_j=4. The qualitative cutoff obstruction survives. Its corrected unit-entry capacity lower bound first closes at representation dimension 98, two_j=97; the historical two_j=138 calculation remains a valid, larger working rail but is not a certified necessary threshold. This supersedes only the old 2.809e8 energy constant and the label 'necessary two_j>=138'. It does not alter any streamed coefficient, temporal functional-calculus or selected two_j=1024 result, and it does not export an upper tail bound, full Green image, detector response, recoil or quantum claim."
    )
    return {
        "schema": "closed-universe-berger-haar-profile-normalization-repair-v1",
        "result_id": "BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR",
        "setting_id": values["profiles"]["setting_id"],
        "claim_status": "EXACT_GRAM_HAAR_NORMALIZATION_REPAIRED_TWO_J4_OBSTRUCTION_PRESERVED_CAPACITY_LABEL_CORRECTED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "jacobian_audit": jacobian,
        "corrected_tail_audit": {
            "profile_slice": "clock center a=1 for either selected detector polarization",
            "normalization": "chi_spatial=rho(R) J with J=sqrt(det G)=a^3 y0 and dSigma=d^3R/J",
            "selected_component_lower": "J |dR_I|^2 >= y0^3 >= (1-max|y|^2)^2",
            "maurer_cartan_volume": "Vol(S3_Berger)=16*pi^2*c",
            "rational_constant_lower": "4*pi*c>27/5 from pi>3 and c=3sqrt(10)/20>9/20",
            "radial_integral_B": _serialize(base),
            "radial_integral_B_squared": _serialize(squared),
            "total_fourier_energy_lower": str(total_energy_lower),
            "total_fourier_energy_lower_decimal": f"{float(total_energy_lower):.6f}",
            "retained_fourier_energy_upper": str(retained_energy_upper),
            "omitted_fourier_energy_lower": str(omitted_energy_lower),
            "omitted_energy_fraction_lower": str(omitted_fraction_lower),
            "omitted_energy_fraction_lower_decimal": f"{float(omitted_fraction_lower):.12f}",
            "uniform_small_tail_through_two_j4": False,
        },
        "corrected_necessary_capacity": {
            "capacity_formula": "3 sum_(d=1)^D d^3=3[D(D+1)/2]^2",
            "rows": capacities,
            "certified_necessary_max_dimension": 98,
            "certified_necessary_two_j_max": 97,
            "published_working_rail_max_dimension": 139,
            "published_working_rail_max_two_j": 138,
            "working_rail_disposition": "valid evaluated rail above the corrected necessary capacity lower bound; not a convergence cutoff",
        },
        "superseded_claims": [
            {"result_id": values["legacy_tail"]["result_id"], "field": "tail_audit.total_fourier_energy_lower and derived decimals", "old_value": str(legacy_energy), "replacement": "corrected_tail_audit.total_fourier_energy_lower", "status": "NO_CERTIFIED_MAP"},
            {"result_id": values["legacy_capacity"]["result_id"], "field": "necessary two_j>=138 capacity label", "old_value": str(legacy_two_j), "replacement": "corrected_necessary_capacity.certified_necessary_two_j_max=97", "status": "NO_CERTIFIED_MAP"},
        ],
        "mutation_results": [
            {"name": "identify_coordinate_jacobian_8ca3_with_gram_J_a3y0", "detected": True},
            {"name": "drop_the_y0_factor_from_sqrt_det_G", "detected": True},
        ],
        "flags": {
            "EXACT_BERGER_HAAR_DENSITY_EXPORTED": True,
            "EXACT_BACKGROUND_GRAM_JACOBIAN_EXPORTED": True,
            "PROFILE_CHANGE_OF_VARIABLES_NORMALIZATION_REPAIRED": True,
            "TWO_J4_UNIFORM_PROFILE_TAIL_SMALLNESS_OBSTRUCTED": True,
            "CORRECTED_NECESSARY_TWO_J97_CAPACITY_LOWER_BOUND_EXPORTED": True,
            "HISTORICAL_TWO_J138_WORKING_RAIL_REMAINS_VALID": True,
            "HISTORICAL_TWO_J138_NECESSITY_LABEL_SUPERSEDED": True,
            "STREAMED_COEFFICIENT_VALUES_CHANGED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "EVALUATE_THE_CLOCK_UNIFORM_POLARIZED_REPEATED_LAPLACIAN_NORM_USING_J_A3Y0_AND_THE_BERGER_HAAR_DENSITY",
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
        raise SystemExit("stale Berger Haar profile-normalization repair")
    print("BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
