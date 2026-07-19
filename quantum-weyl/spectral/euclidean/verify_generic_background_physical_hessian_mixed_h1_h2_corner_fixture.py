#!/usr/bin/env python3
"""Independent arithmetic and provenance replay of the mixed H1-H2 fixture."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-mixed-h1-h2-corner-fixture-v1.schema.json"


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)

    fixture = stored["equal_box_fixture"]
    momenta = [
        tuple(_fraction(component) for component in momentum)
        for momentum in fixture["momenta"]
    ]
    if momenta != [
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(-1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)),
        (Fraction(-1, 2), Fraction(-1, 2), Fraction(-1, 2), Fraction(-1, 2)),
    ]:
        raise ValueError("mixed H1-H2 momenta drifted")
    if any(sum(momentum[index] ** 2 for index in range(4)) != 1 for momentum in momenta):
        raise ValueError("mixed H1-H2 equal-box identity failed")
    if any(sum(momentum[index] for momentum in momenta) != 0 for index in range(4)):
        raise ValueError("mixed H1-H2 momentum conservation failed")

    h1 = stored["three_H1_corner"]
    orientation_a = [_fraction(value) for value in h1["orientation_A_corner_weights"]]
    orientation_b = [_fraction(value) for value in h1["orientation_B_corner_weights"]]
    if orientation_a != [Fraction(-161, 72), Fraction(-137, 108), Fraction(-461, 432)]:
        raise ValueError("first H1 cyclic orientation drifted")
    if orientation_b != [Fraction(-461, 432), Fraction(-137, 108), Fraction(-161, 72)]:
        raise ValueError("second H1 cyclic orientation drifted")
    full_h1 = 3 * (sum(orientation_a) + sum(orientation_b))
    if full_h1 != Fraction(-1975, 72):
        raise ValueError("full six-ordering H1 corner coefficient failed")

    bubbles = stored["operational_H2"]["bubble_rows"]
    expected_endpoint = [Fraction(1127, 54), Fraction(115, 9), Fraction(887, 54)]
    for index, (row, expected) in enumerate(zip(bubbles, expected_endpoint)):
        if row["singled_H1_leg"] != index:
            raise ValueError("mixed bubble leg ordering drifted")
        if (
            _fraction(row["left_endpoint_log_coefficient"]) != expected
            or _fraction(row["right_endpoint_log_coefficient"]) != expected
            or row["H2_covariant_rank"] != 9
            or row["H2_representation_rank"] != 9
        ):
            raise ValueError("mixed H1-H2 endpoint replay failed")
    full_h2 = 2 * sum(expected_endpoint)
    combined = full_h1 + full_h2
    if full_h2 != Fraction(2704, 27) or combined != Fraction(15707, 216):
        raise ValueError("combined raw logarithmic coefficient failed")
    result = stored["combined_raw_logarithm"]
    if (
        _fraction(result["three_H1_corner_coefficient"]) != full_h1
        or _fraction(result["mixed_H1_H2_endpoint_coefficient"]) != full_h2
        or _fraction(result["sum"]) != combined
    ):
        raise ValueError("stored mixed H1-H2 total does not replay")

    flags = stored["claim_flags"]
    if (
        flags["RAW_ALGEBRAIC_H2_CANCELLATION_IDENTITY_REFUTED_BY_FIXTURE"]
        is not True
        or flags["RENORMALIZED_SUBTRACTION_FIXED"] is not False
        or flags["PHYSICAL_M14_CORNER_CLASS_DISPOSED"] is not False
        or flags["QME_OR_ANOMALY_STATUS_CHANGED"] is not False
    ):
        raise ValueError("mixed H1-H2 claim boundary drifted")

    for reference in stored["dependencies"].values():
        path = ROOT / reference["path"]
        if not path.is_file() or _sha256(path) != reference["sha256"]:
            raise ValueError(f"mixed H1-H2 dependency drifted: {reference['path']}")
    return stored


def main() -> int:
    verify()
    print("independent physical mixed H1-H2 corner replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
