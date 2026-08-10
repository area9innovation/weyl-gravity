#!/usr/bin/env python3
"""Independent verifier for the BT coherent projector-transport witness.

This rail does not import the producer.  It reads the recorded algebraic
matrices, rederives the formal projector equations, and independently solves
their forced diagonal blocks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-collinear-projector-transport-v1.schema.json",
)


@dataclass(frozen=True)
class Q2:
    p: Fraction = Fraction(0)
    q: Fraction = Fraction(0)

    def __add__(self, other):
        other = cast(other)
        return Q2(self.p + other.p, self.q + other.q)

    __radd__ = __add__

    def __neg__(self):
        return Q2(-self.p, -self.q)

    def __sub__(self, other):
        return self + (-cast(other))

    def __rsub__(self, other):
        return cast(other) - self

    def __mul__(self, other):
        other = cast(other)
        return Q2(
            self.p * other.p + 2 * self.q * other.q,
            self.p * other.q + self.q * other.p,
        )

    __rmul__ = __mul__

    def __eq__(self, other):
        other = cast(other)
        return self.p == other.p and self.q == other.q


def cast(value):
    return value if isinstance(value, Q2) else Q2(Fraction(value))


ZERO = Q2()
ONE = Q2(Fraction(1))


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def q2(payload):
    return Q2(fraction(payload["rational"]), fraction(payload["sqrt2"]))


def matrix(payload):
    out = zeros()
    occupied = set()
    for entry in payload:
        location = (entry["row"], entry["column"])
        if location in occupied:
            raise ValueError("duplicate sparse matrix entry")
        occupied.add(location)
        out[location[0]][location[1]] = q2(entry["value"])
    return out


def zeros(size=4):
    return [[ZERO for _ in range(size)] for _ in range(size)]


def add(*matrices):
    return [
        [sum((item[i][j] for item in matrices), ZERO)
         for j in range(len(matrices[0]))]
        for i in range(len(matrices[0]))
    ]


def scale(coefficient, value):
    coefficient = cast(coefficient)
    return [[coefficient * entry for entry in row] for row in value]


def multiply(left, right):
    size = len(left)
    return [
        [sum((left[i][k] * right[k][j] for k in range(size)), ZERO)
         for j in range(size)]
        for i in range(size)
    ]


def transpose(value):
    return [list(row) for row in zip(*value)]


def matrix_trace(value):
    return sum((value[i][i] for i in range(len(value))), ZERO)


def all_zero(value):
    return all(entry == ZERO for row in value for entry in row)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(path):
    with open(path, encoding="utf-8") as handle:
        cert = json.load(handle)
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)

    errors = sorted(
        Draft202012Validator(schema).iter_errors(cert),
        key=lambda error: list(error.path),
    )
    checks = {"strict_schema": not errors}
    for error in errors[:8]:
        print(f"SCHEMA: {'/'.join(map(str, error.path))}: {error.message}")

    try:
        transport = cert["projector_transport"]
        k = matrix(transport["generator_K"])
        p0 = matrix(transport["P0"])
        p1 = matrix(transport["P1"])
        p2 = matrix(transport["P2"])
        amplitude = q2(transport["mixing_amplitude"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        k = p0 = p1 = p2 = zeros()
        amplitude = ZERO

    expected_p0 = zeros()
    expected_p0[0][0] = ONE
    expected_k = zeros()
    expected_amplitude = Q2(Fraction(0), Fraction(1, 32))
    for channel in range(1, 4):
        expected_k[0][channel] = -expected_amplitude
        expected_k[channel][0] = expected_amplitude

    checks["exact_generator"] = (
        amplitude == expected_amplitude
        and amplitude * amplitude == Q2(Fraction(1, 512))
        and k == expected_k
        and all_zero(add(k, transpose(k)))
    )
    checks["exact_bare_projector"] = p0 == expected_p0

    independent_p1 = add(multiply(k, p0), scale(-1, multiply(p0, k)))
    checks["first_order_transport"] = p1 == independent_p1

    order_one_defect = add(multiply(p0, p1), multiply(p1, p0), scale(-1, p1))
    order_two_defect = add(
        multiply(p0, p2), multiply(p2, p0), multiply(p1, p1), scale(-1, p2)
    )
    checks["formal_idempotence"] = (
        all_zero(order_one_defect) and all_zero(order_two_defect)
    )
    checks["rank_trace_preserved"] = (
        matrix_trace(p0) == ONE
        and matrix_trace(p1) == ZERO
        and matrix_trace(p2) == ZERO
    )

    p1_square = multiply(p1, p1)
    # Solve the block-diagonal part of P^2=P independently.  These are the
    # unique forced values; no exponential formula is used here.
    forced_hard = -p1_square[0][0]
    forced_collinear = [
        [p1_square[i][j] for j in range(1, 4)] for i in range(1, 4)
    ]
    recorded_collinear = [
        [p2[i][j] for j in range(1, 4)] for i in range(1, 4)
    ]
    checks["independent_forced_blocks"] = (
        p2[0][0] == forced_hard == Q2(Fraction(-3, 512))
        and recorded_collinear == forced_collinear
        and all(entry == Q2(Fraction(1, 512))
                for row in recorded_collinear for entry in row)
    )

    real_diagonal = sum((p2[i][i] for i in range(1, 4)), ZERO)
    responses = cert.get("forced_responses", {})
    checks["exact_response_cancellation"] = (
        real_diagonal == Q2(Fraction(3, 512))
        and p2[0][0] + real_diagonal == ZERO
        and fraction(responses.get("three_pair_real_diagonal", {}))
        == Fraction(3, 512)
        and fraction(responses.get("hard_normalization_diagonal", {}))
        == Fraction(-3, 512)
        and fraction(responses.get("sum", {})) == 0
    )

    no_hard = [row[:] for row in p2]
    no_hard[0][0] = ZERO
    mutated_defect = add(
        multiply(p0, no_hard), multiply(no_hard, p0),
        multiply(p1, p1), scale(-1, no_hard),
    )
    checks["omitted_normalization_rejected"] = (
        mutated_defect[0][0] == Q2(Fraction(3, 512))
    )

    gate = cert.get("bt_charge_gate", {})
    charge_shift = gate.get("generator_total_charge_shift")
    checks["neutral_charge_gate"] = (
        charge_shift == 0
        and gate.get("result")
        == "PRESERVES_ONE_SIDED_NEGATIVE_RELATIVE_RADICAL"
        and all(charge + charge_shift < 0 for charge in range(-6, 0))
        and -2 + 2 == 0
    )
    disposition = cert.get("disposition", {})
    checks["claim_boundary_fail_closed"] = (
        disposition.get("finite_coherent_projector_transport")
        == "EXACT_EXISTENCE_WITNESS"
        and disposition.get("bt_asymptotic_hamiltonian_derivation")
        == "NOT_CONSTRUCTED"
        and disposition.get("continuum_collinear_projector")
        == "NOT_CONSTRUCTED"
        and disposition.get("full_nlo_quotient_trace") == "NOT_COMPUTED"
        and disposition.get("physical_nlo_probability") == "NOT_ESTABLISHED"
        and any("LORENTZIAN-CAUSAL" in item
                for item in cert.get("does_not_establish", []))
    )
    inputs = cert.get("provenance", {}).get("inputs", [])
    try:
        checks["provenance_hashes"] = len(inputs) == 2 and all(
            item["sha256"] == sha256(item["path"]) for item in inputs
        )
    except (KeyError, OSError):
        checks["provenance_hashes"] = False
    checks["producer_checks"] = (
        cert.get("checks", {}).get("ok") is True
        and cert.get("checks", {}).get("passed")
        == cert.get("checks", {}).get("total") == 18
    )

    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} "
          f"({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
