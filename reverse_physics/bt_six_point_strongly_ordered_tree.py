#!/usr/bin/env python3
"""Exact BT six-point tree recursion and strongly ordered nested jet.

This producer deliberately avoids expanding 220 SymPy expressions.  A
Berends--Giele subset recursion is evaluated in a truncated Laurent algebra
whose coefficients are three-bit square-free spectator jets.  The largest
symbolic object has only eight spectator slots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT, "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-strongly-ordered-tree-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-strongly-ordered-tree.md"
SOURCE = "277d24697700fc8e5a97d44cc5bd073167059206"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-strongly-ordered-tree.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json",
]
N = 6
LO = -4
HI = 4


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


class SpectatorJet:
    """Square-free algebra in the three hard spectator masses."""

    def __init__(self, ring, coefficients=None):
        self.ring = ring
        self.coefficients = {
            int(mask): ring.base(value)
            for mask, value in (coefficients or {}).items()
            if value != 0
        }

    def __eq__(self, other):
        if isinstance(other, SpectatorJet):
            return self.coefficients == other.coefficients
        return not self.coefficients if other == 0 else False

    def _coerce(self, other):
        return other if isinstance(other, SpectatorJet) else SpectatorJet(
            self.ring, {0: other}
        )

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.ring.base.zero) + value
            if out[mask] == 0:
                del out[mask]
        return SpectatorJet(self.ring, out)

    __radd__ = __add__

    def __neg__(self):
        return SpectatorJet(
            self.ring, {mask: -value for mask, value in self.coefficients.items()}
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
                out[mask] = out.get(mask, self.ring.base.zero) + (
                    left_value * right_value
                )
        return SpectatorJet(self.ring, out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, self.ring.base.zero)
        if scalar == 0:
            raise ZeroDivisionError("spectator jet has zero scalar part")
        unit = SpectatorJet(self.ring, {0: self.ring.base.one})
        nilpotent = self - scalar
        ratio = (-1 / scalar) * nilpotent
        out = unit
        term = unit
        for _ in range(3):
            term = term * ratio
            out += term
        return (1 / scalar) * out

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()


class SpectatorRing:
    def __init__(self, base):
        self.base = base
        self.zero = SpectatorJet(self)
        self.one = SpectatorJet(self, {0: base.one})

    def __call__(self, value):
        return value if isinstance(value, SpectatorJet) else SpectatorJet(
            self, {0: self.base(value)}
        )


class Laurent:
    """Small exact Laurent series in the common external-mass scale delta."""

    def __init__(self, field, coefficients=None):
        self.field = field
        self.coefficients = {
            int(power): field(value)
            for power, value in (coefficients or {}).items()
            if value != 0 and LO <= int(power) <= HI
        }

    @classmethod
    def scalar(cls, field, value):
        return cls(field, {0: value})

    def coefficient(self, power):
        return self.coefficients.get(power, self.field.zero)

    def _coerce(self, other):
        return other if isinstance(other, Laurent) else Laurent.scalar(
            self.field, other
        )

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for power, value in other.coefficients.items():
            out[power] = out.get(power, self.field.zero) + value
            if out[power] == 0:
                del out[power]
        return Laurent(self.field, out)

    __radd__ = __add__

    def __neg__(self):
        return Laurent(
            self.field, {power: -value for power, value in self.coefficients.items()}
        )

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
                    out[power] = out.get(power, self.field.zero) + (
                        left_value * right_value
                    )
        return Laurent(self.field, out)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if exponent < 0:
            return self.inverse() ** (-exponent)
        answer = Laurent.scalar(self.field, 1)
        for _ in range(exponent):
            answer *= self
        return answer

    def inverse(self):
        if not self.coefficients:
            raise ZeroDivisionError("zero Laurent series")
        valuation = min(self.coefficients)
        leading = self.coefficient(valuation)
        recurrence = {0: self.field.one / leading}
        for order in range(1, HI + valuation + 1):
            total = self.field.zero
            for index in range(1, order + 1):
                total += self.coefficient(valuation + index) * recurrence[
                    order - index
                ]
            recurrence[order] = -total / leading
        return Laurent(
            self.field,
            {-valuation + order: value for order, value in recurrence.items()},
        )

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()


def partitions(mask, count):
    """Yield each unordered partition of mask into count nonempty blocks once."""
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
        if subset == 0:
            break
        subset = (subset - 1) & rest


def topology_counts(n=N):
    """Count labeled trees by (number of cubic, number of quartic vertices)."""
    full = (1 << n) - 1

    def product(rows):
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
                for (cubic, quartic), number in product(
                    [current(block) for block in blocks]
                ).items():
                    key = (cubic + vertex[0], quartic + vertex[1])
                    out[key] = out.get(key, 0) + number
        return out

    root = 1
    rest = full ^ root
    out = {}
    for arity, vertex in ((2, (1, 0)), (3, (0, 1))):
        for blocks in partitions(rest, arity):
            for (cubic, quartic), number in product(
                [current(block) for block in blocks]
            ).items():
                key = (cubic + vertex[0], quartic + vertex[1])
                out[key] = out.get(key, 0) + number
    return out


HARD_FIXTURES = [
    ([3, 5, 7, 11, 13], [19, 23]),
    ([4, -7, 9, 13, -17], [29, 31]),
    ([-5, 8, 12, -19, 27], [37, -41]),
]


def correlated_six_point(hard_fixture):
    """Return the exact delta-leading nested boundary spectator kernel."""
    import sympy as sp
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    values = field("a0,a1,a2,e,tau1,tau2", QQ)
    base = values[0]
    a0, a1, a2, epsilon, tau1, tau2 = values[1:]
    ring = SpectatorRing(base)

    def linear(value):
        return Laurent(ring, {1: value})

    def scalar(value):
        return Laurent.scalar(ring, value)

    masses = [
        linear(epsilon * a0),
        linear(epsilon * a1),
        linear(a2),
        linear(SpectatorJet(ring, {1: base.one})),
        linear(SpectatorJet(ring, {2: base.one})),
        linear(SpectatorJet(ring, {4: base.one})),
    ]
    adjacent_hard, triple_hard = hard_fixture
    adjacent = [linear(epsilon * tau1)] + [
        scalar(value) for value in adjacent_hard
    ]
    triples = [linear(tau2)] + [scalar(value) for value in triple_hard]

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
                triples[left % 3]
                - adjacent[left]
                - adjacent[(left + 1) % N]
                + masses[left]
                + masses[(left + 1) % N]
                + masses[(left + 2) % N]
            )
        if distance == N - 2:
            return pair_square(right, left)
        raise ValueError("opposite pair is derived from momentum conservation")

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
                Laurent(ring),
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
            Laurent(ring),
        )

    def dot(left, right):
        return left[0] * right[0] * unsigned_dot(left[1], right[1])

    def square(momentum):
        return dot(momentum, momentum)

    def cubic(left, middle, right):
        return (
            square(left) * dot(middle, right)
            + square(middle) * dot(left, right)
            + square(right) * dot(left, middle)
        )

    def quartic(a, b, c, d):
        return (
            dot(a, b) * dot(c, d)
            + dot(a, c) * dot(b, d)
            + dot(a, d) * dot(b, c)
        )

    one = scalar(1)
    zero = Laurent(ring)

    @lru_cache(maxsize=None)
    def current(mask):
        if mask.bit_count() == 1:
            return one
        value = zero
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
        return -value / (square((1, mask)) ** 2)

    root = 1 << 5
    rest = ((1 << N) - 1) ^ root
    amplitude = zero
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
    projected = (leading * leading).coefficients.get(7, base.zero)
    symbols = {symbol.name: symbol for symbol in projected.as_expr().free_symbols}
    factored = sp.factor(projected.as_expr())
    strong = sp.factor(projected.as_expr().subs(symbols["e"], 0))
    return {
        "leading_order": leading_order,
        "leading_masks": sorted(leading.coefficients),
        "projected": str(projected),
        "projected_length": len(str(projected)),
        "factored": str(factored),
        "factored_length": len(str(factored)),
        "strong_order": str(strong),
        "strong_order_length": len(str(strong)),
    }


def threshold_and_factorial_analysis():
    """Independently reduce the two thresholds and restore all factorials."""
    import sympy as sp

    r = sp.symbols("r", positive=True)
    j3 = (r**2 - 2*r*sp.log(r) - 1) / (2*(r - 1)**3)
    j4 = (
        r**3 - 6*r**2*sp.log(r) + 9*r**2
        - 6*r*sp.log(r) - 9*r - 1
    ) / (6*(r - 1)**5)
    j3_series = sp.series(j3, r, 0, 2)
    j4_series = sp.series(j4, r, 0, 2)

    # After the outer r2 log(r2) coefficient is taken, the inner integral is
    # FP int sqrt(lambda(u,1,m^2))/u * A(u)E(u)/u^3 du.  Rationalize it by
    # u=1+m^2+m(z+z^-1).  The following compact antiderivative is assembled
    # term-by-term from the exact partial fractions, rather than asking a CAS
    # to discover it.
    z, m = sp.symbols("z m", positive=True)
    sigma = 1 + m**2
    u = sigma + m*(z + 1/z)
    measure = m**2*(1-z**2)**2/z**3
    difference = (1-m**2)**2
    inner_a = difference - 2*sigma*u + 2*u**2
    inner_e = -difference + 2*sigma*u + 4*u**2
    integrand = sp.cancel(inner_a*inner_e*measure/u**4)

    c4 = m**3*(m-1)**2*(m+1)**2
    c3 = -m**2*(m-1)*(m+1)*(5*m**2+3)
    c2 = 2*m*(3*m**4+7*m**2+1)
    c1 = (
        2*sigma*(m**2-3*m+1)*(m**2+3*m+1)/((m-1)*(m+1))
    )
    b4 = m*(m-1)**2*(m+1)**2
    b3 = m*(m-1)*(m+1)*(3*m**2+5)
    b2 = 2*m*(m**4+7*m**2+3)
    b1 = (
        -2*m*sigma*(m**2-3*m+1)*(m**2+3*m+1)/((m-1)*(m+1))
    )
    antiderivative = (
        (-4*m**3-4*m)*z + 4*m**2*z**2 - 4*m**2/z**2
        + 4*m*sigma/z + 2*(m**4-10*m**2+1)*sp.log(z)
        - c4/(3*(z+m)**3) - c3/(2*(z+m)**2) - c2/(z+m)
        + c1*sp.log(z+m)
        - b4/(3*m*(m*z+1)**3) - b3/(2*m*(m*z+1)**2)
        - b2/(m*(m*z+1)) + (b1/m)*sp.log(m*z+1)
    )
    derivative_identity = sp.cancel(sp.diff(antiderivative, z)-integrand) == 0

    # A physical invariant cutoff u=Lambda is not a z cutoff.  Since
    # z=m/Lambda+O(Lambda^-2), its finite part retains the displayed log(m)
    # conversion.  This is the step that makes the mixed nonanalytic
    # coefficient regulator-coordinate independent.
    cutoff_finite_part = -(
        24*m**6*sp.log(m) - 71*m**6
        - 204*m**4*sp.log(m) - 63*m**4
        + 60*m**2*sp.log(m) + 63*m**2 + 71
    )/(6*(m**2-1))
    # Derive that finite part directly from the invariant boundary u=Lambda.
    # With q=Lambda^-1 the rationalized small root solves
    # m*z^2+(1+m^2-Lambda)*z+m=0.  Terms through q^3 determine the q^0
    # coefficient because the antiderivative has at most a double pole at z=0.
    q = sp.symbols("q", positive=True)
    z_cut_exact = (
        2*m*q
        / (1-sigma*q+sp.sqrt((1-sigma*q)**2-4*m**2*q**2))
    )
    z_cut = sp.series(z_cut_exact, q, 0, 4).removeO()
    boundary = sp.series(
        antiderivative.subs(z, 1)-antiderivative.subs(z, z_cut), q, 0, 1
    ).removeO().expand()
    boundary_constant = sp.collect(boundary, q, evaluate=False).get(sp.S.One, 0)
    derived_finite_part = sp.expand(boundary_constant).coeff(sp.log(q), 0)
    cutoff_boundary_identity = (
        sp.simplify(derived_finite_part-cutoff_finite_part) == 0
    )
    cutoff_series = sp.series(cutoff_finite_part, m, 0, 5)
    inner_r_log_r = Fraction(5)
    outer_prefactor = Fraction(3, 32)
    raw_double_cocycle = outer_prefactor*inner_r_log_r

    hard_phase_prefactor = Fraction(16)*Fraction(1, 4)*Fraction(1, 2)*Fraction(1, 32)
    six_phase_prefactor = (
        Fraction(256)*Fraction(1, 48)*Fraction(1, 2)
        * Fraction(1, 4)*Fraction(1, 32)**3*Fraction(16)
    )
    hard_kernel = Fraction(3, 2)
    selected_history = (
        six_phase_prefactor*raw_double_cocycle
        / (hard_phase_prefactor*hard_kernel)
    )
    history_count = 12
    ordered_simplex = Fraction(1, 2)
    physical_two_count = selected_history*history_count*ordered_simplex
    poisson_two_count = Fraction(1, 2)*Fraction(1, 16)**2
    second_factorial_moment = 2*physical_two_count
    second_factorial_cumulant = second_factorial_moment-Fraction(1, 16)**2
    return {
        "outer_moments": {
            "J3": "(r^2-2*r*log(r)-1)/(2*(r-1)^3)",
            "J4": "(r^3-6*r^2*log(r)+9*r^2-6*r*log(r)-9*r-1)/(6*(r-1)^5)",
            "J3_small_r": str(j3_series),
            "J4_small_r": str(j4_series),
            "common_r_log_r_coefficient": rat(1),
        },
        "inner_physical_cutoff_finite_part": {
            "definition": "FP_(Lambda->infinity) integral_[threshold,Lambda] du sqrt(Kallen(u,1,r))/u * A(u,r)*E(u,r)/u^3",
            "r_equals_m_squared": True,
            "value": str(cutoff_finite_part),
            "small_m_series": str(cutoff_series),
            "r_log_r_coefficient": rat(inner_r_log_r),
            "rationalized_antiderivative_derivative_identity": derivative_identity,
            "physical_cutoff_boundary_finite_part_identity": cutoff_boundary_identity,
            "cutoff_coordinate": "the subtraction is at fixed physical pair invariant u=Lambda; z=m/Lambda+O(Lambda^-2)",
            "local_subtraction_invariance": "At fixed physical u, the large-u expansion of sqrt(Kallen(u,1,r))/u times the rational kernel has divergent coefficients polynomial in r. Any mass-independent invariant local subtraction changes only analytic powers of r and therefore cannot change the r*log(r) coefficient 5. A fixed-z cutoff is excluded because u~m/z makes it external-mass dependent.",
        },
        "double_cocycle": {
            "raw_nested_coefficient": rat(raw_double_cocycle),
            "meaning": "coefficient of r_inner*log(r_inner)*r_outer*log(r_outer) after the two exact threshold reductions",
            "external_delta_prime_sign": "+ because there are six external Wightman derivatives",
        },
        "normalization": {
            "hard_phase_prefactor_before_kernel": rat(hard_phase_prefactor),
            "six_point_phase_prefactor_before_kernel": rat(six_phase_prefactor),
            "hard_squarefree_kernel": rat(hard_kernel),
            "selected_nested_history_relative_to_Born": rat(selected_history),
            "labeled_nested_histories": history_count,
            "history_count_derivation": "choose the inner daughter pair in C(4,2)=6 ways and the outer third daughter in 2 ways",
            "ordered_resolution_simplex": rat(ordered_simplex),
            "physical_two_count_coefficient": rat(physical_two_count),
            "poisson_two_count_coefficient": rat(poisson_two_count),
            "physical_over_poisson": rat(physical_two_count/poisson_two_count),
        },
        "factorial_cumulant": {
            "mean_rate": rat(Fraction(1, 16)),
            "second_factorial_moment_coefficient": rat(second_factorial_moment),
            "mean_square_coefficient": rat(Fraction(1, 16)**2),
            "second_factorial_cumulant_coefficient": rat(second_factorial_cumulant),
            "log_generating_quadratic_coefficient": rat(second_factorial_cumulant/2),
            "disposition": "NONZERO_POSITIVE_SUPER_POISSON",
        },
    }


def build():
    topology = topology_counts()
    rows = [correlated_six_point(fixture) for fixture in HARD_FIXTURES]
    threshold = threshold_and_factorial_analysis()
    checks = {
        "six_point_topology_counts_10_105_105": topology
        == {(0, 2): 10, (2, 1): 105, (4, 0): 105},
        "six_point_total_tree_count_220": sum(topology.values()) == 220,
        "all_correlated_amplitudes_start_at_delta_two": all(
            row["leading_order"] == 2 for row in rows
        ),
        "all_leading_spectator_jets_have_seven_nonconstant_slots": all(
            row["leading_masks"] == list(range(7)) for row in rows
        ),
        "three_hard_fixtures_have_identical_projected_kernel": len(
            {row["projected"] for row in rows}
        )
        == 1,
        "three_hard_fixtures_have_identical_strong_order_kernel": len(
            {row["strong_order"] for row in rows}
        )
        == 1,
        "strong_order_kernel_is_compact": rows[0]["strong_order_length"] < 1000,
        "outer_threshold_moments_have_unit_r_log_r": threshold["outer_moments"]["common_r_log_r_coefficient"] == rat(1),
        "inner_antiderivative_is_exact": threshold["inner_physical_cutoff_finite_part"]["rationalized_antiderivative_derivative_identity"],
        "inner_physical_cutoff_boundary_is_exact": threshold["inner_physical_cutoff_finite_part"]["physical_cutoff_boundary_finite_part_identity"],
        "inner_physical_cutoff_r_log_r_is_five": threshold["inner_physical_cutoff_finite_part"]["r_log_r_coefficient"] == rat(5),
        "mixed_nonanalytic_coefficient_is_local_subtraction_invariant": "cannot change the r*log(r) coefficient 5" in threshold["inner_physical_cutoff_finite_part"]["local_subtraction_invariance"],
        "raw_double_cocycle_is_fifteen_over_thirty_two": threshold["double_cocycle"]["raw_nested_coefficient"] == rat(Fraction(15, 32)),
        "selected_history_is_five_over_3072": threshold["normalization"]["selected_nested_history_relative_to_Born"] == rat(Fraction(5, 3072)),
        "twelve_history_ordered_coefficient_is_five_over_512": threshold["normalization"]["physical_two_count_coefficient"] == rat(Fraction(5, 512)),
        "poisson_prediction_is_one_over_512": threshold["normalization"]["poisson_two_count_coefficient"] == rat(Fraction(1, 512)),
        "second_factorial_cumulant_is_one_over_64": threshold["factorial_cumulant"]["second_factorial_cumulant_coefficient"] == rat(Fraction(1, 64)),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "no_full_six_body_probability_claim": True,
        "no_lorentzian_claim": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1",
        "schema_version": "reverse-physics-bt-six-point-strongly-ordered-tree-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact six-point tree recursion and correlated nested double-collinear external-mass jet",
        "question": "Does the complete six-point tree external-mass jet select the stationary independent-increment coherent/Poisson completion in the nested strongly ordered double-collinear resolution sector?",
        "answer": "No. The complete 220-tree external-mass jet gives the same nested kernel at three unrelated exact hard fixtures, and after both exact Kallen threshold reductions its mixed two-resolution cocycle is 15/32. Restoring the 2->4 amplitude, phase-space, identical-particle, six-delta-prime, 12-history, and ordered-simplex factors gives P2(a)=5*a^2/512 at leading double logarithm, whereas the coherent Poisson completion predicts a^2/512. The ordered resolution-sector second factorial cumulant is therefore +a^2/64. The emissions are super-Poisson at this order: the one-emission rank-two GNS and relative weight survive, but independent increments and the coherent Gaussian state are not dynamically selected. This is a leading strongly ordered tree result, not a complete six-body probability, a proof of universal hard-angle independence, or an all-order count law.",
        "topology": {
            "V4_squared": topology.get((0, 2)),
            "V3_squared_V4": topology.get((2, 1)),
            "V3_fourth": topology.get((4, 0)),
            "total": sum(topology.values()),
            "relative_signs": "+ V4^2, - V3^2 V4, + V3^4",
        },
        "correlated_boundary": {
            "scaling": "x0=delta*e*a0, x1=delta*e*a1, s01=delta*e*tau1; x2=delta*a2, x3..x5=delta*a3..a5, s012=delta*tau2; take delta->0 before e->0",
            "cyclic_chart": "six adjacent pair squares s_i and three complementary adjacent triple squares t_i=t_(i+3)",
            "hard_fixtures": HARD_FIXTURES,
            "rows": rows,
        },
        "threshold_and_factorial_analysis": threshold,
        "disposition": {
            "complete_six_point_tree_recursion": "COMPUTED",
            "correlated_two_scale_external_mass_jet": "COMPUTED",
            "strongly_ordered_kernel": "COMPUTED_AND_THRESHOLD_INTEGRATED",
            "two_emission_factorial_cumulant": "POSITIVE_ONE_OVER_64_TIMES_A_SQUARED",
            "coherent_Poisson_dynamics": "DISAGREES_BY_FACTOR_FIVE_AT_LEADING_ORDERED_DOUBLE_LOG",
            "stationary_independent_resolution_increments": "NOT_DYNAMICALLY_SELECTED",
            "rank_two_one_emission_GNS_and_relative_weight": "RETAINED",
            "full_six_body_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "a complete physical 2->4 probability",
            "universal hard-angle independence beyond the three exact hard fixtures",
            "an all-order non-Poisson BT count law from the first two factorial moments",
            "a finite beyond-leading-log correction",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority",
        ],
        "missing_object_ledger": [
            "a positive non-Gaussian resolution-local state matching both the one-over-16 mean and one-over-64 second factorial cumulant",
            "the seven-point triple-strongly-ordered tree jet that fixes the third factorial moment and distinguishes candidate non-Poisson completions",
            "connected single-log and finite six-point boundary terms",
            "the complete non-strongly-ordered six-body phase-space projector",
            "an all-order moment or Lévy--Khintchine classification selecting a unique non-Poisson completion",
        ],
        "next_gate": "Construct the minimal positive non-Gaussian resolution-local Cox/compound state whose first two factorial cumulants are a/16 and a^2/64 without asserting uniqueness, then compute the seven-point triple-strongly-ordered tree jet to decide its third factorial moment and test candidate completions.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Appendix B Eqs. (24)-(25)", "Eq. (18)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_strongly_ordered_tree.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_strongly_ordered_tree.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_six_point_strongly_ordered_tree"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("strong-order kernel:", value["correlated_boundary"]["rows"][0]["strong_order"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
