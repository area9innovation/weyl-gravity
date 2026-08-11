#!/usr/bin/env python3
"""Independent finite-point check of the BT eight-point tree recursion."""
from __future__ import annotations

import sys
import argparse
import hashlib
import json
import os
from fractions import Fraction
from functools import lru_cache

from jsonschema import Draft202012Validator


N = 8
LO = -8
HI = 4
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-hard-profile-obstruction-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


class Jet:
    def __init__(self, coefficients=None):
        self.coefficients = {
            int(mask): Fraction(value)
            for mask, value in (coefficients or {}).items()
            if value
        }

    def _coerce(self, other):
        return other if isinstance(other, Jet) else Jet({0: other})

    def __eq__(self, other):
        if isinstance(other, Jet):
            return self.coefficients == other.coefficients
        return not self.coefficients if other == 0 else False

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, Fraction(0)) + value
            if not out[mask]:
                del out[mask]
        return Jet(out)

    __radd__ = __add__

    def __neg__(self):
        return Jet({mask: -value for mask, value in self.coefficients.items()})

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_mask, left_value in self.coefficients.items():
            for right_mask, right_value in other.coefficients.items():
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                out[mask] = out.get(mask, Fraction(0)) + left_value * right_value
        return Jet(out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, Fraction(0))
        if not scalar:
            raise ZeroDivisionError("noninvertible spectator jet")
        unit = Jet({0: 1})
        ratio = -Fraction(1, 1) / scalar * (self - scalar)
        out = unit
        power = unit
        for _ in range(3):
            power *= ratio
            out += power
        return Fraction(1, 1) / scalar * out

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()


class Series:
    def __init__(self, coefficients=None):
        self.coefficients = {
            int(power): (value if isinstance(value, Jet) else Jet({0: value}))
            for power, value in (coefficients or {}).items()
            if value != 0 and LO <= int(power) <= HI
        }

    @classmethod
    def scalar(cls, value):
        return cls({0: value})

    def coefficient(self, power):
        return self.coefficients.get(power, Jet())

    def _coerce(self, other):
        return other if isinstance(other, Series) else Series.scalar(other)

    def __eq__(self, other):
        if isinstance(other, Series):
            return self.coefficients == other.coefficients
        return not self.coefficients if other == 0 else False

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for power, value in other.coefficients.items():
            out[power] = out.get(power, Jet()) + value
            if out[power] == 0:
                del out[power]
        return Series(out)

    __radd__ = __add__

    def __neg__(self):
        return Series({power: -value for power, value in self.coefficients.items()})

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_power, left_value in self.coefficients.items():
            for right_power, right_value in other.coefficients.items():
                power = left_power + right_power
                if LO <= power <= HI:
                    out[power] = out.get(power, Jet()) + left_value * right_value
        return Series(out)

    __rmul__ = __mul__

    def inverse(self):
        valuation = min(self.coefficients)
        leading = self.coefficient(valuation)
        recurrence = {0: 1 / leading}
        for order in range(1, HI + valuation + 1):
            total = Jet()
            for index in range(1, order + 1):
                total += self.coefficient(valuation + index) * recurrence[order - index]
            recurrence[order] = -total / leading
        return Series(
            {-valuation + order: value for order, value in recurrence.items()}
        )

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()


def partitions(mask, count):
    if count == 1:
        yield (mask,)
        return
    first = mask & -mask
    rest = mask ^ first
    subset = rest
    while True:
        block = first | subset
        remainder = mask ^ block
        if remainder.bit_count() >= count - 1:
            for tail in partitions(remainder, count - 1):
                yield (block,) + tail
        if not subset:
            break
        subset = (subset - 1) & rest


def topology_counts():
    def multiply(rows):
        out = {(0, 0): 1}
        for row in rows:
            updated = {}
            for (c0, q0), left in out.items():
                for (c1, q1), right in row.items():
                    key = (c0 + c1, q0 + q1)
                    updated[key] = updated.get(key, 0) + left * right
            out = updated
        return out

    @lru_cache(maxsize=None)
    def current(mask):
        if mask.bit_count() == 1:
            return {(0, 0): 1}
        out = {}
        for arity, vertex in ((2, (1, 0)), (3, (0, 1))):
            for blocks in partitions(mask, arity):
                for (cubic, quartic), number in multiply(
                    [current(block) for block in blocks]
                ).items():
                    key = (cubic + vertex[0], quartic + vertex[1])
                    out[key] = out.get(key, 0) + number
        return out

    rest = (1 << 7) - 1
    out = {}
    for arity, vertex in ((2, (1, 0)), (3, (0, 1))):
        for blocks in partitions(rest, arity):
            for (cubic, quartic), number in multiply(
                [current(block) for block in blocks]
            ).items():
                key = (cubic + vertex[0], quartic + vertex[1])
                out[key] = out.get(key, 0) + number
    return out


def finite_tree_kernel(soft_fixture, hard_fixture, epsilons):
    """Sum the complete tree at one exact hierarchy point."""
    a0, a1, a2, a3, a4, tau1, tau2, tau3, tau4 = map(
        Fraction, soft_fixture
    )
    e1, e2, e3 = map(Fraction, epsilons)
    adjacent_hard, triple_hard, quartet_hard = hard_fixture

    def linear(value):
        return Series({1: value})

    masses = [
        linear(e1 * e2 * e3 * a0),
        linear(e1 * e2 * e3 * a1),
        linear(e2 * e3 * a2),
        linear(e3 * a3),
        linear(a4),
        linear(Jet({1: 1})),
        linear(Jet({2: 1})),
        linear(Jet({4: 1})),
    ]
    adjacent = [linear(e1 * e2 * e3 * tau1)] + [
        Series.scalar(Fraction(value)) for value in adjacent_hard
    ]
    triple_values = iter(triple_hard)
    triples = []
    for index in range(N):
        if index == 0:
            triples.append(linear(e2 * e3 * tau2))
        elif index == 5:
            triples.append(linear(tau4))
        else:
            triples.append(Series.scalar(Fraction(next(triple_values))))
    quartets = [linear(e3 * tau3)] + [
        Series.scalar(Fraction(value)) for value in quartet_hard
    ]

    @lru_cache(maxsize=None)
    def pair_square(left, right):
        if left == right:
            return masses[left]
        distance = (right - left) % N
        if distance == 1:
            return adjacent[left]
        if distance == N - 1:
            return adjacent[right]
        if distance == 2:
            return (
                triples[left]
                - adjacent[left]
                - adjacent[(left + 1) % N]
                + masses[left]
                + masses[(left + 1) % N]
                + masses[(left + 2) % N]
            )
        if distance == N - 2:
            return pair_square(right, left)
        if distance == 3:
            indices = [(left + offset) % N for offset in range(4)]
            known = sum(
                (
                    pair_square(indices[p], indices[q])
                    for p in range(4)
                    for q in range(p + 1, 4)
                    if (p, q) != (0, 3)
                ),
                Series(),
            )
            return (
                quartets[left % 4]
                + 2 * sum((masses[index] for index in indices), Series())
                - known
            )
        if distance == N - 3:
            return pair_square(right, left)
        raise ValueError("opposite pair is fixed by momentum conservation")

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return masses[left]
        if (right - left) % N == 4:
            return -masses[left] - sum(
                (
                    basis_dot(left, index)
                    for index in range(N)
                    if index not in (left, right)
                ),
                Series(),
            )
        return (pair_square(left, right) - masses[left] - masses[right]) / 2

    @lru_cache(maxsize=None)
    def unsigned_dot(left_mask, right_mask):
        return sum(
            (
                basis_dot(left, right)
                for left in range(N)
                if left_mask & (1 << left)
                for right in range(N)
                if right_mask & (1 << right)
            ),
            Series(),
        )

    def square(momentum):
        sign, mask = momentum
        return sign * sign * unsigned_dot(mask, mask)

    def dot(left, right):
        return left[0] * right[0] * unsigned_dot(left[1], right[1])

    def cubic(a, b, c):
        za, zb, zc = square(a), square(b), square(c)
        return (
            za * za
            + zb * zb
            + zc * zc
            - 2 * za * zb
            - 2 * za * zc
            - 2 * zb * zc
        ) / 2

    def quartic(a, b, c, d):
        return (
            dot(a, b) * dot(c, d)
            + dot(a, c) * dot(b, d)
            + dot(a, d) * dot(b, c)
        )

    one = Series.scalar(1)

    @lru_cache(maxsize=None)
    def current(mask):
        if mask.bit_count() == 1:
            return one
        value = Series()
        for left, right in partitions(mask, 2):
            value += (
                cubic((1, left), (1, right), (-1, mask))
                * current(left)
                * current(right)
            )
        for a, b, c in partitions(mask, 3):
            value += (
                quartic((1, a), (1, b), (1, c), (-1, mask))
                * current(a)
                * current(b)
                * current(c)
            )
        propagator = square((1, mask))
        return -value / (propagator * propagator)

    root = 1 << 7
    rest = root - 1
    amplitude = Series()
    for left, right in partitions(rest, 2):
        amplitude += (
            cubic((1, root), (1, left), (1, right))
            * current(left)
            * current(right)
        )
    for a, b, c in partitions(rest, 3):
        amplitude += (
            quartic((1, root), (1, a), (1, b), (1, c))
            * current(a)
            * current(b)
            * current(c)
        )
    amplitude = -amplitude
    leading_order = min(amplitude.coefficients)
    leading = amplitude.coefficient(leading_order)
    projected = (leading * leading).coefficients.get(7, Fraction(0))
    return leading_order, sorted(leading.coefficients), projected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    certificate = load(args.verify)
    schema = load(SCHEMA)
    schema_errors = list(Draft202012Validator(schema).iter_errors(certificate))
    soft = [1, 4, 3, 2, 1, 10, 7, 5, 3]
    hard_fixtures = [
        (
            [4, 6, 9, 14, 18, 25, 33],
            [35, 39, 45, 52, 61, 67],
            [71, 79, 83],
        ),
        (
            [4, 6, 9, 14, 18, 25, 34],
            [35, 39, 45, 52, 61, 67],
            [71, 79, 83],
        ),
    ]
    expected = [
        Fraction(520471052635202957, 31004982162000000),
        Fraction(511691474216301555234829, 31171230876352644000000),
    ]
    rows = [
        finite_tree_kernel(
            soft,
            hard,
            [Fraction(1, 5), Fraction(2, 7), Fraction(3, 11)],
        )
        for hard in hard_fixtures
    ]
    recorded_rows = certificate["correlated_boundary"]["rows"]
    recorded_finite = [Fraction(row["finite_projected_value"]) for row in recorded_rows]
    recorded_residues = [Fraction(row["strong_order"]) for row in recorded_rows]
    counts = topology_counts()
    inputs = certificate["provenance"]["inputs"]
    checks = {
        "schema_validation": not schema_errors,
        "independent_topology_counts": counts
        == {(6, 0): 10395, (4, 1): 17325, (2, 2): 6300, (0, 3): 280},
        "amplitudes_start_at_delta_two": all(row[0] == 2 for row in rows),
        "all_spectator_masks_present": all(
            row[1] == list(range(8)) for row in rows
        ),
        "both_independent_finite_tree_values": [row[2] for row in rows]
        == expected,
        "recorded_finite_values_match": recorded_finite == expected,
        "hard_profile_dependence_is_nonzero": expected[0] != expected[1],
        "recorded_residue_difference_is_257_over_1568": (
            recorded_residues[0] - recorded_residues[1]
            == frac(certificate["correlated_boundary"]["strong_residue_difference"])
            == Fraction(257, 1568)
        ),
        "ordered_valuation_is_recorded_fail_closed": all(
            row["hierarchy_valuations"]
            == [["e1", 0], ["e2", 0], ["e3", -1]]
            for row in recorded_rows
        ),
        "input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "fourth_moment_remains_uncomputed": certificate["disposition"][
            "threshold_integrated_fourth_moment"
        ]
        == "NOT_COMPUTED",
        "Eq19_remains_open": certificate["disposition"]["Eq19_all_orders"]
        == "NOT_PROVED",
    }
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("projected:", [str(row[2]) for row in rows])
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
