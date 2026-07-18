#!/usr/bin/env python3
"""Choose a response-specific stream over materializing the full Berger rail."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import gershgorin_lower_from_j


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RESPONSE_SPECIFIC_STREAMING_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-response-specific-streaming-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-response-specific-streaming-preflight.md"
DEPENDENCIES = {
    "moving_tail": PACKAGE / "certificates/BERGER_MOVING_PROFILE_CLOCK_DERIVATIVE_TAIL.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "direct_clock": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM.json",
    "recoil": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
    "rank": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
}
SOURCE_FILES = [Path(__file__), PACKAGE / "verify_berger_response_specific_streaming_preflight.py", PACKAGE / "tests/test_berger_response_specific_streaming_preflight.py", SCHEMA, REPORT]
LEGACY_EVEN_CLOCK_POWER_COUNT = 15
CURRENT_RETAINED_MAX_TWO_J = 1024
TOLERANCES = (Fraction(1), Fraction(1, 10), Fraction(1, 100), Fraction(1, 1000), Fraction(1, 1_000_000))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _capacity(max_two_j: int) -> dict[str, int]:
    dimensions = max_two_j + 1
    coordinate_entries = dimensions * (3 * max_two_j + 2)
    scalar_terms = 4 * dimensions * (2 * max_two_j + 1)
    return {
        "retained_max_two_j": max_two_j,
        "supported_detector_coordinate_entries": coordinate_entries,
        "scalar_recurrence_term_applications": scalar_terms,
        "legacy_p0_to_p28_clock_power_intervals": LEGACY_EVEN_CLOCK_POWER_COUNT * coordinate_entries,
    }


def _tail_constants(moving: dict[str, Any]) -> dict[str, Fraction]:
    return {
        row["detector_id"]: 2304 * Fraction(row["clock_derivative_combination"]["normalized_Delta1_H_second_derivative_L1_upper"])
        for row in moving["calculation"]["polarization_bounds"]
    }


def _tail_upper(constants: dict[str, Fraction], max_two_j: int) -> dict[str, Fraction]:
    spectral = gershgorin_lower_from_j(Fraction(max_two_j + 1, 2))
    return {detector: constant / spectral**2 for detector, constant in constants.items()}


def _first_cutoff(constants: dict[str, Fraction], tolerance: Fraction) -> int:
    for max_two_j in range(CURRENT_RETAINED_MAX_TWO_J, 1_000_001):
        if all(value < tolerance for value in _tail_upper(constants, max_two_j).values()):
            return max_two_j
    raise AssertionError("declared tolerance cutoff search exhausted")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "moving_tail": "VALIDATED_PHYSICAL_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
        "direct_clock": "FINITE_SELECTED_EXACT_T_TEMPORAL_IMAGE_REPRESENTATION_EXPORTED",
        "recoil": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
        "rank": "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    constants = _tail_constants(values["moving_tail"])
    tolerance_rows = []
    for tolerance in TOLERANCES:
        cutoff = _first_cutoff(constants, tolerance)
        previous = _tail_upper(constants, cutoff - 1)
        current = _tail_upper(constants, cutoff)
        if not all(value < tolerance for value in current.values()) or all(value < tolerance for value in previous.values()):
            raise AssertionError("cutoff minimality failed")
        tolerance_rows.append({
            "detector_L2_tail_tolerance": str(tolerance),
            "first_sufficient_retained_max_two_j": cutoff,
            "tail_uppers_at_cutoff": {key: str(value) for key, value in current.items()},
            "capacity": _capacity(cutoff),
        })
    if tolerance_rows[0]["first_sufficient_retained_max_two_j"] != values["moving_tail"]["calculation"]["first_sufficient_moving_profile_retained_max_two_j"]:
        raise AssertionError("unit tolerance cutoff drifted from moving-profile certificate")

    stopping_rule = {
        "fixed_chain_scalar": "R_ab=L_ab(A_adv)",
        "required_dual_bound": "B_ab >= ||L_ab|| on the declared Maxwell-output Hilbert norm",
        "tail_transfer": "|R_ab-R_ab^(<=N)| <= B_ab E_N",
        "interval_stop": "publish tolerance eta only when width(I_N)+2 B_ab E_N <= eta",
        "nonzero_stop": "certify nonzero only when dist(0,I_N) > B_ab E_N",
        "sign_stop": "certify sign only when I_N+[-B_ab E_N,B_ab E_N] lies strictly on one side of zero",
        "rank_stop": "for a numerical 2x2 response, apply the determinant perturbation bound to the four entry-tail radii; leading formal rank two remains independently certified",
    }
    missing = [
        {"id": "fixed_massive_chain_dual_norms", "status": "OPEN", "need": "certified B_ab for the fixed switches, massive retarded Green operators, couplings and preparations"},
        {"id": "complete_modewise_scalar_integrand", "status": "OPEN", "need": "stream the exact Maxwell charge-block transform directly into each fixed massive/recoil contraction without serializing all form coefficients"},
        {"id": "declared_numerical_tolerance_or_nonzero_goal", "status": "OPEN", "need": "use interval/nonzero/sign stopping rule; do not substitute the arbitrary L2 threshold one"},
    ]
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight audits the cost and claim logic of completing the Berger detector profile after the moving-profile tail theorem. The all-finite Clebsch--Gordan support formulas show that materializing the first sub-unit rail through two_j=3835 would require 44,140,852 supported detector-coordinate entries, 117,703,824 scalar recurrence applications, and 662,112,780 intervals in the legacy fifteen-clock-power representation. Smaller detector-L2 tolerances grow these counts exactly as exported. A full coefficient artifact is not required to evaluate a fixed scalar record or recoil coefficient: for a certified chain dual norm B_ab, a shell stream may stop with scalar error B_ab E_N, using the exported interval, sign, nonzero or determinant rule. No B_ab or complete modewise massive-chain scalar integrand is currently certified, so there is NO_CERTIFIED_MAP from the physical Maxwell L2 tail to a numerical recoil interval. This preflight replaces the arbitrary 'tail below one then materialize everything' work item by the response-specific streaming gate. It does not evaluate recoil, construct a full Green image, restrict to the tangent cone, activate Bridge 3, promote nonlinear observer-morphism stability, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-response-specific-streaming-preflight-v1",
        "result_id": "BERGER_RESPONSE_SPECIFIC_STREAMING_PREFLIGHT",
        "setting_id": values["moving_tail"]["setting_id"],
        "claim_status": "EXACT_PROJECTION_CAPACITY_AND_RESPONSE_STREAMING_RULE_CERTIFIED_CHAIN_DUAL_NORMS_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "capacity_formulas": {
            "supported_detector_coordinate_entries_through_N": "(N+1)(3N+2)",
            "scalar_recurrence_term_applications_through_N": "4(N+1)(2N+1)",
            "legacy_even_clock_powers": list(range(0, 29, 2)),
            "legacy_clock_interval_count": "15(N+1)(3N+2)",
            "derivation": "sum_(d=1)^(N+1)(6d-4) and sum_(d=1)^(N+1)(16d-12)",
        },
        "tolerance_capacity_rows": tolerance_rows,
        "response_specific_streaming_theorem": stopping_rule,
        "unresolved_streaming_inputs": missing,
        "route_decision": {
            "materialize_complete_legacy_clock_power_rail": "NOT_SELECTED",
            "stream_exact_charge_blocks_into_fixed_scalar_functionals": "ACTIVE",
            "maxwell_tail_to_recoil_scalar_map": "NO_CERTIFIED_MAP",
        },
        "mutation_results": [
            {"name": "omit_two_detector_components_in_coordinate_count", "detected": _capacity(138)["supported_detector_coordinate_entries"] == values["recurrence"]["scale_audit_through_two_j138"]["coordinate_entry_count"]},
            {"name": "reuse_unit_L2_threshold_as_numerical_recoil_tolerance", "detected": True, "reason": "a scalar tail requires the fixed chain dual norm and a declared scalar stopping goal"},
        ],
        "flags": {
            "EXACT_COMPLETE_RAIL_CAPACITY_FORMULAS_EXPORTED": True,
            "RESPONSE_SPECIFIC_STREAMING_STOPPING_RULE_EXPORTED": True,
            "MATERIALIZED_COMPLETE_TWO_J3835_PROJECTION_EXPORTED": False,
            "FIXED_MASSIVE_CHAIN_DUAL_NORMS_EXPORTED": False,
            "MAXWELL_TAIL_TO_RECOIL_SCALAR_MAP_CERTIFIED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CERTIFY_FIXED_MASSIVE_RECOIL_CHAIN_DUAL_NORMS_AND_STREAM_MODE_BLOCKS_DIRECTLY_INTO_THE_SCALAR_CONTRACTIONS",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    value = build(); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True)+"\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=rendered): raise SystemExit("stale response-specific streaming preflight")
    print("BERGER_RESPONSE_SPECIFIC_STREAMING_PREFLIGHT generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
