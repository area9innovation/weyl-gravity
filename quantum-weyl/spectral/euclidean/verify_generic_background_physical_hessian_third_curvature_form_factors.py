#!/usr/bin/env python3
"""Independent consumer for the physical third-curvature form factors."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json"
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _polynomial(terms: list[dict[str, Any]], exponent_key: str) -> sp.Expr:
    return sum(
        _q(term["coefficient"])
        * sp.prod(variable**power for variable, power in zip(XS, term[exponent_key]))
        for term in terms
    )


def _rational_function(value: dict[str, Any]) -> sp.Expr:
    return sp.cancel(
        _polynomial(value["numerator_terms"], "exponents")
        / _polynomial(value["denominator_terms"], "exponents")
    )


def _row_function(
    row: dict[str, Any], terms_key: str, denominator_key: str
) -> sp.Expr:
    denominator = sp.prod(
        variable**power for variable, power in zip(XS, row[denominator_key])
    )
    return sp.cancel(_polynomial(row[terms_key], "box_exponents") / denominator)


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _evaluate(expression: sp.Expr, point: list[int]) -> sp.Rational:
    return sp.Rational(expression.subs(dict(zip(XS, point))))


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    dependencies = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
        dependency = json.loads(path.read_text())
        assert dependency["result_id"] == reference["result_id"]
        dependencies[name] = dependency

    payload = {
        key: value[key] for key in ("function_basis", "carrier_functions", "quotient_ledger")
    }
    assert _digest(payload) == value["formula_digest"]
    triangle = {
        row["channel_id"]: row
        for row in dependencies["integrated_physical_triangle"]["channel_rows"]
    }
    incidence = {
        row["channel_id"]: row
        for row in dependencies["combined_boundary_incidence"]["channel_rows"]
    }
    contacts: dict[str, list[dict[str, Any]]] = {}
    for row in dependencies["finite_H1_H2_contacts"]["projection_rows"]:
        channel_id = f"{row['carrier_id']}_{''.join(str(label) for label in row['label_order'])}"
        contacts.setdefault(channel_id, []).append(row)

    channels = [
        channel
        for carrier in value["carrier_functions"]
        for channel in carrier["orientation_channels"]
    ]
    assert len(value["carrier_functions"]) == 5
    assert len(channels) == 11
    for channel in channels:
        channel_id = channel["channel_id"]
        assert len(contacts[channel_id]) == 3
        contact_sum = sp.cancel(
            sum(
                (
                    _row_function(
                        row,
                        "minimal_subtraction_finite_terms",
                        "box_denominator_exponents",
                    )
                    for row in contacts[channel_id]
                ),
                sp.S.Zero,
            )
        )
        assert sp.cancel(contact_sum - _rational_function(channel["finite_contact_sum"])) == 0
        triangle_rational = _rational_function(
            triangle[channel_id]["integrated_function_basis"]["rational_corner"]
        )
        assembled = _rational_function(channel["assembled_rational_coordinate"])
        assert sp.cancel(assembled - triangle_rational - contact_sum) == 0
        scale = _row_function(
            incidence[channel_id]["combined_scale_row"],
            "numerator_terms",
            "box_denominator_exponents",
        )
        for holdout in channel["exact_holdouts"]:
            point = holdout["box_point"]
            assert _evaluate(contact_sum, point) == _q(holdout["finite_contact_sum"])
            assert _evaluate(assembled, point) == _q(
                holdout["assembled_rational_coordinate"]
            )
            assert _evaluate(scale, point) == _q(
                holdout["combined_scale_derivative"]
            )

    i28 = next(
        carrier for carrier in value["carrier_functions"] if carrier["carrier_id"] == "I28"
    )["orientation_channels"]
    for key in ("finite_contact_sum", "assembled_rational_coordinate"):
        assert sp.cancel(sum(_rational_function(row[key]) for row in i28)) == 0
    for basis in value["function_basis"]["triangle_basis"]:
        assert sp.cancel(
            sum(
                _rational_function(
                    triangle[row["channel_id"]]["integrated_function_basis"][basis]
                )
                for row in i28
            )
        ) == 0
    assert value["claim_flags"]["FIVE_PHYSICAL_CARRIER_FUNCTIONS_ASSEMBLED"] is True
    assert value["claim_flags"]["ABSOLUTE_FINITE_C2_NORMALIZATION_FIXED"] is False
    assert value["claim_flags"]["FULL_BV_FORM_FACTORS_COMPUTED"] is False
    assert value["claim_flags"]["LORENTZIAN_CERTIFIED"] is False
    print("independent physical third-curvature form-factor verification: PASS")


if __name__ == "__main__":
    verify()
