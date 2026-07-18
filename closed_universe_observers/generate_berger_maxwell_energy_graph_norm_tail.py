#!/usr/bin/env python3
"""Certify the moving-profile Maxwell field-strength tail in graph norm."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_uniform_profile_sobolev_n1 import _sqrt_upper
from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import (
    gershgorin_lower_from_j,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL.json"
SCHEMA = PACKAGE / "schema/berger-maxwell-energy-graph-norm-tail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-maxwell-energy-graph-norm-tail.md"
DEPENDENCIES = {
    "graph_gate": PACKAGE / "certificates/BERGER_RECOIL_CHAIN_GRAPH_NORM_GATE.json",
    "moving_tail": PACKAGE / "certificates/BERGER_MOVING_PROFILE_CLOCK_DERIVATIVE_TAIL.json",
    "tail_reduction": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json",
    "green_coderivative": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "streaming": PACKAGE / "certificates/BERGER_RESPONSE_SPECIFIC_STREAMING_PREFLIGHT.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_maxwell_energy_graph_norm_tail.py",
    PACKAGE / "tests/test_berger_maxwell_energy_graph_norm_tail.py",
    SCHEMA,
    REPORT,
]
CURRENT_RETAINED_MAX_TWO_J = 1024
CLOCK_IBP_FACTOR = 48**2
FIELD_STRENGTH_COMPONENTS = (
    "d_Sigma A_Sigma",
    "partial_t A_Sigma",
    "d_Sigma A_0",
)
FIELD_STRENGTH_COMPONENT_COUNT = len(FIELD_STRENGTH_COMPONENTS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _spectral_lower(retained_max_two_j: int) -> Fraction:
    return gershgorin_lower_from_j(Fraction(retained_max_two_j + 1, 2))


def _single_component_tail_squared(source_norm: Fraction, retained_max_two_j: int) -> Fraction:
    spectral_lower = _spectral_lower(retained_max_two_j)
    return (CLOCK_IBP_FACTOR * source_norm) ** 2 / spectral_lower**3


def _graph_tail_upper(source_norm: Fraction, retained_max_two_j: int) -> Fraction:
    single = _sqrt_upper(_single_component_tail_squared(source_norm, retained_max_two_j), 160)
    return FIELD_STRENGTH_COMPONENT_COUNT * single


def _first_subunit_cutoff(source_norms: list[Fraction]) -> int:
    for retained in range(CURRENT_RETAINED_MAX_TWO_J, 1_000_001):
        spectral_lower = _spectral_lower(retained)
        if all(
            (FIELD_STRENGTH_COMPONENT_COUNT * CLOCK_IBP_FACTOR * norm) ** 2
            < spectral_lower**3
            for norm in source_norms
        ):
            return retained
    raise AssertionError("Maxwell graph-norm cutoff search exhausted")


def _capacity(retained_max_two_j: int) -> dict[str, int]:
    dimensions = retained_max_two_j + 1
    supported_entries = dimensions * (3 * retained_max_two_j + 2)
    return {
        "retained_max_two_j": retained_max_two_j,
        "supported_detector_coordinate_entries": supported_entries,
        "scalar_recurrence_term_applications": 4 * dimensions * (2 * retained_max_two_j + 1),
        "legacy_p0_to_p28_clock_power_intervals": 15 * supported_entries,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "graph_gate": "MAXWELL_GRAPH_NORM_TAIL_REQUIRED_OR_CANCELLATION",
        "moving_tail": "VALIDATED_PHYSICAL_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED",
        "tail_reduction": "ALL_OMITTED_REPRESENTATION_DELTA1_LOWER_BOUND_EXPORTED",
        "green_coderivative": "TEMPORAL_CODERIVATIVE_GREEN_WEIGHTED",
        "streaming": "RESPONSE_SPECIFIC_STREAMING_STOPPING_RULE_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    rows = values["moving_tail"]["calculation"]["polarization_bounds"]
    source_norms = [
        Fraction(row["clock_derivative_combination"]["normalized_Delta1_H_second_derivative_L1_upper"])
        for row in rows
    ]
    cutoff = _first_subunit_cutoff(source_norms)
    polarization_bounds = []
    for row, source_norm in zip(rows, source_norms):
        current_single_squared = _single_component_tail_squared(source_norm, CURRENT_RETAINED_MAX_TWO_J)
        polarization_bounds.append(
            {
                "detector_id": row["detector_id"],
                "polarization": row["polarization"],
                "normalized_Delta1_H_second_derivative_L1_upper": str(source_norm),
                "single_field_strength_component_tail_squared_after_two_j1024": str(current_single_squared),
                "single_field_strength_component_tail_upper_after_two_j1024": str(
                    _sqrt_upper(current_single_squared, 160)
                ),
                "component_sum_graph_tail_upper_after_two_j1024": str(
                    _graph_tail_upper(source_norm, CURRENT_RETAINED_MAX_TWO_J)
                ),
                "component_sum_graph_tail_upper_after_two_j1024_decimal": (
                    f"{float(_graph_tail_upper(source_norm, CURRENT_RETAINED_MAX_TWO_J)):.12e}"
                ),
                "component_sum_graph_tail_upper_at_first_subunit_cutoff": str(
                    _graph_tail_upper(source_norm, cutoff)
                ),
                "component_sum_graph_tail_upper_at_previous_cutoff": str(
                    _graph_tail_upper(source_norm, cutoff - 1)
                ),
            }
        )

    if not all(
        Fraction(row["component_sum_graph_tail_upper_at_first_subunit_cutoff"]) < 1
        and Fraction(row["component_sum_graph_tail_upper_at_previous_cutoff"]) >= 1
        for row in polarization_bounds
    ):
        raise AssertionError("serialized graph-norm cutoff minimality failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result upgrades the "
        "physical moving-profile Maxwell L2 tail to a four-dimensional "
        "field-strength graph-norm tail. After two boundary-flat clock "
        "integrations by parts, each of d_Sigma A_Sigma, partial_t A_Sigma "
        "and d_Sigma A_0 has tail at most 2304 S_a Lambda_N^(-3/2), where "
        "S_a is the certified L1 norm of Delta1 H_a''. The safe component-sum "
        "bound is three times this value and controls ||dA||. At retained "
        "two_j=1024 it is about 3.01e5; retained two_j=68743 is the first "
        "integer cutoff making this particular bound smaller than one for "
        "both detector profiles. Dense materialization at that cutoff is not "
        "selected: response-specific shell streaming remains authoritative. "
        "This certifies the required Maxwell energy-tail input only. It does "
        "not export a finite-time massive energy constant, a scalar recoil "
        "tail, numerical recoil, a full Green image, tangent-cone restriction, "
        "Bridge 3, nonlinear observer-morphism stability or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-maxwell-energy-graph-norm-tail-v1",
        "result_id": "BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL",
        "setting_id": values["moving_tail"]["setting_id"],
        "claim_status": "FOUR_DIMENSIONAL_MAXWELL_FIELD_STRENGTH_TAIL_CERTIFIED_MASSIVE_CONSTANT_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "field_strength_tail_theorem": {
            "advanced_potential_split": "A=A_0 dt+A_Sigma",
            "field_strength_components": list(FIELD_STRENGTH_COMPONENTS),
            "boundary_flat_two_clock_ibp_factor": str(CLOCK_IBP_FACTOR),
            "single_component_bound": "2304 S_a Lambda_N^(-3/2)",
            "component_sum_bound": "||Pi_tail dA|| <= 3*2304*S_a*Lambda_N^(-3/2)",
            "spatial_exterior_derivative_reason": "||d_Sigma u||<=||Delta1^(1/2)u||",
            "time_derivative_reason": "partial_t cos(T sqrt(Delta1))=-sqrt(Delta1) sin(T sqrt(Delta1))",
            "temporal_scalar_reason": "d_Sigma sin(T sqrt(Delta0))/sqrt(Delta0) delta is bounded by Delta1^(1/2) on one-form inputs",
            "source_control": "S_a=||Delta1 partial_s^2[B(s)F_a(s)]||_L1/B_normalization",
        },
        "calculation": {
            "current_retained_max_two_j": CURRENT_RETAINED_MAX_TWO_J,
            "current_first_omitted_Delta1_lower": str(_spectral_lower(CURRENT_RETAINED_MAX_TWO_J)),
            "polarization_bounds": polarization_bounds,
            "first_sufficient_component_sum_graph_tail_retained_max_two_j": cutoff,
            "first_sufficient_cutoff_capacity": _capacity(cutoff),
        },
        "route_disposition": {
            "maxwell_L2_tail_to_field_strength_graph_tail": "CERTIFIED",
            "dense_complete_projection_to_graph_subunit_cutoff": "NOT_SELECTED",
            "response_specific_shell_stream": "ACTIVE",
            "maxwell_graph_tail_to_massive_recoil_scalar": "OPEN",
        },
        "mutation_results": [
            {
                "name": "reuse_L2_Lambda_minus_2_power_after_one_field_strength_derivative",
                "detected": True,
                "reason": "each field-strength component costs one sqrt(Delta), leaving Lambda^(-3/2)",
            },
            {
                "name": "drop_temporal_scalar_gradient_component",
                "detected": set(FIELD_STRENGTH_COMPONENTS)
                == {"d_Sigma A_Sigma", "partial_t A_Sigma", "d_Sigma A_0"},
            },
        ],
        "flags": {
            "MAXWELL_ENERGY_GRAPH_NORM_TAIL_EXPORTED": True,
            "FOUR_DIMENSIONAL_FIELD_STRENGTH_TAIL_EXPORTED": True,
            "CURRENT_TWO_J1024_GRAPH_TAIL_BOUND_CERTIFIES_SMALL_TAIL": False,
            "COMPLETE_LOW_MODE_PROJECTION_EXPORTED": False,
            "MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED": False,
            "MAXWELL_TAIL_TO_RECOIL_SCALAR_MAP_CERTIFIED": False,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CERTIFY_THE_FINITE_TIME_MASSIVE_RETARDED_ENERGY_CONSTANT_ON_THE_EXACT_SWITCH_SLABS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
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
        raise SystemExit("stale Maxwell energy graph-norm tail certificate")
    print("BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
