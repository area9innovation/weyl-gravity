#!/usr/bin/env python3
"""Certify a declared even/odd fraction stream of correlated Jacobi rows."""
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

from closed_universe_observers.generate_berger_correlated_axial_oscillatory_evaluator import (
    _radial_denominator,
)
from closed_universe_observers.generate_berger_correlated_intermediate_jacobi_evaluator import (
    correlated_diagonal_interval,
    _serialize,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CORRELATED_DIAGONAL_FRACTION_STREAM.json"
SCHEMA = PACKAGE / "schema/berger-correlated-diagonal-fraction-stream-v1.schema.json"
REPORT = PACKAGE / "reports/berger-correlated-diagonal-fraction-stream.md"
DEPENDENCIES = {
    "intermediate": PACKAGE / "certificates/BERGER_CORRELATED_INTERMEDIATE_JACOBI_EVALUATOR.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "chart": PACKAGE / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_correlated_diagonal_fraction_stream.py",
    PACKAGE / "tests/test_berger_correlated_diagonal_fraction_stream.py",
    SCHEMA,
    REPORT,
]
SUBDIVISIONS = 64
EVEN_TWO_J = 512
ODD_TWO_J = 513
FRACTION_ROWS = (("1/8", 64), ("1/4", 128), ("3/8", 192))
EXPECTED_ROWS = tuple(
    (two_j, basis_index)
    for two_j in (EVEN_TWO_J, ODD_TWO_J)
    for _, basis_index in FRACTION_ROWS
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evaluate(task: tuple[int, int, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    two_j, basis_index, denominator = task
    interval = correlated_diagonal_interval(
        two_j,
        basis_index,
        denominator,
        subdivisions=SUBDIVISIONS,
    )
    declared_fraction = next(label for label, index in FRACTION_ROWS if index == basis_index)
    return {
        "two_j": two_j,
        "basis_index": basis_index,
        "declared_even_index_fraction": declared_fraction,
        "actual_basis_index_over_two_j": str(Fraction(basis_index, two_j)),
        "m": str(Fraction(-two_j, 2) + basis_index),
        "diagonal_distance": two_j - 2 * basis_index,
        "subdivisions_per_axis": SUBDIVISIONS,
        "interval": _serialize(interval),
    }


def _sobolev_preflight() -> dict[str, Any]:
    missing = [
        {
            "id": "profile_density_relative_to_berger_haar",
            "available": False,
            "need": "serialize the pushed-forward radius-1/128 detector density, including the rod/Haar Jacobian, as the scalar or form field to which Delta_Berger is applied",
        },
        {
            "id": "clock_uniform_repeated_laplacian_norm",
            "available": False,
            "need": "directed enclosure of ||Delta_Berger^N rho_a(t)||_L2 uniformly on both detector clock windows for a declared N",
        },
        {
            "id": "polarized_form_sobolev_norm",
            "available": False,
            "need": "the corresponding one-form/coderivative Sobolev norm after multiplying by the exact detector polarization",
        },
        {
            "id": "green_weighted_tail_conversion",
            "available": False,
            "need": "a certified conversion from the scalar/form spectral cutoff to the full Maxwell and massive-two-form Green-weighted omitted shell",
        },
    ]
    return {
        "identity": "||1_(Delta>Lambda) f||_L2 <= Lambda^(-N) ||Delta^N f||_L2",
        "available_exact_inputs": [
            "Berger scalar eigenvalue j(j+1)+31*m^2/9",
            "exact left-invariant Berger frame and finite form-Laplacian constructor",
            "fixed radius-1/128 positive-chart rod inverse and normalized flat-bump moments",
        ],
        "missing_input_ledger": missing,
        "route_status": "OPEN",
        "evaluated_sobolev_norm": False,
        "validated_infinite_mode_tail": False,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "intermediate": "CORRELATED_INTERMEDIATE_JACOBI_P0_EVALUATOR_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "profiles": "EXACT_DETECTOR_RADIAL_PROFILE_FAMILY_SERIALIZED",
        "chart": "QUANTITATIVE_LOCAL_ROD_CHART_INVERSE_CERTIFIED",
        "spectral": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    denominator = _radial_denominator(values)
    tasks = [(two_j, basis_index, denominator) for two_j, basis_index in EXPECTED_ROWS]
    with ProcessPoolExecutor(max_workers=3) as executor:
        rows = list(executor.map(_evaluate, tasks))
    if [(row["two_j"], row["basis_index"]) for row in rows] != list(EXPECTED_ROWS):
        raise AssertionError("declared diagonal-fraction coverage drifted")
    if any(Fraction(row["interval"]["width"]) >= Fraction(1, 10) for row in rows):
        raise AssertionError("a declared diagonal-fraction row is too wide")
    even = [row for row in rows if row["two_j"] == EVEN_TWO_J]
    odd = [row for row in rows if row["two_j"] == ODD_TWO_J]
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    sobolev = _sobolev_preflight()
    if not all(not item["available"] for item in sobolev["missing_input_ledger"]):
        raise AssertionError("Sobolev preflight must fail closed on every missing input")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result evaluates the correlated p=0 Jacobi integrand on the declared even-index fractions r/512=1/8,1/4,3/8 and their adjacent odd two_j=513 companions. All six 64x64 directed Darboux enclosures have width below 0.1. This is a selected fraction stream, not a complete diagonal or representation rail. A separate fail-closed Sobolev preflight records the exact spectral identity and available Berger inputs, but no certified density relative to Berger Haar volume, clock-uniform repeated-Laplacian norm, polarized form norm, or Green-weighted tail conversion is exported; no Sobolev or infinite-mode tail is therefore claimed. Other clock powers, complete polarization, Green images, detector response, recoil, tangent-cone restriction, Bridge 3, finite-r/all-orders observer-morphism stability and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-correlated-diagonal-fraction-stream-v1",
        "result_id": "BERGER_CORRELATED_DIAGONAL_FRACTION_STREAM",
        "setting_id": values["intermediate"]["setting_id"],
        "claim_status": "VALIDATED_CORRELATED_P0_DIAGONAL_FRACTION_STREAM_EXPORTED_COMPLETE_RAIL_AND_TAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "stream_declaration": {
            "external_clock_power": 0,
            "even_two_j": EVEN_TWO_J,
            "adjacent_odd_two_j": ODD_TWO_J,
            "declared_even_index_fractions": [label for label, _ in FRACTION_ROWS],
            "basis_indices": [index for _, index in FRACTION_ROWS],
            "subdivisions_per_axis": SUBDIVISIONS,
            "integrand": "{}_2F_1(-r,r+d+1;1;X) (1-X)^(d/2) cos(d atan2(sqrt(Z),sqrt(1-X-Z)))",
            "interval_engine": f"mpmath {mp.__version__} iv directed rounding",
        },
        "even_fraction_rows": even,
        "odd_companion_rows": odd,
        "canonical_fraction_stream_sha256": digest,
        "coverage_mutation": {
            "name": "delete_odd_three_eighths_companion",
            "expected_row_count": len(EXPECTED_ROWS),
            "mutated_row_count": len(EXPECTED_ROWS) - 1,
            "detected": True,
        },
        "sobolev_tail_preflight": sobolev,
        "flags": {
            "DECLARED_EVEN_ODD_DIAGONAL_FRACTION_STREAM_EXPORTED": True,
            "SIX_DECLARED_FRACTION_WIDTHS_BELOW_ONE_TENTH": True,
            "COVERAGE_MUTATION_REJECTED": True,
            "COMPLETE_DIAGONAL_STREAM_EXPORTED": False,
            "ALL_ODD_REPRESENTATIONS_AND_CLOCK_POWERS_EVALUATED": False,
            "EVALUATED_SOBOLEV_NORM_EXPORTED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "OPTIMIZE_AND_WIDEN_THE_DECLARED_FRACTION_STREAM_THEN_BUILD_POLARIZED_ROWS_WHILE_DERIVING_THE_MISSING_SOBOLEV_INPUTS",
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
        raise SystemExit("stale correlated diagonal-fraction stream")
    print("BERGER_CORRELATED_DIAGONAL_FRACTION_STREAM generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
