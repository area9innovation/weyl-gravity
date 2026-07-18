#!/usr/bin/env python3
"""Decide whether the degree-ten temporal Green polynomial reaches two_j=138."""

from __future__ import annotations

import argparse
from fractions import Fraction
from math import factorial
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    _infinity_norm_upper,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import laplacian

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_TEMPORAL_GREEN_ORDER_FIVE_HIGH_MODE_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-temporal-green-order-five-high-mode-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-temporal-green-order-five-high-mode-preflight.md"
DEPENDENCIES = {
    "polarization": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138.json",
    "sectors": PACKAGE / "certificates/BERGER_STREAMABLE_POLARIZATION_SECTORS.json",
    "green": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_temporal_green_order_preflight.py",
    "tests": PACKAGE / "tests/test_berger_temporal_green_order_preflight.py",
    "schema": SCHEMA,
    "report": REPORT,
}
TOP_TWO_J = 138
SERIES_ORDER = 5


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extreme_positive_charge_eigenvalue(two_j: int) -> Fraction:
    """Delta_1 eigenvalue on the one-dimensional q=j+1, theta_+ block."""
    j = Fraction(two_j, 2)
    return j * (j + 1) + (31 * j * j + 71 * j + 40) / 9


def cosine_polynomial(y: Fraction, order: int = SERIES_ORDER) -> Fraction:
    return sum(((-1) ** n) * y**n / factorial(2 * n) for n in range(order + 1))


def first_contractive_order(y: Fraction) -> int:
    for order in range(SERIES_ORDER, 10_000):
        if y < (2 * order + 3) * (2 * order + 4):
            return order
    raise AssertionError("no contractive order found")


def build() -> dict:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["polarization"]["flags"].get("DETECTOR_PREFACTORED_POLARIZATION_INTERVAL_STREAM_TWO_J0_TO_138_EXPORTED") is not True:
        raise AssertionError("polarization stream dropped")
    if values["sectors"]["flags"].get("MAXIMUM_GREEN_CHARGE_BLOCK_DIMENSION_THREE") is not True:
        raise AssertionError("charge-block decomposition dropped")
    if values["green"]["series_convention"].get("order") != SERIES_ORDER:
        raise AssertionError("low-mode Green series order changed")

    top_operator_norm = _infinity_norm_upper(laplacian(TOP_TWO_J, 1))
    witness_lambda = extreme_positive_charge_eigenvalue(TOP_TWO_J)
    detectors = []
    tau_by_detector = {"D0": Fraction(1, 8), "D1": Fraction(5, 24)}
    for detector, tau in tau_by_detector.items():
        witness_y = witness_lambda * tau**2
        polynomial = cosine_polynomial(witness_y)
        error_lower = abs(polynomial) - 1
        norm_y = top_operator_norm * tau**2
        required_order = first_contractive_order(norm_y)
        if error_lower <= 0 or required_order <= SERIES_ORDER:
            raise AssertionError("fixed-order high-mode obstruction disappeared")
        detectors.append({
            "detector_id": detector,
            "tau_max": str(tau),
            "extreme_charge_q": "j+1",
            "extreme_block_dimension": 1,
            "extreme_block_eigenvalue": str(witness_lambda),
            "witness_y_lambda_tau_squared": str(witness_y),
            "degree_ten_cosine_polynomial": str(polynomial),
            "cosine_error_absolute_lower": str(error_lower),
            "Delta1_infinity_norm_upper": str(top_operator_norm),
            "norm_y_upper": str(norm_y),
            "first_geometric_contractive_series_order": required_order,
            "required_even_clock_power_maximum": 2 * required_order,
        })
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight proves that the six p=0,2,...,10 rails define the formal order-five cosine/sine matrix polynomial but cannot certify it as the advanced Green function through form two_j=138. On the one-dimensional extreme q=j+1 block, Delta1=196000/9; at the certified detector time radii the degree-ten cosine polynomial differs from the bounded exact cosine by at least the exported positive rational lower bounds. The existing geometric entire-series rail first becomes contractive at series order 8 for D0 and 14 for D1, requiring external-clock streams through p=28 for a common proof. This is an obstruction to fixed-order promotion, not an obstruction to the exact Green function. Charge-block polynomial application, adaptive rails, the spatial tail, full Maxwell/massive images, recoil, tangent-cone restriction, Bridge 3 and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-temporal-green-order-five-high-mode-preflight-v1",
        "result_id": "BERGER_TEMPORAL_GREEN_ORDER_FIVE_HIGH_MODE_PREFLIGHT",
        "setting_id": values["polarization"]["setting_id"],
        "claim_status": "FIXED_DEGREE_TEN_GREEN_PROMOTION_OBSTRUCTED_ADAPTIVE_ORDER_FOURTEEN_REQUIRED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "top_rail_two_j": TOP_TWO_J,
        "input_series_order": SERIES_ORDER,
        "detector_audits": detectors,
        "mutation_results": [{"name": "promote_degree_ten_polynomial_to_green_without_remainder", "detected": True, "reason": "the exact extreme-block error lower bound is positive"}],
        "flags": {
            "DEGREE_TEN_FORMAL_TEMPORAL_POLYNOMIAL_DEFINED": True,
            "DEGREE_TEN_UNIFORM_GREEN_APPROXIMATION_TWO_J0_TO_138_CERTIFIED": False,
            "FIXED_ORDER_GREEN_PROMOTION_OBSTRUCTED": True,
            "COMMON_SERIES_ORDER_AT_LEAST_FOURTEEN_REQUIRED_BY_CURRENT_REMAINDER_RAIL": True,
            "CLOCK_WEIGHTED_STREAMS_THROUGH_S28_EXPORTED": False,
            "TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED": False,
            "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "EXTEND_EXTERNAL_CLOCK_WEIGHTED_SCALAR_AND_POLARIZATION_STREAMS_THROUGH_P28_THEN_APPLY_ADAPTIVE_ORDER_FOURTEEN_CHARGE_BLOCK_POLYNOMIAL",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
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
        raise SystemExit("stale temporal Green order preflight")
    print("BERGER_TEMPORAL_GREEN_ORDER_FIVE_HIGH_MODE_PREFLIGHT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
