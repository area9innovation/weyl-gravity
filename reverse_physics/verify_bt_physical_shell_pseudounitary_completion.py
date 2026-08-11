#!/usr/bin/env python3
"""Independent verifier for the BT physical-shell pseudo-unitarity theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-physical-shell-pseudounitary-completion-v1.schema.json",
)


@dataclass(frozen=True)
class Q3:
    p: Fraction = Fraction(0)
    q: Fraction = Fraction(0)

    def __add__(self, other):
        other = cast(other)
        return Q3(self.p + other.p, self.q + other.q)

    __radd__ = __add__

    def __neg__(self):
        return Q3(-self.p, -self.q)

    def __sub__(self, other):
        return self + (-cast(other))

    def __mul__(self, other):
        other = cast(other)
        return Q3(
            self.p * other.p + 3 * self.q * other.q,
            self.p * other.q + self.q * other.p,
        )

    __rmul__ = __mul__


def cast(value):
    return value if isinstance(value, Q3) else Q3(Fraction(value))


ZERO = Q3()


def load(path):
    with open(path) as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def q3(value):
    return Q3(fraction(value["rational"]), fraction(value["sqrt3"]))


def zeros():
    return [[ZERO for _ in range(4)] for _ in range(4)]


def matrix(entries):
    result = zeros()
    occupied = set()
    for entry in entries:
        position = (entry["row"], entry["column"])
        if position in occupied:
            raise ValueError("duplicate sparse entry")
        occupied.add(position)
        result[position[0]][position[1]] = q3(entry["value"])
    return result


def add(*matrices):
    return [
        [sum((item[i][j] for item in matrices), ZERO) for j in range(4)]
        for i in range(4)
    ]


def scale(coefficient, value):
    return [[cast(coefficient) * entry for entry in row] for row in value]


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(4)), ZERO)
            for j in range(4)
        ]
        for i in range(4)
    ]


def transpose(value):
    return [list(row) for row in zip(*value)]


def all_zero(value):
    return all(entry == ZERO for row in value for entry in row)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    witness = certificate.get("exact_witness", {})
    try:
        first = matrix(witness.get("A", []))
        second = matrix(witness.get("B_equals_A2_over_2", []))
        amplitude = q3(witness.get("per_pair_amplitude", {}))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        first = second = zeros()
        amplitude = ZERO

    first_square = multiply(first, first)
    first_adjoint_first = multiply(transpose(first), first)
    real_source = load(
        os.path.join(
            ROOT,
            "reverse_physics/certificates/"
            "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
        )
    )
    object_source = load(
        os.path.join(
            ROOT,
            "reverse_physics/certificates/"
            "REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
        )
    )
    source_physical = object_source.get("object_types", {}).get("physical_process", {})
    ledger = certificate.get("response_ledger", {})
    disposition = certificate.get("disposition", {})
    hard_amplitude = -first_adjoint_first[0][0] * Fraction(1, 2)
    hard_probability = 2 * hard_amplitude
    real_norm = sum(
        (first[channel][0] * first[channel][0] for channel in range(1, 4)),
        ZERO,
    )
    checks = {
        "schema": not errors,
        "source_real_coefficient": (
            real_source.get("phase_and_combinatorics", {}).get("common_three_pair_shift")
            == "+3*lambda^6*log(c)/(512*pi^4*s)"
            and fraction(source_physical.get("real_pair_Born_normalized", {}))
            == Fraction(1, 48)
        ),
        "physical_object_typing": (
            certificate.get("assumptions", {}).get("physical_operator")
            == "S_phys(x), not R_t P R_t^dagger"
        ),
        "exact_real_column": (
            amplitude * amplitude == Q3(Fraction(1, 48))
            and real_norm == Q3(Fraction(1, 16))
        ),
        "order_one_pseudounitarity": all_zero(add(transpose(first), first)),
        "order_two_pseudounitarity": all_zero(
            add(transpose(second), second, first_adjoint_first)
        ),
        "exponential_witness": second == scale(Fraction(1, 2), first_square),
        "independent_hard_diagonal": (
            hard_amplitude == Q3(Fraction(-1, 32))
            and hard_probability == Q3(Fraction(-1, 16))
        ),
        "response_conversion": (
            fraction(ledger.get("forced_hard_amplitude_real_part", {}))
            == Fraction(-1, 32)
            and fraction(ledger.get("forced_hard_survival_Born_normalized", {}))
            == Fraction(-1, 16)
            and fraction(ledger.get("forced_hard_absolute", {}))
            == Fraction(3, 32) * Fraction(-1, 16)
            == Fraction(-3, 512)
            and fraction(ledger.get("inclusive_log_response", {})) == 0
        ),
        "conditional_boundary": (
            disposition.get("hard_response_under_physical_shell_pseudounitarity")
            == "FORCED_MINUS_3_OVER_512"
            and disposition.get("continuum_dressed_physical_S_matrix")
            == "NOT_CONSTRUCTED"
            and disposition.get("physical_inclusive_NLO_log_cancellation")
            == "CONDITIONAL_ON_DRESSED_S_EXISTENCE"
            and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
        ),
        "hashes": (
            len(certificate.get("provenance", {}).get("inputs", [])) == 5
            and all(
                row["sha256"] == sha256(row["path"])
                for row in certificate.get("provenance", {}).get("inputs", [])
            )
        ),
        "producer_ledger": (
            certificate.get("checks", {}).get("passed")
            == certificate.get("checks", {}).get("total")
            == 16
            and certificate.get("checks", {}).get("failures") == []
            and all(certificate.get("checks", {}).get("details", {}).values())
        ),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT PHYSICAL SHELL PSEUDOUNITARY VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(
        "BT PHYSICAL SHELL PSEUDOUNITARY VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
