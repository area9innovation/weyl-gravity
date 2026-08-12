#!/usr/bin/env python3
"""Independent explicit-tree verifier for planar BT Born-density positivity."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache

from jsonschema import Draft202012Validator
from sympy.polys.domains import QQ
from sympy.polys.fields import field


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PLANAR_PHYSICAL_BORN_DENSITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-planar-physical-born-density-v1.schema.json",
)
N = 6
FULL = 63


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


class Jet:
    """Independent 64-slot square-free jet over the exact field Q(t)."""

    def __init__(self, base, coefficients=None):
        self.base = base
        self.coefficients = {
            int(mask): base(value)
            for mask, value in (coefficients or {}).items()
            if value
        }

    def _coerce(self, other):
        return other if isinstance(other, Jet) else Jet(self.base, {0: other})

    def __eq__(self, other):
        if isinstance(other, Jet):
            return self.coefficients == other.coefficients
        return not self.coefficients if other == 0 else False

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.base.zero) + value
            if not out[mask]:
                del out[mask]
        return Jet(self.base, out)

    __radd__ = __add__

    def __neg__(self):
        return Jet(
            self.base, {mask: -value for mask, value in self.coefficients.items()}
        )

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
                out[mask] = out.get(mask, self.base.zero) + left_value * right_value
        return Jet(self.base, out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, self.base.zero)
        if not scalar:
            raise ZeroDivisionError("noninvertible jet")
        one = Jet(self.base, {0: 1})
        ratio = (-1 / scalar) * (self - scalar)
        out = one
        power = one
        for _ in range(N):
            power *= ratio
            out += power
        return (1 / scalar) * out

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


def explicit_tree_family(tilt_ratio=Fraction(0), parameter_value=None):
    """Enumerate all trees; do not use the producer's summed-current recursion."""
    if parameter_value is None:
        values = field("t", QQ)
        base, t = values
    else:
        base = QQ
        parameter_fraction = Fraction(parameter_value)
        t = base(parameter_fraction.numerator, parameter_fraction.denominator)

    def rational(value):
        fraction = Fraction(value)
        if parameter_value is None:
            return base(fraction)
        return base(fraction.numerator, fraction.denominator)

    def vector(*entries):
        return tuple(rational(value) for value in entries)

    def add_vectors(*vectors):
        return tuple(
            sum((value[index] for value in vectors), base.zero)
            for index in range(4)
        )

    def minkowski_square(value):
        return value[0] * value[0] - sum(
            (entry * entry for entry in value[1:]), base.zero
        )

    cosine = (1 - t * t) / (1 + t * t)
    sine = 2 * t / (1 + t * t)
    tilt = rational(tilt_ratio) * t
    tilt_cosine = (1 - tilt * tilt) / (1 + tilt * tilt)
    tilt_sine = 2 * tilt / (1 + tilt * tilt)
    incoming = [
        vector("6/5", "6/5", 0, 0),
        vector(1, "-3/5", "4/5", 0),
        vector(1, "-3/5", "-4/5", 0),
    ]
    outgoing = []
    for value in incoming:
        rotated_x = cosine * value[1] - sine * value[2]
        rotated_y = sine * value[1] + cosine * value[2]
        outgoing.append(
            (
                value[0],
                rotated_x,
                tilt_cosine * rotated_y,
                tilt_sine * rotated_y,
            )
        )
    momenta = incoming + [tuple(-entry for entry in value) for value in outgoing]
    adjacent = [
        minkowski_square(add_vectors(momenta[i], momenta[(i + 1) % N]))
        for i in range(N)
    ]
    triples = [
        minkowski_square(
            add_vectors(momenta[i], momenta[(i + 1) % N], momenta[(i + 2) % N])
        )
        for i in range(3)
    ]
    masses = [Jet(base, {1 << index: 1}) for index in range(N)]

    @lru_cache(maxsize=None)
    def pair_square(left, right):
        if left == right:
            return masses[left]
        distance = (right - left) % N
        if distance == 1:
            return Jet(base, {0: adjacent[left]})
        if distance == N - 1:
            return Jet(base, {0: adjacent[right]})
        if distance == 2:
            return (
                Jet(base, {0: triples[left % 3]})
                - adjacent[left]
                - adjacent[(left + 1) % N]
                + masses[left]
                + masses[(left + 1) % N]
                + masses[(left + 2) % N]
            )
        if distance == N - 2:
            return pair_square(right, left)
        raise ValueError("opposite pair")

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return masses[left]
        if (right - left) % N == 3:
            return -masses[left] - sum(
                (
                    basis_dot(left, index)
                    for index in range(N)
                    if index not in (left, right)
                ),
                Jet(base),
            )
        return (pair_square(left, right) - masses[left] - masses[right]) / 2

    @lru_cache(maxsize=None)
    def unsigned_dot(left, right):
        return sum(
            (
                basis_dot(i, j)
                for i in range(N)
                if left & (1 << i)
                for j in range(N)
                if right & (1 << j)
            ),
            Jet(base),
        )

    def dot(left, right):
        return left[0] * right[0] * unsigned_dot(left[1], right[1])

    def square(momentum):
        return dot(momentum, momentum)

    def cubic(a, b, c):
        za, zb, zc = square(a), square(b), square(c)
        return (
            za * za + zb * zb + zc * zc
            - 2 * za * zb - 2 * za * zc - 2 * zb * zc
        ) / 2

    def quartic(a, b, c, d):
        return (
            dot(a, b) * dot(c, d)
            + dot(a, c) * dot(b, d)
            + dot(a, d) * dot(b, c)
        )

    @lru_cache(maxsize=None)
    def current_terms(mask):
        if mask.bit_count() == 1:
            return ((Jet(base, {0: 1}), 0, 0),)
        propagator = square((1, mask)) * square((1, mask))
        rows = []
        for left, right in partitions(mask, 2):
            vertex = cubic((1, left), (1, right), (-1, mask))
            for lrow, rrow in itertools.product(
                current_terms(left), current_terms(right)
            ):
                rows.append(
                    (-vertex * lrow[0] * rrow[0] / propagator,
                     lrow[1] + rrow[1] + 1, lrow[2] + rrow[2])
                )
        for a, b, c in partitions(mask, 3):
            vertex = quartic((1, a), (1, b), (1, c), (-1, mask))
            for arow, brow, crow in itertools.product(
                current_terms(a), current_terms(b), current_terms(c)
            ):
                rows.append(
                    (-vertex * arow[0] * brow[0] * crow[0] / propagator,
                     arow[1] + brow[1] + crow[1],
                     arow[2] + brow[2] + crow[2] + 1)
                )
        return tuple(rows)

    root = 1 << 5
    rest = FULL ^ root
    trees = []
    for left, right in partitions(rest, 2):
        vertex = cubic((1, root), (1, left), (1, right))
        for lrow, rrow in itertools.product(
            current_terms(left), current_terms(right)
        ):
            trees.append(
                (-vertex * lrow[0] * rrow[0],
                 lrow[1] + rrow[1] + 1, lrow[2] + rrow[2])
            )
    for a, b, c in partitions(rest, 3):
        vertex = quartic((1, root), (1, a), (1, b), (1, c))
        for arow, brow, crow in itertools.product(
            current_terms(a), current_terms(b), current_terms(c)
        ):
            trees.append(
                (-vertex * arow[0] * brow[0] * crow[0],
                 arow[1] + brow[1] + crow[1],
                 arow[2] + brow[2] + crow[2] + 1)
            )
    amplitude = sum((row[0] for row in trees), Jet(base))
    topology_counts = {}
    topology_amplitudes = {}
    for value, cubic_count, quartic_count in trees:
        key = (cubic_count, quartic_count)
        topology_counts[key] = topology_counts.get(key, 0) + 1
        topology_amplitudes[key] = topology_amplitudes.get(key, Jet(base)) + value
    return {
        "base": base,
        "t": t,
        "momenta": momenta,
        "adjacent": adjacent,
        "triples": triples,
        "tree_count": len(trees),
        "topology_counts": topology_counts,
        "topology_amplitudes": topology_amplitudes,
        "amplitude": amplitude,
    }


def verify(certificate):
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_match = all(
        row["sha256"] == sha256(row["path"]) for row in inputs
    )
    if not hashes_match:
        return {
            "schema_validation": True,
            "all_input_hashes_match": False,
        }

    result = explicit_tree_family()
    base = result["base"]
    amplitude = result["amplitude"]
    degree_three = {
        mask: value
        for mask, value in amplitude.coefficients.items()
        if mask.bit_count() == 3
    }
    representatives = [
        mask for mask in sorted(degree_three) if mask < (FULL ^ mask)
    ]
    squarefree = (amplitude * amplitude).coefficients.get(FULL, base.zero)
    square_sum = 2 * sum(
        (degree_three[mask] * degree_three[mask] for mask in representatives),
        base.zero,
    )
    numerator_gcd = degree_three[representatives[0]].numer
    for mask in representatives[1:]:
        numerator_gcd = numerator_gcd.gcd(degree_three[mask].numer)
    family = certificate["exact_physical_family"]
    recorded = {row["mask"]: row for row in family["middle_coefficients"]}
    topology_nontrivial = []
    topology_cancellation = []
    for mask in representatives:
        differences = []
        for topology in sorted(result["topology_amplitudes"]):
            values = result["topology_amplitudes"][topology].coefficients
            differences.append(
                values.get(mask, base.zero) - values.get(FULL ^ mask, base.zero)
            )
        topology_nontrivial.append(any(value != 0 for value in differences))
        topology_cancellation.append(sum(differences, base.zero) == 0)
    total_momentum = [
        sum((row[index] for row in result["momenta"]), base.zero)
        for index in range(4)
    ]
    massless = [
        row[0] * row[0] - sum((entry * entry for entry in row[1:]), base.zero)
        for row in result["momenta"]
    ]
    disposition = certificate["interpretation"]
    density = certificate["local_born_density"]
    checks = {
        "schema_validation": True,
        "all_input_hashes_match": hashes_match,
        "independent_physical_momenta_are_null_and_conserved": (
            all(value == 0 for value in massless + total_momentum)
        ),
        "independent_invariants_match": (
            [str(value) for value in result["adjacent"]]
            == family["adjacent_invariants"]
            and [str(value) for value in result["triples"]]
            == family["triple_invariants"]
        ),
        "explicit_tree_count_and_topologies": (
            result["tree_count"] == 220
            and result["topology_counts"] == {(4, 0): 105, (2, 1): 105, (0, 2): 10}
        ),
        "amplitude_support_matches": (
            len(amplitude.coefficients) == 42
            and sorted({mask.bit_count() for mask in amplitude.coefficients})
            == [3, 4, 5, 6]
        ),
        "twenty_middle_coefficients_and_ten_complements": (
            len(degree_three) == 20 and len(representatives) == 10
            and all(degree_three[mask] == degree_three[FULL ^ mask]
                    for mask in representatives)
        ),
        "recorded_middle_coefficients_match": (
            set(recorded) == set(representatives)
            and all(
                recorded[mask]["complement_mask"] == FULL ^ mask
                and recorded[mask]["coefficient"] == str(degree_three[mask])
                and recorded[mask]["complement_coefficient"]
                == str(degree_three[FULL ^ mask])
                for mask in representatives
            )
        ),
        "topology_antisymmetry_is_real_and_cancels": (
            all(topology_nontrivial) and all(topology_cancellation)
        ),
        "independent_square_sum_identity": (
            squarefree == square_sum
            and str(squarefree) == family["squarefree_squared_amplitude"]
        ),
        "independent_numerator_gcd_is_constant": (
            numerator_gcd.degree() == 0
            and str(numerator_gcd.monic()) == family["degree_three_numerator_gcd"]
        ),
        "denominator_is_even_pole_product": (
            all(multiplicity % 2 == 0
                for _, multiplicity in squarefree.denom.factor_list()[1])
            and len(squarefree.denom.factor_list()[1]) == 6
        ),
        "six_derivative_measure_decoupling_is_typed": (
            density["amplitude_minimum_mass_degree"] == 3
            and density["squared_amplitude_minimum_mass_degree"] == 6
            and density["status"]
            == "STRICTLY_POSITIVE_ON_DECLARED_REGULAR_PHYSICAL_FAMILY"
        ),
        "claim_boundary_is_fail_closed": (
            disposition["complete_nonplanar_six_body_phase_space"] == "NOT_COMPUTED"
            and disposition["integrated_normalized_probability"] == "NOT_COMPUTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and any("LORENTZIAN-CAUSAL" in row
                    for row in certificate["does_not_establish"])
        ),
        "next_gate_is_nonplanar_then_integrated": (
            "nonplanar two-parameter" in certificate["next_gate"]
            and "integrate" in certificate["next_gate"]
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
