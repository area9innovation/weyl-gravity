#!/usr/bin/env python3
"""Independent verifier for the BT seven-point Cox-selection result.

The producer sums cached dot-product subset currents over a rational-function
field.  This verifier uses exact rational parameters, explicitly retains every
rooted tree value, and evaluates cubic vertices through the invariant triangle
polynomial.  It does not import the producer.
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
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-seven-point-cox-selection-v1.schema.json",
)
N = 7
LO = -6
HI = 4
POINTS = [
    (1, 4, 9, 16, Fraction(1, 5), Fraction(2, 7), 10, 17, 26),
    (2, 7, 5, 11, Fraction(2, 9), Fraction(3, 8), 13, 23, 31),
    (4, 1, 11, 6, Fraction(3, 11), Fraction(1, 4), 19, 29, 43),
]


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


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
            out[mask] = out.get(mask, Fraction(0))+value
            if not out[mask]:
                del out[mask]
        return Jet(out)

    __radd__ = __add__

    def __neg__(self):
        return Jet({mask: -value for mask, value in self.coefficients.items()})

    def __sub__(self, other):
        return self+(-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other)-self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_mask, left_value in self.coefficients.items():
            for right_mask, right_value in other.coefficients.items():
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                out[mask] = out.get(mask, Fraction(0))+left_value*right_value
        return Jet(out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, Fraction(0))
        if not scalar:
            raise ZeroDivisionError("noninvertible spectator jet")
        unit = Jet({0: 1})
        ratio = -Fraction(1, 1)/scalar*(self-scalar)
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
            out[power] = out.get(power, Jet())+value
            if out[power] == 0:
                del out[power]
        return Series(out)

    __radd__ = __add__

    def __neg__(self):
        return Series({power: -value for power, value in self.coefficients.items()})

    def __sub__(self, other):
        return self+(-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other)-self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_power, left_value in self.coefficients.items():
            for right_power, right_value in other.coefficients.items():
                power = left_power+right_power
                if LO <= power <= HI:
                    out[power] = out.get(power, Jet())+left_value*right_value
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
    """Enumerate all 2,485 rooted tree values at one exact parameter point."""
    a0, a1, a2, a3, e1, e2, tau1, tau2, tau3 = map(Fraction, parameters)
    adjacent_hard, triple_hard = hard_fixture

    def linear(value):
        return Series({1: value})

    masses = [
        linear(e1*e2*a0), linear(e1*e2*a1), linear(e2*a2), linear(a3),
        linear(Jet({1: 1})), linear(Jet({2: 1})), linear(Jet({4: 1})),
    ]
    adjacent = [linear(e1*e2*tau1)] + [
        Series.scalar(Fraction(value)) for value in adjacent_hard
    ]
    triples = [linear(e2*tau2), None, None, None, linear(tau3), None, None]
    hard_values = iter(triple_hard)
    triples = [
        Series.scalar(Fraction(next(hard_values))) if value is None else value
        for value in triples
    ]

    @lru_cache(maxsize=None)
    def pair_square(left, right):
        if left == right:
            return masses[left]
        distance = (right-left) % N
        if distance == 1:
            return adjacent[left]
        if distance == N-1:
            return adjacent[right]
        if distance == 2:
            return (
                triples[left]-adjacent[left]-adjacent[(left+1) % N]
                + masses[left]+masses[(left+1) % N]+masses[(left+2) % N]
            )
        if distance == N-2:
            return pair_square(right, left)
        if distance == 3:
            indices = [left, (left+1) % N, (left+2) % N, (left+3) % N]
            quartet = triples[(left+4) % N]
            known = sum(
                (
                    pair_square(indices[p], indices[q])
                    for p in range(4) for q in range(p+1, 4)
                    if (p, q) != (0, 3)
                ),
                Series(),
            )
            return quartet+2*sum((masses[index] for index in indices), Series())-known
        if distance == N-3:
            return pair_square(right, left)
        raise ValueError((left, right, distance))

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return masses[left]
        return (pair_square(left, right)-masses[left]-masses[right])/2

    @lru_cache(maxsize=None)
    def unsigned_dot(left_mask, right_mask):
        return sum(
            (
                basis_dot(left, right)
                for left in range(N) if left_mask & (1 << left)
                for right in range(N) if right_mask & (1 << right)
            ),
            Series(),
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
            for left_term, right_term in itertools.product(
                current_terms(left), current_terms(right)
            ):
                rows.append(-vertex*left_term*right_term/propagator)
        for a, b, c in partitions(mask, 3):
            vertex = quartic((1, a), (1, b), (1, c), (-1, mask))
            for terms in itertools.product(
                current_terms(a), current_terms(b), current_terms(c)
            ):
                rows.append(-vertex*terms[0]*terms[1]*terms[2]/propagator)
        return tuple(rows)

    root = 1 << 6
    rest = root-1
    trees = []
    for left, right in partitions(rest, 2):
        vertex = cubic((1, root), (1, left), (1, right))
        for left_term, right_term in itertools.product(
            current_terms(left), current_terms(right)
        ):
            trees.append(-vertex*left_term*right_term)
    for a, b, c in partitions(rest, 3):
        vertex = quartic((1, root), (1, a), (1, b), (1, c))
        for terms in itertools.product(
            current_terms(a), current_terms(b), current_terms(c)
        ):
            trees.append(-vertex*terms[0]*terms[1]*terms[2])
    amplitude = sum(trees, Series())
    leading_order = min(amplitude.coefficients)
    leading = amplitude.coefficient(leading_order)
    projected = (leading*leading).coefficients.get(7, Fraction(0))
    if return_leading:
        return leading_order, len(trees), projected, leading
    return leading_order, len(trees), projected


def independent_symbolic_checks(certificate):
    import sympy as sp

    a0, a1, a2, a3, tau1, tau2, tau3 = sp.symbols(
        "a0 a1 a2 a3 tau1 tau2 tau3"
    )
    aa = (a0-a1)**2-2*tau1*(a0+a1)+2*tau1**2
    bb = a2*aa+2*tau2*(-aa+3*tau1**2)
    cc = a2*bb+2*tau2**2*(aa+tau1**2)
    dd = a3*cc+2*tau3*(-cc+3*tau2**2*aa)
    expected_kernel = sp.cancel(3*a3**3*cc*dd/(128*tau1**4*tau2**4*tau3**3))
    recorded_kernel = sp.sympify(
        certificate["correlated_boundary"]["rows"][0]["strong_order"]
    )

    outer = sp.expand(cc*(-cc+6*tau2**2*aa))
    middle = sp.factor(sum(outer.coeff(tau2, power) for power in range(5)).subs(a2, 1))
    inner = sp.factor((aa+8*tau1**2)*(5*aa-8*tau1**2))

    z, m = sp.symbols("z m", positive=True)
    sigma = 1+m**2
    u = sigma+m*(z+1/z)
    measure = m**2*(1-z**2)**2/z**3
    difference = (1-m**2)**2
    inner_a = difference-2*sigma*u+2*u**2
    integrand = sp.cancel(
        (inner_a+8*u**2)*(5*inner_a-8*u**2)*measure/u**4
    )
    # Method-distinct from the producer's residue() calls: use the explicit
    # derivative formula for a pole of known order.
    def pole_residue(expression, point, order):
        if order <= 0:
            return sp.S.Zero
        regular = sp.cancel((z-point)**order*expression)
        return sp.factor(
            sp.limit(
                sp.diff(regular, z, order-1)/sp.factorial(order-1),
                z,
                point,
            )
        )

    residue_zero = pole_residue(integrand, 0, 3)
    residue_minus_m = pole_residue(integrand, -m, 4)
    log_coefficient = sp.factor(-(residue_zero+residue_minus_m))
    r_log = sp.expand(sp.series(log_coefficient, m, 0, 3).removeO()).coeff(m, 2)/2

    universal = []
    for power in range(1, 6):
        moment_integrand = sp.cancel(measure/u**power)
        r0 = pole_residue(moment_integrand, 0, max(3-power, 0))
        rm = pole_residue(moment_integrand, -m, power)
        coefficient = sp.series(-(r0+rm), m, 0, 3).removeO().expand()
        universal.append(coefficient.coeff(m, 2)/2)
    return {
        "recursive_kernel": sp.cancel(recorded_kernel-expected_kernel) == 0,
        "middle_reduction": sp.expand(middle-inner) == 0,
        "inner_physical_cutoff_r_log": r_log == -27,
        "J1_through_J5_unit_r_log": universal == [1]*5,
    }


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    boundary = certificate.get("correlated_boundary", {})
    threshold = certificate.get("threshold_analysis", {})
    normalization = threshold.get("normalization", {})
    factorial = threshold.get("factorial_data", {})
    cox = certificate.get("cox_completion", {})
    disposition = certificate.get("disposition", {})
    rows = boundary.get("rows", [])
    projected_text = boundary.get("projected_expression", "")
    atom = cox.get("minimal_two_atom_cox_candidate", {})
    preflight = (
        not errors
        and certificate.get("topology", {}).get("total") == 2485
        and len(rows) == 2
        and len({row.get("projected_sha256") for row in rows}) == 1
        and text_sha256(projected_text) == boundary.get("projected_expression_sha256") == rows[0].get("projected_sha256")
        and frac(threshold.get("inner_reduction", {}).get("r_log_r_coefficient", {"numerator": 0, "denominator": 1})) == -27
        and frac(normalization.get("signed_raw_triple_cocycle", {"numerator": 0, "denominator": 1})) == Fraction(81, 128)
        and frac(normalization.get("leading_three_count_coefficient", {"numerator": 0, "denominator": 1})) == Fraction(9, 8192)
        and frac(factorial.get("third_factorial_cumulant_coefficient", {"numerator": 0, "denominator": 1})) == Fraction(7, 2048)
        and disposition.get("gamma_cox_completion") == "RULED_OUT"
        and disposition.get("minimal_two_atom_cox_state") == "CONSTRUCTED_THROUGH_THREE_MOMENTS"
        and disposition.get("unique_all_order_count_law") == "NOT_SELECTED"
        and disposition.get("complete_five_body_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
        and "universal hard-angle independence beyond the exact producer and verifier fixtures" in certificate.get("does_not_establish", [])
        and len(atom.get("support", [])) == len(atom.get("weights", [])) == 2
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    projected_hash_ok = text_sha256(projected_text) == boundary.get(
        "projected_expression_sha256"
    ) == rows[0].get("projected_sha256")
    names = "a0 a1 a2 a3 e1 e2 tau1 tau2 tau3".split()
    symbols = sp.symbols(" ".join(names))
    expression = sp.sympify(projected_text, locals=dict(zip(names, symbols)))
    hard_fixture = boundary.get("independent_verifier_hard_fixture")
    amplitude_ok = True
    tree_counts = set()
    for point in POINTS:
        expected = sp.cancel(expression.subs(dict(zip(symbols, point))))
        expected_fraction = Fraction(int(sp.numer(expected)), int(sp.denom(expected)))
        order, count, value = exact_tree_kernel(point, hard_fixture)
        tree_counts.add(count)
        amplitude_ok &= order == 2 and value == expected_fraction

    symbolic = independent_symbolic_checks(certificate)
    hard_phase = Fraction(1, 16)
    hard_kernel = Fraction(3, 2)
    seven_phase = (
        Fraction(1024)*Fraction(1, 240)*Fraction(1, 2)
        * Fraction(1, 8)*Fraction(1, 32)**4*Fraction(64)
    )
    signed_raw = Fraction(81, 128)
    selected = seven_phase*signed_raw/(hard_phase*hard_kernel)
    p3 = selected*60*Fraction(1, 6)
    m1, m2, m3 = Fraction(1, 16), Fraction(5, 256), 6*p3
    kappa3 = m3-3*m2*m1+2*m1**3
    lower = m2*m2/m1

    root = sp.sqrt(113)
    support = [(11-root)/64, (11+root)/64]
    weights = [(root+7)/(2*root), (root-7)/(2*root)]
    moments = [
        sp.simplify(sum(weights[index]*support[index]**power for index in range(2)))
        for power in range(1, 4)
    ]
    stored_support = [sp.sympify(value) for value in atom.get("support", [])]
    stored_weights = [sp.sympify(value) for value in atom.get("weights", [])]
    stored_moments = [
        sp.simplify(
            sum(
                stored_weights[index]*stored_support[index]**power
                for index in range(2)
            )
        )
        for power in range(1, 4)
    ]
    checks = {
        "schema": not errors,
        "identity_tags_lifecycle": certificate.get("certificate") == "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1" and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"] and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED",
        "projected_expression_hash": projected_hash_ok,
        "independent_explicit_2485_tree_fixture": amplitude_ok and tree_counts == {2485},
        "recursive_kernel": symbolic["recursive_kernel"],
        "middle_reduction": symbolic["middle_reduction"],
        "inner_physical_cutoff_r_log": symbolic["inner_physical_cutoff_r_log"],
        "J1_through_J5_unit_r_log": symbolic["J1_through_J5_unit_r_log"],
        "normalization": seven_phase == Fraction(1, 61440) and selected == Fraction(9, 81920) and p3 == Fraction(9, 8192),
        "factorial_cumulant": m3 == Fraction(27, 4096) and kappa3 == Fraction(7, 2048),
        "cox_stieltjes_bound": m3 >= lower and lower == Fraction(25, 4096),
        "gamma_cox_rejection": frac(cox["gamma_cox_candidate"]["third_rate_moment"]) == Fraction(45, 4096) and frac(cox["gamma_cox_candidate"]["tree_over_gamma_P3"]) == Fraction(3, 5),
        "two_atom_moments": stored_support == support and stored_weights == weights and moments == stored_moments == [sp.Rational(1, 16), sp.Rational(5, 256), sp.Rational(27, 4096)],
        "next_two_atom_prediction": frac(cox["minimal_two_atom_cox_candidate"]["next_fourth_rate_moment"]) == Fraction(73, 32768),
        "claim_boundary": disposition.get("unique_all_order_count_law") == "NOT_SELECTED" and disposition.get("complete_five_body_probability") == "NOT_CONSTRUCTED" and disposition.get("Eq19_all_orders") == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", []),
        "hashes": len(certificate.get("provenance", {}).get("inputs", [])) == 3 and all(row.get("sha256") == sha256(row.get("path", "")) for row in certificate.get("provenance", {}).get("inputs", [])),
        "producer_checks": certificate.get("checks", {}).get("passed") == certificate.get("checks", {}).get("total") == 18 and certificate.get("checks", {}).get("failures") == [] and all(certificate.get("checks", {}).get("details", {}).values()),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print("[%-3s] %s" % ("OK" if ok else "BAD", name))
    passed = sum(bool(value) for value in checks.values())
    print("checks %d/%d" % (passed, len(checks)))
    ok = passed == len(checks)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
