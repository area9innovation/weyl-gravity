#!/usr/bin/env python3
"""Independent verifier for the BT six-point strongly ordered tree result.

The producer sums cached subset currents with dot-product cubic vertices over a
rational-function field.  This verifier instead enumerates all rooted labeled
trees explicitly, uses the invariant triangle polynomial for every cubic
vertex, and checks the recorded symbolic kernel at exact rational points.
"""
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


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-strongly-ordered-tree-v1.schema.json")
N = 6
LO = -4
HI = 4


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
                out[mask] = out.get(mask, Fraction(0)) + left_value*right_value
        return Jet(out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, Fraction(0))
        if not scalar:
            raise ZeroDivisionError("noninvertible spectator jet")
        unit = Jet({0: 1})
        ratio = (-Fraction(1, 1)/scalar)*(self-scalar)
        out = unit
        power = unit
        for _ in range(3):
            power *= ratio
            out += power
        return Fraction(1, 1)/scalar*out

    def __truediv__(self, other):
        return self*self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other)*self.inverse()


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
        return self._coerce(other)-self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_power, left_value in self.coefficients.items():
            for right_power, right_value in other.coefficients.items():
                power = left_power+right_power
                if LO <= power <= HI:
                    out[power] = out.get(power, Jet()) + left_value*right_value
        return Series(out)

    __rmul__ = __mul__

    def inverse(self):
        valuation = min(self.coefficients)
        leading = self.coefficient(valuation)
        recurrence = {0: 1/leading}
        for order in range(1, HI+valuation+1):
            total = Jet()
            for index in range(1, order+1):
                total += self.coefficient(valuation+index)*recurrence[order-index]
            recurrence[order] = -total/leading
        return Series({-valuation+order: value for order, value in recurrence.items()})

    def __truediv__(self, other):
        return self*self._coerce(other).inverse()


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
        if remainder.bit_count() >= count-1:
            for tail in partitions(remainder, count-1):
                yield (block,)+tail
        if not subset:
            break
        subset = (subset-1)&rest


def exact_tree_kernel(parameters, hard_fixture, return_leading=False):
    """Enumerate, rather than recursively sum, all 220 tree values."""
    a0, a1, a2, epsilon, tau1, tau2 = map(Fraction, parameters)
    adjacent_hard, triple_hard = hard_fixture

    def linear(value):
        return Series({1: value})

    masses = [
        linear(epsilon*a0), linear(epsilon*a1), linear(a2),
        linear(Jet({1: 1})), linear(Jet({2: 1})), linear(Jet({4: 1})),
    ]
    adjacent = [linear(epsilon*tau1)] + [Series.scalar(Fraction(v)) for v in adjacent_hard]
    triples = [linear(tau2)] + [Series.scalar(Fraction(v)) for v in triple_hard]

    @lru_cache(maxsize=None)
    def pair_square(left, right):
        if left == right:
            return masses[left]
        distance = (right-left) % N
        if distance == 1:
            return adjacent[left]
        if distance == 5:
            return adjacent[right]
        if distance == 2:
            return (triples[left % 3]-adjacent[left]-adjacent[(left+1) % N]
                    +masses[left]+masses[(left+1) % N]+masses[(left+2) % N])
        if distance == 4:
            return pair_square(right, left)
        raise ValueError("opposite")

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return masses[left]
        if (right-left) % N == 3:
            return -masses[left]-sum(
                (basis_dot(left, index) for index in range(N)
                 if index not in (left, right)), Series()
            )
        return (pair_square(left, right)-masses[left]-masses[right])/2

    @lru_cache(maxsize=None)
    def unsigned_dot(left_mask, right_mask):
        return sum(
            (basis_dot(i, j) for i in range(N) if left_mask & (1 << i)
             for j in range(N) if right_mask & (1 << j)), Series()
        )

    def dot(left, right):
        return left[0]*right[0]*unsigned_dot(left[1], right[1])

    def square(momentum):
        return dot(momentum, momentum)

    def cubic(a, b, c):
        za, zb, zc = square(a), square(b), square(c)
        return (za*za+zb*zb+zc*zc-2*za*zb-2*za*zc-2*zb*zc)/2

    def quartic(a, b, c, d):
        return dot(a, b)*dot(c, d)+dot(a, c)*dot(b, d)+dot(a, d)*dot(b, c)

    @lru_cache(maxsize=None)
    def current_terms(mask):
        if mask.bit_count() == 1:
            return (Series.scalar(1),)
        propagator = square((1, mask))*square((1, mask))
        rows = []
        for left, right in partitions(mask, 2):
            vertex = cubic((1, left), (1, right), (-1, mask))
            for lterm, rterm in itertools.product(current_terms(left), current_terms(right)):
                rows.append(-vertex*lterm*rterm/propagator)
        for a, b, c in partitions(mask, 3):
            vertex = quartic((1, a), (1, b), (1, c), (-1, mask))
            for terms in itertools.product(current_terms(a), current_terms(b), current_terms(c)):
                rows.append(-vertex*terms[0]*terms[1]*terms[2]/propagator)
        return tuple(rows)

    root = 1 << 5
    rest = 31
    trees = []
    topology = {(4, 0): 0, (2, 1): 0, (0, 2): 0}
    # Counts are recovered independently from the number and arities of terms;
    # the value list itself is the check used below.
    for left, right in partitions(rest, 2):
        vertex = cubic((1, root), (1, left), (1, right))
        for lterm, rterm in itertools.product(current_terms(left), current_terms(right)):
            trees.append(-vertex*lterm*rterm)
    for a, b, c in partitions(rest, 3):
        vertex = quartic((1, root), (1, a), (1, b), (1, c))
        for terms in itertools.product(current_terms(a), current_terms(b), current_terms(c)):
            trees.append(-vertex*terms[0]*terms[1]*terms[2])
    amplitude = sum(trees, Series())
    leading_order = min(amplitude.coefficients)
    leading = amplitude.coefficient(leading_order)
    projected = (leading*leading).coefficients.get(7, Fraction(0))
    if return_leading:
        return leading_order, len(trees), projected, leading
    return leading_order, len(trees), projected


POINTS = [
    (1, 4, 9, Fraction(1, 5), 10, 17),
    (2, 7, 5, Fraction(2, 7), 13, 23),
    (4, 1, 11, Fraction(3, 8), 19, 29),
    (9, 16, 3, Fraction(1, 3), 31, 43),
]


def independent_threshold_checks():
    import sympy as sp

    z, m = sp.symbols("z m", positive=True)
    sigma = 1+m**2
    u = sigma+m*(z+1/z)
    measure = m**2*(1-z**2)**2/z**3
    difference = (1-m**2)**2
    aa = difference-2*sigma*u+2*u**2
    ee = -difference+2*sigma*u+4*u**2
    integrand = sp.cancel(aa*ee*measure/u**4)
    apart = sp.apart(integrand, z)
    expected_log_residue = 2*(m**4-10*m**2+1)
    log_residue = sp.residue(apart, z, 0)

    c4 = m**3*(m-1)**2*(m+1)**2
    c3 = -m**2*(m-1)*(m+1)*(5*m**2+3)
    c2 = 2*m*(3*m**4+7*m**2+1)
    c1 = 2*sigma*(m**2-3*m+1)*(m**2+3*m+1)/((m-1)*(m+1))
    b4 = m*(m-1)**2*(m+1)**2
    b3 = m*(m-1)*(m+1)*(3*m**2+5)
    b2 = 2*m*(m**4+7*m**2+3)
    b1 = -2*m*sigma*(m**2-3*m+1)*(m**2+3*m+1)/((m-1)*(m+1))
    anti = ((-4*m**3-4*m)*z+4*m**2*z**2-4*m**2/z**2+4*m*sigma/z
            +2*(m**4-10*m**2+1)*sp.log(z)
            -c4/(3*(z+m)**3)-c3/(2*(z+m)**2)-c2/(z+m)+c1*sp.log(z+m)
            -b4/(3*m*(m*z+1)**3)-b3/(2*m*(m*z+1)**2)-b2/(m*(m*z+1))
            +(b1/m)*sp.log(m*z+1))
    finite = -(24*m**6*sp.log(m)-71*m**6-204*m**4*sp.log(m)-63*m**4
               +60*m**2*sp.log(m)+63*m**2+71)/(6*(m**2-1))
    # Independently recover the finite term from the small root of u=Lambda,
    # instead of accepting the serialized expression as a second input.
    q = sp.symbols("q", positive=True)
    z_cut_exact = 2*m*q/(1-sigma*q+sp.sqrt((1-sigma*q)**2-4*m**2*q**2))
    z_cut = sp.series(z_cut_exact, q, 0, 4).removeO()
    boundary = sp.series(anti.subs(z, 1)-anti.subs(z, z_cut), q, 0, 1).removeO().expand()
    boundary_constant = sp.collect(boundary, q, evaluate=False).get(sp.S.One, 0)
    derived_finite = sp.expand(boundary_constant).coeff(sp.log(q), 0)
    series = sp.series(finite, m, 0, 3)
    return {
        "partial_fraction_log_residue": sp.factor(log_residue-expected_log_residue) == 0,
        "manual_antiderivative": sp.cancel(sp.diff(anti, z)-integrand) == 0,
        "physical_cutoff_boundary": sp.simplify(derived_finite-finite) == 0,
        "physical_cutoff_series": series == sp.Rational(71, 6)+m**2*(10*sp.log(m)+sp.Rational(67, 3))+sp.Order(m**3),
    }


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    rows = certificate.get("correlated_boundary", {}).get("rows", [])
    analysis = certificate.get("threshold_and_factorial_analysis", {})
    normalization = analysis.get("normalization", {})
    cumulant = analysis.get("factorial_cumulant", {})
    disposition = certificate.get("disposition", {})
    # Mutation tests should not pay for the 220-tree rail when a serialized
    # theorem constant or claim boundary is already wrong.  A valid payload
    # crosses this gate and still runs every independent calculation below.
    preflight = (
        not errors
        and certificate.get("topology", {}).get("total") == 220
        and len(rows) == 3
        and len({row.get("projected") for row in rows}) == 1
        and frac(analysis.get("double_cocycle", {}).get("raw_nested_coefficient", {"numerator": 0, "denominator": 1})) == Fraction(15, 32)
        and normalization.get("labeled_nested_histories") == 12
        and frac(cumulant.get("second_factorial_cumulant_coefficient", {"numerator": 0, "denominator": 1})) == Fraction(1, 64)
        and disposition.get("coherent_Poisson_dynamics") == "DISAGREES_BY_FACTOR_FIVE_AT_LEADING_ORDERED_DOUBLE_LOG"
        and disposition.get("full_six_body_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
        and "universal hard-angle independence beyond the three exact hard fixtures" in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}
    symbols = sp.symbols("a0 a1 a2 e tau1 tau2")
    symbolic = sp.sympify(rows[0]["projected"], locals=dict(zip(("a0","a1","a2","e","tau1","tau2"), symbols)))
    hard_fixtures = certificate.get("correlated_boundary", {}).get("hard_fixtures", [])
    amplitude_ok = len(rows) == 3 and len(hard_fixtures) == 3
    tree_counts = set()
    for point in POINTS:
        expected = sp.cancel(symbolic.subs(dict(zip(symbols, point))))
        expected_fraction = Fraction(int(sp.numer(expected)), int(sp.denom(expected)))
        for hard in hard_fixtures:
            order, count, value = exact_tree_kernel(point, hard)
            tree_counts.add(count)
            amplitude_ok &= order == 2 and value == expected_fraction

    thresholds = independent_threshold_checks()
    selected = Fraction(5, 3072)
    physical = 12*Fraction(1, 2)*selected
    poisson = Fraction(1, 2)*Fraction(1, 16)**2
    checks = {
        "schema": not errors,
        "identity_tags_lifecycle": certificate.get("certificate") == "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1" and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"] and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED",
        "independent_explicit_220_tree_fixtures": amplitude_ok and tree_counts == {220},
        "recorded_hard_fixture_independence": len({row["projected"] for row in rows}) == 1 and len({row["strong_order"] for row in rows}) == 1,
        "partial_fraction_log_residue": thresholds["partial_fraction_log_residue"],
        "manual_inner_antiderivative": thresholds["manual_antiderivative"],
        "physical_invariant_cutoff_boundary": thresholds["physical_cutoff_boundary"] and analysis.get("inner_physical_cutoff_finite_part", {}).get("physical_cutoff_boundary_finite_part_identity") is True,
        "physical_invariant_cutoff_series": thresholds["physical_cutoff_series"],
        "local_subtraction_boundary": "cannot change the r*log(r) coefficient 5" in analysis.get("inner_physical_cutoff_finite_part", {}).get("local_subtraction_invariance", ""),
        "raw_double_cocycle": frac(analysis.get("double_cocycle", {}).get("raw_nested_coefficient")) == Fraction(15, 32),
        "selected_history_normalization": frac(normalization.get("selected_nested_history_relative_to_Born")) == selected,
        "history_and_simplex_normalization": normalization.get("labeled_nested_histories") == 12 and frac(normalization.get("ordered_resolution_simplex")) == Fraction(1, 2) and frac(normalization.get("physical_two_count_coefficient")) == physical,
        "poisson_factor_five_disagreement": frac(normalization.get("poisson_two_count_coefficient")) == poisson and frac(normalization.get("physical_over_poisson")) == 5,
        "factorial_cumulant": frac(cumulant.get("second_factorial_moment_coefficient")) == Fraction(5, 256) and frac(cumulant.get("second_factorial_cumulant_coefficient")) == Fraction(1, 64) and cumulant.get("disposition") == "NONZERO_POSITIVE_SUPER_POISSON",
        "claim_boundary": certificate.get("disposition", {}).get("coherent_Poisson_dynamics") == "DISAGREES_BY_FACTOR_FIVE_AT_LEADING_ORDERED_DOUBLE_LOG" and certificate.get("disposition", {}).get("full_six_body_probability") == "NOT_CONSTRUCTED" and certificate.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", []) and "universal hard-angle independence beyond the three exact hard fixtures" in certificate.get("does_not_establish", []),
        "hashes": len(certificate.get("provenance", {}).get("inputs", [])) == 5 and all(row.get("sha256") == sha256(row.get("path", "")) for row in certificate.get("provenance", {}).get("inputs", [])),
        "producer_checks": certificate.get("checks", {}).get("passed") == certificate.get("checks", {}).get("total") == 20 and certificate.get("checks", {}).get("failures") == [] and all(certificate.get("checks", {}).get("details", {}).values()),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    certificate = load(args.verify)
    checks = verify(certificate)
    for name, ok in checks.items():
        print(("[OK ] " if ok else "[FAIL] ")+name)
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (len(checks)-len(failures), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
