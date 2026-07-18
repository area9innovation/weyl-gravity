#!/usr/bin/env python3
"""Enclose normalized moments of the fixed detector and clock flat bumps."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json"
SCHEMA = PACKAGE / "schema/berger-validated-flat-bump-moment-enclosures-v1.schema.json"
REPORT = PACKAGE / "reports/berger-validated-flat-bump-moment-enclosures.md"
DEPENDENCIES = {
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_validated_flat_bump_moments.py",
    "tests": PACKAGE / "tests/test_berger_validated_flat_bump_moments.py",
    "schema": SCHEMA,
    "report": REPORT,
}
SUBDIVISIONS = 32768
IV_DPS = 50
MAX_K = 6
OUTPUT_DYADIC_BITS = 160


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_from_mpf_tuple(value: tuple[int, int, int, int]) -> Fraction:
    sign, mantissa, exponent, _ = value
    result = Fraction(mantissa)
    if exponent >= 0:
        result *= 2**exponent
    else:
        result /= 2 ** (-exponent)
    return -result if sign else result


def _interval_endpoints(value: Any) -> tuple[Fraction, Fraction]:
    raw = value._mpi_
    return _fraction_from_mpf_tuple(raw[0]), _fraction_from_mpf_tuple(raw[1])


def _bump_at(r: Fraction) -> tuple[Fraction, Fraction]:
    if r == 0:
        return Fraction(1), Fraction(1)
    if r == 1:
        return Fraction(0), Fraction(0)
    x = mp.iv.mpf(r.numerator) / r.denominator
    return _interval_endpoints(mp.iv.exp(1 - 1 / (1 - x * x)))


def _q(p: int, r: Fraction) -> Fraction:
    """Numerator controlling the sign of d log(r^p B(r))/dr."""
    return p * (1 - r * r) ** 2 - 2 * r * r


def _round_outward(lower: Fraction, upper: Fraction, bits: int = OUTPUT_DYADIC_BITS) -> tuple[Fraction, Fraction]:
    denominator = 2**bits
    lower_numerator = lower.numerator * denominator // lower.denominator
    upper_numerator = -(-upper.numerator * denominator // upper.denominator)
    return Fraction(lower_numerator, denominator), Fraction(upper_numerator, denominator)


def integral_enclosures(subdivisions: int = SUBDIVISIONS, max_k: int = MAX_K) -> dict[int, tuple[Fraction, Fraction]]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    mp.iv.dps = IV_DPS
    grid = [Fraction(i, subdivisions) for i in range(subdivisions + 1)]
    bump = [_bump_at(r) for r in grid]
    powers = sorted(set(range(0, 2 * max_k + 1, 2)) | set(range(2, 2 * max_k + 3, 2)))
    result: dict[int, tuple[Fraction, Fraction]] = {}
    width = Fraction(1, subdivisions)
    for p in powers:
        values = []
        for r, (b_lo, b_hi) in zip(grid, bump):
            rp = r**p if p else Fraction(1)
            values.append((rp * b_lo, rp * b_hi))
        lower = Fraction(0)
        upper = Fraction(0)
        for i in range(subdivisions):
            lower += width * min(values[i][0], values[i + 1][0])
            if p and _q(p, grid[i]) >= 0 >= _q(p, grid[i + 1]):
                cell_upper = Fraction(1)
            else:
                cell_upper = max(values[i][1], values[i + 1][1])
            upper += width * cell_upper
        result[p] = _round_outward(lower, upper)
    return result


def _serialize_interval(lower: Fraction, upper: Fraction) -> dict[str, str]:
    lower, upper = _round_outward(lower, upper)
    if not 0 <= lower <= upper:
        raise AssertionError("invalid interval")
    return {
        "lower": str(lower),
        "upper": str(upper),
        "width": str(upper - lower),
    }


def normalized_moments(integrals: dict[int, tuple[Fraction, Fraction]], dimension: int, max_k: int = MAX_K) -> list[dict[str, Any]]:
    base_power = dimension - 1
    base_lower, base_upper = integrals[base_power]
    rows = []
    for k in range(max_k + 1):
        if k == 0:
            lower = upper = Fraction(1)
        else:
            numerator_lower, numerator_upper = integrals[base_power + 2 * k]
            lower = numerator_lower / base_upper
            upper = numerator_upper / base_lower
        rows.append({"k": k, "normalized_even_moment": _serialize_interval(lower, upper)})
    return rows


def scaled_moments(rows: list[dict[str, Any]], scale: Fraction) -> list[dict[str, Any]]:
    answer = []
    for row in rows:
        k = row["k"]
        interval = row["normalized_even_moment"]
        factor = scale ** (2 * k)
        answer.append({
            "k": k,
            "scale": str(scale),
            "scaled_even_moment": _serialize_interval(
                factor * Fraction(interval["lower"]),
                factor * Fraction(interval["upper"]),
            ),
        })
    return answer


def endpoint_only_peak_mutation(p: int = 2, subdivisions: int = 64) -> dict[str, Any]:
    mp.iv.dps = IV_DPS
    for i in range(subdivisions):
        a = Fraction(i, subdivisions)
        b = Fraction(i + 1, subdivisions)
        if _q(p, a) >= 0 >= _q(p, b):
            endpoint_upper = max(a**p * _bump_at(a)[1], b**p * _bump_at(b)[1])
            candidates = [a + (b - a) * Fraction(j, 8) for j in range(1, 8)]
            witness = max((r**p * _bump_at(r)[0], r) for r in candidates)
            return {
                "power": p,
                "cell": [str(a), str(b)],
                "endpoint_only_upper": str(endpoint_upper),
                "interior_witness_point": str(witness[1]),
                "interior_witness_lower": str(witness[0]),
                "detected": witness[0] > endpoint_upper,
            }
    raise AssertionError("peak cell not found")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "profiles": "EXACT_DETECTOR_RADIAL_PROFILE_FAMILY_SERIALIZED",
        "chart": "EXACT_DETECTOR_RADII_FIXED",
        "spectral": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "kernels": "EXACT_FINITE_MODE_MAXWELL_GREEN_KERNELS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if values["chart"]["selected_profiles"]["epsilon_0"] != "1/128" or values["chart"]["selected_profiles"]["epsilon_1"] != "1/128":
        raise AssertionError("fixed detector radius drifted")

    integrals = integral_enclosures()
    clock = normalized_moments(integrals, 1)
    radial = normalized_moments(integrals, 3)
    mutation = endpoint_only_peak_mutation()
    if not mutation["detected"]:
        raise AssertionError("endpoint-only peak mutation escaped")
    for family in (clock, radial):
        if any(Fraction(row["normalized_even_moment"]["width"]) >= Fraction(1, 1000) for row in family):
            raise AssertionError("moment enclosure wider than declared tolerance")

    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL input certificate interval-encloses the normalized even moments through order twelve of the standard one-dimensional and radial three-dimensional flat bump B(r)=exp(1-1/(1-r^2)). It uses a 32768-cell dyadic Darboux enclosure, directed-rounding transcendental endpoint intervals, and the exact unimodality polynomial p(1-r^2)^2-2r^2. Exact scaling then fixes the clock-radius 1/64 and detector rod-radius 1/128 moments. The endpoint-only mutation is rejected by a rational interior witness. These moment enclosures are reusable inputs to the Peter-Weyl coefficient calculation; they are not the coefficients themselves. No full harmonic expansion, evaluated Sobolev norm, validated infinite-mode tail, advanced Green image, recoil coefficient, interacting theorem, or quantum claim is made."
    )
    return {
        "schema": "closed-universe-berger-validated-flat-bump-moment-enclosures-v1",
        "result_id": "BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES",
        "setting_id": values["profiles"]["setting_id"],
        "claim_status": "VALIDATED_STANDARD_BUMP_MOMENTS_EXPORTED_MODE_COEFFICIENTS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "quadrature_method": {
            "integrand_family": "f_p(r)=r^p exp(1-1/(1-r^2)), 0<=r<1, with f_p(1)=0",
            "subdivisions": SUBDIVISIONS,
            "grid": "dyadic uniform grid on [0,1]",
            "interval_engine": f"mpmath {mp.__version__} iv directed rounding",
            "decimal_precision": IV_DPS,
            "output_dyadic_bits": OUTPUT_DYADIC_BITS,
            "unimodality_identity": "sign(d log(f_p)/dr)=sign(p(1-r^2)^2-2r^2) for 0<r<1",
            "cell_rule": "lower=min(endpoint lowers); upper=max(endpoint uppers), except the unique peak cell uses the global bound f_p<=1",
            "serialized_endpoints": "exact rational values of the directed-rounded binary endpoints",
        },
        "raw_radial_integral_enclosures": [
            {"power": p, "integral": _serialize_interval(*integrals[p])} for p in sorted(integrals)
        ],
        "normalized_moments": {
            "clock_core_dimension_1": clock,
            "radial_core_dimension_3": radial,
        },
        "fixed_profile_scaled_moments": {
            "clock_radius_1_over_64": scaled_moments(clock, Fraction(1, 64)),
            "detector_rod_radius_1_over_128": scaled_moments(radial, Fraction(1, 128)),
        },
        "isotropic_tensor_reductions": {
            "second": "E[z_i z_j]=delta_ij E[|z|^2]/3",
            "fourth_diagonal": "E[z_i^4]=E[|z|^4]/5",
            "fourth_mixed": "E[z_i^2 z_j^2]=E[|z|^4]/15 for i!=j",
            "odd": "all odd Cartesian moments vanish",
        },
        "spectral_tail_reduction": {
            "identity": "||1_(Delta>Lambda) f||_L2 <= Lambda^(-N) ||Delta^N f||_L2",
            "evaluated_sobolev_norm": False,
            "validated_infinite_mode_tail": False,
        },
        "mutation_results": [{"name": "replace_peak_cell_cap_by_endpoint_only_upper", **mutation}],
        "flags": {
            "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED": True,
            "FIXED_CLOCK_AND_DETECTOR_RADIUS_MOMENT_SCALING_EXPORTED": True,
            "ISOTROPIC_CARTESIAN_MOMENT_REDUCTION_EXPORTED": True,
            "PETER_WEYL_MODE_COEFFICIENTS_EVALUATED": False,
            "EVALUATED_SOBOLEV_NORM_EXPORTED": False,
            "VALIDATED_INFINITE_MODE_TAIL_BOUND_EXPORTED": False,
            "ADVANCED_GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMBINE_THE_MOMENTS_WITH_EXACT_LOCAL_SU2_MODE_POLYNOMIALS_AND_BOUND_THE_Y0_BINOMIAL_REMAINDER",
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
        raise SystemExit("stale validated flat-bump moment certificate")
    print("BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
