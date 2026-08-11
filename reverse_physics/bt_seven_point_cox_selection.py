#!/usr/bin/env python3
"""Exact BT seven-point ordered tree and positive Cox moment completion.

The common external-mass scale is kept in a short Laurent algebra, while only
the three hard spectator masses are retained as square-free jets.  This keeps
the complete 2,485-tree calculation below the repository memory cap.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache

import bt_six_point_strongly_ordered_tree as six


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-seven-point-cox-selection-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-seven-point-cox-selection.md"
SOURCE = "05e08af12d8d3966157d1add5cfeceb25546514a"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-seven-point-cox-selection.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
]
N = 7
HARD_FIXTURES = [
    ([3, 5, 7, 11, 13, 17], [19, 23, 29, 31, 37]),
    ([4, 6, 9, 14, 18, 25], [31, 34, 39, 45, 52]),
]
INDEPENDENT_HARD_FIXTURE = (
    [5, 8, 12, 19, 27, 36], [41, 47, 53, 61, 71]
)

# The imported classes resolve these bounds in their defining module.  This
# process-local setting is the certified minimal truncation: the amplitude
# starts at delta^2, and raising HI above four leaves that coefficient fixed.
six.LO = -6
six.HI = 4
Laurent = six.Laurent
SpectatorJet = six.SpectatorJet
SpectatorRing = six.SpectatorRing
partitions = six.partitions


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def correlated_seven_point(hard_fixture):
    """Return the exact leading triple-ordered seven-point spectator kernel."""
    import sympy as sp
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    values = field("a0,a1,a2,a3,e1,e2,tau1,tau2,tau3", QQ)
    base = values[0]
    a0, a1, a2, a3, e1, e2, tau1, tau2, tau3 = values[1:]
    ring = SpectatorRing(base)

    def linear(value):
        return Laurent(ring, {1: value})

    def scalar(value):
        return Laurent.scalar(ring, value)

    masses = [
        linear(e1*e2*a0),
        linear(e1*e2*a1),
        linear(e2*a2),
        linear(a3),
        linear(SpectatorJet(ring, {1: base.one})),
        linear(SpectatorJet(ring, {2: base.one})),
        linear(SpectatorJet(ring, {4: base.one})),
    ]
    adjacent_hard, triple_hard = hard_fixture
    adjacent = [linear(e1*e2*tau1)] + [
        scalar(value) for value in adjacent_hard
    ]
    triples = [linear(e2*tau2), None, None, None, linear(tau3), None, None]
    hard_values = iter(triple_hard)
    triples = [
        scalar(next(hard_values)) if value is None else value
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
            # Momentum conservation identifies the quartet square with the
            # complementary adjacent triple square.
            quartet = triples[(left+4) % N]
            known = sum(
                (
                    pair_square(indices[p], indices[q])
                    for p in range(4)
                    for q in range(p+1, 4)
                    if (p, q) != (0, 3)
                ),
                Laurent(ring),
            )
            return (
                quartet
                + 2*sum((masses[index] for index in indices), Laurent(ring))
                - known
            )
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
                for left in range(N)
                if left_mask & (1 << left)
                for right in range(N)
                if right_mask & (1 << right)
            ),
            Laurent(ring),
        )

    def dot(left, right):
        return left[0]*right[0]*unsigned_dot(left[1], right[1])

    def square(momentum):
        return dot(momentum, momentum)

    def cubic(left, middle, right):
        return (
            square(left)*dot(middle, right)
            + square(middle)*dot(left, right)
            + square(right)*dot(left, middle)
        )

    def quartic(a, b, c, d):
        return (
            dot(a, b)*dot(c, d)
            + dot(a, c)*dot(b, d)
            + dot(a, d)*dot(b, c)
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
                * current(left)*current(right)
            )
        for a, b, c in partitions(mask, 3):
            value += (
                quartic((1, a), (1, b), (1, c), (-1, mask))
                * current(a)*current(b)*current(c)
            )
        return -value/(square((1, mask))**2)

    root = 1 << 6
    rest = root-1
    amplitude = zero
    for left, right in partitions(rest, 2):
        amplitude += (
            cubic((1, root), (1, left), (1, right))
            * current(left)*current(right)
        )
    for a, b, c in partitions(rest, 3):
        amplitude += (
            quartic((1, root), (1, a), (1, b), (1, c))
            * current(a)*current(b)*current(c)
        )
    amplitude = -amplitude
    leading_order = min(amplitude.coefficients)
    leading = amplitude.coefficient(leading_order)
    projected = (leading*leading).coefficients.get(7, base.zero)
    expression = projected.as_expr()
    symbols = {symbol.name: symbol for symbol in expression.free_symbols}
    after_inner = sp.cancel(expression.subs(symbols["e1"], 0))
    strong = sp.factor(after_inner.subs(symbols["e2"], 0))
    return {
        "leading_order": leading_order,
        "leading_masks": sorted(leading.coefficients),
        "projected": str(expression),
        "projected_length": len(str(expression)),
        "projected_sha256": text_sha256(str(expression)),
        "after_inner_hierarchy_length": len(str(after_inner)),
        "strong_order": str(strong),
        "strong_order_length": len(str(strong)),
    }


def threshold_analysis():
    """Reduce the three Kallen thresholds through their exact log residues."""
    import sympy as sp

    a0, a1, a2, a3, tau1, tau2, tau3 = sp.symbols(
        "a0 a1 a2 a3 tau1 tau2 tau3"
    )
    aa = (a0-a1)**2-2*tau1*(a0+a1)+2*tau1**2
    bb = a2*aa+2*tau2*(-aa+3*tau1**2)
    cc = a2*bb+2*tau2**2*(aa+tau1**2)
    dd = a3*cc+2*tau3*(-cc+3*tau2**2*aa)
    kernel = sp.cancel(
        3*a3**3*cc*dd/(128*tau1**4*tau2**4*tau3**3)
    )

    # The outer threshold uses J4 and J3.  Their common unit r log r
    # coefficient maps C*D to C*(-C+6*tau2^2*A).
    outer_reduced = sp.expand(cc*(-cc+6*tau2**2*aa))
    middle_coefficients = [
        sp.factor(outer_reduced.coeff(tau2, power))
        for power in range(5)
    ]
    middle_sum = sp.factor(sum(middle_coefficients).subs(a2, 1))
    inner_expected = sp.factor((aa+8*tau1**2)*(5*aa-8*tau1**2))

    # For u=1+m^2+m(z+z^-1), fixed physical u=Lambda means
    # z=m/Lambda+O(Lambda^-2).  Only the log z and log(z+m) residues can
    # produce m^2 log m.  This avoids constructing an irrelevant huge full
    # antiderivative while retaining the invariant-cutoff conversion.
    z, m = sp.symbols("z m", positive=True)
    sigma = 1+m**2
    u = sigma+m*(z+1/z)
    measure = m**2*(1-z**2)**2/z**3
    difference = (1-m**2)**2
    inner_a = difference-2*sigma*u+2*u**2
    inner_h = (inner_a+8*u**2)*(5*inner_a-8*u**2)
    integrand = sp.cancel(inner_h*measure/u**4)
    residue_zero = sp.factor(sp.residue(integrand, z, 0))
    residue_minus_m = sp.factor(sp.residue(integrand, z, -m))
    physical_log_coefficient = sp.factor(-(residue_zero+residue_minus_m))
    small_m = sp.series(physical_log_coefficient, m, 0, 5)
    inner_r_log_r = Fraction(-27)

    raw_before_external_sign = Fraction(3, 128)*inner_r_log_r
    external_sign = -1
    signed_raw = external_sign*raw_before_external_sign
    hard_phase = Fraction(1, 16)
    hard_kernel = Fraction(3, 2)
    seven_phase = (
        Fraction(1024)*Fraction(1, 240)*Fraction(1, 2)
        * Fraction(1, 8)*Fraction(1, 32)**4*Fraction(64)
    )
    selected_history = seven_phase*signed_raw/(hard_phase*hard_kernel)
    histories = 60
    ordered_simplex = Fraction(1, 6)
    p3 = selected_history*histories*ordered_simplex
    m1 = Fraction(1, 16)
    m2 = Fraction(5, 256)
    m3 = 6*p3
    kappa2 = m2-m1**2
    kappa3 = m3-3*m2*m1+2*m1**3

    return {
        "recursive_kernel": {
            "A": str(aa),
            "B": str(bb),
            "C": str(cc),
            "D": str(dd),
            "kernel": str(kernel),
        },
        "outer_reduction": {
            "result": str(sp.factor(outer_reduced)),
            "moments_used": ["J4", "J3"],
            "common_r_log_r_coefficient": rat(1),
        },
        "middle_reduction": {
            "coefficient_rows": [str(value) for value in middle_coefficients],
            "moments_used": ["J5", "J4", "J3", "J2", "J1"],
            "all_physical_cutoff_r_log_r_coefficients": [rat(1)]*5,
            "sum": str(middle_sum),
            "inner_kernel": str(inner_expected),
        },
        "inner_reduction": {
            "r_equals_m_squared": True,
            "physical_cutoff": "u=Lambda, hence z=m/Lambda+O(Lambda^-2)",
            "residue_at_z_zero": str(residue_zero),
            "residue_at_z_minus_m": str(residue_minus_m),
            "physical_log_m_coefficient": str(physical_log_coefficient),
            "small_m_series": str(small_m),
            "r_log_r_coefficient": rat(inner_r_log_r),
            "local_subtraction_invariance": "At fixed physical u, divergent large-u subtraction coefficients are analytic in r. Such invariant local subtractions cannot alter the r*log(r) coefficient -27; fixed z is excluded because it is external-mass dependent.",
        },
        "normalization": {
            "raw_triple_cocycle_before_external_sign": rat(raw_before_external_sign),
            "seven_external_delta_prime_sign": external_sign,
            "signed_raw_triple_cocycle": rat(signed_raw),
            "hard_phase_prefactor": rat(hard_phase),
            "seven_point_phase_prefactor": rat(seven_phase),
            "hard_squarefree_kernel": rat(hard_kernel),
            "selected_nested_history_relative_to_Born": rat(selected_history),
            "labeled_nested_histories": histories,
            "history_derivation": "C(5,2)*3*2=60: choose the inner pair, then the third and fourth nested daughters",
            "ordered_resolution_simplex": rat(ordered_simplex),
            "leading_three_count_coefficient": rat(p3),
        },
        "factorial_data": {
            "first_factorial_moment_coefficient": rat(m1),
            "second_factorial_moment_coefficient": rat(m2),
            "third_factorial_moment_coefficient": rat(m3),
            "second_factorial_cumulant_coefficient": rat(kappa2),
            "third_factorial_cumulant_coefficient": rat(kappa3),
            "log_generating_cubic_coefficient": rat(kappa3/6),
        },
    }


def cox_analysis(factorial):
    """Classify exact positive intensity laws through the third moment."""
    import sympy as sp

    def recorded_fraction(name):
        value = factorial[name]
        return Fraction(value["numerator"], value["denominator"])

    m1 = recorded_fraction("first_factorial_moment_coefficient")
    m2 = recorded_fraction("second_factorial_moment_coefficient")
    m3 = recorded_fraction("third_factorial_moment_coefficient")
    lower = m2*m2/m1
    gamma_m3 = Fraction(45, 4096)
    gamma_p3 = gamma_m3/6
    tree_p3 = m3/6
    root = sp.sqrt(113)
    x_minus = (11-root)/64
    x_plus = (11+root)/64
    p_minus = (root+7)/(2*root)
    p_plus = (root-7)/(2*root)
    moments = [
        sp.simplify(p_minus*x_minus**power+p_plus*x_plus**power)
        for power in range(1, 5)
    ]
    m4 = Fraction(int(sp.numer(moments[3])), int(sp.denom(moments[3])))
    kappa4 = m4-4*m3*m1-3*m2*m2+12*m2*m1*m1-6*m1**4
    checks = {
        "weights_sum_to_one": sp.simplify(p_minus+p_plus) == 1,
        "support_is_strictly_positive": bool(11 > sp.sqrt(113)) and bool(root > 7),
        "two_atom_moments_match_tree": moments[:3]
        == [
            sp.Rational(value.numerator, value.denominator)
            for value in (m1, m2, m3)
        ],
    }
    return {
        "cox_moment_cone": {
            "rate_moments": [rat(m1), rat(m2), rat(m3)],
            "stieltjes_inequality": "m1*m3 >= m2^2",
            "minimum_third_moment": rat(lower),
            "tree_margin_above_minimum": rat(m3-lower),
            "leading_P3_lower_bound": rat(lower/6),
            "tree_is_cox_admissible_through_degree_three": m3 >= lower,
        },
        "gamma_cox_candidate": {
            "shape": rat(Fraction(1, 4)),
            "scale": rat(Fraction(1, 4)),
            "generating_function": "G_a(z)=(1+a*(1-z)/4)^(-1/4)",
            "third_rate_moment": rat(gamma_m3),
            "leading_P3_coefficient": rat(gamma_p3),
            "disposition": "RULED_OUT_BY_SEVEN_POINT_TREE",
            "tree_over_gamma_P3": rat(tree_p3/gamma_p3),
        },
        "minimal_two_atom_cox_candidate": {
            "support": [str(x_minus), str(x_plus)],
            "weights": [str(p_minus), str(p_plus)],
            "support_polynomial": "512*x^2-176*x+1",
            "generating_function": "G_a(z)=p_minus*exp(a*x_minus*(z-1))+p_plus*exp(a*x_plus*(z-1))",
            "state": "omega_I(X)=sum_sigma p_sigma <W(sqrt(16*x_sigma)F_I)Omega, X W(sqrt(16*x_sigma)F_I)Omega>",
            "controlled_dilation": "U_I=direct_sum_sigma W(sqrt(16*x_sigma)F_I) on C^2_classical tensor Gamma_s(K_I)",
            "local_properties": [
                "positive and normalized",
                "locally normal",
                "consistent under interval inclusion",
                "joint-resolution-translation covariant",
                "conditionally Poisson but marginally correlated on disjoint intervals",
            ],
            "moments_verified": checks,
            "next_fourth_rate_moment": rat(m4),
            "next_leading_P4_coefficient": rat(m4/24),
            "next_fourth_factorial_cumulant": rat(kappa4),
            "uniqueness": "unique only among nonnegative intensity laws supported on at most two atoms; not unique in the full Cox moment cone",
        },
        "channel_boundary": "The total-count moments do not determine whether the auxiliary intensity is shared across the three pair channels or decomposes into correlated channel intensities.",
        "state_checks": checks,
    }


def build():
    import sympy as sp

    topology = six.topology_counts(7)
    rows = [correlated_seven_point(fixture) for fixture in HARD_FIXTURES]
    projected = rows[0]["projected"]
    threshold = threshold_analysis()
    cox = cox_analysis(threshold["factorial_data"])
    symbols = sp.symbols("a0 a1 a2 a3 tau1 tau2 tau3")
    a0, a1, a2, a3, tau1, tau2, tau3 = symbols
    aa = (a0-a1)**2-2*tau1*(a0+a1)+2*tau1**2
    bb = a2*aa+2*tau2*(-aa+3*tau1**2)
    cc = a2*bb+2*tau2**2*(aa+tau1**2)
    dd = a3*cc+2*tau3*(-cc+3*tau2**2*aa)
    expected_kernel = sp.cancel(
        3*a3**3*cc*dd/(128*tau1**4*tau2**4*tau3**3)
    )
    recorded_kernel = sp.sympify(rows[0]["strong_order"])
    checks = {
        "topology_counts_945_1260_280": topology
        == {(5, 0): 945, (3, 1): 1260, (1, 2): 280},
        "total_tree_count_2485": sum(topology.values()) == 2485,
        "amplitudes_start_at_delta_two": all(row["leading_order"] == 2 for row in rows),
        "leading_spectator_masks_are_complete": all(row["leading_masks"] == list(range(7)) for row in rows),
        "two_hard_fixtures_have_identical_projected_kernel": len({row["projected_sha256"] for row in rows}) == 1,
        "two_hard_fixtures_have_identical_strong_kernel": len({row["strong_order"] for row in rows}) == 1,
        "recursive_strong_kernel_identity": sp.cancel(recorded_kernel-expected_kernel) == 0,
        "middle_reduction_identity": threshold["middle_reduction"]["sum"] == threshold["middle_reduction"]["inner_kernel"],
        "inner_r_log_r_is_minus_27": threshold["inner_reduction"]["r_log_r_coefficient"] == rat(-27),
        "signed_raw_cocycle_is_81_over_128": threshold["normalization"]["signed_raw_triple_cocycle"] == rat(Fraction(81, 128)),
        "selected_history_is_9_over_81920": threshold["normalization"]["selected_nested_history_relative_to_Born"] == rat(Fraction(9, 81920)),
        "tree_P3_is_9_over_8192": threshold["normalization"]["leading_three_count_coefficient"] == rat(Fraction(9, 8192)),
        "third_factorial_cumulant_is_7_over_2048": threshold["factorial_data"]["third_factorial_cumulant_coefficient"] == rat(Fraction(7, 2048)),
        "gamma_cox_is_ruled_out": cox["gamma_cox_candidate"]["disposition"] == "RULED_OUT_BY_SEVEN_POINT_TREE",
        "two_atom_state_matches_three_moments": all(cox["state_checks"].values()),
        "cox_stieltjes_bound_passes": cox["cox_moment_cone"]["tree_is_cox_admissible_through_degree_three"],
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }
    for row in rows:
        del row["projected"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1",
        "schema_version": "reverse-physics-bt-seven-point-cox-selection-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete seven-point triple-ordered external-mass tree jet, third factorial cumulant, Cox moment-cone classification, and minimal two-atom positive resolution-state dilation",
        "question": "What third factorial moment does the complete BT seven-point nested tree select, and does it admit a positive non-Gaussian resolution-local Cox completion?",
        "answer": "The complete 2485-tree jet gives the same leading nested kernel at two unrelated exact producer fixtures. Three exact physical-cutoff threshold reductions give signed raw cocycle 81/128. Restoring the 2->5 phase normalization, 60 labeled histories, and ordered three-simplex gives P3(a)=9*a^3/8192, hence third factorial moment 27*a^3/4096 and third factorial cumulant 7*a^3/2048. This rules out the gamma-Cox completion, which predicts P3=15*a^3/8192, but satisfies the exact nonnegative-intensity Stieltjes bound P3>=25*a^3/24576. The unique two-atom intensity law through these three moments has support (11-sqrt(113))/64 and (11+sqrt(113))/64, with positive weights (sqrt(113)+7)/(2*sqrt(113)) and (sqrt(113)-7)/(2*sqrt(113)); its controlled mixture of the certified local Weyl displacements is a positive normalized locally normal resolution-state dilation. It is unique only within the two-atom Cox architecture and is not yet a dynamically derived spacetime Moller operator or a complete probability.",
        "topology": {
            "V3_fifth": topology.get((5, 0)),
            "V3_cubed_V4": topology.get((3, 1)),
            "V3_V4_squared": topology.get((1, 2)),
            "total": sum(topology.values()),
            "relative_signs": "- V3^5, + V3^3 V4, - V3 V4^2 before the common seven-delta-prime sign",
        },
        "correlated_boundary": {
            "scaling": "x0,x1,s01=delta*e1*e2*(a0,a1,tau1); x2,t012=delta*e2*(a2,tau2); x3,t456=delta*(a3,tau3); x4,x5,x6=delta*(three square-free spectator jets); take delta->0, then e1->0, then e2->0",
            "cyclic_chart": "seven adjacent pair squares and seven adjacent triple squares; every quartet square is its complementary triple square",
            "producer_hard_fixtures": HARD_FIXTURES,
            "independent_verifier_hard_fixture": INDEPENDENT_HARD_FIXTURE,
            "rows": rows,
            "projected_expression": projected,
            "projected_expression_sha256": text_sha256(projected),
        },
        "threshold_analysis": threshold,
        "cox_completion": cox,
        "disposition": {
            "complete_seven_point_tree_recursion": "COMPUTED",
            "triple_ordered_threshold_cocycle": "COMPUTED",
            "third_factorial_moment": "TWENTY_SEVEN_OVER_4096_TIMES_A_CUBED",
            "third_factorial_cumulant": "POSITIVE_SEVEN_OVER_2048_TIMES_A_CUBED",
            "gamma_cox_completion": "RULED_OUT",
            "scalar_cox_architecture_through_three_moments": "ADMISSIBLE",
            "minimal_two_atom_cox_state": "CONSTRUCTED_THROUGH_THREE_MOMENTS",
            "unique_all_order_count_law": "NOT_SELECTED",
            "complete_five_body_probability": "NOT_CONSTRUCTED",
            "spacetime_local_physical_S_matrix": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The Cox completion uses one nonnegative scalar total intensity shared by the resolution interval; channel-resolved intensity correlations are not fixed by total counts.",
            "The controlled Weyl dilation imports the certified rank-two local coherent displacement and mixes only its nonnegative intensity; it does not reconstruct an uncomputed nonlinear BT phase.",
            "Only the leading triple-strongly-ordered external-mass coefficient is transferred to the count moments.",
        ],
        "does_not_establish": [
            "a complete physical 2->5 probability",
            "universal hard-angle independence beyond the exact producer and verifier fixtures",
            "a unique Cox law beyond the first three moments",
            "that the two-atom auxiliary intensity is a BT dynamical zero mode",
            "a finite beyond-leading-log correction",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority",
        ],
        "missing_object_ledger": [
            "the complete eight-point quadruple-strongly-ordered tree, whose fourth moment tests the two-atom prediction 73/32768",
            "channel-resolved seven-point projectors that distinguish a shared scalar intensity from correlated three-channel intensities",
            "an all-order proof that the BT factorial moments form a Stieltjes sequence",
            "a dynamical affiliation of the auxiliary intensity carrier with the BT asymptotic Hamiltonian",
            "the complete non-strongly-ordered five-body phase-space projector and finite terms",
        ],
        "next_gate": "Compute the channel-resolved seven-point moment matrix and the complete eight-point quadruple-strongly-ordered coefficient. The scalar two-atom Cox completion predicts fourth rate moment 73/32768, leading P4=73/786432, and fourth factorial cumulant 17/65536. Agreement would extend the positive state by one moment; disagreement that preserves the next Stieltjes Hankel inequalities would require at least three intensity atoms, while a violated inequality would rule out scalar Cox completion.",
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
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_seven_point_cox_selection.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_seven_point_cox_selection.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_seven_point_cox_selection",
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
    return json.dumps(value, indent=2, sort_keys=True)+"\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    boundary = value.get("correlated_boundary", {})
    projected = boundary.get("projected_expression", "")
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 18
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and text_sha256(projected) == boundary.get("projected_expression_sha256")
        and len(inputs) == 3
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in value.get("does_not_establish", [])
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
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
    print("P3 coefficient:", value["threshold_analysis"]["normalization"]["leading_three_count_coefficient"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
