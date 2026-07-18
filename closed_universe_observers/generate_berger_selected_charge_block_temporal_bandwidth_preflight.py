#!/usr/bin/env python3
"""Audit the temporal microphase bandwidth of the completed selected blocks."""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
from math import factorial
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_stream import (
    SERIES_ORDER,
    block_powers,
    dressed_block,
)
from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import scalar_eigenvalue


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_TEMPORAL_BANDWIDTH_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-selected-charge-block-temporal-bandwidth-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-selected-charge-block-temporal-bandwidth-preflight.md"
DEPENDENCIES = {
    "completed_inputs": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_FORM_COMPANION_CLOCK_RAIL.json",
    "exact_blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
    "lower_band_preflight": PACKAGE / "certificates/BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_PREFLIGHT.json",
    "lower_band_stream": PACKAGE / "certificates/BERGER_BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_STREAM_TWO_J138.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_selected_charge_block_temporal_bandwidth_preflight.py",
    PACKAGE / "tests/test_berger_selected_charge_block_temporal_bandwidth_preflight.py",
    SCHEMA,
    REPORT,
]
TARGET_REMAINDER = Fraction(1, 10**17)
INTERNAL_CLOCK_SCALE_SQUARED = Fraction(1, 48**2)

ComplexInterval = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _complex_interval(value: dict[str, Any]) -> ComplexInterval:
    return (
        (Fraction(value["real"]["lower"]), Fraction(value["real"]["upper"])),
        (Fraction(value["imaginary"]["lower"]), Fraction(value["imaginary"]["upper"])),
    )


def _width(value: ComplexInterval) -> Fraction:
    return max(value[0][1] - value[0][0], value[1][1] - value[1][0])


def _entry_absolute_upper(value: ComplexInterval) -> Fraction:
    return max(abs(value[0][0]), abs(value[0][1])) + max(abs(value[1][0]), abs(value[1][1]))


def _matrix_infinity_norm_upper(matrix: tuple[tuple[ComplexInterval, ...], ...]) -> Fraction:
    return max(sum((_entry_absolute_upper(entry) for entry in row), Fraction(0)) for row in matrix)


def _cosine_polynomial(y: Fraction, order: int = SERIES_ORDER) -> Fraction:
    return sum(Fraction((-1) ** index) * y**index / factorial(2 * index) for index in range(order + 1))


def _geometric_cosine_remainder(y: Fraction, order: int) -> tuple[Fraction, Fraction]:
    ratio = y / Fraction((2 * order + 3) * (2 * order + 4))
    if ratio >= 1:
        raise AssertionError("selected microphase remainder is not contractive")
    tail = y ** (order + 1) / factorial(2 * order + 2) / (1 - ratio)
    return ratio, tail


def _first_target_order(y: Fraction) -> tuple[int, Fraction, Fraction]:
    for order in range(SERIES_ORDER, 1000):
        ratio = y / Fraction((2 * order + 3) * (2 * order + 4))
        if ratio >= 1:
            continue
        tail = y ** (order + 1) / factorial(2 * order + 2) / (1 - ratio)
        if tail < TARGET_REMAINDER:
            return order, ratio, tail
    raise AssertionError("no selected microphase order reaches the target")


def _serialize_interval(value: ComplexInterval) -> list[list[str]]:
    return [[str(endpoint) for endpoint in axis] for axis in value]


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "completed_inputs": "ALL_18_SELECTED_CHARGE_BLOCK_INPUTS_CLOSED",
        "exact_blocks": "ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED",
        "lower_band_preflight": "EXISTING_EVEN_CLOCK_INPUTS_P0_TO_P28_SUFFICIENT",
        "lower_band_stream": "FINITE_RAIL_EXACT_T_TEMPORAL_FUNCTIONAL_CALCULUS_IMAGE_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if max(row["two_j"] for row in values["lower_band_stream"]["mode_summaries"]) != 138:
        raise AssertionError("lower-band stream scope drifted")

    blocks = values["completed_inputs"]["completed_charge_block_inputs"]
    charges = sorted({Fraction(block["charge_q"]) for block in blocks})
    if len(blocks) != 18 or len(charges) != 9:
        raise AssertionError("selected block or charge coverage drifted")

    charge_audits = []
    for charge in charges:
        members, powers, _ = block_powers(1024, charge)
        norm_upper = _matrix_infinity_norm_upper(powers[1])
        y_upper = norm_upper * INTERNAL_CLOCK_SCALE_SQUARED
        order14_ratio, order14_tail = _geometric_cosine_remainder(y_upper, SERIES_ORDER)
        scalar_lambda_expr = scalar_eigenvalue(1024, charge)
        scalar_lambda = Fraction(int(sp.numer(scalar_lambda_expr)), int(sp.denom(scalar_lambda_expr)))
        scalar_y = scalar_lambda * INTERNAL_CLOCK_SCALE_SQUARED
        polynomial = _cosine_polynomial(scalar_y)
        exact_error_lower = abs(polynomial) - 1
        required_order, required_ratio, required_tail = _first_target_order(y_upper)
        if exact_error_lower <= 0 or required_order <= SERIES_ORDER:
            raise AssertionError("selected order-14 obstruction disappeared")
        charge_audits.append({
            "charge_q": str(charge),
            "block_dimension": len(members),
            "member_helicity_and_m": [[component, str(m)] for component, m in members],
            "Delta1_block_infinity_norm_upper": str(norm_upper),
            "internal_microphase_y_upper": str(y_upper),
            "embedded_scalar_eigenvalue": str(scalar_lambda),
            "embedded_scalar_microphase_y": str(scalar_y),
            "order14_geometric_ratio": str(order14_ratio),
            "order14_cosine_remainder_upper": str(order14_tail),
            "order14_scalar_cosine_polynomial": str(polynomial),
            "order14_exact_cosine_error_absolute_lower": str(exact_error_lower),
            "first_geometric_order_with_remainder_below_1e_minus_17": required_order,
            "required_even_clock_power_maximum": 2 * required_order,
            "required_order_ratio": str(required_ratio),
            "required_order_remainder_upper": str(required_tail),
        })

    actual_rows = []
    digest_rows = []
    for block in blocks:
        charge = Fraction(block["charge_q"])
        moments = {
            row["clock_power"]: [_complex_interval(entry["value"]) for entry in row["helicity_input_vector"]]
            for row in block["clock_power_helicity_vectors"]
        }
        members, powers, _ = block_powers(1024, charge)
        expected_members = [
            (entry["helicity_component"], Fraction(entry["form_row"] - 512))
            for entry in block["clock_power_helicity_vectors"][0]["helicity_input_vector"]
        ]
        if members != expected_members:
            raise AssertionError("selected input member order drifted")
        spatial, temporal = dressed_block(1024, charge, moments, powers)
        maximum_width = max(_width(value) for value in [*spatial, temporal])
        actual_rows.append({
            "detector_id": block["detector_id"],
            "form_column": block["form_column"],
            "charge_q": block["charge_q"],
            "maximum_order14_independent_interval_width": str(maximum_width),
            "width_below_one_tenth": maximum_width < Fraction(1, 10),
        })
        digest_rows.append({
            "detector_id": block["detector_id"],
            "form_column": block["form_column"],
            "charge_q": block["charge_q"],
            "spatial": [_serialize_interval(value) for value in spatial],
            "temporal": _serialize_interval(temporal),
        })
    widths = [Fraction(row["maximum_order14_independent_interval_width"]) for row in actual_rows]
    if any(row["width_below_one_tenth"] for row in actual_rows):
        raise AssertionError("selected independent-interval obstruction disappeared")

    maximum_required_order = max(row["first_geometric_order_with_remainder_below_1e_minus_17"] for row in charge_audits)
    maximum_required_power = max(row["required_even_clock_power_maximum"] for row in charge_audits)
    minimum_witness = min(Fraction(row["order14_exact_cosine_error_absolute_lower"]) for row in charge_audits)
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight audits the 18 completed selected Maxwell charge-block inputs at form two_j=1024. The previously certified order-14 p<=28 microphase theorem is scoped only through two_j=138 and cannot be widened by name. On all nine distinct selected charges, an exact rational scalar eigenvalue embedded in the three-dimensional one-form block gives a positive order-14 cosine-error lower bound from |P14|-1; the minimum is exported. Direct application of the existing independent interval-matrix-power rail to all 18 completed inputs has width above 0.1 in every case, and interval addition cannot narrow those enclosures by merely appending higher monomials. The current geometric proof first reaches remainder below 1e-17 at orders up to 39, requiring even powers through p=78, but this does not repair the independent-interval cancellation loss. The certified next route is a correlated direct normalized clock-microphase transform in the exact block spectral projectors, with low-band overlap. This obstructs only order-14/p28 promotion and the current independent-moment interval class, not the exact temporal functional calculus. No spatial tail, full Green image, detector response, recoil, cone restriction, active Bridge 3, finite-r/all-orders observer-morphism stability or quantum claim is certified."
    )
    return {
        "schema": "closed-universe-berger-selected-charge-block-temporal-bandwidth-preflight-v1",
        "result_id": "BERGER_SELECTED_CHARGE_BLOCK_TEMPORAL_BANDWIDTH_PREFLIGHT",
        "setting_id": values["completed_inputs"]["setting_id"],
        "claim_status": "ORDER14_P28_SELECTED_TWO_J1024_MICROPHASE_PROMOTION_OBSTRUCTED_CORRELATED_DIRECT_TRANSFORM_REQUIRED",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "scope": {
            "form_two_j": 1024,
            "completed_selected_block_count": len(blocks),
            "distinct_charge_count": len(charges),
            "input_even_clock_power_maximum": 28,
            "input_series_order": SERIES_ORDER,
            "lower_band_certificate_maximum_two_j": 138,
        },
        "charge_audits": charge_audits,
        "actual_completed_input_order14_interval_audits": actual_rows,
        "coverage": {
            "minimum_exact_order14_cosine_error_absolute_lower": str(minimum_witness),
            "minimum_actual_order14_independent_interval_width": str(min(widths)),
            "maximum_actual_order14_independent_interval_width": str(max(widths)),
            "maximum_required_geometric_order_for_1e_minus_17": maximum_required_order,
            "maximum_required_even_clock_power": maximum_required_power,
            "canonical_order14_completed_input_output_sha256": hashlib.sha256(json.dumps(digest_rows, sort_keys=True).encode()).hexdigest(),
        },
        "route_disposition": {
            "order14_p28_promotion": "OBSTRUCTED",
            "higher_monomial_extension_in_current_independent_interval_class": "OBSTRUCTED_FOR_WIDTH_BELOW_ONE_TENTH",
            "exact_temporal_functional_calculus": "OPEN",
            "next_route": "CORRELATED_DIRECT_NORMALIZED_CLOCK_MICROPHASE_TRANSFORM_IN_EXACT_BLOCK_SPECTRAL_PROJECTORS_WITH_LOW_BAND_OVERLAP",
        },
        "mutation_results": [{
            "name": "reuse_two_j138_order14_preflight_at_two_j1024_by_matching_carrier_names",
            "detected": True,
            "reason": "the mode scope differs and every selected charge has a positive exact order-14 cosine-error lower bound",
        }],
        "flags": {
            "ALL_18_COMPLETED_SELECTED_BLOCK_INPUTS_AUDITED": True,
            "ALL_9_DISTINCT_SELECTED_CHARGES_AUDITED": True,
            "ORDER14_P28_SELECTED_MICROPHASE_PROMOTION_OBSTRUCTED": True,
            "CURRENT_INDEPENDENT_MOMENT_INTERVAL_ROUTE_WIDTH_BELOW_ONE_TENTH_OBSTRUCTED": True,
            "GEOMETRIC_REMAINDER_BELOW_ONE_E_MINUS_SEVENTEEN_REQUIRES_POWERS_THROUGH_P78": True,
            "CORRELATED_DIRECT_CLOCK_MICROPHASE_TRANSFORM_REQUIRED": True,
            "TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED": False,
            "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CERTIFY_A_CORRELATED_DIRECT_NORMALIZED_CLOCK_MICROPHASE_TRANSFORM_IN_THE_EXACT_SELECTED_BLOCK_SPECTRAL_PROJECTORS_WITH_LOW_BAND_OVERLAP",
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
        raise SystemExit("stale selected charge-block temporal bandwidth preflight")
    print("BERGER_SELECTED_CHARGE_BLOCK_TEMPORAL_BANDWIDTH_PREFLIGHT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
