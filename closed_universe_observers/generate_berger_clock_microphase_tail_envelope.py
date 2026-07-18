#!/usr/bin/env python3
"""Certify a uniform clock-microphase envelope for frozen Berger profiles."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp

from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import gershgorin_lower_from_j
from closed_universe_observers.generate_berger_validated_flat_bump_moments import _interval_endpoints


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CLOCK_MICROPHASE_TAIL_ENVELOPE.json"
SCHEMA = PACKAGE / "schema/berger-clock-microphase-tail-envelope-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-microphase-tail-envelope.md"
DEPENDENCIES = {
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "selected_transform": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM.json",
    "tail_reduction": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json",
    "profile_n1": PACKAGE / "certificates/BERGER_CORRELATED_PROFILE_SOBOLEV_N1.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_clock_microphase_tail_envelope.py",
    PACKAGE / "tests/test_berger_clock_microphase_tail_envelope.py",
    SCHEMA,
    REPORT,
]
IV_DPS = 80
OUTPUT_DYADIC_BITS = 160
CURRENT_RETAINED_MAX_TWO_J = 1024


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _round_upper(value: Fraction, bits: int = OUTPUT_DYADIC_BITS) -> Fraction:
    denominator = 1 << bits
    return Fraction(-(-value.numerator * denominator // value.denominator), denominator)


def _serialize_upper(value: Fraction) -> dict[str, str]:
    value = _round_upper(value)
    return {"exact_dyadic_upper": str(value), "decimal_upper": f"{float(value):.12e}"}


def _maximum_bump_slope_upper() -> tuple[Fraction, dict[str, str]]:
    """Enclose max |d/ds B(s^2)| at its unique interior critical point."""
    mp.iv.dps = IV_DPS
    alpha = (3 + mp.iv.sqrt(3)) / 2
    s_star = mp.iv.sqrt(1 - 1 / alpha)
    slope = 2 * s_star * alpha**2 * mp.iv.exp(1 - alpha)
    alpha_bounds = _interval_endpoints(alpha)
    s_bounds = _interval_endpoints(s_star)
    slope_bounds = _interval_endpoints(slope)
    return _round_upper(slope_bounds[1]), {
        "critical_t_interval": f"[{alpha_bounds[0]},{alpha_bounds[1]}]",
        "critical_s_interval": f"[{s_bounds[0]},{s_bounds[1]}]",
        "maximum_abs_slope_upper": str(_round_upper(slope_bounds[1])),
    }


def _clock_envelope(moment_certificate: dict[str, Any]) -> dict[str, Any]:
    power_zero = next(row for row in moment_certificate["raw_radial_integral_enclosures"] if row["power"] == 0)
    denominator_lower = Fraction(power_zero["integral"]["lower"])
    denominator_upper = Fraction(power_zero["integral"]["upper"])
    max_slope, critical = _maximum_bump_slope_upper()
    mp.iv.dps = IV_DPS
    nu_bounds = _interval_endpoints(mp.iv.sqrt(58) / 288)
    nu_upper = _round_upper(nu_bounds[1])

    # For B(s)=exp(1-1/(1-s^2)), t=(1-s^2)^(-1),
    # B_ss=2 t^2(2t^2-6t+3)e^(1-t).  It changes sign once for
    # t>=1, so total variation of B_s is exactly 2 max|B_s|.
    second_derivative_l1_upper = 2 * max_slope
    weighted_second_derivative_l1_upper = (
        second_derivative_l1_upper + 2 * nu_upper + nu_upper**2 * denominator_upper
    )
    normalized_constant_upper = _round_upper(weighted_second_derivative_l1_upper / denominator_lower)
    return {
        "clock_bump_denominator": {
            "lower": str(denominator_lower),
            "upper": str(denominator_upper),
        },
        "external_clock_frequency_nu": {
            "exact": "sqrt(58)/288",
            "upper": str(nu_upper),
        },
        "flat_bump_derivative_audit": {
            **critical,
            "B_ss_identity": "B_ss=2 t^2(2 t^2-6 t+3) exp(1-t), t=(1-s^2)^(-1)",
            "unique_sign_change_for_t_ge_1": "t=(3+sqrt(3))/2",
            "integral_abs_B_ss_upper": str(_round_upper(second_derivative_l1_upper)),
            "integral_abs_B_s": "1",
        },
        "weighted_second_derivative_L1_upper": str(_round_upper(weighted_second_derivative_l1_upper)),
        "normalized_envelope_constant_C_upper": str(normalized_constant_upper),
        "uniform_transform_envelope": "|T(lambda)| <= 2304 C/lambda for lambda>0",
    }


def _cutoff_row(retained_max_two_j: int, norm_upper: Fraction, constant_upper: Fraction) -> dict[str, Any]:
    first_omitted_j = Fraction(retained_max_two_j + 1, 2)
    spectral_lower = gershgorin_lower_from_j(first_omitted_j)
    transform_upper = _round_upper(2304 * constant_upper / spectral_lower)
    frozen_tail_upper = _round_upper(2304 * constant_upper * norm_upper / spectral_lower**2)
    return {
        "retained_max_two_j": retained_max_two_j,
        "first_omitted_j": str(first_omitted_j),
        "first_omitted_delta1_lower": str(spectral_lower),
        "clock_transform_operator_norm_upper": _serialize_upper(transform_upper),
        "frozen_profile_N1_tail_upper": _serialize_upper(frozen_tail_upper),
        "frozen_profile_tail_below_one": frozen_tail_upper < 1,
    }


def _first_sufficient_cutoff(norms: list[Fraction], constant_upper: Fraction) -> int:
    for retained_max_two_j in range(CURRENT_RETAINED_MAX_TWO_J, 100_001):
        spectral_lower = gershgorin_lower_from_j(Fraction(retained_max_two_j + 1, 2))
        if all(2304 * constant_upper * norm < spectral_lower**2 for norm in norms):
            return retained_max_two_j
    raise AssertionError("frozen-profile sufficient cutoff search exceeded declared rail")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "selected_transform": "FINITE_SELECTED_EXACT_T_TEMPORAL_IMAGE_REPRESENTATION_EXPORTED",
        "tail_reduction": "GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED",
        "profile_n1": "VALIDATED_CORRELATED_CLOCK_UNIFORM_DELTA1_NORM_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    envelope = _clock_envelope(values["moments"])
    constant_upper = Fraction(envelope["normalized_envelope_constant_C_upper"])
    norms = {
        row["detector_id"]: Fraction(row["normalized_Delta1_profile_L2_norm_upper"])
        for row in values["profile_n1"]["polarization_bounds"]
    }
    sufficient_cutoff = _first_sufficient_cutoff(list(norms.values()), constant_upper)
    current_rows = [
        {"detector_id": detector_id, **_cutoff_row(CURRENT_RETAINED_MAX_TWO_J, norm, constant_upper)}
        for detector_id, norm in sorted(norms.items())
    ]
    sufficient_rows = [
        {"detector_id": detector_id, **_cutoff_row(sufficient_cutoff, norm, constant_upper)}
        for detector_id, norm in sorted(norms.items())
    ]
    if any(row["frozen_profile_tail_below_one"] for row in current_rows):
        raise AssertionError("current frozen-profile cutoff unexpectedly became small")
    if not all(row["frozen_profile_tail_below_one"] for row in sufficient_rows):
        raise AssertionError("reported frozen-profile cutoff is not sufficient")
    previous_rows = [
        _cutoff_row(sufficient_cutoff - 1, norm, constant_upper) for norm in norms.values()
    ]
    if all(row["frozen_profile_tail_below_one"] for row in previous_rows):
        raise AssertionError("reported frozen-profile cutoff is not minimal")

    mutated_l1 = Fraction(envelope["weighted_second_derivative_L1_upper"]) - Fraction(envelope["flat_bump_derivative_audit"]["maximum_abs_slope_upper"])
    mutation_detected = mutated_l1 < Fraction(envelope["weighted_second_derivative_L1_upper"])
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result certifies a uniform second-integration-by-parts envelope for the normalized flat-clock transform of a fixed spatial Berger one-form: |T(lambda)|<=2304 C/lambda. The proof uses boundary flatness, the exact B_ss identity, its single sign change, and the total variation integral integral|B_ss|=2 max|B_s|. Combined with the correlated N=1 spatial norm, the frozen-profile tail above retained two_j=1024 is still non-small, while retained two_j=3421 is the first certified integer cutoff at which this particular bound is below one for both detector polarizations. This is a quantitative route certificate, not the physical moving-profile tail: the actual F_a(s) depends on the clock-driven rods and Gram factor, and no clock-derivative/commutator estimate identifying it with a frozen vector is certified. The complete low-mode projection is also absent. Therefore no full Maxwell or massive image, detector response or rank, recoil, tangent-cone restriction, active Bridge 3, nonlinear observer-morphism stability, or quantum claim is promoted."
    )
    return {
        "schema": "closed-universe-berger-clock-microphase-tail-envelope-v1",
        "result_id": "BERGER_CLOCK_MICROPHASE_TAIL_ENVELOPE",
        "setting_id": values["profile_n1"]["setting_id"],
        "claim_status": "UNIFORM_FROZEN_PROFILE_CLOCK_MICROPHASE_ENVELOPE_CERTIFIED_MOVING_PROFILE_TAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "method": {
            "normalized_transform": "T(lambda)=D^(-1) integral_0^1 B(s) cos(nu s) cos(s sqrt(lambda)/48) ds",
            "boundary_conditions": "B and every derivative vanish at s=1; h'(0)=0 and sin(0)=0",
            "integration_by_parts_count": 2,
            "spectral_combination": "||Pi_tail T(Delta1)F|| <= 2304 C Lambda^(-2)||Delta1 F|| for clock-independent F",
        },
        "clock_envelope": envelope,
        "cutoff_analysis": {
            "current_cutoff_rows": current_rows,
            "first_sufficient_frozen_profile_retained_max_two_j": sufficient_cutoff,
            "first_sufficient_rows": sufficient_rows,
            "minimality_witness_at_previous_cutoff": previous_rows,
            "moving_profile_status": "NO_CERTIFIED_MAP",
            "complete_low_mode_projection_status": "OPEN",
        },
        "mutation_results": [{
            "name": "replace_total_variation_2max_abs_Bs_by_one_sided_max_abs_Bs",
            "detected": mutation_detected,
            "mutated_weighted_second_derivative_L1_upper": str(mutated_l1),
        }],
        "flags": {
            "UNIFORM_FIXED_VECTOR_CLOCK_MICROPHASE_ENVELOPE_EXPORTED": True,
            "FROZEN_PROFILE_SUFFICIENT_CUTOFF_EXPORTED": True,
            "CURRENT_TWO_J1024_FROZEN_PROFILE_BOUND_CERTIFIES_SMALL_TAIL": False,
            "MOVING_DETECTOR_PROFILE_CLOCK_DERIVATIVE_BOUND_EXPORTED": False,
            "VALIDATED_PHYSICAL_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": False,
            "COMPLETE_LOW_MODE_PROJECTION_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "MASSIVE_TWO_FORM_TAIL_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BOUND_THE_CLOCK_DERIVATIVES_OF_THE_MOVING_BERGER_PROFILE_AND_COMBINE_THEM_WITH_THE_MICROPHASE_ENVELOPE",
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
        raise SystemExit("stale Berger clock-microphase tail-envelope certificate")
    print("BERGER_CLOCK_MICROPHASE_TAIL_ENVELOPE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
