#!/usr/bin/env python3
"""Independent consumer replay of the generic H1-H2 contact projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_physical_hessian_h1_h2_contact_residue_projection import (
    UNSEEN_MOMENTUM_FIXTURES,
    _fixture_coordinates,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json"
FIXTURES = HERE / "fixtures/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_COORDINATES.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-h1-h2-contact-residue-projection-v1.schema.json"
FIXTURE_SCHEMA = HERE / "schema/generic-background-physical-hessian-h1-h2-contact-residue-fixture-ledger-v1.schema.json"


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _evaluate(row: dict[str, object], boxes: list[int]) -> sp.Rational:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(
            sp.Integer(boxes[index]) ** exponent
            for index, exponent in enumerate(term["box_exponents"])
        )
        for term in row["single_endpoint_terms"]
    )
    denominator = sp.prod(
        sp.Integer(boxes[index]) ** exponent
        for index, exponent in enumerate(row["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def _verify_reference(reference: dict[str, str]) -> None:
    path = ROOT / reference["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
        raise ValueError(f"dependency hash drifted: {path}")
    if json.loads(path.read_text())["result_id"] != reference["result_id"]:
        raise ValueError(f"dependency result id drifted: {path}")


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    fixture = json.loads(FIXTURES.read_text())
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
        raise ValueError("fixture entry digest drifted")
    if value["interpolation"]["formula_digest"] != _digest(
        value["projection_rows"]
    ):
        raise ValueError("projection formula digest drifted")

    # Replay a genuinely unseen point from the tensor vertices rather than
    # trusting the frozen coordinate ledger or interpolation code.
    replay = _fixture_coordinates(UNSEEN_MOMENTUM_FIXTURES[0])
    stored = fixture["entries"][fixture["training_fixture_count"]]
    if replay != stored:
        raise ValueError("independent unseen tensor replay drifted")
    for row_index, row in enumerate(value["projection_rows"]):
        contact_index, channel_index = divmod(row_index, 11)
        expected = _from_q(
            replay["contacts"][contact_index]["single_endpoint_coordinates"]
            [channel_index]
        )
        if _evaluate(row, replay["boxes"]) != expected:
            raise ValueError(f"independent row replay failed at {row_index}")

    for contact_index in range(3):
        block = value["projection_rows"][11 * contact_index : 11 * (contact_index + 1)]
        exponents = {
            tuple(term["box_exponents"])
            for row in block[7:10]
            for term in row["single_endpoint_terms"]
        }
        for exponent in exponents:
            coefficient = sum(
                _from_q(term["coefficient"])
                for row in block[7:10]
                for term in row["single_endpoint_terms"]
                if tuple(term["box_exponents"]) == exponent
            )
            if coefficient != 0:
                raise ValueError("independent symmetric I28 relation failed")

    if value["equal_box_regression"]["combined_all_contacts"] != {
        "numerator": 2704,
        "denominator": 27,
    }:
        raise ValueError("equal-box regression drifted")
    flags = value["claim_flags"]
    for required in (
        "GENERIC_H1_H2_CONTACT_ENDPOINT_KERNELS_EVALUATED",
        "ALL_THREE_CONTACT_CELLS_PROJECTED",
        "LEFT_RIGHT_ENDPOINT_EQUALITY_CERTIFIED",
        "GENERIC_CONTACT_SCALE_LOG_KERNELS_COMPUTED",
        "SYMMETRIC_I28_QUOTIENT_SECTION_PRESERVED",
    ):
        if not flags[required]:
            raise ValueError(f"required claim absent: {required}")
    for forbidden in (
        "GENERIC_CONTACT_FINITE_LOCAL_ROWS_FIXED",
        "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED",
        "PHYSICAL_M14_CORNER_CLASS_DISPOSED",
        "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE",
        "QME_OR_ANOMALY_STATUS_CHANGED",
        "LORENTZIAN_CERTIFIED",
    ):
        if flags[forbidden]:
            raise ValueError(f"claim boundary crossed: {forbidden}")

    print("independent physical H1-H2 contact residue projection: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
