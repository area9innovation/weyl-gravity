#!/usr/bin/env python3
"""Independent verifier for the BT five-point tree-amplitude jet.

The producer is not imported.  This rail rewrites the vertices in terms of
the triangle polynomial of squared momenta and solves inverse propagator jets
from the convolution identity D^2 D^-2 = 1.  The producer instead evaluates
the published dot-product vertices and uses a geometric series.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import combinations

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-five-point-tree-jet-v1.schema.json",
)
N = 5
FULL_MASK = 31


class RationalDomain:
    zero = Fraction(0)
    one = Fraction(1)

    @staticmethod
    def convert(value):
        return Fraction(value)


class FieldDomain:
    def __init__(self, field):
        self.field = field
        self.zero = field.zero
        self.one = field.one

    def convert(self, value):
        return self.field(value)


class Jet:
    def __init__(self, domain, coefficients=None, max_degree=N):
        self.domain = domain
        self.max_degree = int(max_degree)
        self.coefficients = {
            int(mask): domain.convert(value)
            for mask, value in (coefficients or {}).items()
            if value != 0 and int(mask).bit_count() <= self.max_degree
        }

    @classmethod
    def scalar(cls, domain, value, max_degree=N):
        return cls(domain, {0: value}, max_degree)

    def _coerce(self, other):
        if isinstance(other, Jet):
            return other
        return Jet.scalar(self.domain, other, self.max_degree)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.domain.zero) + value
        return Jet(self.domain, out, self.max_degree)

    __radd__ = __add__

    def __neg__(self):
        return Jet(
            self.domain,
            {mask: -value for mask, value in self.coefficients.items()},
            self.max_degree,
        )

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_mask, left_value in self.coefficients.items():
            for right_mask, right_value in other.coefficients.items():
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                if mask.bit_count() > self.max_degree:
                    continue
                out[mask] = out.get(mask, self.domain.zero) + (
                    left_value * right_value
                )
        return Jet(self.domain, out, self.max_degree)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return self * (self.domain.one / self.domain.convert(scalar))

    def coefficient(self, mask):
        return self.coefficients.get(mask, self.domain.zero)

    def inverse_square_recurrence(self):
        """Solve (self*self)*answer=1 coefficient by coefficient."""
        squared = self * self
        constant = squared.coefficient(0)
        if constant == 0:
            raise ZeroDivisionError("zero channel constant")
        answer = {0: self.domain.one / constant}
        masks = sorted(range(1, 1 << N), key=lambda mask: mask.bit_count())
        for mask in masks:
            if mask.bit_count() > self.max_degree:
                continue
            total = self.domain.zero
            subset = mask
            while subset:
                left = squared.coefficient(subset)
                if left != 0:
                    total += left * answer.get(mask ^ subset, self.domain.zero)
                subset = (subset - 1) & mask
            answer[mask] = -total / constant
        return Jet(self.domain, answer, self.max_degree)


def triangle(a, b, c):
    return (a * a + b * b + c * c
            - 2 * a * b - 2 * a * c - 2 * b * c) / 2


def build_amplitude(domain, s_values, max_degree=N, sign=-1):
    """Independent invariant-only derivation of A5=M5/(8 lambda^3)."""
    s_values = [domain.convert(value) for value in s_values]

    def x(index):
        return Jet(domain, {1 << index: domain.one}, max_degree)

    def pair_square(i, j):
        i, j = sorted((i, j))
        if j == i + 1:
            return Jet.scalar(domain, s_values[i], max_degree)
        if (i, j) == (0, 4):
            return Jet.scalar(domain, s_values[4], max_degree)
        # Orient the nonadjacent pair as (a,a+2) modulo five.
        if (j - i) % N == 2:
            a = i
        else:
            a = j
        constant = (
            s_values[(a + 3) % N]
            - s_values[a]
            - s_values[(a + 1) % N]
        )
        return (
            Jet.scalar(domain, constant, max_degree)
            + x(a) + x((a + 1) % N) + x((a + 2) % N)
        )

    pairs = list(combinations(range(N), 2))
    pair_squares = {pair: pair_square(*pair) for pair in pairs}

    def z(pair):
        return pair_squares[tuple(sorted(pair))]

    def end(pair):
        i, j = pair
        channel = z(pair)
        return (
            triangle(x(i), x(j), channel)
            * channel.inverse_square_recurrence()
        )

    def quartic_for_pair(pair):
        remaining = [index for index in range(N) if index not in pair]
        internal_square = z(pair)
        out = Jet(domain, max_degree=max_degree)
        for left, right in combinations(remaining, 2):
            other = next(index for index in remaining
                         if index not in (left, right))
            channel = z((left, right))
            out += (
                (channel - x(left) - x(right))
                * (channel - x(other) - internal_square)
            ) / 4
        return out

    ends = {pair: end(pair) for pair in pairs}
    amplitude = Jet(domain, max_degree=max_degree)
    for pair in pairs:
        amplitude += ends[pair] * quartic_for_pair(pair)

    topology_rows = []
    for central in range(N):
        remaining = [index for index in range(N) if index != central]
        anchor = remaining[0]
        for partner in remaining[1:]:
            left = tuple(sorted((anchor, partner)))
            right = tuple(sorted(index for index in remaining
                                 if index not in left))
            amplitude += sign * (
                ends[left] * ends[right]
                * triangle(z(left), z(right), x(central))
            )
            topology_rows.append((central, left, right))
    return amplitude, topology_rows


def fraction(payload):
    return Fraction(payload["numerator"], payload["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def symbolic_field(names):
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    values = field(",".join(names), QQ)
    return values[0], list(values[1:])


def polynomial_valuation(poly):
    return min(monomial[0] for monomial, _ in poly.terms())


def valuation(value):
    return polynomial_valuation(value.numer) - polynomial_valuation(value.denom)


def verify(certificate, full_symbolic=False):
    checks = {}
    try:
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)
        checks["strict_schema"] = True
    except Exception:
        checks["strict_schema"] = False

    checks["identity_and_boundary"] = (
        certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
        and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
        and any("LORENTZIAN-CAUSAL" in item
                for item in certificate.get("does_not_establish", []))
    )

    try:
        inputs = certificate["provenance"]["inputs"]
        checks["input_hashes"] = len(inputs) == 2 and all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        )
    except (KeyError, OSError):
        checks["input_hashes"] = False

    topology = certificate.get("topology", {})
    cq_rows = topology.get("cubic_quartic_rows", [])
    checks["independent_topology_enumeration"] = (
        topology.get("cubic_quartic_count") == 10
        and topology.get("three_cubic_count") == 15
        and topology.get("total_count") == 25
        and {tuple(row["cubic_external_pair"]) for row in cq_rows}
        == set(combinations(range(N), 2))
    )

    fixtures_ok = True
    for fixture in certificate.get("exact_fixtures", []):
        invariants = [fraction(row) for row in fixture["cyclic_invariants"]]
        amplitude, rows = build_amplitude(
            RationalDomain(), invariants, max_degree=N)
        recorded = {
            row["mask"]: fraction(row["coefficient"])
            for row in fixture["jet_rows"]
        }
        fixtures_ok = fixtures_ok and (
            len(rows) == 15
            and len(recorded) == 32
            and all(amplitude.coefficient(mask) == recorded[mask]
                    for mask in range(32))
            and sorted(amplitude.coefficients) == fixture["nonzero_masks"]
            and min(mask.bit_count() for mask in amplitude.coefficients) == 3
            and (amplitude * amplitude).coefficient(FULL_MASK)
            == fraction(fixture["projected_square"]) == 0
        )
    checks["independent_exact_fixtures"] = (
        len(certificate.get("exact_fixtures", [])) == 3 and fixtures_ok
    )

    field_object, generators = symbolic_field(["s0", "s1", "s2", "s3", "s4"])
    field_domain = FieldDomain(field_object)
    low_amplitude, _ = build_amplitude(
        field_domain, generators, max_degree=2)
    recorded_low = certificate.get("symbolic_jet", {}).get(
        "zero_low_degree_rows", [])
    checks["independent_symbolic_low_degree_zero"] = (
        len(recorded_low) == 16
        and not low_amplitude.coefficients
        and all(row.get("canonical_zero") is True for row in recorded_low)
    )

    if full_symbolic:
        full_amplitude, _ = build_amplitude(
            field_domain, generators, max_degree=N)
        hashes = []
        for mask, coefficient in sorted(full_amplitude.coefficients.items()):
            canonical = str(coefficient)
            hashes.append({
                "mask": mask,
                "subset": [index + 1 for index in range(N)
                           if mask & (1 << index)],
                "degree": mask.bit_count(),
                "canonical_length": len(canonical),
                "sha256": hashlib.sha256(
                    canonical.encode("utf-8")).hexdigest(),
            })
        checks["independent_full_symbolic_hashes"] = (
            hashes == certificate["symbolic_jet"]["coefficient_hashes"]
            and (full_amplitude * full_amplitude).coefficient(FULL_MASK) == 0
        )

    face_ok = True
    epsilon_field, epsilon_generators = symbolic_field(["epsilon"])
    epsilon = epsilon_generators[0]
    epsilon_domain = FieldDomain(epsilon_field)
    trajectories = {
        "ADJACENT_COLLINEAR_s0": [epsilon, 3, 5, 7, 11],
        "NONADJACENT_COLLINEAR_z02": [2, 3, 7, 5 + epsilon, 11],
        "SOFT_LEG_5": [2, 3, 2 + 5 * epsilon, 7 * epsilon, 11 * epsilon],
    }
    for face in certificate.get("soft_collinear_faces", []):
        amplitude, _ = build_amplitude(
            epsilon_domain, trajectories[face["face"]], max_degree=N)
        rows = [
            {
                "mask": mask,
                "degree": mask.bit_count(),
                "epsilon_valuation": valuation(coefficient),
            }
            for mask, coefficient in sorted(amplitude.coefficients.items())
        ]
        face_ok = face_ok and (
            rows == face["coefficient_rows"]
            and (amplitude * amplitude).coefficient(FULL_MASK) == 0
        )
    checks["independent_face_valuations"] = (
        len(certificate.get("soft_collinear_faces", [])) == 3 and face_ok
    )

    disposition = certificate.get("disposition", {})
    checks["fail_closed_disposition"] = (
        disposition.get("complete_five_point_tree_jet")
        == "COMPUTED_AND_HASHED"
        and disposition.get("pointwise_D5_amplitude_square") == "ZERO"
        and disposition.get("five_body_phase_space_projector")
        == "NOT_CONSTRUCTED"
        and disposition.get("distributional_boundary_terms")
        == "NOT_CLASSIFIED"
        and disposition.get("physical_nlo_process_map") == "NOT_CONSTRUCTED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )

    checks["missing_objects_populated"] = (
        len(certificate.get("missing_object_ledger", [])) >= 6
        and "distributional" in " ".join(
            certificate.get("does_not_establish", []))
        and "KLN" in " ".join(certificate.get("does_not_establish", []))
    )
    recorded_checks = certificate.get("checks", {})
    checks["producer_checks_recorded"] = (
        recorded_checks.get("ok") is True
        and recorded_checks.get("passed") == recorded_checks.get("total")
        and not recorded_checks.get("failures")
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="independent BT five-point tree-jet verifier")
    parser.add_argument("--verify", default=DEFAULT_CERT)
    parser.add_argument("--full-symbolic", action="store_true")
    args = parser.parse_args(argv)
    with open(args.verify, encoding="utf-8") as handle:
        certificate = json.load(handle)
    checks = verify(certificate, full_symbolic=args.full_symbolic)
    for name, passed in checks.items():
        print(("[OK ] " if passed else "[FAIL] ") + name)
    failures = [name for name, passed in checks.items() if not passed]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT: %s" % ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
