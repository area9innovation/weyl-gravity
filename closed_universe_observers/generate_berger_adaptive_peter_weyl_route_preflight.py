#!/usr/bin/env python3
"""Choose a fail-closed route beyond the obstructed two_j<=4 profile cutoff."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-adaptive-peter-weyl-route-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-adaptive-peter-weyl-route-preflight.md"
DEPENDENCIES = {
    "tail_obstruction": PACKAGE / "certificates/BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION.json",
    "form_engine": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "green_weighted": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_adaptive_peter_weyl_route_preflight.py",
    "tests": PACKAGE / "tests/test_berger_adaptive_peter_weyl_route_preflight.py",
    "schema": SCHEMA,
    "report": REPORT,
}
TARGET_FRACTIONS = (Fraction(9, 10), Fraction(99, 100), Fraction(999, 1000), Fraction(1))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def weighted_capacity(max_dimension: int) -> int:
    """Maximum three-component Peter--Weyl energy through dimension D."""
    triangular = max_dimension * (max_dimension + 1) // 2
    return 3 * triangular**2


def unweighted_mutation_capacity(max_dimension: int) -> int:
    """Mutation which incorrectly omits the Peter--Weyl dimension weight."""
    return 3 * max_dimension * (max_dimension + 1) * (2 * max_dimension + 1) // 6


def minimum_dimension(target: Fraction, capacity: Callable[[int], int] = weighted_capacity) -> int:
    dimension = 1
    while capacity(dimension) < target:
        dimension += 1
    return dimension


def cutoff_row(total_energy_lower: Fraction, fraction: Fraction) -> dict[str, Any]:
    target = fraction * total_energy_lower
    dimension = minimum_dimension(target)
    if weighted_capacity(dimension - 1) >= target or weighted_capacity(dimension) < target:
        raise AssertionError("cutoff minimality failed")
    return {
        "fraction_of_certified_energy_lower": str(fraction),
        "minimum_max_dimension_for_capacity": dimension,
        "minimum_two_j_max_for_capacity": dimension - 1,
        "previous_capacity": str(weighted_capacity(dimension - 1)),
        "selected_capacity": str(weighted_capacity(dimension)),
        "interpretation": "necessary capacity condition only; it neither bounds the actual tail nor proves that the retained coefficients attain this capacity",
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "tail_obstruction": "TWO_J4_UNIFORM_PROFILE_TAIL_SMALLNESS_OBSTRUCTED",
        "form_engine": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "green_weighted": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    energy_lower = Fraction(values["tail_obstruction"]["tail_audit"]["total_fourier_energy_lower"])
    rows = [cutoff_row(energy_lower, fraction) for fraction in TARGET_FRACTIONS]
    full_row = rows[-1]
    dimension = full_row["minimum_max_dimension_for_capacity"]
    sum_squares = dimension * (dimension + 1) * (2 * dimension + 1) // 6
    triangular = dimension * (dimension + 1) // 2
    wrong_dimension = minimum_dimension(energy_lower, unweighted_mutation_capacity)
    if dimension != 139 or full_row["minimum_two_j_max_for_capacity"] != 138:
        raise AssertionError("radius-scale necessary cutoff drifted")
    if wrong_dimension == dimension:
        raise AssertionError("Peter--Weyl multiplicity mutation escaped")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight converts the certified clock-center profile-energy lower bound into necessary Peter--Weyl capacity cutoffs. Under the certified unit bound on each of three coframe coefficient entries, capacity through representation dimension D is 3(sum_{d=1}^D d)^2. Reaching even 99 percent of the certified lower bound requires D>=139, equivalently two_j>=138; D=138 is insufficient. The existing exact finite-block form engine therefore selects a streamed, symmetry-reduced adaptive Peter--Weyl contraction as the next repository-supported route. A dense full-matrix JSON export is not selected, and physical-space propagation remains open because no validated Berger hyperbolic PDE solver is present. These are necessary capacity and implementation-route results only: they do not certify convergence at two_j=138, an infinite tail upper bound, a full Maxwell or massive-two-form image, recoil, tangent-cone restriction, a physical-branch map, or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-adaptive-peter-weyl-route-preflight-v1",
        "result_id": "BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT",
        "setting_id": values["tail_obstruction"]["setting_id"],
        "claim_status": "ADAPTIVE_PETER_WEYL_STREAMING_ROUTE_SELECTED_FULL_IMAGE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "capacity_convention": {
            "entry_bound": "|hat F^alpha_mn(j)|<=1 for alpha=1,2,3",
            "parseval_weight": "d=2j+1",
            "capacity_formula": "3 sum_{d=1}^D d^3 = 3[D(D+1)/2]^2",
            "profile_energy_lower": str(energy_lower),
        },
        "necessary_cutoffs": rows,
        "selected_route": {
            "route": "STREAMED_SYMMETRY_REDUCED_ADAPTIVE_PETER_WEYL_CONTRACTION",
            "status": "SELECTED_FOR_NEXT_GATE",
            "starting_capacity_rail": "two_j_max=138 is necessary but not certified sufficient",
            "serialization": "stream per-representation detector contractions and tail witnesses; do not export every dense Green-image matrix entry",
            "next_calculation": "derive the polarization coefficient recurrence and operator-norm Green tail, then increase the cutoff until the declared response tolerance closes",
        },
        "route_dispositions": [
            {"route": "dense full-matrix symbolic JSON through two_j=138", "status": "NOT_SELECTED", "reason": "unnecessary artifact expansion; use streamed contractions"},
            {"route": "validated physical-space Green chain", "status": "OPEN_NO_VALIDATED_SOLVER", "reason": "no certified Berger hyperbolic PDE solver or error estimator exists in the repository"},
        ],
        "scale_audit": {
            "top_scalar_representation_dimension": dimension,
            "top_one_form_block_dimension": 3 * dimension,
            "three_component_coefficient_entries_through_cutoff": 3 * sum_squares,
            "dense_one_form_operator_entries_through_cutoff": 9 * sum_squares,
            "dense_apply_scalar_multiplication_upper_count": 9 * triangular**2,
        },
        "mutation_results": [{"name": "omit_Peter_Weyl_dimension_weight", "detected": True, "mutated_minimum_max_dimension": wrong_dimension}],
        "flags": {
            "NECESSARY_TWO_J138_CAPACITY_RAIL_EXPORTED": True,
            "STREAMED_ADAPTIVE_PETER_WEYL_ROUTE_SELECTED": True,
            "TWO_J138_CONVERGENCE_CERTIFIED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "ADVANCED_MASSIVE_EMITTER_GREEN_IMAGE_EVALUATED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "DERIVE_STREAMABLE_POLARIZATION_COEFFICIENT_RECURRENCE_AND_GREEN_WEIGHTED_OPERATOR_NORM_TAIL",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()],
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
        raise SystemExit("stale adaptive Peter-Weyl route preflight")
    print("BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
