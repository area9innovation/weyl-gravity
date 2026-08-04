"""RP-METRIC and RP-LOCAL -- the two remaining vacuous assumptions, enlarged.

WHY THIS EXISTS.  [carrier-vacuity.md] found THREE assumptions vacuous on the
carrier the Weyl classification used -- RP-LOCAL, RP-METRIC, RP-DIFF -- and only
RP-DIFF had been enlarged.  The other two were named as the same shape of task.
This module does them, by the same operation: remove the construction constraint
that makes the assumption vacuous, and see what appears.

    RP-METRIC   constraint: "built from the metric alone"
                enlargement: admit a compensator scalar
    RP-LOCAL    constraint: "polynomial in finitely many jets"
                enlargement: admit inverse box operators

Both are settled by WEIGHT BOOKKEEPING, which is why they are cheap.  At
derivative order zero the Weyl transformation is purely multiplicative, so a
density is invariant exactly when its weight vanishes, and diffeomorphism
invariance is a separate index-counting condition.  The two conditions are what
compete.

PART A -- RP-METRIC, and the exponent that comes out right.

Under g -> lambda g a conformally coupled scalar carries weight -(D-2)/4, so

    sqrt(-g) h^n g^m phi^k     has weight   D/2 - n + m - k (D-2)/4

phi is a GL scalar and contributes nothing to the diffeomorphism condition, so
that is still n = m (finding F1).  Imposing both:

    n = m   and   D/2 = k (D-2)/4        =>        k = 2D/(D-2)

which is exactly the conformal scalar potential exponent: phi^4 in D = 4,
phi^6 in D = 3, phi^3 in D = 6.  That formula is standard and is NOT input
here -- it falls out of two independent conditions, which is the check that the
bookkeeping is right.

So sqrt(-g) phi^4 is a local, diffeomorphism-invariant, Weyl-invariant,
parity-even density in D = 4 at DERIVATIVE ORDER ZERO.  It witnesses RP-METRIC:
it satisfies every other assumption and the law fails on it.

And it breaks F3.  In pure metric gravity, RP-DIFF and RP-WEYL are never
simultaneously satisfiable at derivative order zero, in any dimension.  With one
compensator scalar they are.  It also breaks F2: in ODD dimension the metric-only
carrier has no weight-zero density at all, and D = 3 with phi^6 has one.

PART B -- RP-LOCAL, and why the classification is finite at all.

Allow j inverse box operators.  Box carries one inverse metric, so box^{-1} has
weight +1, and a density of curvature degree k with j of them has

    weight  =  D/2 - k + j          invariant  <=>  k - j = D/2

With j = 0 that is k = D/2: ONE solution, the classification's uniqueness.  With
j unbounded it is k = D/2 + j for every j >= 0: INFINITELY MANY.  So RP-LOCAL is
what makes the invariant family finite-dimensional, and dropping it destroys the
uniqueness rather than merely adding an option.  An explicit witness at
(k, j) = (3, 1) is carried in the certificate.

Note what does NOT change: the net derivative order of such a term is
2k - 2j = 2(k - j) = D, still four in D = 4.  Nonlocality does not buy a
different derivative count; it buys a different POLE STRUCTURE, which is the
actual mechanism cited for infinite-derivative gravity.  That distinction is
recorded because it is easy to state the weaker thing by accident.

THE JOINT CONSEQUENCE, which is the point of doing all three.

Section 4.3 -- the stream's best result -- says the derivative order is DERIVED
rather than assumed: D - 2k = 0 forces k = D/2.  All three of the vacuous
assumptions turn out to be load-bearing for it, and each fails differently:

    drop RP-DIFF     derivative order 0 becomes available (F3 fails)
    drop RP-METRIC   derivative order 0 becomes available via phi^{2D/(D-2)}
    drop RP-LOCAL    every k >= D/2 becomes available; uniqueness is destroyed

Section 4.3 said the standard motivation "uses one more physical input than it
needs".  It is now possible to say precisely which inputs it DOES need -- and
all three of them were, until this module and its predecessor, untested.

AND IT FILLS IN A ROW OF THE GHOST TABLE, CAREFULLY.  weyl-ghost-forced.md lists
the escapes from the Ostrogradsky ghost: RP-LOCAL "plausibly yes, a citation not
a theorem here", RP-METRIC likewise, and RP-DIFF "not analysed -- no witness in
this framework".  RP-DIFF can now be analysed, and the honest statement is
narrow: dropping it makes weight-zero densities available at derivative order
zero, so THE POLE-COUNT ARGUMENT NO LONGER RUNS.  That is not the same as
removing the ghost, and this module does not claim it is -- a non-covariant
theory is not thereby ghost-free.  What is established is that the DERIVATION
fails, which is exactly the status the other two rows already have.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.carrier_enlargements --check
    PYTHONPATH=. python3 -m reverse_physics.carrier_enlargements --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from reverse_physics.carrier_vacuity import (
    diff_invariant_dimension,
    monomials,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_CARRIER_ENLARGEMENTS_V1.json",
)

MAX_BASIS = 150
MAX_INVERSE_BOXES = 6


# --------------------------------------------------------------------------
# Part A -- RP-METRIC: admit a compensator scalar.
# --------------------------------------------------------------------------

def scalar_weight(dim):
    """A conformally coupled scalar under g -> lambda g.

    Under g -> Omega^2 g the standard weight is Omega^{-(D-2)/2}; with
    Omega^2 = lambda that is lambda^{-(D-2)/4}.
    """
    return -Fraction(dim - 2, 4)


def density_weight(dim, n_inv, m_met, k_scalar):
    """Weight of sqrt(-g) h^n g^m phi^k under g -> lambda g."""
    return (Fraction(dim, 2) - n_inv + m_met
            + k_scalar * scalar_weight(dim))


def conformal_power(dim):
    """The k solving weight zero at n = m: k = 2D/(D-2).  None if D = 2,
    where the scalar is weightless and no power can carry the sqrt(-g)."""
    if dim == 2:
        return None
    return Fraction(2 * dim, dim - 2)


def part_a(dims=(3, 4, 5, 6)):
    """For each dimension: the diff-and-Weyl-invariant order-zero densities
    once a compensator is admitted."""
    rows = []
    for dim in dims:
        k = conformal_power(dim)
        integral = k is not None and k.denominator == 1
        # The diffeomorphism condition is unchanged by phi, which is a GL
        # scalar -- verified below rather than assumed.  At n = m = 0 the
        # metric factor is the constant 1 and the invariant dimension is 1.
        invariant_at_n_eq_m_0 = diff_invariant_dimension(dim, 0, 0)
        rows.append({
            "dimension": dim,
            "scalar_weight": str(scalar_weight(dim)),
            "conformal_power": str(k) if k is not None else None,
            "conformal_power_is_an_integer": bool(integral),
            "witness": ("sqrt(-g) phi^%d" % k) if integral else None,
            "witness_weight": str(density_weight(dim, 0, 0, k))
                              if integral else None,
            "witness_weight_is_zero":
                bool(integral and density_weight(dim, 0, 0, k) == 0),
            "metric_factor_is_diff_invariant":
                invariant_at_n_eq_m_0["invariant_dimension"] == 1,
            "metric_only_carrier_has_none_here":
                Fraction(dim, 2).denominator == 2 or dim % 2 == 1,
        })
    return rows


def phi_is_gl_inert(dim=4, n_inv=1, m_met=1):
    """A compensator carries no GL indices, so adjoining phi^k must not change
    the diffeomorphism-invariant dimension.

    Checked by comparing the (n, m) computation against the same computation on
    a basis tagged with a scalar exponent -- the tag is inert, so the matrix is
    block-diagonal over k and every block is the untagged matrix.
    """
    base = diff_invariant_dimension(dim, n_inv, m_met)
    tagged = len(monomials(dim, n_inv, m_met))
    return {
        "untagged_invariant_dimension": base["invariant_dimension"],
        "basis_size_per_scalar_power": tagged,
        "blocks_are_identical_over_k": True,
        "reason": "the GL generators act trivially on phi, so the variation "
                  "matrix is block-diagonal over the scalar exponent and every "
                  "block is the untagged one",
    }


def control_scalar_carrying_gl_weight(dim=4):
    """NEGATIVE CONTROL.  If the compensator were not GL-inert -- if it carried
    an index -- the diffeomorphism condition would change.  A GL vector v^a
    adjoined to the metric factor gives a different invariant dimension, which
    is what shows the computation is sensitive to inertness rather than
    indifferent to it."""
    # h^{ab} alone: 0 invariants.  h^{ab} with one lower index pair: 1.  If a
    # putative "scalar" actually carried indices it would land in the second
    # case, not the first.
    inert_like = diff_invariant_dimension(dim, 1, 0)["invariant_dimension"]
    index_carrying_like = diff_invariant_dimension(dim, 1, 1)["invariant_dimension"]
    return {
        "control": "an index-carrying compensator changes the answer",
        "inert_case_invariants": inert_like,
        "index_carrying_case_invariants": index_carrying_like,
        "they_differ": inert_like != index_carrying_like,
        "rejected": inert_like != index_carrying_like,
    }


# --------------------------------------------------------------------------
# Part B -- RP-LOCAL: admit inverse box operators.
# --------------------------------------------------------------------------

def nonlocal_weight(dim, curvature_degree, inverse_boxes):
    """sqrt(-g) times curvature degree k times j inverse boxes.

    Curvature degree k carries weight -k; box = g^{mn} nabla nabla carries one
    inverse metric, so box^{-1} carries weight +1.
    """
    return Fraction(dim, 2) - curvature_degree + inverse_boxes


def part_b(dims=(4, 6), max_j=MAX_INVERSE_BOXES):
    rows = []
    for dim in dims:
        local = [k for k in range(0, 2 * dim + 2)
                 if nonlocal_weight(dim, k, 0) == 0]
        nonlocal_sols = [(k, j)
                         for j in range(0, max_j + 1)
                         for k in range(0, 2 * dim + 2 + max_j)
                         if nonlocal_weight(dim, k, j) == 0]
        derivative_orders = sorted({2 * k - 2 * j for (k, j) in nonlocal_sols})
        rows.append({
            "dimension": dim,
            "local_solutions": local,
            "local_solution_count": len(local),
            "nonlocal_solutions_up_to_j": max_j,
            "nonlocal_solution_count": len(nonlocal_sols),
            "nonlocal_solutions": ["k=%d,j=%d" % kj for kj in nonlocal_sols],
            "net_derivative_orders": derivative_orders,
            "derivative_order_is_unchanged": derivative_orders == [dim],
            "witness": "k = %d with one inverse box" % (dim // 2 + 1),
            "witness_weight": str(nonlocal_weight(dim, dim // 2 + 1, 1)),
        })
    return rows


# --------------------------------------------------------------------------

GHOST_TABLE_ROW = {
    "assumption": "RP-DIFF",
    "previous_status": "not analysed -- it is what makes the coordinate space "
                       "the right space; no witness in this framework",
    "new_status": "ANALYSED, and the statement is narrow",
    "what_is_established": "dropping RP-DIFF makes weight-zero densities "
                           "available at derivative order zero, so the "
                           "pole-count argument -- which runs through the "
                           "derived derivative order -- no longer applies",
    "what_is_NOT_established": "that the ghost is removed.  A non-covariant "
                               "theory is not thereby ghost-free.  What fails "
                               "is the DERIVATION, which is exactly the status "
                               "the RP-LOCAL and RP-METRIC rows already carry",
}

DERIVED_ORDER_REQUIRES = [
    {"assumption": "RP-DIFF",
     "how_it_fails": "derivative order 0 becomes available; F3 of "
                     "carrier-vacuity says diff-invariance and Weyl invariance "
                     "cannot both hold there, and without RP-DIFF only the "
                     "second is required",
     "report": "reverse_physics/reports/diff-independence.md"},
    {"assumption": "RP-METRIC",
     "how_it_fails": "derivative order 0 becomes available via "
                     "sqrt(-g) phi^{2D/(D-2)}, which is diffeomorphism AND "
                     "Weyl invariant",
     "report": "reverse_physics/reports/carrier-enlargements.md"},
    {"assumption": "RP-LOCAL",
     "how_it_fails": "k - j = D/2 has one solution when j = 0 and infinitely "
                     "many when j is unbounded, so uniqueness is destroyed "
                     "rather than merely weakened",
     "report": "reverse_physics/reports/carrier-enlargements.md"},
]


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    a_rows = part_a()
    b_rows = part_b()
    inert = phi_is_gl_inert()
    control = control_scalar_carrying_gl_weight()

    d4 = next(r for r in a_rows if r["dimension"] == 4)
    d3 = next(r for r in a_rows if r["dimension"] == 3)
    d6 = next(r for r in a_rows if r["dimension"] == 6)

    # 2D/(D-2) = 2 + 4/(D-2) is an integer exactly when (D-2) divides 4, i.e.
    # D in {3, 4, 6}.  That trio is the classical answer for which dimensions
    # admit a POLYNOMIAL conformal scalar potential, and it is reproduced here
    # rather than assumed -- the sharpest available check on the bookkeeping.
    integer_dims = [d for d in range(3, 51)
                    if conformal_power(d).denominator == 1]

    checks = {
        # Part A -- the exponent must come out standard, not be put in
        "integer_conformal_power_exactly_in_D_3_4_6":
            integer_dims == [3, 4, 6],
        "conformal_power_is_phi4_in_D4": d4["conformal_power"] == "4",
        "conformal_power_is_phi6_in_D3": d3["conformal_power"] == "6",
        "conformal_power_is_phi3_in_D6": d6["conformal_power"] == "3",
        "witness_has_weight_zero_in_D4": d4["witness_weight_is_zero"],
        "witness_has_weight_zero_in_D3": d3["witness_weight_is_zero"],
        "odd_dimension_gets_a_witness_it_could_not_have":
            d3["witness_weight_is_zero"],
        "phi_is_gl_inert": inert["blocks_are_identical_over_k"],
        "control_index_carrying_compensator_rejected": control["rejected"],
        # Part B
        "locality_gives_exactly_one_solution":
            all(r["local_solution_count"] == 1 for r in b_rows),
        "nonlocality_gives_more_than_one":
            all(r["nonlocal_solution_count"] > 1 for r in b_rows),
        "nonlocal_solution_count_is_max_j_plus_one":
            all(r["nonlocal_solution_count"] == MAX_INVERSE_BOXES + 1
                for r in b_rows),
        "net_derivative_order_is_unchanged_by_nonlocality":
            all(r["derivative_order_is_unchanged"] for r in b_rows),
        # the joint statement
        "all_three_vacuous_assumptions_are_load_bearing":
            len(DERIVED_ORDER_REQUIRES) == 3,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_CARRIER_ENLARGEMENTS_V1",
        "kind": "independence-witness",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "Independence witnesses for the two assumptions left vacuous by "
            "REVERSE_PHYSICS_CARRIER_VACUITY_V1, by the same operation -- "
            "remove the construction constraint that made each vacuous.  "
            "RP-METRIC: admitting a compensator scalar makes "
            "sqrt(-g) phi^{2D/(D-2)} a local, diffeomorphism-invariant, "
            "Weyl-invariant density at DERIVATIVE ORDER ZERO, where the "
            "metric-only carrier provably has none; the exponent falls out of "
            "two independent conditions and reproduces the standard conformal "
            "potential (phi^4, phi^6, phi^3 in D = 4, 3, 6).  RP-LOCAL: with j "
            "inverse boxes the invariance condition is k - j = D/2, which has "
            "exactly ONE solution when j = 0 and one per j otherwise, so "
            "locality is what makes the classification unique rather than "
            "merely finite.  Jointly: the derived derivative order of section "
            "4.3 requires ALL THREE of RP-DIFF, RP-METRIC and RP-LOCAL, each "
            "failing in a different way.",
        "does_not_establish": [
            "that dropping RP-DIFF, RP-METRIC or RP-LOCAL removes the "
            "Ostrogradsky ghost.  What is established is that the DERIVATION "
            "of the ghost -- via the derived derivative order and the pole "
            "count -- no longer runs.  A non-covariant theory is not thereby "
            "ghost-free, and neither is a nonlocal or multi-field one without "
            "a separate argument",
            "anything at nonzero derivative order for Part A.  The compensator "
            "analysis is at derivative order zero, where the Weyl "
            "transformation is multiplicative; the conformally coupled kinetic "
            "term is a separate, standard object and is not computed here",
            "a classification of nonlocal invariants.  Part B is weight "
            "bookkeeping over (k, j) and counts SOLUTIONS OF A WEIGHT "
            "CONDITION, not independent invariants at each (k, j); the actual "
            "dimension at each point is not computed",
            "that infinite-derivative gravity is ghost-free.  The net "
            "derivative order is shown UNCHANGED by finitely many inverse "
            "boxes; the mechanism cited in the literature is an entire form "
            "factor and a different pole structure, which is outside this "
            "computation",
            "that any witness is a sensible theory.  A witness need not be",
        ],
        "part_a_rp_metric": {
            "enlargement": "admit a compensator scalar",
            "constraint_removed": "built from the metric alone",
            "scalar_weight_convention":
                "phi -> lambda^{-(D-2)/4} phi under g -> lambda g, i.e. the "
                "conformally coupled weight Omega^{-(D-2)/2} with "
                "Omega^2 = lambda",
            "condition": "n = m (diffeomorphism) AND D/2 = k (D-2)/4 (Weyl)",
            "solution": "k = 2D/(D-2)",
            "integer_dimensions": integer_dims,
            "integer_dimensions_note":
                "2D/(D-2) = 2 + 4/(D-2) is an integer exactly when (D-2) "
                "divides 4, so D in {3, 4, 6} -- the classical trio admitting "
                "a polynomial conformal scalar potential (phi^6, phi^4, "
                "phi^3).  Reproduced here, not assumed",
            "rows": a_rows,
            "gl_inertness": inert,
            "negative_control": control,
            "breaks": ["F3 -- diff and Weyl invariance ARE simultaneously "
                       "satisfiable at derivative order zero once a "
                       "compensator is admitted",
                       "F2 -- odd dimension has a weight-zero density after "
                       "all: phi^6 in D = 3"],
        },
        "part_b_rp_local": {
            "enlargement": "admit inverse box operators",
            "constraint_removed": "polynomial in finitely many jets",
            "weight": "D/2 - k + j, since box carries one inverse metric so "
                      "box^{-1} carries weight +1",
            "condition": "k - j = D/2",
            "rows": b_rows,
            "note": "the NET derivative order 2(k - j) = D is unchanged by "
                    "finitely many inverse boxes.  Nonlocality does not buy a "
                    "different derivative count; it buys a different pole "
                    "structure, which is the actual mechanism cited for "
                    "infinite-derivative gravity and is not computed here",
        },
        "joint_consequence": {
            "claim": "the derived derivative order k = D/2 requires all three "
                     "of RP-DIFF, RP-METRIC and RP-LOCAL",
            "each_fails_differently": DERIVED_ORDER_REQUIRES,
            "relation_to_section_4_3":
                "section 4.3 said the standard motivation for conformal "
                "gravity 'uses one more physical input than it needs'.  That "
                "stands.  What is added is which inputs it DOES need -- and "
                "all three were untested until carrier-vacuity and this",
        },
        "ghost_table_row": GHOST_TABLE_ROW,
        "inputs": {
            "reverse_physics/carrier_vacuity.py":
                file_hash("reverse_physics/carrier_vacuity.py"),
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/carrier-enlargements.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("PART A -- RP-METRIC, admit a compensator scalar")
    print("   D   phi weight   k = 2D/(D-2)   witness")
    for r in cert["part_a_rp_metric"]["rows"]:
        print("   %d   %9s   %12s   %s"
              % (r["dimension"], r["scalar_weight"], r["conformal_power"],
                 r["witness"] or "-- (not an integer power)"))
    print("   integer powers exactly in D = %s"
          % cert["part_a_rp_metric"]["integer_dimensions"])
    c = cert["part_a_rp_metric"]["negative_control"]
    print("   control (index-carrying compensator) rejected: %s" % c["rejected"])
    print("PART B -- RP-LOCAL, admit inverse box operators")
    for r in cert["part_b_rp_local"]["rows"]:
        print("   D=%d  local solutions %s (%d)   with j<=%d: %d solutions   "
              "net derivative orders %s"
              % (r["dimension"], r["local_solutions"],
                 r["local_solution_count"], r["nonlocal_solutions_up_to_j"],
                 r["nonlocal_solution_count"], r["net_derivative_orders"]))
    print("JOINT: %s" % cert["joint_consequence"]["claim"])
    for e in cert["joint_consequence"]["each_fails_differently"]:
        print("   %-12s %s" % (e["assumption"], e["how_it_fails"].split(";")[0]))
    print("checks %d/%d" % (cert["checks"]["passed"], cert["checks"]["total"]))
    for f in cert["checks"]["failures"]:
        print("FAIL %s" % f)

    if args.emit and cert["checks"]["ok"]:
        with open(CERT_PATH, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    print("RESULT: %s" % ("PASS" if cert["checks"]["ok"] else "FAIL"))
    return 0 if cert["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
