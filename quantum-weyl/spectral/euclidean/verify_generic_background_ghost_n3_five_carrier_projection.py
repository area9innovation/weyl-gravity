#!/usr/bin/env python3
"""Independent holdout replay of the ghost n=3 five-carrier projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_five_carrier_projection import (
    DEPENDENCIES,
    OUTPUT,
    ROOT,
    SCHEMA,
    _carrier_system,
    _fixture_momenta,
    _transverse_tracefree_basis,
    _triangle_value,
)


HOLDOUTS = (
    (((1, 2, 0, 1), (0, 1, 3, 0)), sp.Rational(1, 5), sp.Rational(3, 10)),
    (((1, 0, 2, -1), (2, -2, 1, 0)), sp.Rational(2, 7), sp.Rational(1, 5)),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _formula_digest(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rational(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _stored_coordinates(
    rows: list[dict[str, Any]],
    momenta: list[sp.Matrix],
    alpha1: sp.Rational,
    alpha2: sp.Rational,
) -> tuple[list[sp.Expr], sp.Expr]:
    alpha0 = 1 - alpha1 - alpha2
    boxes = [momentum.dot(momentum) for momentum in momenta]
    delta = (
        alpha0 * alpha1 * boxes[0]
        + alpha1 * alpha2 * boxes[1]
        + alpha2 * alpha0 * boxes[2]
    )
    if delta == 0:
        raise ValueError("holdout entered an exceptional momentum configuration")
    coordinates = []
    for row in rows:
        numerator = sp.S.Zero
        for term in row["terms"]:
            numerator += (
                _rational(term["coefficient"])
                * alpha1 ** term["alpha_exponents"][0]
                * alpha2 ** term["alpha_exponents"][1]
                * sp.prod(
                    boxes[index] ** term["box_exponents"][index]
                    for index in range(3)
                )
            )
        coordinates.append(numerator / delta ** row["common_denominator_power"])
    return coordinates, delta


def _verify_holdout(
    value: dict[str, Any],
    fixture: tuple[tuple[int, ...], tuple[int, ...]],
    alpha1: sp.Rational,
    alpha2: sp.Rational,
) -> None:
    momenta = _fixture_momenta(fixture)
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    choices, carrier_matrix, _, _ = _carrier_system(momenta)
    coordinates, delta = _stored_coordinates(
        value["projection_rows"], momenta, alpha1, alpha2
    )
    direct_values = []
    for choice in choices:
        tensors = [bases[index][choice[index]] for index in range(3)]
        direct, direct_delta = _triangle_value(
            momenta, tensors, alpha1, alpha2
        )
        if direct_delta != delta:
            raise ValueError("holdout simplex denominator drifted")
        direct_values.append(direct)
    residual = carrier_matrix * sp.Matrix(coordinates) - sp.Matrix(direct_values)
    if any(component != 0 for component in residual):
        raise ValueError("stored carrier formula failed an unseen exact tensor holdout")
    if sum(coordinates[7:10]) != 0:
        raise ValueError("stored carrier formula left the symmetric I28 gauge section")


def verify(value: dict[str, Any] | None = None) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)

    for name, path in DEPENDENCIES.items():
        dependency = json.loads(path.read_text())
        reference = stored["dependencies"][name]
        if (
            reference["path"] != str(path.relative_to(ROOT))
            or reference["result_id"] != dependency["result_id"]
            or reference["sha256"] != _sha256(path)
        ):
            raise ValueError(f"projection dependency drifted: {name}")

    rows = stored["projection_rows"]
    if _formula_digest(rows) != stored["formula_digest"]:
        raise ValueError("projection formula digest drifted")
    if [row["channel_id"] for row in rows] != stored["quotient_section"][
        "raw_channel_order"
    ]:
        raise ValueError("projection channel order drifted")
    if any(row["term_count"] != len(row["terms"]) for row in rows):
        raise ValueError("projection term count drifted")
    if any(
        sum(term["box_exponents"]) != row["numerator_box_degree"]
        or sum(term["alpha_exponents"]) > 9
        for row in rows
        for term in row["terms"]
    ):
        raise ValueError("projection term grading drifted")

    for fixture, alpha1, alpha2 in HOLDOUTS:
        _verify_holdout(stored, fixture, alpha1, alpha2)

    true_flags = {
        "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED",
        "GENERIC_GHOST_N3_SCALAR_FLAT_QUOTIENT_SECTION_EXACT",
    }
    flags = stored["claim_flags"]
    if any(flags[name] is not True for name in true_flags) or any(
        flag is not False for name, flag in flags.items() if name not in true_flags
    ):
        raise ValueError("projection crossed its claim boundary")
    return stored


def main() -> int:
    verify()
    print("independent generic ghost n=3 five-carrier projection: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
