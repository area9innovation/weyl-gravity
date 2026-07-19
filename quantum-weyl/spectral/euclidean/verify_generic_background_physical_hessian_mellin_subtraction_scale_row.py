#!/usr/bin/env python3
"""Independent replay of the fixture Mellin subtraction scale row."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json"
SOURCE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json"


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def main() -> int:
    result = json.loads(CERTIFICATE.read_text())
    source = json.loads(SOURCE.read_text())
    a = [_q(value) for value in source["three_H1_corner"]["orientation_A_corner_weights"]]
    b = [_q(value) for value in source["three_H1_corner"]["orientation_B_corner_weights"]]
    assert b == list(reversed(a))
    triangle = 3 * (sum(a) + sum(b))
    mixed = _q(source["mixed_H1_H2_endpoint"]["full_endpoint_log_coefficient"])
    total = triangle + mixed
    assert triangle == Fraction(-1975, 72)
    assert mixed == Fraction(2704, 27)
    assert total == Fraction(15707, 216)
    assert _q(result["resolved_boundary_ledger"]["combined_residue"]) == total
    assert _q(result["renormalization_scale_row"]["coefficient"]) == total
    assert result["claim_flags"]["FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED"] is True
    assert result["claim_flags"]["GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED"] is False
    assert result["claim_flags"]["PHYSICAL_M14_CORNER_CLASS_DISPOSED"] is False
    print("independent physical Mellin subtraction scale row: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
