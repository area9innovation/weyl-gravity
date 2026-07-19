#!/usr/bin/env python3
"""Independent consumer for the generic physical full-boundary incidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json"


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _evaluate(row: dict[str, Any], boxes: tuple[int, int, int]) -> sp.Rational:
    numerator = sum(
        _q(term["coefficient"])
        * sp.prod(value**power for value, power in zip(boxes, term["box_exponents"]))
        for term in row["numerator_terms"]
    )
    denominator = sp.prod(
        value**power for value, power in zip(boxes, row["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["result_state"] == (
        "GENERIC_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED_M14_NONZERO_RENORMALIZED"
    )
    assert len(value["channel_rows"]) == 11
    for row in value["channel_rows"]:
        for boxes in ((1, 1, 1), (2, 3, 5)):
            assert _evaluate(row["triangle_six_ordering_scale_row"], boxes) + _evaluate(
                row["contact_six_endpoint_scale_row"], boxes
            ) == _evaluate(row["combined_scale_row"], boxes)
    for component in (
        "triangle_six_ordering_scale_row",
        "contact_six_endpoint_scale_row",
        "combined_scale_row",
    ):
        assert sum(
            _evaluate(value["channel_rows"][index][component], (2, 3, 5))
            for index in range(7, 10)
        ) == 0
    assert value["exact_fixture_replay"]["combined"] == {
        "numerator": 15707,
        "denominator": 216,
    }
    flags = value["claim_flags"]
    assert flags["FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"] is True
    assert flags["GENERIC_PHYSICAL_M14_DISPOSED"] is True
    assert flags["FINITE_LOCAL_MIXED_ROWS_FIXED"] is False
    assert flags["QME_OR_ANOMALY_STATUS_CHANGED"] is False
    print("independent generic physical full boundary incidence: PASS")


if __name__ == "__main__":
    verify()
