#!/usr/bin/env python3
"""Exact BT eight-point fourth-moment hard-profile preflight."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-hard-profile-obstruction-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-hard-profile-obstruction.md"
SOURCE = "b216fe66"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-hard-profile-obstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
]
N = 8

# The fourth nested jet requires two more negative Laurent orders than the
# seven-point calculation.  The retained delta^2 amplitude is stable once the
# upper rail reaches four.
six.LO = -8
six.HI = 4
Laurent = six.Laurent
SpectatorJet = six.SpectatorJet
SpectatorRing = six.SpectatorRing
partitions = six.partitions

HARD_FIXTURES = [
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
SOFT_FIXTURE = [1, 4, 3, 2, 1, 10, 7, 5, 3]


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


def _correlated_eight_point_fixture(
    hard_fixture,
    soft_fixture,
    include_outer_profile=False,
    include_middle_profile=False,
    include_tau2_profile=False,
):
    """One exact square-free spectator fixture with hierarchy-first limits."""
    import sympy as sp
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if sum(
        (include_outer_profile, include_middle_profile, include_tau2_profile)
    ) > 1:
        raise ValueError("select at most one retained threshold profile")
    if include_middle_profile:
        field_names = "e1,e2,e3,tau3,tau4"
    elif include_tau2_profile:
        field_names = "e1,e2,e3,tau2"
    elif include_outer_profile:
        field_names = "e1,e2,e3,tau4"
    else:
        field_names = "e1,e2,e3"
    values = field(field_names, QQ)
    base = values[0]
    e1, e2, e3 = values[1:4]
    soft_values = [base(value) for value in soft_fixture]
    a0, a1, a2, a3, a4, tau1 = soft_values[:6]
    if include_middle_profile:
        tau2 = soft_values[6]
        tau3, tau4 = values[4:6]
    elif include_tau2_profile:
        tau2 = values[4]
        # The first two fixed-invariant nonanalytic functionals are scaled
        # evaluations at tau4=a4 and tau3=a3.  Their nonzero overall scale
        # factors are applied by the dedicated threshold producer.
        tau3, tau4 = a3, a4
    else:
        tau2 = soft_values[6]
        tau3 = soft_values[7]
        tau4 = values[4] if include_outer_profile else soft_values[8]
    ring = SpectatorRing(base)

    def linear(value):
        return Laurent(ring, {1: value})

    def scalar(value):
        return Laurent.scalar(ring, value)

    masses = [
        linear(e1 * e2 * e3 * a0),
        linear(e1 * e2 * e3 * a1),
        linear(e2 * e3 * a2),
        linear(e3 * a3),
        linear(a4),
        linear(SpectatorJet(ring, {1: base.one})),
        linear(SpectatorJet(ring, {2: base.one})),
        linear(SpectatorJet(ring, {4: base.one})),
    ]
    adjacent_hard, triple_hard, quartet_hard = hard_fixture
    adjacent = [linear(e1 * e2 * e3 * tau1)] + [
        scalar(value) for value in adjacent_hard
    ]
    triple_values = iter(triple_hard)
    triples = []
    for index in range(N):
        if index == 0:
            triples.append(linear(e2 * e3 * tau2))
        elif index == 5:
            triples.append(linear(tau4))
        else:
            triples.append(scalar(next(triple_values)))
    quartets = [linear(e3 * tau3)] + [
        scalar(value) for value in quartet_hard
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
            indices = [left, (left + 1) % N, (left + 2) % N, (left + 3) % N]
            quartet = quartets[left % 4]
            known = sum(
                (
                    pair_square(indices[p], indices[q])
                    for p in range(4)
                    for q in range(p + 1, 4)
                    if (p, q) != (0, 3)
                ),
                Laurent(ring),
            )
            return (
                quartet
                + 2 * sum((masses[index] for index in indices), Laurent(ring))
                - known
            )
        if distance == N - 3:
            return pair_square(right, left)
        raise ValueError("opposite pair is derived from momentum conservation")

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
                * current(left) * current(right)
            )
        for a, b, c in partitions(mask, 3):
            value += (
                quartic((1, a), (1, b), (1, c), (-1, mask))
                * current(a) * current(b) * current(c)
            )
        return -value / (square((1, mask)) ** 2)

    root = 1 << 7
    rest = root - 1
    amplitude = zero
    for left, right in partitions(rest, 2):
        amplitude += (
            cubic((1, root), (1, left), (1, right))
            * current(left) * current(right)
        )
    for a, b, c in partitions(rest, 3):
        amplitude += (
            quartic((1, root), (1, a), (1, b), (1, c))
            * current(a) * current(b) * current(c)
        )
    amplitude = -amplitude
    leading_order = min(amplitude.coefficients)
    leading = amplitude.coefficient(leading_order)
    def leading_at_zero(expression, variable):
        """Return exact valuation and leading coefficient at zero."""
        expression = sp.cancel(expression)
        numerator, denominator = sp.fraction(expression)
        numerator_poly = sp.Poly(numerator, variable)
        denominator_poly = sp.Poly(denominator, variable)
        numerator_order = min(power[0] for power in numerator_poly.as_dict())
        denominator_order = min(power[0] for power in denominator_poly.as_dict())
        numerator_lead = numerator_poly.coeff_monomial(variable**numerator_order)
        denominator_lead = denominator_poly.coeff_monomial(
            variable**denominator_order
        )
        return (
            numerator_order - denominator_order,
            sp.cancel(numerator_lead / denominator_lead),
        )

    def hierarchy_leading(expression):
        symbols = {symbol.name: symbol for symbol in expression.free_symbols}
        valuations = []
        for name in ("e1", "e2", "e3"):
            if name in symbols and symbols[name] in expression.free_symbols:
                valuation, expression = leading_at_zero(expression, symbols[name])
                valuations.append((name, valuation))
        return valuations, sp.factor(expression)

    # Individual spectator components and even individual complementary
    # products are hierarchy-singular.  The square-free projector is their
    # sum, and its cross-pair cancellations must occur before any limit.
    projected_field = 2 * sum(
        (
            leading.coefficients.get(mask, base.zero)
            * leading.coefficients.get(7 ^ mask, base.zero)
            for mask in range(4)
        ),
        base.zero,
    )
    projected_expression = projected_field.as_expr()
    if include_outer_profile or include_middle_profile or include_tau2_profile:
        outer_expression = projected_expression
        outer_symbols = {
            symbol.name: symbol for symbol in outer_expression.free_symbols
        }
        outer_valuations = []
        hierarchy_names = (
            ("e1", "e2", "e3")
            if include_middle_profile or include_tau2_profile
            else ("e1", "e2")
        )
        for name in hierarchy_names:
            valuation, outer_expression = leading_at_zero(
                outer_expression, outer_symbols[name]
            )
            outer_valuations.append((name, valuation))
        outer_expression = sp.factor(outer_expression)
        return {
            "leading_order": leading_order,
            "leading_masks": sorted(leading.coefficients),
            "inner_hierarchy_valuations": outer_valuations,
            "outer_profile": str(outer_expression),
            "outer_profile_length": len(str(outer_expression)),
            "outer_profile_sha256": text_sha256(str(outer_expression)),
        }
    finite_point = {
        "e1": sp.Rational(1, 5),
        "e2": sp.Rational(2, 7),
        "e3": sp.Rational(3, 11),
    }
    expression_symbols = {
        symbol.name: symbol for symbol in projected_expression.free_symbols
    }
    finite_value = sp.cancel(
        projected_expression.subs(
            {
                expression_symbols[name]: value
                for name, value in finite_point.items()
                if name in expression_symbols
            }
        )
    )
    hierarchy_valuations, projected = hierarchy_leading(projected_expression)
    return {
        "leading_order": leading_order,
        "leading_masks": sorted(leading.coefficients),
        "projected_length": len(str(projected_expression)),
        "projected_sha256": text_sha256(str(projected_expression)),
        "finite_evaluation_point": {
            name: str(value) for name, value in finite_point.items()
        },
        "finite_projected_value": str(finite_value),
        "hierarchy_valuations": hierarchy_valuations,
        "strong_order": str(projected),
    }


def correlated_eight_point(hard_fixture, soft_fixture):
    """Return the exact strong-order mixed spectator coefficient."""
    row = _correlated_eight_point_fixture(hard_fixture, soft_fixture)
    row["strong_order_sha256"] = text_sha256(row["strong_order"])
    return row


def outer_profile_eight_point(hard_fixture, soft_fixture):
    """Retain the outer parent invariant after the first two hierarchy limits."""
    return _correlated_eight_point_fixture(
        hard_fixture, soft_fixture, include_outer_profile=True
    )


def middle_profile_eight_point(hard_fixture, soft_fixture):
    """Retain the final two parent invariants after all hierarchy valuations."""
    return _correlated_eight_point_fixture(
        hard_fixture, soft_fixture, include_middle_profile=True
    )


def tau2_profile_eight_point(hard_fixture, soft_fixture):
    """Retain tau2 after evaluating the first two threshold functionals."""
    return _correlated_eight_point_fixture(
        hard_fixture, soft_fixture, include_tau2_profile=True
    )


def build():
    topology = six.topology_counts(8)
    rows = [correlated_eight_point(hard, SOFT_FIXTURE) for hard in HARD_FIXTURES]
    residues = [Fraction(row["strong_order"]) for row in rows]
    finite_values = [Fraction(row["finite_projected_value"]) for row in rows]
    residue_difference = residues[0] - residues[1]
    finite_difference = finite_values[0] - finite_values[1]
    checks = {
        "topology_counts_10395_17325_6300_280": topology
        == {(6, 0): 10395, (4, 1): 17325, (2, 2): 6300, (0, 3): 280},
        "total_tree_count_34300": sum(topology.values()) == 34300,
        "amplitudes_start_at_delta_two": all(
            row["leading_order"] == 2 for row in rows
        ),
        "all_spectator_masks_present": all(
            row["leading_masks"] == list(range(8)) for row in rows
        ),
        "same_soft_fixture": True,
        "hard_fixtures_differ_in_one_adjacent_invariant": (
            HARD_FIXTURES[0][0][:-1] == HARD_FIXTURES[1][0][:-1]
            and HARD_FIXTURES[0][0][-1] + 1 == HARD_FIXTURES[1][0][-1]
            and HARD_FIXTURES[0][1:] == HARD_FIXTURES[1][1:]
        ),
        "same_ordered_hierarchy_valuation": all(
            row["hierarchy_valuations"] == [("e1", 0), ("e2", 0), ("e3", -1)]
            for row in rows
        ),
        "finite_projected_values_differ": finite_difference != 0,
        "strong_residues_differ": residue_difference != 0,
        "residue_difference_is_257_over_1568": residue_difference
        == Fraction(257, 1568),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-eight-point-hard-profile-obstruction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "complete eight-point quadruple-ordered external-mass tree preflight and exact hard-profile obstruction to the direct scalar fourth-jump extraction",
        "question": "Does the complete BT eight-point tree admit the same hard-independent bare strong-hierarchy scalar reduction that fixed the second and third ordered moments at six and seven points?",
        "answer": "No on the bare hierarchy carrier. The complete 34,300-tree amplitude starts at common external-mass order two and contains every square-free spectator mask on both exact fixtures. The fixtures use identical soft data and differ only by changing one hard adjacent invariant from 33 to 34. Their complete projected squares have the same ordered hierarchy valuation (0,0,-1), but the leading residues differ by exactly 257/1568; their values at the same finite rational hierarchy point also differ. An independent rational-series implementation using the invariant triangle cubic vertex reproduces both finite values. Therefore the hard-independent scalar extraction used at six and seven points does not directly define a fourth jump at eight points. This does not prove that the threshold-integrated fourth moment fails to exist: an outer Kallen reduction, hard-profile quotient, or channel-resolved recombination may remove the dependence. Until that calculation is performed, the provisional coefficient 629 and the claimed exclusion of the two-atom Cox completion are withdrawn.",
        "topology": {
            "V3_sixth": topology.get((6, 0)),
            "V3_fourth_V4": topology.get((4, 1)),
            "V3_squared_V4_squared": topology.get((2, 2)),
            "V4_cubed": topology.get((0, 3)),
            "total": sum(topology.values()),
        },
        "correlated_boundary": {
            "scaling": "x0,x1,s01=delta*e1*e2*e3*(a0,a1,tau1); x2,s012=delta*e2*e3*(a2,tau2); x3,s0123=delta*e3*(a3,tau3); x4,s01234=delta*(a4,tau4); x5,x6,x7=delta*(three square-free spectator jets); take delta->0, then ordered leading valuations in e1,e2,e3",
            "cyclic_chart": "eight adjacent pair squares, eight adjacent triple squares, and four complementary adjacent quartet squares",
            "soft_fixture": SOFT_FIXTURE,
            "hard_fixtures": HARD_FIXTURES,
            "rows": rows,
            "finite_value_difference": rat(finite_difference),
            "strong_residue_difference": rat(residue_difference),
        },
        "disposition": {
            "complete_eight_point_tree_recursion": "COMPUTED_ON_TWO_EXACT_HARD_FIXTURES",
            "bare_quadruple_strong_hierarchy": "SINGULAR_WITH_VALUATION_MINUS_ONE_AT_OUTERMOST_DECLARED_LIMIT",
            "hard_independent_scalar_fourth_jump": "OBSTRUCTED_ON_BARE_HIERARCHY_CARRIER",
            "threshold_integrated_fourth_moment": "NOT_COMPUTED",
            "two_atom_Cox_completion": "NOT_DECIDED_AT_FOURTH_MOMENT",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "nonexistence of a fourth physical factorial moment after the outer threshold integration",
            "failure of every hard-profile or channel-resolved quotient",
            "exclusion of the two-atom Cox completion",
            "a complete physical 2->6 probability",
            "universal behavior outside the two exact hard fixtures",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority",
        ],
        "next_gate": "Retain the outer hierarchy parameter through the complete projected square and perform the outer fixed-physical-invariant Kallen threshold reduction before taking e3 to zero. Resolve the resulting hard-profile coefficient on the pre-trace quotient. Only if that reduction becomes hard independent may it be normalized as the physical fourth jump and compared with the two-atom Cox prediction P4=73/786432.",
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
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_fourth_moment.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_fourth_moment.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_hard_profile_obstruction",
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


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    rows = value.get("correlated_boundary", {}).get("rows", [])
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 12
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(rows) == 2
        and all(
            text_sha256(row.get("strong_order", ""))
            == row.get("strong_order_sha256")
            for row in rows
        )
        and len(inputs) == 4
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("threshold_integrated_fourth_moment")
        == "NOT_COMPUTED"
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=int, default=0)
    parser.add_argument("--outer-profile", action="store_true")
    parser.add_argument("--middle-profile", action="store_true")
    parser.add_argument("--tau2-profile", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    if not args.write and not args.check:
        if sum((args.outer_profile, args.middle_profile, args.tau2_profile)) > 1:
            parser.error("select at most one profile mode")
        if args.tau2_profile:
            row = tau2_profile_eight_point(
                HARD_FIXTURES[args.fixture], SOFT_FIXTURE
            )
        elif args.middle_profile:
            row = middle_profile_eight_point(
                HARD_FIXTURES[args.fixture], SOFT_FIXTURE
            )
        elif args.outer_profile:
            row = outer_profile_eight_point(
                HARD_FIXTURES[args.fixture], SOFT_FIXTURE
            )
        else:
            row = correlated_eight_point(HARD_FIXTURES[args.fixture], SOFT_FIXTURE)
        print(json.dumps(row, indent=2, sort_keys=True))
        return 0
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
    print(
        "residue difference:",
        value["correlated_boundary"]["strong_residue_difference"],
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
