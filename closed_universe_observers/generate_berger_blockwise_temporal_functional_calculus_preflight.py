#!/usr/bin/env python3
"""Certify the angle-addition route around the obstructed temporal Taylor rail."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from math import factorial
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-blockwise-temporal-functional-calculus-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-blockwise-temporal-functional-calculus-preflight.md"
SERIES_ORDER = 14
INTERNAL_CLOCK_SCALE = Fraction(1, 48)
DEPENDENCIES = {
    "order14": PACKAGE / "certificates/BERGER_ORDER14_TEMPORAL_GREEN_CHARGE_STREAM_TWO_J138.json",
    "blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
    "polarization": PACKAGE / "certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_POLARIZATION_STREAM_P12_TO_P28_TWO_J138.json",
    "moments": PACKAGE / "certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "low_green": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_blockwise_temporal_functional_calculus_preflight.py",
    PACKAGE / "tests/test_berger_blockwise_temporal_functional_calculus_preflight.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tail(y: Fraction, first_denominator: int, factorial_denominator: int) -> tuple[Fraction, Fraction]:
    ratio = y / Fraction(first_denominator * (first_denominator + 1))
    if ratio >= 1:
        raise AssertionError("microphase geometric tail is not contractive")
    return ratio, y ** (SERIES_ORDER + 1) / factorial(factorial_denominator) / (1 - ratio)


def microphase_audit(lambda0: Fraction, lambda1: Fraction) -> dict:
    y1 = lambda1 * INTERNAL_CLOCK_SCALE**2
    y0 = lambda0 * INTERNAL_CLOCK_SCALE**2
    cosine_ratio, cosine_tail = _tail(y1, 2 * SERIES_ORDER + 3, 2 * SERIES_ORDER + 2)
    scalar_cosine_ratio, scalar_cosine_tail = _tail(y0, 2 * SERIES_ORDER + 3, 2 * SERIES_ORDER + 2)
    sine_ratio, sine_tail_base = _tail(y0, 2 * SERIES_ORDER + 4, 2 * SERIES_ORDER + 3)
    sine_tail = INTERNAL_CLOCK_SCALE * sine_tail_base
    return {
        "normalized_clock_support": "-1 <= s <= 1",
        "internal_physical_offset": "s/48",
        "Delta1_infinity_norm_upper": str(lambda1),
        "Delta0_infinity_norm_upper": str(lambda0),
        "Delta1_internal_y_upper": str(y1),
        "Delta0_internal_y_upper": str(y0),
        "cosine_geometric_ratio": str(cosine_ratio),
        "scalar_cosine_geometric_ratio": str(scalar_cosine_ratio),
        "sine_geometric_ratio": str(sine_ratio),
        "Delta1_cosine_microphase_remainder_upper": str(cosine_tail),
        "Delta0_cosine_microphase_remainder_upper": str(scalar_cosine_tail),
        "Delta0_sine_microphase_remainder_upper": str(sine_tail),
        "all_ratios_below_one_over_one_hundred": max(cosine_ratio, scalar_cosine_ratio, sine_ratio) < Fraction(1, 100),
        "all_microphase_remainders_below_one_e_minus_seventeen": max(cosine_tail, scalar_cosine_tail, sine_tail) < Fraction(1, 10**17),
    }


@lru_cache(maxsize=1)
def build() -> dict:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["order14"]["atlas_status"] != "OBSTRUCTED":
        raise AssertionError("order-14 global Taylor obstruction dropped")
    if values["blocks"]["flags"].get("ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED") is not True:
        raise AssertionError("exact charge-block formulas dropped")
    if values["polarization"]["flags"].get("COMMON_ORDER14_POLARIZATION_INPUTS_P0_TO_P28_COMPLETE") is not True:
        raise AssertionError("p<=28 polarization inputs dropped")
    if values["moments"]["flags"].get("VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED") is not True:
        raise AssertionError("p<=28 clock moments dropped")
    source_convention = values["low_green"]["series_convention"]
    if source_convention["physical_time_offset"] != "source_time=t_detector_center+s/48":
        raise AssertionError("physical clock-offset convention changed")

    old_rows = values["order14"]["remainder_audits"]
    lambda1 = Fraction(old_rows[0]["Delta1_infinity_norm_upper"])
    lambda0 = Fraction(old_rows[0]["Delta0_infinity_norm_upper"])
    audit = microphase_audit(lambda0, lambda1)
    if not audit["all_ratios_below_one_over_one_hundred"] or not audit["all_microphase_remainders_below_one_e_minus_seventeen"]:
        raise AssertionError("angle-addition microphase rail is not sufficiently small")

    # Replacing the internal s/48 phase by the full D1 propagation radius must
    # reproduce the already-certified bad order-14 global Taylor tail.
    mutated_tail = Fraction(old_rows[1]["spatial_cosine_entry_remainder_upper"])
    if mutated_tail <= 1:
        raise AssertionError("full-tau mutation no longer exposes the obstruction")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight replaces the obstructed global Taylor expansion in tau=T+s/48 by the exact commuting angle-addition identities in every at-most-three-dimensional positive Maxwell charge block. The large T dependence remains in the exact spectral functions cos(T sqrt(B)) and sin(T sqrt(B))/sqrt(B), with the entire extension at zero. Only the internal normalized clock microphase |s|/48<=1/48 is Taylor expanded. Its order-14 geometric ratios are all below 1/100 and its exported operator remainders are below 1e-17. The fixed detector integrand is even in s, so its odd microphase transform vanishes and the already-certified p=0,2,...,28 rails supply the required cosine transform. This certifies the route and error budget, not the streamed blockwise functional-calculus image, spatial tail, full Maxwell/massive images, recoil, tangent-cone restriction, Bridge 3 or quantum claims."
    )
    return {
        "schema": "closed-universe-berger-blockwise-temporal-functional-calculus-preflight-v1",
        "result_id": "BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_PREFLIGHT",
        "setting_id": values["order14"]["setting_id"],
        "claim_status": "ANGLE_ADDITION_ROUTE_CERTIFIED_MICROPHASE_REMAINDER_SMALL_BLOCKWISE_APPLICATION_OPEN",
        "atlas_status": "OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "exact_functional_identities": {
            "cosine": "cos((T+s/48)sqrt(B))=cos(Tsqrt(B))cos((s/48)sqrt(B))-sin(Tsqrt(B))sin((s/48)sqrt(B))",
            "sine_over_root": "sin((T+s/48)sqrt(B))/sqrt(B)=sin(Tsqrt(B))/sqrt(B) cos((s/48)sqrt(B))+cos(Tsqrt(B)) sin((s/48)sqrt(B))/sqrt(B)",
            "zero_eigenvalue_extension": "sin(Tsqrt(lambda))/sqrt(lambda) at lambda=0 is T",
            "commutation_reason": "all factors are entire functions of the same finite Hermitian nonnegative charge block B",
        },
        "clock_parity": {
            "normalized_variable": "s=(Theta-Theta_a)/(1/64)",
            "support": "[-1,1]",
            "joint_detector_integrand_parity": "even flat bump times even a(t)=cos(lambda s) and even sec(lambda s) powers",
            "odd_joint_moments": "exactly zero",
            "required_even_powers": list(range(0, 29, 2)),
            "existing_p0_to_p28_inputs_sufficient": True,
        },
        "microphase_remainder_audit": audit,
        "large_T_disposition": {
            "status": "EXACT_BLOCKWISE_FUNCTIONAL_CALCULUS_REQUIRED",
            "cosine_spectral_norm_upper": "1",
            "sine_over_root_spectral_norm_upper": "|T|",
            "no_T_taylor_truncation": True,
        },
        "mutation_results": [{
            "name": "replace_internal_s_over_48_microphase_by_full_D1_tau_radius",
            "detected": True,
            "mutated_cosine_remainder_upper": str(mutated_tail),
            "reason": "the mutation restores the certified inaccurate global order-14 Taylor rail",
        }],
        "flags": {
            "ANGLE_ADDITION_BLOCKWISE_ROUTE_CERTIFIED": True,
            "EXISTING_EVEN_CLOCK_INPUTS_P0_TO_P28_SUFFICIENT": True,
            "INTERNAL_MICROPHASE_REMAINDER_BELOW_ONE_E_MINUS_SEVENTEEN": True,
            "LARGE_T_TAYLOR_EXPANSION_REMOVED": True,
            "BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_IMAGE_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "STREAM_MICROPHASE_DRESSED_INPUTS_AND_RETAIN_EXACT_T_DEPENDENCE_IN_EACH_CHARGE_BLOCK",
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
        raise SystemExit("stale blockwise temporal functional-calculus preflight")
    print("BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_PREFLIGHT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
