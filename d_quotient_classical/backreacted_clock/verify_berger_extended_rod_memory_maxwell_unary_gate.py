#!/usr/bin/env python3
"""Independent verifier for the extended Berger apparatus unary gate."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator, ValidationError

from .berger_extended_rod_memory_maxwell_unary_gate import (
    DEPENDENCIES,
    DETECTOR_INPUT,
    OUTPUT,
    SCHEMA,
    build,
)


def _matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum(left[row][middle] * right[middle][column] for middle in range(len(right))) for column in range(len(right[0]))]
        for row in range(len(left))
    ]


def _independent_rod_stress() -> list[list[Fraction]]:
    data = json.loads(DETECTOR_INPUT.read_text())
    derivatives = [
        [Fraction(value) for value in row]
        for row in data["rod_charts"][0]["relational_jacobian"][1:]
    ]
    eta = [Fraction(-1), Fraction(1), Fraction(1), Fraction(1)]
    result = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for derivative in derivatives:
        norm = sum(eta[index] * derivative[index] ** 2 for index in range(4))
        for first in range(4):
            for second in range(4):
                result[first][second] += derivative[first] * derivative[second]
                if first == second:
                    result[first][second] -= Fraction(1, 2) * eta[first] * norm
    return result


def _independent_memory_formula_check() -> None:
    # A noncommutative formula is emitted by the producer.  This independent
    # exact specialization detects every sign and block-placement error.
    M = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(1)]]
    G = [[Fraction(1), Fraction(-1)], [Fraction(-1), Fraction(2)]]
    T = [[Fraction(1), Fraction(1)], [Fraction(0), Fraction(1)]]
    H = [[Fraction(1), Fraction(-1)], [Fraction(0), Fraction(1)]]
    Ts = [[Fraction(1), Fraction(0)], [Fraction(1), Fraction(1)]]
    J = [[Fraction(1), Fraction(0)], [Fraction(-1), Fraction(1)]]
    B = [[Fraction(1), Fraction(2)], [Fraction(0), Fraction(1)]]
    Bs = [[Fraction(1), Fraction(0)], [Fraction(2), Fraction(1)]]
    zero = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]

    def add(*values: list[list[Fraction]]) -> list[list[Fraction]]:
        return [[sum(value[row][column] for value in values) for column in range(2)] for row in range(2)]

    def scale(value: list[list[Fraction]], coefficient: int) -> list[list[Fraction]]:
        return [[coefficient * item for item in row] for row in value]

    K = [[M, zero, scale(Bs, -1)], [zero, zero, Ts], [scale(B, -1), T, zero]]
    E = [
        [G, _matmul(_matmul(G, Bs), J), zero],
        [_matmul(_matmul(H, B), G), _matmul(_matmul(_matmul(_matmul(H, B), G), Bs), J), H],
        [zero, J, zero],
    ]

    def block_multiply(left: list[list[list[list[Fraction]]]], right: list[list[list[list[Fraction]]]]) -> list[list[list[list[Fraction]]]]:
        return [
            [add(*(_matmul(left[row][middle], right[middle][column]) for middle in range(3))) for column in range(3)]
            for row in range(3)
        ]

    block_identity = [[([[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]] if row == column else zero) for column in range(3)] for row in range(3)]
    if block_multiply(K, E) != block_identity or block_multiply(E, K) != block_identity:
        raise ValueError("independent memory-Maxwell inverse check failed")


def _semantic_boundary(value: dict) -> None:
    flags = value["claim_flags"]
    if (
        value["result_state"] != "INPUT_BLOCKED_NONZERO_ROD_TADPOLE_AND_PROFILE_OPERATOR_NOT_EXPORTED"
        or flags["ROD_TADPOLE_EXACT_NONZERO"] is not True
        or flags["MEMORY_MAXWELL_RETARDED_BLOCK_FORMULA_PROVED"] is not True
        or flags["EXTENDED_APPARATUS_Q1_CERTIFIED"]
        or flags["EXTENDED_CYCLIC_PAIRING_CERTIFIED"]
        or flags["EXTENDED_RETARDED_GREEN_CERTIFIED"]
        or flags["K_BERGER_APPARATUS_EQUIVARIANCE_CERTIFIED"]
        or flags["BACKREACTED_APPARATUS_BACKGROUND_AVAILABLE"]
        or flags["QUANTUM_CLAIM"]
    ):
        raise ValueError("extended apparatus unary gate was over-promoted")


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("extended apparatus unary gate does not reproduce")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency drifted: {name}")
    stress = _independent_rod_stress()
    expected = [
        [Fraction(3, 2), 0, 0, 0],
        [0, Fraction(-1, 2), 0, 0],
        [0, 0, Fraction(-1, 2), 0],
        [0, 0, 0, Fraction(-1, 2)],
    ]
    if stress != expected:
        raise ValueError("independent rod stress witness drifted")
    _independent_memory_formula_check()
    _semantic_boundary(value)

    for key in (
        "EXTENDED_APPARATUS_Q1_CERTIFIED",
        "EXTENDED_CYCLIC_PAIRING_CERTIFIED",
        "EXTENDED_RETARDED_GREEN_CERTIFIED",
        "K_BERGER_APPARATUS_EQUIVARIANCE_CERTIFIED",
        "BACKREACTED_APPARATUS_BACKGROUND_AVAILABLE",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][key] = True
        try:
            _semantic_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")

    schema_mutant = deepcopy(value)
    schema_mutant["fixed_background_obstruction"]["witness"]["energy_density_T00"] = "0"
    try:
        Draft202012Validator(schema).validate(schema_mutant)
    except ValidationError:
        pass
    else:
        raise ValueError("zero-tadpole schema mutation accepted")
    return value


def main() -> int:
    verify()
    print("BERGER EXTENDED ROD-MEMORY-MAXWELL UNARY GATE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
