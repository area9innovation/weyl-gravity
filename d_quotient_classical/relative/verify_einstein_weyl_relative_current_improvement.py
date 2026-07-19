#!/usr/bin/env python3
"""Independent consumer for the relative current-improvement table."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.product_taylor_engine import BASE_POINT, COORDINATES, BilinearOperator
from d_quotient_classical.relative.einstein_weyl_relative_lee_wald_pbw import (
    canonical_green_current,
    relative_lee_wald_current_symbolic,
    symbolic_green_current,
)
from d_quotient_classical.relative.einstein_weyl_relative_noether_current import (
    relative_symplectic_current_component,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GREEN_LEE_WALD_IMPROVEMENT_V1.json"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_current_improvement_v1/improvement.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-green-lee-wald-improvement-v1.schema.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(operator: BilinearOperator) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (left, left_word, right, right_word, value)
        for left, left_word, right, right_word, coefficient in operator.terms
        if (value := sp.trigsimp(sp.cancel(coefficient))) != 0
    )


def _read_potential(payload: dict) -> dict[tuple[int, int], BilinearOperator]:
    theta = COORDINATES[2]
    grouped: dict[tuple[int, int], list[tuple]] = {}
    for term in payload["terms"]:
        pair = tuple(term["spacetime_pair"])
        coefficient = sum(
            sp.Rational(item["coefficient"])
            * sp.cos(theta) ** item["cosine_power"]
            * sp.sin(theta) ** item["sine_power"]
            for item in term["coefficient_basis"]
        )
        grouped.setdefault(pair, []).append(
            (
                term["left"]["field"],
                tuple(term["left"]["word"]),
                term["right"]["field"],
                tuple(term["right"]["word"]),
                coefficient,
            )
        )
    return {pair: BilinearOperator.from_terms(terms) for pair, terms in grouped.items()}


def _divergence(potential: dict[tuple[int, int], BilinearOperator]) -> tuple[BilinearOperator, ...]:
    output = [BilinearOperator() for _ in range(4)]
    for (left, right), value in potential.items():
        output[left] = output[left] + value.derivative(right)
        output[right] = output[right] - value.derivative(left)
    return tuple(_normalize(value) for value in output)


def _coordinate_fixture() -> None:
    theta = COORDINATES[2]
    metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    field = sp.zeros(4)
    field[2, 3] = sp.sin(theta)
    field[3, 2] = -sp.sin(theta)
    first_metric = sp.zeros(4)
    first_metric[0, 0] = 1
    second_metric = sp.zeros(4)
    second_metric[0, 2] = second_metric[2, 0] = theta - sp.pi / 2
    zero_potential = sp.zeros(4, 1)
    coordinate = relative_symplectic_current_component(
        metric,
        field,
        (first_metric, zero_potential),
        (second_metric, zero_potential),
        COORDINATES,
        0,
    )
    if sp.limit(coordinate, theta, sp.pi / 2) != -sp.Rational(3, 8):
        raise AssertionError("coordinate Lee-Wald fixture drifted")
    sparse = relative_lee_wald_current_symbolic()[0].at_base_point()
    coefficient = next(
        value
        for left, left_word, right, right_word, value in sparse.terms
        if (left, left_word, right, right_word) == (0, (), 2, (2,))
    )
    if coefficient != -sp.Rational(3, 8):
        raise AssertionError("sparse Lee-Wald fixture disagrees with coordinate evaluator")


def verify() -> dict[str, int]:
    certificate = _load(CERTIFICATE)
    payload = _load(GENERATED)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for dependency in certificate["dependencies"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency hash drifted: {dependency['path']}")
    for relative, expected in certificate["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source manifest drifted: {relative}")
    if payload["term_count"] != len(payload["terms"]):
        raise AssertionError("generated improvement term count drifted")

    symbolic_green = tuple(value.at_base_point() for value in symbolic_green_current())
    if any((left - right).terms for left, right in zip(symbolic_green, canonical_green_current())):
        raise AssertionError("symbolic Green current disagrees with serialized Hessian current")
    difference = tuple(
        _normalize(left - right)
        for left, right in zip(relative_lee_wald_current_symbolic(), symbolic_green_current())
    )
    potential = _read_potential(payload)
    reconstructed = _divergence(potential)
    defects = tuple(
        _normalize(left - right)
        for left, right in zip(difference, reconstructed)
    )
    if any(value.terms for value in defects):
        first = next(value.terms[0] for value in defects if value.terms)
        raise AssertionError(f"horizontal improvement defect: {first}")
    for pair, value in potential.items():
        swapped = value.koszul_swapped((0,) * 10)
        if _normalize(value + swapped).terms:
            raise AssertionError(f"field-slot antisymmetry drifted in U^{pair}")
    _coordinate_fixture()
    return {
        "improvement_terms": payload["term_count"],
        "horizontal_defects": 0,
        "coordinate_fixture_defects": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
