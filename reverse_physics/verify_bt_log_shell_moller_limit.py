#!/usr/bin/env python3
"""Independent verifier for the BT logarithmic-shell Moller-limit theorem."""
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
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-log-shell-moller-limit-v1.schema.json",
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


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def q3(value):
    return Q3(frac(value["rational"]), frac(value["sqrt3"]))


def zeros():
    return [[ZERO for _ in range(4)] for _ in range(4)]


def sparse(entries):
    result = zeros()
    occupied = set()
    for entry in entries:
        position = (entry["row"], entry["column"])
        if position in occupied:
            raise ValueError("duplicate sparse entry")
        occupied.add(position)
        result[position[0]][position[1]] = q3(entry["value"])
    return result


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(4)), ZERO)
            for j in range(4)
        ]
        for i in range(4)
    ]


def add(*matrices):
    return [
        [sum((item[i][j] for item in matrices), ZERO) for j in range(4)]
        for i in range(4)
    ]


def scale(coefficient, matrix):
    return [[cast(coefficient) * entry for entry in row] for row in matrix]


def all_zero(matrix):
    return all(entry == ZERO for row in matrix for entry in row)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    model = certificate.get("continuum_model", {})
    shells = model.get("shell_fixtures", [])
    obstruction = certificate.get("strong_limit_obstruction", {})
    bundle = certificate.get("dressed_boundary_bundle", {})
    disposition = certificate.get("disposition", {})
    try:
        intervals = [
            tuple(frac(endpoint) for endpoint in shell["y_interval_in_units_of_ell"])
            for shell in shells
        ]
        a_star = sparse(bundle.get("pullback_A", []))
        b_star = sparse(bundle.get("pullback_B", []))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        intervals = []
        a_star = b_star = zeros()

    def overlap(left, right):
        return max(Fraction(0), min(left[1], right[1]) - max(left[0], right[0]))

    source = load(
        os.path.join(
            ROOT,
            "reverse_physics/certificates/"
            "REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
        )
    )
    source_ledger = source.get("response_ledger", {})
    a2 = multiply(a_star, a_star)
    norm = sum((a_star[i][0] * a_star[i][0] for i in range(1, 4)), ZERO)
    distance_square = 2 * norm
    weak_b = b_star[0][0]
    weak_defect = 2 * weak_b
    normalized_v = [
        ZERO,
        Q3(Fraction(0), Fraction(1, 3)),
        Q3(Fraction(0), Fraction(1, 3)),
        Q3(Fraction(0), Fraction(1, 3)),
    ]
    a_on_v = [
        sum((a_star[i][j] * normalized_v[j] for j in range(4)), ZERO)
        for i in range(4)
    ]
    checks = {
        "schema": not errors,
        "source_coefficient": (
            frac(source_ledger.get("real_per_pair_Born_normalized", {}))
            == Fraction(1, 48)
            and frac(source_ledger.get("real_total_Born_normalized", {}))
            == Fraction(1, 16)
        ),
        "six_exact_shells": (
            len(intervals) == 6
            and all(right - left == 1 for left, right in intervals)
        ),
        "pairwise_shell_orthogonality": (
            len(intervals) == 6
            and all(
                overlap(intervals[n], intervals[m]) == 0
                for n in range(6)
                for m in range(6)
                if n != m
            )
        ),
        "recorded_inner_products": (
            len(shells) == 6
            and all(
                frac(entry["inner_product"])
                == (1 if entry["other"] == shell["n"] else 0)
                for shell in shells
                for entry in shell["inner_products"]
            )
        ),
        "exact_pullback_generator": (
            all_zero(add(transpose(a_star), a_star))
            and norm == Q3(Fraction(1, 16))
        ),
        "noncauchy_distance": (
            distance_square == Q3(Fraction(1, 8))
            and frac(obstruction.get("distinct_shell_column_distance_square", {}))
            == Fraction(1, 8)
            and all(
                frac(row["distance_square_Ah"]) == Fraction(1, 8)
                for row in obstruction.get("noncauchy_fixtures", [])
            )
        ),
        "strong_limit_logic": (
            obstruction.get("disposition")
            == "NO_STRONG_MOLLER_LIMIT_ON_ORDINARY_LOG_SHELL_CARRIER"
            and "Cauchy" in obstruction.get("theorem", "")
        ),
        "all_order_rotation": (
            sum((entry * entry for entry in normalized_v), ZERO) == Q3(Fraction(1))
            and a_on_v == [Q3(Fraction(-1, 4)), ZERO, ZERO, ZERO]
            and obstruction.get("all_order_shell_image")
            == "exp(x A_n)h=cos(x/4)h+sin(x/4)v_n with v_n=4 A_n h"
            and obstruction.get("all_order_distinct_shell_distance_square")
            == "2 sin(x/4)^2"
            and "small nonzero perturbative x"
            in obstruction.get("all_order_condition", "")
        ),
        "finite_shell_pseudounitarity": (
            b_star == scale(Fraction(1, 2), a2)
            and all_zero(add(transpose(b_star), b_star, multiply(transpose(a_star), a_star)))
        ),
        "weak_limit_defect": (
            weak_b == Q3(Fraction(-1, 32))
            and weak_defect == Q3(Fraction(-1, 16))
            and certificate.get("weak_limit", {}).get("disposition")
            == "CONTRACTION_NOT_ISOMETRY"
        ),
        "all_order_weak_and_bundle_identity": (
            certificate.get("weak_limit", {}).get("S_weak_all_order")
            == "1+(cos(x/4)-1)|h><h|"
            and certificate.get("weak_limit", {}).get("pseudounitarity_defect_all_order")
            == "-sin(x/4)^2|h><h|"
            and bundle.get("hard_probability_all_order") == "cos(x/4)^2"
            and bundle.get("endpoint_probability_all_order") == "sin(x/4)^2"
            and bundle.get("inclusive_probability_all_order") == "1"
        ),
        "bundle_probability": (
            frac(bundle.get("hard_survival_response", {})) == Fraction(-1, 16)
            and frac(bundle.get("real_total_response", {})) == Fraction(1, 16)
            and frac(bundle.get("inclusive_response", {})) == 0
        ),
        "claim_boundary": (
            disposition.get("ordinary_L2_strong_Moller_limit") == "EXACT_OBSTRUCTION"
            and disposition.get("dressed_boundary_fibre")
            == "CONSTRUCTED_AT_LEADING_LOG_REDUCED_MODE"
            and disposition.get("local_LSZ_or_AQFT_affiliation") == "NOT_ESTABLISHED"
            and disposition.get("full_dynamical_dressed_S_matrix") == "NOT_CONSTRUCTED"
            and disposition.get("complete_NLO_probability") == "NOT_ESTABLISHED"
            and disposition.get("inclusive_shell_probability_cylinder")
            == "REGULATOR_INDEPENDENT_FOR_EXACT_FINITE_SHELL_EXPONENTIAL"
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
            == 22
            and certificate.get("checks", {}).get("failures") == []
            and all(certificate.get("checks", {}).get("details", {}).values())
        ),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT LOG SHELL MOLLER LIMIT VERIFY: FAIL", *failures, sep="\n  ")
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
        "BT LOG SHELL MOLLER LIMIT VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
