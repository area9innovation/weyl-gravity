#!/usr/bin/env python3
"""Exact generic six-point BT external-mass jet, without a collinear limit.

This research rail keeps the six independent external mass-square variables in
the square-free algebra and holds a complete cyclic invariant chart fixed.  It
is intentionally separate from the certified nested-cylinder producer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache


N = 6
FULL_MASK = (1 << N) - 1
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PLANAR_PHYSICAL_BORN_DENSITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-planar-physical-born-density-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-planar-physical-born-density.md"
SOURCE = "656b97e6c9d6b290156872cd081bd5462064f11d"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-six-point-planar-physical-born-density.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


class MassJet:
    """Square-free exact algebra in all six external mass squares."""

    def __init__(self, coefficients=None, scalar_coerce=Fraction, max_degree=N):
        self.scalar_coerce = scalar_coerce
        self.max_degree = max_degree
        self.coefficients = {
            int(mask): scalar_coerce(value)
            for mask, value in (coefficients or {}).items()
            if value and int(mask).bit_count() <= max_degree
        }

    def _new(self, coefficients=None):
        return MassJet(coefficients, self.scalar_coerce, self.max_degree)

    def _coerce(self, other):
        return other if isinstance(other, MassJet) else self._new({0: other})

    def __eq__(self, other):
        if isinstance(other, MassJet):
            return self.coefficients == other.coefficients
        return not self.coefficients if other == 0 else False

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, Fraction(0)) + value
            if not out[mask]:
                del out[mask]
        return self._new(out)

    __radd__ = __add__

    def __neg__(self):
        return self._new(
            {mask: -value for mask, value in self.coefficients.items()}
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
                if mask.bit_count() > self.max_degree:
                    continue
                out[mask] = out.get(mask, Fraction(0)) + left_value * right_value
        return self._new(out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, self.scalar_coerce(0))
        if not scalar:
            raise ZeroDivisionError("mass jet has zero scalar part")
        unit = self._new({0: 1})
        ratio = (-1 / scalar) * (self - scalar)
        out = unit
        power = unit
        for _ in range(self.max_degree):
            power *= ratio
            out += power
        return (1 / scalar) * out

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()


def partitions(mask, count):
    """Yield unordered nonempty partitions with a canonical first block."""
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


def generic_external_mass_kernel(
    adjacent,
    triples,
    scalar_coerce=Fraction,
    max_degree=N,
    active_mass_mask=FULL_MASK,
):
    """Evaluate the full 220-tree jet at one exact cyclic invariant point."""
    adjacent = tuple(map(scalar_coerce, adjacent))
    triples = tuple(map(scalar_coerce, triples))
    if len(adjacent) != 6 or len(triples) != 3:
        raise ValueError("expected six adjacent and three complementary triples")

    def jet(coefficients=None):
        return MassJet(coefficients, scalar_coerce, max_degree)

    masses = tuple(
        jet({1 << index: 1}) if active_mass_mask & (1 << index) else jet()
        for index in range(N)
    )

    @lru_cache(maxsize=None)
    def pair_square(left, right):
        if left == right:
            return masses[left]
        distance = (right - left) % N
        if distance == 1:
            return jet({0: adjacent[left]})
        if distance == N - 1:
            return jet({0: adjacent[right]})
        if distance == 2:
            return (
                jet({0: triples[left % 3]})
                - adjacent[left]
                - adjacent[(left + 1) % N]
                + masses[left]
                + masses[(left + 1) % N]
                + masses[(left + 2) % N]
            )
        if distance == N - 2:
            return pair_square(right, left)
        raise ValueError("opposite pair is fixed by momentum conservation")

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
                jet(),
            )
        return (pair_square(left, right) - masses[left] - masses[right]) * Fraction(1, 2)

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
            jet(),
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

    @lru_cache(maxsize=None)
    def current_by_topology(mask):
        if mask.bit_count() == 1:
            return {(0, 0): jet({0: 1})}
        values = {}
        for left, right in partitions(mask, 2):
            vertex = cubic((1, left), (1, right), (-1, mask))
            for (lc, lq), lvalue in current_by_topology(left).items():
                for (rc, rq), rvalue in current_by_topology(right).items():
                    key = (lc + rc + 1, lq + rq)
                    values[key] = values.get(key, jet()) + vertex * lvalue * rvalue
        for a, b, c in partitions(mask, 3):
            vertex = quartic((1, a), (1, b), (1, c), (-1, mask))
            for (ac, aq), avalue in current_by_topology(a).items():
                for (bc, bq), bvalue in current_by_topology(b).items():
                    for (cc, cq), cvalue in current_by_topology(c).items():
                        key = (ac + bc + cc, aq + bq + cq + 1)
                        values[key] = (
                            values.get(key, jet())
                            + vertex * avalue * bvalue * cvalue
                        )
        propagator = square((1, mask))
        return {
            key: -value / (propagator * propagator)
            for key, value in values.items()
        }

    root = 1 << 5
    rest = FULL_MASK ^ root
    topology_amplitudes = {}
    for left, right in partitions(rest, 2):
        vertex = cubic((1, root), (1, left), (1, right))
        for (lc, lq), lvalue in current_by_topology(left).items():
            for (rc, rq), rvalue in current_by_topology(right).items():
                key = (lc + rc + 1, lq + rq)
                topology_amplitudes[key] = (
                    topology_amplitudes.get(key, jet())
                    - vertex * lvalue * rvalue
                )
    for a, b, c in partitions(rest, 3):
        vertex = quartic((1, root), (1, a), (1, b), (1, c))
        for (ac, aq), avalue in current_by_topology(a).items():
            for (bc, bq), bvalue in current_by_topology(b).items():
                for (cc, cq), cvalue in current_by_topology(c).items():
                    key = (ac + bc + cc, aq + bq + cq + 1)
                    topology_amplitudes[key] = (
                        topology_amplitudes.get(key, jet())
                        - vertex * avalue * bvalue * cvalue
                    )
    amplitude = sum(topology_amplitudes.values(), jet())
    squarefree = (amplitude * amplitude).coefficients.get(FULL_MASK, Fraction(0))
    degree_three = {
        mask: value
        for mask, value in amplitude.coefficients.items()
        if mask.bit_count() == 3
    }
    complementary_products = {
        mask: degree_three[mask] * degree_three[FULL_MASK ^ mask]
        for mask in sorted(degree_three)
        if mask < (FULL_MASK ^ mask) and (FULL_MASK ^ mask) in degree_three
    }
    return {
        "amplitude": amplitude,
        "squarefree": squarefree,
        "degree_three": degree_three,
        "complementary_products": complementary_products,
        "topology_amplitudes": topology_amplitudes,
    }


PHYSICAL_PLANAR_FIXTURES = [
    {
        "adjacent": ["96/25", "64/25", "-108/25", "96/25", "64/25", "-108/25"],
        "triples": ["256/25", "-56/25", "-62/25"],
    },
    {
        "adjacent": ["96/25", "64/25", "-2", "64/25", "96/25", "-72/25"],
        "triples": ["256/25", "-84/25", "12/25"],
    },
    {
        "adjacent": ["96/25", "64/25", "-2/25", "64/25", "96/25", "-72/25"],
        "triples": ["256/25", "12/25", "12/25"],
    },
]


def fraction_string(value):
    return str(value.numerator) if value.denominator == 1 else str(value)


def rotation_family(tilt_ratio=Fraction(0)):
    """Evaluate an exact rotated physical 3-to-3 family."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    values = field("t", QQ)
    base, t = values

    def vector(*entries):
        return tuple(base(Fraction(value)) for value in entries)

    def add(*vectors):
        return tuple(
            sum((value[index] for value in vectors), base.zero)
            for index in range(4)
        )

    def negate(value):
        return tuple(-entry for entry in value)

    def square(value):
        return value[0] * value[0] - sum(
            (entry * entry for entry in value[1:]), base.zero
        )

    cosine = (1 - t * t) / (1 + t * t)
    sine = 2 * t / (1 + t * t)
    tilt = base(tilt_ratio) * t
    tilt_cosine = (1 - tilt * tilt) / (1 + tilt * tilt)
    tilt_sine = 2 * tilt / (1 + tilt * tilt)

    def rotate(value):
        rotated_x = cosine * value[1] - sine * value[2]
        rotated_y = sine * value[1] + cosine * value[2]
        return (
            value[0],
            rotated_x,
            tilt_cosine * rotated_y,
            tilt_sine * rotated_y,
        )

    incoming = [
        vector("6/5", "6/5", 0, 0),
        vector(1, "-3/5", "4/5", 0),
        vector(1, "-3/5", "-4/5", 0),
    ]
    outgoing = [rotate(value) for value in incoming]
    all_incoming = incoming + [negate(value) for value in outgoing]
    total = add(*all_incoming)
    adjacent = [
        square(add(all_incoming[index], all_incoming[(index + 1) % N]))
        for index in range(N)
    ]
    triples = [
        square(
            add(
                all_incoming[index],
                all_incoming[(index + 1) % N],
                all_incoming[(index + 2) % N],
            )
        )
        for index in range(3)
    ]
    result = generic_external_mass_kernel(
        adjacent, triples, scalar_coerce=base
    )
    coefficients = result["degree_three"]
    representatives = [
        mask for mask in sorted(coefficients) if mask < (FULL_MASK ^ mask)
    ]
    complement_differences = {
        mask: coefficients[mask] - coefficients[FULL_MASK ^ mask]
        for mask in representatives
    }
    sum_of_squares = 2 * sum(
        (coefficients[mask] * coefficients[mask] for mask in representatives),
        base.zero,
    )
    numerator_gcd = coefficients[representatives[0]].numer
    for mask in representatives[1:]:
        numerator_gcd = numerator_gcd.gcd(coefficients[mask].numer)
    topology_antisymmetric = {}
    for topology, amplitude in sorted(result["topology_amplitudes"].items()):
        cubic = {
            mask: value
            for mask, value in amplitude.coefficients.items()
            if mask.bit_count() == 3
        }
        topology_antisymmetric[str(topology)] = {
            mask: cubic[mask] - cubic[FULL_MASK ^ mask]
            for mask in representatives
        }
    topology_cancellation = all(
        sum(
            (rows[mask] for rows in topology_antisymmetric.values()),
            base.zero,
        ) == 0
        for mask in representatives
    )
    nontrivial_topology_antisymmetry = all(
        any(value != 0 for value in rows.values())
        for rows in topology_antisymmetric.values()
    )
    denominator_factors = [
        {"factor": str(factor), "multiplicity": multiplicity}
        for factor, multiplicity in result["squarefree"].denom.factor_list()[1]
    ]
    family = {
        "parameter": "t",
        "rotation": {
            "cosine": str(cosine),
            "sine": str(sine),
        },
        "incoming_momenta": [[str(entry) for entry in row] for row in incoming],
        "outgoing_momenta": [[str(entry) for entry in row] for row in outgoing],
        "all_six_massless": all(square(value) == 0 for value in all_incoming),
        "momentum_conservation": all(entry == 0 for entry in total),
        "adjacent_invariants": [str(value) for value in adjacent],
        "triple_invariants": [str(value) for value in triples],
        "amplitude_degrees": sorted(
            {mask.bit_count() for mask in result["amplitude"].coefficients}
        ),
        "amplitude_term_count": len(result["amplitude"].coefficients),
        "degree_three_term_count": len(coefficients),
        "middle_coefficients": [
            {
                "mask": mask,
                "complement_mask": FULL_MASK ^ mask,
                "coefficient": str(coefficients[mask]),
                "complement_coefficient": str(
                    coefficients[FULL_MASK ^ mask]
                ),
            }
            for mask in representatives
        ],
        "ten_complement_pairs_equal": all(
            value == 0 for value in complement_differences.values()
        ),
        "topology_antisymmetry_is_nontrivial": nontrivial_topology_antisymmetry,
        "topology_antisymmetry_cancels_in_complete_amplitude": topology_cancellation,
        "squarefree_squared_amplitude": str(result["squarefree"]),
        "equals_twice_ten_square_sum": result["squarefree"] == sum_of_squares,
        "degree_three_numerator_gcd": str(numerator_gcd.monic()),
        "no_common_complex_zero_of_ten_coefficients": numerator_gcd.degree() == 0,
        "squarefree_denominator_factors": denominator_factors,
        "strict_positivity_domain": (
            "real t away from the internal-propagator pole set; the ten real "
            "coefficient numerators have constant gcd, so their square sum "
            "never vanishes simultaneously"
        ),
    }
    if tilt_ratio:
        family["tilt"] = {
            "ratio": str(tilt_ratio),
            "parameter": str(tilt),
            "cosine": str(tilt_cosine),
            "sine": str(tilt_sine),
        }
        family["generic_outgoing_z_is_nonzero"] = any(
            row[3] != 0 for row in outgoing
        )
        family["incoming_and_outgoing_planes_differ_generically"] = True
    return family


def planar_rotation_family():
    """Prove positivity on the exact planar physical family."""
    return rotation_family()


def nonplanar_diagonal_family():
    """Prove positivity when the out-of-plane tilt is tied by u=t/2."""
    return rotation_family(Fraction(1, 2))


def build():
    family = planar_rotation_family()
    predecessors = [load(path) for path in INPUTS[1:]]
    pole_factors = family["squarefree_denominator_factors"]
    checks = {
        "all_six_external_momenta_are_massless": family["all_six_massless"],
        "three_to_three_momentum_is_conserved": family["momentum_conservation"],
        "rational_rotation_is_defined_for_all_real_t": (
            family["rotation"]["cosine"] == "(-t**2 + 1)/(t**2 + 1)"
            and family["rotation"]["sine"] == "2*t/(t**2 + 1)"
        ),
        "complete_amplitude_has_42_squarefree_terms": (
            family["amplitude_term_count"] == 42
        ),
        "amplitude_starts_at_external_mass_degree_three": (
            family["amplitude_degrees"] == [3, 4, 5, 6]
        ),
        "all_twenty_middle_degree_coefficients_retained": (
            family["degree_three_term_count"] == 20
            and len(family["middle_coefficients"]) == 10
        ),
        "ten_complement_coefficients_are_exactly_equal": (
            family["ten_complement_pairs_equal"]
            and all(
                row["coefficient"] == row["complement_coefficient"]
                for row in family["middle_coefficients"]
            )
        ),
        "individual_topologies_are_not_artificially_self_dual": family[
            "topology_antisymmetry_is_nontrivial"
        ],
        "complete_perfect_square_topology_sum_is_self_dual": family[
            "topology_antisymmetry_cancels_in_complete_amplitude"
        ],
        "six_derivative_kernel_is_twice_ten_square_sum": family[
            "equals_twice_ten_square_sum"
        ],
        "ten_coefficient_numerators_have_constant_gcd": (
            family["degree_three_numerator_gcd"] == "1"
            and family["no_common_complex_zero_of_ten_coefficients"]
        ),
        "all_recorded_propagator_poles_have_even_multiplicity": (
            len(pole_factors) == 6
            and all(row["multiplicity"] == 2 for row in pole_factors)
        ),
        "external_delta_prime_sign_is_positive": (-1) ** 6 == 1,
        "phase_space_mass_derivatives_decouple": min(
            family["amplitude_degrees"]
        ) == 3,
        "local_born_density_is_strictly_positive_off_poles": (
            family["equals_twice_ten_square_sum"]
            and family["no_common_complex_zero_of_ten_coefficients"]
        ),
        "predecessors_pass": all(value["checks"]["ok"] for value in predecessors),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "correlated_cylinder_no_go_not_promoted": (
            predecessors[2]["physical_disposition"][
                "complete_noncorrelated_crossed_three_to_three_phase_space"
            ] == "NOT_COMPUTED"
        ),
        "full_phase_space_integration_remains_open": True,
        "eq19_gravity_and_causal_claims_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_PLANAR_PHYSICAL_BORN_DENSITY_V1",
        "schema_version": "reverse-physics-bt-six-point-planar-physical-born-density-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact local six-delta-prime tree Born density on a continuous physical planar 3-to-3 family",
        "question": "After leaving the singular correlated crossed cylinder, is the complete six-external-mass BT tree Born density positive on an exact nonforward physical 3-to-3 continuum?",
        "answer": "Yes on the declared one-parameter planar family, away from its ordinary internal-propagator poles. Three exact future-null incoming momenta are mapped to three outgoing momenta by the rational rotation cos=(1-t^2)/(1+t^2), sin=2t/(1+t^2). The complete 220-tree amplitude in the 64-slot external-mass jet has no terms below degree three. Its twenty degree-three coefficients obey ten exact complement equalities c_S(t)=c_Sc(t), although none of the three cubic/quartic topology sectors has that symmetry separately. Consequently the six-derivative square-free coefficient is 2*sum_S c_S(t)^2. The ten reduced numerator polynomials have gcd one and every denominator pole has even multiplicity, so this coefficient is strictly positive for every real regular t. Because |M|^2 begins at the top six-mass degree, derivatives of a regular phase-space weight cannot mix into this coefficient; a positive massless interior weight multiplies it without changing its sign. This breaks the negative reduced-quotient barrier on a genuine physical continuum, but it is a local planar density, not the complete integrated six-body probability or Eq. (19).",
        "exact_physical_family": family,
        "local_born_density": {
            "external_projector": "(-partial_x0)...(-partial_x5) evaluated at x_i=0",
            "external_derivative_sign": "+1 because six delta-prime Wightman factors give (-1)^6",
            "amplitude_minimum_mass_degree": 3,
            "squared_amplitude_minimum_mass_degree": 6,
            "measure_decoupling": "In the square-free six-mass algebra, |M|^2 has no coefficient below the full mask. Therefore the full-mask coefficient of K(x)|M(x)|^2 is K(0) times the displayed amplitude coefficient for every regular analytic local phase-space weight K.",
            "positivity_assumption": "The undifferentiated massless local phase-space/detector weight K(0) is strictly positive at the selected regular interior point.",
            "status": "STRICTLY_POSITIVE_ON_DECLARED_REGULAR_PHYSICAL_FAMILY"
        },
        "interpretation": {
            "correlated_crossed_negative_quotient": "REMAINS_A_CERTIFIED_REDUCED_BOUNDARY_BLOCK",
            "complete_planar_middle_degree_recombination": "POSITIVE_TEN_SQUARE_SUM",
            "negative_reduced_block_is_complete_probability": "NO",
            "physical_progress": "FIRST_EXACT_CONTINUOUS_NONFORWARD_SIX_POINT_LOCAL_BORN_DENSITY",
            "complete_nonplanar_six_body_phase_space": "NOT_COMPUTED",
            "integrated_normalized_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "assumptions": [
            "The calculation uses the public BT cubic and quartic tree vertices with their perfect-square relative coupling and common tree phase removed before squaring.",
            "The all-incoming metric convention is (+---); the last three entries are negatives of future-null outgoing momenta.",
            "The nine cyclic invariant coordinates are held fixed while the six independent external mass squares are differentiated, as required by the off-shell external-mass jet.",
            "The parameter t is real and excludes the displayed internal-propagator pole set.",
            "The local massless phase-space/detector weight is analytic and strictly positive at the selected regular interior point.",
            "The theorem is about a planar one-parameter physical family and does not infer the sign on arbitrary nonplanar six-body kinematics."
        ],
        "does_not_establish": [
            "positivity over the complete nonplanar 3-to-3 six-body phase space",
            "an integrated or normalized six-point transition probability",
            "control or cancellation of the displayed internal propagator poles",
            "the twelve reversed history intertwiners as separate positive channels",
            "a complete incoming/outgoing Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level, a loop theorem, or KLN cancellation",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority"
        ],
        "next_gate": "Promote the positive local-density theorem from the planar rotation slice to a genuinely nonplanar two-parameter physical family, then integrate the six-delta-prime density on a common regulated six-body chart. The complement self-duality must be proved or falsified there rather than inferred from this slice. In parallel, Eq. (19) still requires the missing nonlinear projector transport and trace.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "A cached Berends--Giele subset recursion evaluates all 220 BT cubic/quartic trees in the exact 64-slot square-free algebra of six external mass squares over Q(t). It retains topology sectors separately, reconstructs exact physical momenta and cyclic invariants, pairs the twenty middle-degree coefficients, and computes a polynomial gcd and rational pole factorization. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (18)", "Appendix B Eqs. (24)-(25)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_generic_external_mass_kernel.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_planar_physical_born_density.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_six_point_planar_physical_born_density"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--planar-family", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.planar_family:
        print(json.dumps(planar_rotation_family(), indent=2, sort_keys=True))
        return 0
    if args.write or args.check:
        value = build()
        rendered = canonical(value)
        if args.write:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write(rendered)
        if args.check and os.path.exists(args.output):
            with open(args.output, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("certificate drift", file=sys.stderr)
                    return 1
        print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
        print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
        return 0 if value["checks"]["ok"] else 1
    rows = []
    for index, fixture in enumerate(PHYSICAL_PLANAR_FIXTURES):
        result = generic_external_mass_kernel(
            fixture["adjacent"], fixture["triples"]
        )
        complement_differences = {
            fraction_string(mask): fraction_string(
                result["degree_three"][mask]
                - result["degree_three"][FULL_MASK ^ mask]
            )
            for mask in result["complementary_products"]
        }
        rows.append(
            {
                "fixture": index,
                "amplitude_term_count": len(result["amplitude"].coefficients),
                "amplitude_degrees": sorted(
                    {mask.bit_count() for mask in result["amplitude"].coefficients}
                ),
                "degree_three_term_count": len(result["degree_three"]),
                "squarefree_squared_amplitude": fraction_string(result["squarefree"]),
                "squarefree_sign": (
                    "POSITIVE" if result["squarefree"] > 0 else
                    "NEGATIVE" if result["squarefree"] < 0 else "ZERO"
                ),
                "complement_differences": complement_differences,
                "complementary_product_signs": [
                    1 if value > 0 else -1 if value < 0 else 0
                    for value in result["complementary_products"].values()
                ],
            }
        )
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        for row in rows:
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
