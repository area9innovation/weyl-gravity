#!/usr/bin/env python3
"""Certify that the two_j<=4 window cannot uniformly resolve the detector profile."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp

from closed_universe_observers.generate_berger_validated_flat_bump_moments import (
    IV_DPS, OUTPUT_DYADIC_BITS, SUBDIVISIONS, _bump_at, _round_outward,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION.json"
SCHEMA = PACKAGE / "schema/berger-two-j4-profile-tail-obstruction-v1.schema.json"
REPORT = PACKAGE / "reports/berger-two-j4-profile-tail-obstruction.md"
DEPENDENCIES = {
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "form": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json",
    "green_weighted": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "volume": ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_two_j4_profile_tail_obstruction.py",
    "tests": PACKAGE / "tests/test_berger_two_j4_profile_tail_obstruction.py",
    "schema": SCHEMA,
    "report": REPORT,
}
EPSILON = Fraction(1, 128)
C_SQUARED = Fraction(9, 40)
MAX_Y_SQUARED = Fraction(93312, 1374979445)
PI_LOWER = Fraction(3)
LOW_MODE_ENTRY_BOUND = Fraction(1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def _squared_peak_sign(r: Fraction) -> Fraction:
    # sign of d log(r^2 B(r)^2)/dr after multiplication by r(1-r^2)^2.
    return 2 * (1 - r * r) ** 2 - 4 * r * r


def squared_radial_integral(subdivisions: int = SUBDIVISIONS) -> tuple[Fraction, Fraction]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    # mpmath interval precision is process-global.  Establish the declared
    # precision here so generation is independent of test/import order.
    mp.iv.dps = IV_DPS
    width = Fraction(1, subdivisions)
    grid = [Fraction(i, subdivisions) for i in range(subdivisions + 1)]
    values = []
    for radius in grid:
        bump = _bump_at(radius)
        values.append((radius**2 * bump[0] ** 2, radius**2 * bump[1] ** 2))
    lower = Fraction(0); upper = Fraction(0)
    for index in range(subdivisions):
        lower += width * min(values[index][0], values[index + 1][0])
        peak_cell = _squared_peak_sign(grid[index]) >= 0 >= _squared_peak_sign(grid[index + 1])
        upper += width * (Fraction(1) if peak_cell else max(values[index][1], values[index + 1][1]))
    return _round_outward(lower, upper, OUTPUT_DYADIC_BITS)


def _base_integral(moment_certificate: dict[str, Any]) -> tuple[Fraction, Fraction]:
    row = next(row for row in moment_certificate["raw_radial_integral_enclosures"] if row["power"] == 2)
    return Fraction(row["integral"]["lower"]), Fraction(row["integral"]["upper"])


def tail_audit(values: dict[str, Any], *, omit_top_retained_representation: bool = False) -> dict[str, Any]:
    base = _base_integral(values["moments"])
    squared = squared_radial_integral()
    # Vol(S3_Berger)=16*pi^2*c and ||rho J alpha||^2 >=
    # 2*c/pi * eps^-3*(1-max|y|^2)*I(B^2)/I(B)^2.
    # Their product is 32*pi*c^2*..., and pi>3 gives the rational lower bound.
    total_energy_lower = (
        32 * PI_LOWER * C_SQUARED * EPSILON**-3 * (1 - MAX_Y_SQUARED)
        * squared[0] / base[1] ** 2
    )
    dimensions = range(1, 5 if omit_top_retained_representation else 6)
    low_energy_upper = LOW_MODE_ENTRY_BOUND**2 * 3 * sum(dimension**3 for dimension in dimensions)
    tail_energy_lower = total_energy_lower - low_energy_upper
    tail_fraction_lower = 1 - Fraction(low_energy_upper, 1) / total_energy_lower
    if tail_energy_lower <= 0 or tail_fraction_lower <= Fraction(99999, 100000):
        raise AssertionError("two_j<=4 tail obstruction was lost")
    return {
        "profile_slice": "clock center a=1 for either selected detector polarization",
        "normalization": "chi_spatial=rho(R) J, dSigma=d^3R/J, J=8c at the clock center",
        "selected_component_lower": "|dR0_1(theta3)|^2 and |dR1_2(theta1)|^2 are y0^2 >= 1-max|y|^2",
        "maurer_cartan_volume": "Vol(S3_Berger)=16*pi^2*c",
        "parseval_convention": "sum_j (2j+1)||hat F(j)||_HS^2 = Vol(S3_Berger)||F||_L2^2",
        "pi_lower": str(PI_LOWER),
        "radial_integral_B": _serialize(base),
        "radial_integral_B_squared": _serialize(squared),
        "total_fourier_energy_lower": str(total_energy_lower),
        "retained_dimensions": list(dimensions),
        "retained_coefficient_absolute_upper": str(LOW_MODE_ENTRY_BOUND),
        "retained_fourier_energy_upper": str(low_energy_upper),
        "omitted_fourier_energy_lower": str(tail_energy_lower),
        "omitted_energy_fraction_lower": str(tail_fraction_lower),
        "omitted_energy_fraction_lower_decimal": f"{float(tail_fraction_lower):.12f}",
        "uniform_small_tail_through_two_j4": False,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "chart": "EXACT_DETECTOR_RADII_FIXED",
        "form": "CLOCK_ZERO_MOMENT_FORM_COEFFICIENTS_TWO_J0_TO_4_EXPORTED",
        "green_weighted": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if values["volume"]["conventions"]["maurer_cartan_volume"] != "V_0=int sigma_1 wedge sigma_2 wedge sigma_3=16 pi^2":
        raise AssertionError("Berger volume convention drifted")
    audit = tail_audit(values)
    mutation = tail_audit(values, omit_top_retained_representation=True)
    if mutation["retained_fourier_energy_upper"] == audit["retained_fourier_energy_upper"]:
        raise AssertionError("cutoff-dimension mutation escaped")
    boundary = "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL obstruction applies Parseval to the actual normalized detector one-form profile at either clock center. Directed-rounding quadrature encloses the radial B^2 integral, the certified rod chart gives y0^2>=1-max|y|^2, and the certified Berger volume fixes the Fourier normalization. The total form-profile Fourier energy is greater than 2.809e8, while every coefficient through two_j=4 has absolute value at most one and their complete weighted energy is at most 675. Therefore more than 0.9999975 of the clock-center profile energy necessarily lies above two_j=4. The current finite window cannot support a uniform small-tail theorem; a substantially larger adaptive Peter-Weyl cutoff or a physical-space Green evaluation is required. This is a lower-bound obstruction, not an upper bound on the infinite tail and not a full advanced-image, recoil, interacting or quantum result."
    return {
        "schema": "closed-universe-berger-two-j4-profile-tail-obstruction-v1",
        "result_id": "BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION",
        "setting_id": values["form"]["setting_id"],
        "claim_status": "OBSTRUCTED_TWO_J4_UNIFORM_PROFILE_TAIL_SMALLNESS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "quadrature": {"subdivisions": SUBDIVISIONS, "interval_precision": IV_DPS, "output_dyadic_bits": OUTPUT_DYADIC_BITS, "squared_bump_peak_identity": "sign d log(r^2 B(r)^2)=sign(2(1-r^2)^2-4r^2)", "cell_rule": "endpoint Darboux bounds; the unique peak cell uses r^2 B^2<=1"},
        "tail_audit": audit,
        "mutation_results": [{"name": "omit_two_j4_representation_from_retained_dimension_count", "detected": True, "mutated_retained_energy_upper": mutation["retained_fourier_energy_upper"]}],
        "flags": {"TWO_J4_UNIFORM_PROFILE_TAIL_SMALLNESS_OBSTRUCTED": True, "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "ADVANCED_MASSIVE_EMITTER_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXTEND_TO_AN_ADAPTIVE_PETER_WEYL_CUTOFF_NEAR_THE_PROFILE_BANDWIDTH_OR_EVALUATE_THE_GREEN_CHAIN_IN_PHYSICAL_SPACE",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    value = build(); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered): raise SystemExit("stale two_j4 profile-tail obstruction certificate")
    print("BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
