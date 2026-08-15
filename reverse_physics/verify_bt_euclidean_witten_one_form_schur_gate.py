#!/usr/bin/env python3
"""Independent verifier for the BT Witten one-form Schur gate."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_"
    "SCHUR_GATE_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-witten-one-form-"
    "schur-gate-v1.schema.json"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_"
        "LOWEST_MODE_CURVATURE_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_"
        "BLOCK_OBSTRUCTION_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_"
        "SCORE_REDUCTION_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_ACTION_FLAT_"
        "CONVEXITY_OBSTRUCTION_V1.json"
    ),
]

DensePolynomial = list[list[Fraction]]


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dense(size: int = 9) -> DensePolynomial:
    return [[Fraction(0) for _ in range(size)] for _ in range(size)]


def make(terms: list[tuple[Fraction | int, int, int]]) -> DensePolynomial:
    result = dense()
    for coefficient, x_power, y_power in terms:
        result[x_power][y_power] += Fraction(coefficient)
    return result


def plus(*items: DensePolynomial) -> DensePolynomial:
    result = dense()
    for item in items:
        for x_power in range(len(item)):
            for y_power in range(len(item[x_power])):
                result[x_power][y_power] += item[x_power][y_power]
    return result


def times(left: DensePolynomial, right: DensePolynomial) -> DensePolynomial:
    result = dense()
    for lx, left_row in enumerate(left):
        for ly, left_value in enumerate(left_row):
            if not left_value:
                continue
            for rx, right_row in enumerate(right):
                for ry, right_value in enumerate(right_row):
                    if right_value and lx + rx < 9 and ly + ry < 9:
                        result[lx + rx][ly + ry] += left_value * right_value
    return result


def diff(item: DensePolynomial, variable: int) -> DensePolynomial:
    result = dense()
    for x_power, row in enumerate(item):
        for y_power, value in enumerate(row):
            powers = [x_power, y_power]
            if powers[variable]:
                factor = powers[variable]
                powers[variable] -= 1
                result[powers[0]][powers[1]] += factor * value
    return result


def negative(item: DensePolynomial) -> DensePolynomial:
    return [[-value for value in row] for row in item]


def scalar_operator(
    potential: DensePolynomial, function: DensePolynomial
) -> DensePolynomial:
    result = negative(plus(diff(diff(function, 0), 0), diff(diff(function, 1), 1)))
    for variable in range(2):
        result = plus(
            result,
            times(diff(potential, variable), diff(function, variable)),
        )
    return result


def one_form_operator(
    potential: DensePolynomial, vector: list[DensePolynomial]
) -> list[DensePolynomial]:
    result = [scalar_operator(potential, component) for component in vector]
    for row in range(2):
        for column in range(2):
            result[row] = plus(
                result[row],
                times(
                    diff(diff(potential, row), column),
                    vector[column],
                ),
            )
    return result


def evaluate(item: DensePolynomial, x: Fraction, y: Fraction) -> Fraction:
    return sum(
        (
            value * x**x_power * y**y_power
            for x_power, row in enumerate(item)
            for y_power, value in enumerate(row)
        ),
        Fraction(0),
    )


def decode_polynomial(items: list[dict]) -> DensePolynomial:
    result = dense()
    for item in items:
        x_power, y_power = item["powers"]
        result[x_power][y_power] = dec(item["coefficient"])
    return result


def reconstruct() -> dict:
    potential = make(
        [
            (Fraction(1, 4), 4, 0),
            (Fraction(-1, 2), 2, 0),
            (Fraction(1, 2), 0, 2),
            (Fraction(1, 3), 1, 1),
        ]
    )
    scalar = make(
        [
            (1, 3, 1),
            (2, 1, 2),
            (Fraction(1, 5), 0, 3),
            (-1, 1, 0),
        ]
    )
    gradient = [diff(scalar, 0), diff(scalar, 1)]
    left = one_form_operator(potential, gradient)
    scalar_image = scalar_operator(potential, scalar)
    right = [diff(scalar_image, 0), diff(scalar_image, 1)]
    hessian = [
        [evaluate(diff(diff(potential, row), column), Fraction(0), Fraction(0))
         for column in range(2)]
        for row in range(2)
    ]
    determinant = hessian[0][0] * hessian[1][1] - hessian[0][1] * hessian[1][0]
    return {
        "potential": potential,
        "scalar": scalar,
        "gradient": gradient,
        "left": left,
        "right": right,
        "hessian": hessian,
        "determinant": determinant,
    }


def verify(certificate: dict | None = None) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if certificate is None:
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            certificate = json.load(handle)
    with open(os.path.join(ROOT, SCHEMA_REL), encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
    except jsonschema.ValidationError as error:
        failures.append(f"schema: {error.message}")
        return False, failures

    exact = reconstruct()
    fixture = certificate["exact_symbolic_fixture"]
    disposition = certificate["method_disposition"]
    imported = certificate["imported_boundary"]

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    declared_potential = decode_polynomial(fixture["potential"])
    declared_scalar = decode_polynomial(fixture["scalar"])
    declared_gradient = [decode_polynomial(item) for item in fixture["gradient"]]
    declared_left = [decode_polynomial(item) for item in fixture["L1_gradient"]]
    declared_right = [decode_polynomial(item) for item in fixture["gradient_L0"]]
    sample_points = [Fraction(value) for value in range(-2, 4)]
    for x in sample_points:
        for y in sample_points:
            require(
                evaluate(declared_potential, x, y)
                == evaluate(exact["potential"], x, y),
                "fixture potential drift",
            )
            require(
                evaluate(declared_scalar, x, y)
                == evaluate(exact["scalar"], x, y),
                "fixture scalar drift",
            )
            for component in range(2):
                require(
                    evaluate(declared_gradient[component], x, y)
                    == evaluate(exact["gradient"][component], x, y),
                    "fixture gradient drift",
                )
                require(
                    evaluate(declared_left[component], x, y)
                    == evaluate(exact["left"][component], x, y),
                    "declared L1 gradient drift",
                )
                require(
                    evaluate(declared_right[component], x, y)
                    == evaluate(exact["right"][component], x, y),
                    "declared gradient L0 drift",
                )
                require(
                    evaluate(exact["left"][component], x, y)
                    == evaluate(exact["right"][component], x, y),
                    "one-form commutator failed",
                )
    require(
        [[dec(value) for value in row] for row in fixture["hessian_at_origin"]]
        == exact["hessian"],
        "origin Hessian drift",
    )
    require(
        dec(fixture["hessian_determinant_at_origin"])
        == exact["determinant"]
        == Fraction(-10, 9),
        "nonconvex fixture determinant drift",
    )
    require(
        certificate["finite_volume_witten_theorem"]["status"]
        == "PROVED_FINITE_VOLUME_IDENTITY",
        "Witten identity status weakened",
    )
    require(
        certificate["lowest_mode_operator_schur_gate"]["status"]
        == "EXACT_REDUCTION_ESTIMATE_OPEN",
        "operator Schur gate status drift",
    )
    require(
        disposition["pointwise_negative_hessian_as_witten_no_go"]
        == "REFUTED"
        and disposition["volume_uniform_witten_schur_coercivity"] == "OPEN"
        and disposition["controlled_low_rayleigh_sequence"] == "OPEN",
        "Witten method boundary drift",
    )
    require(
        disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN"
        and disposition["continuum_limit"] == "NOT_ESTABLISHED",
        "one-form identity promoted to continuum estimate",
    )
    require(
        disposition["born_rule"] == "NOT_ESTABLISHED"
        and disposition["krein_reconstruction"] == "NOT_ASSESSED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED",
        "reconstruction boundary weakened",
    )
    with open(os.path.join(ROOT, INPUTS[0]), encoding="utf-8") as handle:
        curvature = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[1]), encoding="utf-8") as handle:
        pointwise = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[2]), encoding="utf-8") as handle:
        center = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[3]), encoding="utf-8") as handle:
        flat = json.load(handle)
    require(
        imported["all_background_fiber_curvature_coefficient"]
        == center["exact_center_reduction"]["curvature_coefficient"]
        == {"numerator": 2, "denominator": 9},
        "conditional curvature import drift",
    )
    require(
        curvature["method_disposition"]
        ["all_background_lowest_mode_strong_convexity"]
        == "PROVED",
        "conditional curvature theorem missing",
    )
    require(
        imported["pointwise_orthogonal_hessian_block"]
        == pointwise["method_disposition"]
        ["global_orthogonal_hessian_block_positivity"]
        == "OBSTRUCTED",
        "pointwise Hessian obstruction import drift",
    )
    require(
        imported["low_action_flat_curvature_upper_bound"]
        == flat["exact_longitudinal_fixture"]
        ["full_four_dimensional_curvature_upper_bound"],
        "low-action flat witness import drift",
    )
    for item in certificate["provenance"]["inputs"]:
        require(
            item["path"] in INPUTS and item["sha256"] == sha256(item["path"]),
            f"hash drift: {item['path']}",
        )
    return not failures, failures


def main() -> int:
    ok, failures = verify()
    if not ok:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    print("BT Witten one-form Schur-gate verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
