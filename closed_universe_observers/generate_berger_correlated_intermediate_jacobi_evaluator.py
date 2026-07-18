#!/usr/bin/env python3
"""Validate correlated Darboux enclosures on intermediate Berger diagonals."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp

from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    A2_AT_CENTER,
    B2_AT_CENTER,
)
from closed_universe_observers.generate_berger_correlated_axial_oscillatory_evaluator import (
    _clock_secant_upper,
    _divide_interval,
    _iv_box,
    _multiply_interval,
    _radial_denominator,
    _round_outward,
    radial_cell_masses,
)
from closed_universe_observers.generate_berger_validated_flat_bump_moments import (
    _interval_endpoints,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CORRELATED_INTERMEDIATE_JACOBI_EVALUATOR.json"
SCHEMA = PACKAGE / "schema/berger-correlated-intermediate-jacobi-evaluator-v1.schema.json"
REPORT = PACKAGE / "reports/berger-correlated-intermediate-jacobi-evaluator.md"
DEPENDENCIES = {
    "axial_seed": PACKAGE / "certificates/BERGER_CORRELATED_AXIAL_OSCILLATORY_EVALUATOR.json",
    "jacobi_preflight": PACKAGE / "certificates/BERGER_JACOBI_AXIAL_STABILITY_PREFLIGHT.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "scalar_s0": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S0_TWO_J139.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_correlated_intermediate_jacobi_evaluator.py",
    PACKAGE / "tests/test_berger_correlated_intermediate_jacobi_evaluator.py",
    SCHEMA,
    REPORT,
]
INTERVAL_DPS = 18
OUTPUT_BITS = 96
REFINED_SUBDIVISIONS = 64
COARSE_SUBDIVISIONS = 32
LOW_SUBDIVISIONS = 16
HIGH_SENTINELS = ((512, 128), (513, 128))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    lower, upper = _round_outward(interval)
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def correlated_diagonal_interval(
    two_j: int,
    basis_index: int,
    radial_denominator: tuple[Fraction, Fraction],
    *,
    subdivisions: int,
) -> tuple[Fraction, Fraction]:
    """Enclose a local diagonal coefficient with Jacobi and axial factors intact."""
    if not 0 <= basis_index <= two_j // 2:
        raise ValueError("basis_index must be in the symmetry-unique half")
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    mp.iv.dps = INTERVAL_DPS
    diagonal_distance = two_j - 2 * basis_index
    masses = radial_cell_masses(subdivisions)
    secant = _iv_box(Fraction(1), _clock_secant_upper())
    exponent = _iv_box(Fraction(diagonal_distance, 2), Fraction(diagonal_distance, 2))
    a2 = mp.iv.mpf(A2_AT_CENTER.numerator) / A2_AT_CENTER.denominator
    b2 = mp.iv.mpf(B2_AT_CENTER.numerator) / B2_AT_CENTER.denominator
    angular_width = Fraction(1, subdivisions)
    total = (Fraction(0), Fraction(0))
    for radial_index, mass in enumerate(masses):
        radial = _iv_box(Fraction(radial_index, subdivisions), Fraction(radial_index + 1, subdivisions))
        for angular_index in range(subdivisions):
            angular = _iv_box(Fraction(angular_index, subdivisions), Fraction(angular_index + 1, subdivisions))
            transverse = a2 * secant**2 * radial**2 * (1 - angular**2)
            axial = b2 * secant**2 * radial**2 * angular**2
            jacobi = mp.iv.hyp2f1(
                -basis_index,
                basis_index + diagonal_distance + 1,
                1,
                transverse,
            )
            amplitude = (1 - transverse) ** exponent
            phase = mp.iv.atan2(mp.iv.sqrt(axial), mp.iv.sqrt(1 - transverse - axial))
            integrand = jacobi * amplitude * mp.iv.cos(diagonal_distance * phase)
            value = _interval_endpoints(integrand)
            contribution = _multiply_interval(
                mass,
                (angular_width * value[0], angular_width * value[1]),
            )
            total = total[0] + contribution[0], total[1] + contribution[1]
    return _divide_interval(total, radial_denominator)


def _old_interval(values: dict[str, Any], two_j: int, basis_index: int) -> tuple[Fraction, Fraction]:
    row = values["scalar_s0"]["modes"][two_j]["unique_diagonal"][basis_index]["clock_weighted_local_amplitude"]
    return Fraction(row["lower"]), Fraction(row["upper"])


def _overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return not (left[1] < right[0] or right[1] < left[0])


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "axial_seed": "CORRELATED_EXTREME_AXIAL_P0_EVALUATOR_EXPORTED",
        "jacobi_preflight": "EXACT_DIAGONAL_JACOBI_FACTORIZATION_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "scalar_s0": "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    denominator = _radial_denominator(values)
    low_interval = correlated_diagonal_interval(4, 1, denominator, subdivisions=LOW_SUBDIVISIONS)
    low_old = _old_interval(values, 4, 1)
    low_audit = {
        "two_j": 4,
        "basis_index": 1,
        "m": "-1",
        "subdivisions_per_axis": LOW_SUBDIVISIONS,
        "interval": _serialize(low_interval),
        "published_interval_overlap": _overlap(low_interval, low_old),
    }
    if not low_audit["published_interval_overlap"]:
        raise AssertionError("intermediate evaluator lost the published low row")
    high_audits = []
    for two_j, basis_index in HIGH_SENTINELS:
        interval = correlated_diagonal_interval(
            two_j,
            basis_index,
            denominator,
            subdivisions=REFINED_SUBDIVISIONS,
        )
        high_audits.append({
            "two_j": two_j,
            "basis_index": basis_index,
            "m": str(Fraction(-two_j, 2) + basis_index),
            "diagonal_distance": two_j - 2 * basis_index,
            "subdivisions_per_axis": REFINED_SUBDIVISIONS,
            "interval": _serialize(interval),
        })
    if any(Fraction(row["interval"]["width"]) >= Fraction(1, 10) for row in high_audits):
        raise AssertionError("a refined intermediate sentinel is too wide")
    coarse = correlated_diagonal_interval(512, 128, denominator, subdivisions=COARSE_SUBDIVISIONS)
    coarse_serialized = _serialize(coarse)
    if Fraction(coarse_serialized["width"]) <= Fraction(1, 10):
        raise AssertionError("coarse intermediate resolution mutation escaped")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result extends the correlated p=0 Darboux method from the extreme axial r=0 row to selected intermediate Jacobi diagonals. The exact terminating factor P_r^(0,d)(1-2X)={}_2F_1(-r,r+d+1;1;X), the axial amplitude/phase and the clock dependence remain inside one directed interval integrand. The 16x16 two_j=4,r=1 audit overlaps the published scalar rail. The 64x64 adjacent even/odd sentinels two_j=512,r=128 and two_j=513,r=128 both have width below 0.1, while the 32x32 two_j=512 mutation remains above 0.1 and is rejected. This certifies two intermediate p=0 sentinels only. It does not export a complete diagonal or odd-representation stream, other clock powers, a polarized/infinite-mode tail, Green images, detector response, recoil, tangent-cone restriction, Bridge 3 or quantum claims."
    )
    digest = hashlib.sha256(json.dumps(high_audits, sort_keys=True).encode()).hexdigest()
    return {
        "schema": "closed-universe-berger-correlated-intermediate-jacobi-evaluator-v1",
        "result_id": "BERGER_CORRELATED_INTERMEDIATE_JACOBI_EVALUATOR",
        "setting_id": values["axial_seed"]["setting_id"],
        "claim_status": "VALIDATED_CORRELATED_INTERMEDIATE_P0_SENTINELS_EXPORTED_COMPLETE_DIAGONAL_STREAM_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "quadrature": {
            "integrand": "{}_2F_1(-r,r+d+1;1;X) (1-X)^(d/2) cos(d atan2(sqrt(Z),sqrt(1-X-Z)))",
            "diagonal_distance": "d=two_j-2r",
            "clock_treatment": "single interval enclosure over the normalized p=0 clock support",
            "interval_engine": f"mpmath {mp.__version__} iv directed rounding",
            "interval_decimal_precision": INTERVAL_DPS,
            "output_dyadic_bits": OUTPUT_BITS,
            "refined_subdivisions_per_axis": REFINED_SUBDIVISIONS,
        },
        "low_rail_audit": low_audit,
        "intermediate_sentinel_audits": high_audits,
        "canonical_intermediate_sentinel_sha256": digest,
        "resolution_mutation": {
            "name": "halve_each_quadrature_axis_at_two_j512_r128",
            "coarse_subdivisions_per_axis": COARSE_SUBDIVISIONS,
            "coarse_interval": coarse_serialized,
            "detected": Fraction(coarse_serialized["width"]) > Fraction(1, 10),
        },
        "flags": {
            "CORRELATED_INTERMEDIATE_JACOBI_P0_EVALUATOR_EXPORTED": True,
            "LOW_TWO_J4_R1_OVERLAP_PASSED": True,
            "TWO_SELECTED_INTERMEDIATE_WIDTHS_BELOW_ONE_TENTH": True,
            "COARSE_GRID_RESOLUTION_MUTATION_REJECTED": True,
            "COMPLETE_DIAGONAL_STREAM_EXPORTED": False,
            "ALL_ODD_REPRESENTATIONS_AND_CLOCK_POWERS_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "STREAM_DECLARED_DIAGONAL_FRACTIONS_AND_ADD_ODD_INTERMEDIATE_SENTINELS_BEFORE_POLARIZATION",
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
        raise SystemExit("stale correlated intermediate Jacobi evaluator")
    print("BERGER_CORRELATED_INTERMEDIATE_JACOBI_EVALUATOR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
