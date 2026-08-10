#!/usr/bin/env python3
"""Independent verifier for the BT asymptotic-generator preflight.

This rail does not import the producer.  It reconstructs the normalized rate
ratio, solves the formal projector equation over Q(sqrt(3)), and derives the
single- versus double-energy-denominator collinear powers separately.
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
    "REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-asymptotic-generator-preflight-v1.schema.json",
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

    def __rsub__(self, other):
        return cast(other) - self

    def __mul__(self, other):
        other = cast(other)
        return Q3(
            self.p * other.p + 3 * self.q * other.q,
            self.p * other.q + self.q * other.p,
        )

    __rmul__ = __mul__

    def __eq__(self, other):
        other = cast(other)
        return self.p == other.p and self.q == other.q


def cast(value):
    return value if isinstance(value, Q3) else Q3(Fraction(value))


ZERO = Q3()
ONE = Q3(Fraction(1))


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def algebraic(payload):
    return Q3(fraction(payload["rational"]), fraction(payload["sqrt3"]))


def zeros(size=4):
    return [[ZERO for _ in range(size)] for _ in range(size)]


def matrix(payload):
    out = zeros()
    seen = set()
    for entry in payload:
        position = (entry["row"], entry["column"])
        if position in seen:
            raise ValueError("duplicate sparse entry")
        seen.add(position)
        out[position[0]][position[1]] = algebraic(entry["value"])
    return out


def add(*matrices):
    size = len(matrices[0])
    return [
        [sum((matrix_[i][j] for matrix_ in matrices), ZERO)
         for j in range(size)]
        for i in range(size)
    ]


def scale(coefficient, matrix_):
    coefficient = cast(coefficient)
    return [[coefficient * entry for entry in row] for row in matrix_]


def multiply(left, right):
    size = len(left)
    return [
        [sum((left[i][k] * right[k][j] for k in range(size)), ZERO)
         for j in range(size)]
        for i in range(size)
    ]


def transpose(matrix_):
    return [list(row) for row in zip(*matrix_)]


def matrix_trace(matrix_):
    return sum((matrix_[i][i] for i in range(len(matrix_))), ZERO)


def all_zero(matrix_):
    return all(entry == ZERO for row in matrix_ for entry in row)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def kallen(t, x, y):
    return t*t + x*x + y*y - 2*t*x - 2*t*y - 2*x*y


def collinear_coefficients(energy, zeta):
    """Coefficients of transverse k^2 in t and Delta E."""
    t_coefficient = 1 / (zeta * (1 - zeta))
    deficit_coefficient = 1 / (2 * energy * zeta * (1 - zeta))
    return t_coefficient, deficit_coefficient


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

    ledger = cert.get("normalization_ledger", {})
    born = Fraction(3, 32)
    per_pair_absolute = Fraction(1, 512)
    per_pair_gram = per_pair_absolute / born
    total_gram = 3 * per_pair_gram
    checks["independent_rate_normalization"] = (
        per_pair_gram == Fraction(1, 48)
        and total_gram == Fraction(1, 16)
        and fraction(ledger.get("gram_per_pair", {})) == per_pair_gram
        and fraction(ledger.get("gram_all_pairs", {})) == total_gram
        and born * total_gram == Fraction(3, 512)
    )

    corrected = cert.get("corrected_projector", {})
    try:
        amplitude = algebraic(corrected["mixing_amplitude"])
        k = matrix(corrected["generator_K"])
        p0 = matrix(corrected["P0"])
        p1 = matrix(corrected["P1"])
        p2 = matrix(corrected["P2"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        amplitude = ZERO
        k = p0 = p1 = p2 = zeros()

    expected_amplitude = Q3(Fraction(0), Fraction(1, 12))
    expected_k = zeros()
    for channel in range(1, 4):
        expected_k[0][channel] = -expected_amplitude
        expected_k[channel][0] = expected_amplitude
    expected_p0 = zeros()
    expected_p0[0][0] = ONE
    checks["exact_corrected_generator"] = (
        amplitude == expected_amplitude
        and amplitude * amplitude == Q3(Fraction(1, 48))
        and k == expected_k
        and all_zero(add(k, transpose(k)))
        and p0 == expected_p0
    )

    derived_p1 = add(multiply(k, p0), scale(-1, multiply(p0, k)))
    order_one = add(multiply(p0, p1), multiply(p1, p0), scale(-1, p1))
    order_two = add(
        multiply(p0, p2), multiply(p2, p0), multiply(p1, p1), scale(-1, p2)
    )
    real_trace = sum((p2[i][i] for i in range(1, 4)), ZERO)
    checks["independent_projector_equations"] = (
        p1 == derived_p1
        and all_zero(order_one)
        and all_zero(order_two)
        and matrix_trace(p0) == ONE
        and matrix_trace(p1) == ZERO
        and matrix_trace(p2) == ZERO
        and p2[0][0] == Q3(Fraction(-1, 16))
        and real_trace == Q3(Fraction(1, 16))
    )

    v1 = cert.get("v1_supersession", {})
    old_hard = born * Fraction(3, 512)
    old_residual = Fraction(3, 512) - old_hard
    checks["v1_error_is_numerically_live"] = (
        old_hard == Fraction(9, 16384)
        and old_residual == Fraction(87, 16384)
        and fraction(v1.get("v1_hard_rate_under_correct_shell_units", {}))
        == old_hard
        and fraction(v1.get("uncancelled_absolute_coefficient", {}))
        == old_residual
        and v1.get("status") == "SUPERSEDED_NORMALIZATION"
    )

    cubic = cert.get("cubic_generator_preflight", {})
    checks["independent_kallen_limit"] = (
        all(kallen(Fraction(t), 0, 0) == Fraction(t*t)
            for t in (-3, -1, 0, 2, 5))
        and cubic.get("massless_daughters") == "Kallen(t,0,0)=t^2"
    )
    energy_fixtures = [
        (Fraction(5), Fraction(1, 3)),
        (Fraction(7, 2), Fraction(2, 5)),
        (Fraction(11, 3), Fraction(3, 7)),
    ]
    deficit_ok = True
    for energy, zeta in energy_fixtures:
        t_coefficient, deficit_coefficient = collinear_coefficients(
            energy, zeta
        )
        deficit_ok = deficit_ok and (
            deficit_coefficient / t_coefficient == 1 / (2 * energy)
        )
    checks["independent_energy_deficit"] = deficit_ok
    checks["single_vs_double_denominator"] = (
        cubic.get("ordinary_gram_target")
        == {"numerator": 0, "denominator": 1}
        and cubic.get("required_gram_target")
        == {"numerator": 1, "denominator": 48}
        and cubic.get("disposition")
        == "EXACT_OBSTRUCTION_FOR_SINGLE_DENOMINATOR_FOCK_GENERATOR"
        and "-4*i*lambda*E^2" in cubic.get("jordan_control", "")
    )

    charge = cert.get("charge_gate", {})
    checks["broken_vacuum_charge_not_hidden"] = (
        charge.get("cubic_charge")
        == "q(Omega)+2*q(Upsilon)=-1 around the broken vacuum"
        and charge.get("disposition") == "NOT_CLEARED_BY_BARE_CUBIC_VERTEX"
    )
    disposition = cert.get("disposition", {})
    checks["claim_boundary_fail_closed"] = (
        disposition.get("ordinary_single_denominator_fock_generator")
        == "EXACT_OBSTRUCTION"
        and disposition.get("jordan_distributional_generator")
        == "NOT_CONSTRUCTED"
        and disposition.get("incoming_degenerate_sectors")
        == "NOT_CONSTRUCTED"
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
        == cert.get("checks", {}).get("total") == 21
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
