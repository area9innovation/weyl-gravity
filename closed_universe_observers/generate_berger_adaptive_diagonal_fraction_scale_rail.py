#!/usr/bin/env python3
"""Certify an adaptive two-scale even/odd correlated Jacobi fraction rail."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
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
CERTIFICATE = PACKAGE / "certificates/BERGER_ADAPTIVE_DIAGONAL_FRACTION_SCALE_RAIL.json"
SCHEMA = PACKAGE / "schema/berger-adaptive-diagonal-fraction-scale-rail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-adaptive-diagonal-fraction-scale-rail.md"
DEPENDENCIES = {
    "fraction_seed": PACKAGE / "certificates/BERGER_CORRELATED_DIAGONAL_FRACTION_STREAM.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_adaptive_diagonal_fraction_scale_rail.py",
    PACKAGE / "tests/test_berger_adaptive_diagonal_fraction_scale_rail.py",
    SCHEMA,
    REPORT,
]
INTERVAL_DPS = 18
OUTPUT_BITS = 96
EVEN_TWO_J = 1024
ODD_TWO_J = 1025
ANGULAR_SUBDIVISIONS = 64
ROW_DECLARATIONS = (
    ("1/8", 128, 64),
    ("1/4", 256, 64),
    ("3/8", 384, 128),
)
EXPECTED_ROWS = tuple(
    (two_j, basis_index)
    for two_j in (EVEN_TWO_J, ODD_TWO_J)
    for _, basis_index, _ in ROW_DECLARATIONS
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    lower, upper = _round_outward(interval)
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def correlated_diagonal_interval_axes(
    two_j: int,
    basis_index: int,
    radial_denominator: tuple[Fraction, Fraction],
    *,
    radial_subdivisions: int,
    angular_subdivisions: int,
) -> tuple[Fraction, Fraction]:
    """Enclose one diagonal while refining the radial and angular axes separately."""
    if not 0 <= basis_index <= two_j // 2:
        raise ValueError("basis_index must be in the symmetry-unique half")
    for value in (radial_subdivisions, angular_subdivisions):
        if value <= 0 or value & (value - 1):
            raise ValueError("axis subdivisions must be positive powers of two")
    mp.iv.dps = INTERVAL_DPS
    diagonal_distance = two_j - 2 * basis_index
    masses = radial_cell_masses(radial_subdivisions)
    secant = _iv_box(Fraction(1), _clock_secant_upper())
    exponent = _iv_box(Fraction(diagonal_distance, 2), Fraction(diagonal_distance, 2))
    a2 = mp.iv.mpf(A2_AT_CENTER.numerator) / A2_AT_CENTER.denominator
    b2 = mp.iv.mpf(B2_AT_CENTER.numerator) / B2_AT_CENTER.denominator
    angular_width = Fraction(1, angular_subdivisions)
    total = (Fraction(0), Fraction(0))
    for radial_index, mass in enumerate(masses):
        radial = _iv_box(
            Fraction(radial_index, radial_subdivisions),
            Fraction(radial_index + 1, radial_subdivisions),
        )
        for angular_index in range(angular_subdivisions):
            angular = _iv_box(
                Fraction(angular_index, angular_subdivisions),
                Fraction(angular_index + 1, angular_subdivisions),
            )
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
            value = _interval_endpoints(jacobi * amplitude * mp.iv.cos(diagonal_distance * phase))
            contribution = _multiply_interval(
                mass,
                (angular_width * value[0], angular_width * value[1]),
            )
            total = total[0] + contribution[0], total[1] + contribution[1]
    return _divide_interval(total, radial_denominator)


def _evaluate(task: tuple[str, int, int, int, int, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    kind, two_j, basis_index, radial_subdivisions, angular_subdivisions, denominator = task
    interval = correlated_diagonal_interval_axes(
        two_j,
        basis_index,
        denominator,
        radial_subdivisions=radial_subdivisions,
        angular_subdivisions=angular_subdivisions,
    )
    label = next(label for label, index, _ in ROW_DECLARATIONS if index == basis_index)
    return {
        "kind": kind,
        "two_j": two_j,
        "basis_index": basis_index,
        "declared_even_index_fraction": label,
        "actual_basis_index_over_two_j": str(Fraction(basis_index, two_j)),
        "m": str(Fraction(-two_j, 2) + basis_index),
        "diagonal_distance": two_j - 2 * basis_index,
        "radial_subdivisions": radial_subdivisions,
        "angular_subdivisions": angular_subdivisions,
        "interval": _serialize(interval),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "fraction_seed": "DECLARED_EVEN_ODD_DIAGONAL_FRACTION_STREAM_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    denominator = _radial_denominator(values)
    declared_tasks = [
        ("declared", two_j, basis_index, radial_subdivisions, ANGULAR_SUBDIVISIONS, denominator)
        for two_j in (EVEN_TWO_J, ODD_TWO_J)
        for _, basis_index, radial_subdivisions in ROW_DECLARATIONS
    ]
    mutation_task = (
        "angular_only_mutation",
        EVEN_TWO_J,
        384,
        64,
        128,
        denominator,
    )
    # Schedule the three expensive 8192-cell rows first; map order remains deterministic.
    tasks = [declared_tasks[2], declared_tasks[5], mutation_task, *declared_tasks[:2], *declared_tasks[3:5]]
    with ProcessPoolExecutor(max_workers=4) as executor:
        evaluated = list(executor.map(_evaluate, tasks))
    mutation = next(row for row in evaluated if row["kind"] == "angular_only_mutation")
    rows = sorted(
        (row for row in evaluated if row["kind"] == "declared"),
        key=lambda row: (row["two_j"], row["basis_index"]),
    )
    if [(row["two_j"], row["basis_index"]) for row in rows] != list(EXPECTED_ROWS):
        raise AssertionError("adaptive scale-rail coverage drifted")
    if any(Fraction(row["interval"]["width"]) >= Fraction(1, 10) for row in rows):
        raise AssertionError("a declared adaptive scale row is too wide")
    if Fraction(mutation["interval"]["width"]) <= Fraction(1, 10):
        raise AssertionError("angular-only refinement mutation escaped")
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result widens the correlated p=0 diagonal-fraction seed to adjacent two_j=1024,1025 representations. The declared r/1024=1/8 and 1/4 rows use 64 radial by 64 angular cells; the 3/8 rows use the minimal tested anisotropic refinement of 128 radial by 64 angular cells. All six declared widths are below 0.1. Refining only the angular axis to 64 by 128 at two_j=1024,r=384 leaves width above 0.1 and is rejected, localizing the adaptive need to the radial enclosure at this sentinel. This is a selected two-scale fraction rail, not a complete diagonal, representation, clock-power or polarized form stream. It does not export a Sobolev/infinite-mode tail, Green image, detector response, recoil, tangent-cone restriction, Bridge 3, finite-r/all-orders observer-morphism stability or quantum claim."
    )
    return {
        "schema": "closed-universe-berger-adaptive-diagonal-fraction-scale-rail-v1",
        "result_id": "BERGER_ADAPTIVE_DIAGONAL_FRACTION_SCALE_RAIL",
        "setting_id": values["fraction_seed"]["setting_id"],
        "claim_status": "VALIDATED_ADAPTIVE_P0_TWO_SCALE_DIAGONAL_FRACTION_RAIL_EXPORTED_COMPLETE_AND_POLARIZED_RAILS_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "rail_declaration": {
            "external_clock_power": 0,
            "even_two_j": EVEN_TWO_J,
            "adjacent_odd_two_j": ODD_TWO_J,
            "rows": [
                {"declared_even_index_fraction": label, "basis_index": index, "radial_subdivisions": radial, "angular_subdivisions": ANGULAR_SUBDIVISIONS}
                for label, index, radial in ROW_DECLARATIONS
            ],
            "interval_engine": f"mpmath {mp.__version__} iv directed rounding",
            "interval_decimal_precision": INTERVAL_DPS,
            "output_dyadic_bits": OUTPUT_BITS,
        },
        "even_scale_rows": [row for row in rows if row["two_j"] == EVEN_TWO_J],
        "odd_scale_rows": [row for row in rows if row["two_j"] == ODD_TWO_J],
        "canonical_scale_rail_sha256": digest,
        "anisotropic_resolution_mutation": {
            **mutation,
            "name": "refine_angular_instead_of_radial_at_two_j1024_r384",
            "detected": True,
        },
        "flags": {
            "ADAPTIVE_TWO_SCALE_EVEN_ODD_FRACTION_RAIL_EXPORTED": True,
            "SIX_TWO_J1024_1025_WIDTHS_BELOW_ONE_TENTH": True,
            "RADIAL_REFINEMENT_NEED_LOCALIZED": True,
            "ANGULAR_ONLY_REFINEMENT_MUTATION_REJECTED": True,
            "COMPLETE_DIAGONAL_STREAM_EXPORTED": False,
            "ALL_CLOCK_POWERS_AND_POLARIZED_ROWS_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "APPLY_THE_CERTIFIED_POLARIZATION_RECURRENCE_TO_THE_DECLARED_TWO_SCALE_ROWS_AND_ADD_EXTERNAL_CLOCK_POWERS",
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
        raise SystemExit("stale adaptive diagonal-fraction scale rail")
    print("BERGER_ADAPTIVE_DIAGONAL_FRACTION_SCALE_RAIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
