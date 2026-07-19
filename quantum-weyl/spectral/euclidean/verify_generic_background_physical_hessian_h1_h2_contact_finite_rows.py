#!/usr/bin/env python3
"""Independent consumer replay of the finite physical H1-H2 contact rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_physical_hessian_h1_h2_contact_finite_rows import (
    FIXTURE_OUTPUT,
    OUTPUT,
    SCHEMA,
    FIXTURE_SCHEMA,
    _fixture_coordinates,
)
from .generic_background_physical_hessian_n3_five_carrier_projection import (
    UNSEEN_MOMENTUM_FIXTURES,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _verify_reference(reference: dict[str, str]) -> None:
    path = ROOT / reference["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
        raise ValueError(f"dependency hash drifted: {path}")
    if json.loads(path.read_text())["result_id"] != reference["result_id"]:
        raise ValueError(f"dependency result id drifted: {path}")


def _evaluate(row: dict[str, object], boxes: list[int]) -> sp.Rational:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(
            sp.Integer(boxes[index]) ** exponent
            for index, exponent in enumerate(term["box_exponents"])
        )
        for term in row["minimal_subtraction_finite_terms"]
    )
    denominator = sp.prod(
        sp.Integer(boxes[index]) ** exponent
        for index, exponent in enumerate(row["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def main() -> int:
    value = json.loads(OUTPUT.read_text())
    fixture = json.loads(FIXTURE_OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    fixture_schema = json.loads(FIXTURE_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    Draft202012Validator.check_schema(fixture_schema)
    Draft202012Validator(fixture_schema).validate(fixture)

    _verify_reference(value["fixture_ledger"])
    for reference in value["dependencies"].values():
        _verify_reference(reference)
    if fixture["entry_digest"] != _digest(fixture["entries"]):
        raise ValueError("finite fixture digest drifted")
    if value["interpolation"]["formula_digest"] != _digest(value["projection_rows"]):
        raise ValueError("finite formula digest drifted")

    replay = _fixture_coordinates(UNSEEN_MOMENTUM_FIXTURES[0])
    stored = fixture["entries"][fixture["training_fixture_count"]]
    if replay != stored:
        raise ValueError("independent unseen finite tensor replay drifted")
    for row_index, row in enumerate(value["projection_rows"]):
        contact_index, channel_index = divmod(row_index, 11)
        expected = _from_q(
            replay["contacts"][contact_index][
                "minimal_subtraction_finite_coordinates"
            ][channel_index]
        )
        if _evaluate(row, replay["boxes"]) != expected:
            raise ValueError(f"independent finite row replay failed: {row_index}")

    for contact_index in range(3):
        block = value["projection_rows"][11 * contact_index : 11 * (contact_index + 1)]
        exponents = {
            tuple(term["box_exponents"])
            for row in block[7:10]
            for term in row["minimal_subtraction_finite_terms"]
        }
        for exponent in exponents:
            if sum(
                _from_q(term["coefficient"])
                for row in block[7:10]
                for term in row["minimal_subtraction_finite_terms"]
                if tuple(term["box_exponents"]) == exponent
            ) != 0:
                raise ValueError("independent finite I28 relation failed")

    if value["equal_box_regression"]["combined_contact_finite_value"] != {
        "numerator": 3188,
        "denominator": 27,
    }:
        raise ValueError("equal-box finite contact regression drifted")
    if value["finite_contact_theorem"]["mellin_endpoint_check"] != {
        "numerator": 0,
        "denominator": 1,
    }:
        raise ValueError("Mellin endpoint finite-part check drifted")
    flags = value["claim_flags"]
    for required in (
        "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED",
        "ALL_THREE_CONTACT_FINITE_ROWS_PROJECTED",
        "QUADRATIC_CONTACT_RECONSTRUCTION_VERIFIED",
        "GENERIC_I28_QUOTIENT_RELATION_PRESERVED",
    ):
        if not flags[required]:
            raise ValueError(f"required finite-contact claim absent: {required}")
    for forbidden in (
        "FINITE_COUNTERTERM_NORMALIZATION_FIXED",
        "RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED",
        "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE",
        "QME_OR_ANOMALY_STATUS_CHANGED",
        "LORENTZIAN_CERTIFIED",
    ):
        if flags[forbidden]:
            raise ValueError(f"finite-contact claim boundary crossed: {forbidden}")

    print("independent physical H1-H2 finite contact rows: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
