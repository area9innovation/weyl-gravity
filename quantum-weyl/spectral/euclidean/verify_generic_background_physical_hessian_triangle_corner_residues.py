#!/usr/bin/env python3
"""Independent consumer for the generic physical triangle corner residues."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES.json"
OBSTRUCTION = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json"


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _evaluate(row: dict[str, Any], boxes: tuple[int, int, int]) -> sp.Rational:
    numerator = sum(
        _q(term["coefficient"])
        * sp.prod(value**power for value, power in zip(boxes, term["box_exponents"]))
        for term in row["numerator_terms"]
    )
    denominator = sp.prod(
        value**power
        for value, power in zip(boxes, row["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    assert value["result_state"] == "GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED"
    assert len(value["channel_rows"]) == 11
    expected = {
        row["channel_id"]: _q(row["log_corner_coefficient"])
        for row in obstruction["channel_rows"]
    }
    for row in value["channel_rows"]:
        assert len(row["corner_rows"]) == 3
        symmetric = sum(_evaluate(corner, (1, 1, 1)) for corner in row["corner_rows"])
        assert symmetric == expected[row["channel_id"]]
        assert _evaluate(row["one_order_total"], (1, 1, 1)) == symmetric
        assert _evaluate(row["six_ordering_total"], (1, 1, 1)) == 6 * symmetric
    for corner in range(3):
        assert sum(
            _evaluate(value["channel_rows"][index]["corner_rows"][corner], (2, 3, 5))
            for index in range(7, 10)
        ) == 0
    flags = value["claim_flags"]
    assert flags["GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED"] is True
    assert flags["FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"] is False
    assert flags["GENERIC_PHYSICAL_M14_DISPOSED"] is False
    print("independent generic physical triangle corner residues: PASS")


if __name__ == "__main__":
    verify()
