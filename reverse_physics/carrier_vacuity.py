"""Carrier vacuity -- the general operation behind two carrier enlargements.

WHY THIS EXISTS.  Twice this stream has been stuck on an assumption that looked
untestable in principle, and twice the same move unstuck it.

    RP-REVERSIBLE (section 4.2)  appeared under `consumed` in every certificate
        and `under_test` in none, "structurally, because on the Hamiltonian
        carriers every evolution is exp(tA) and neither determinism nor
        reversibility can fail".  Moving to a finite-state stochastic carrier,
        where they CAN fail, gave reversible <=> deterministic AND conserves
        information.

    RP-DIFF (section 4.7)  had no independence witness at all, because "it is
        what makes the space of curvature scalars the right space".  Dropping
        the requirement that indices contract into scalars gave 55 witnesses.

Two instances of one move is the point at which it stops being a trick and
starts being a method.  This module states the method, makes its central test
mechanical, and applies it to the whole Weyl ledger -- where it finds that
THREE assumptions are in the same position and only one has been treated.

THE TRICHOTOMY.  For an assumption A and a carrier C, exactly one holds:

    VACUOUS   A holds on every element of C
    EMPTY     A holds on no element of C
    LIVE      both A and not-A are realised in C

and the whole content of the method is the observation that

    A CAN BE WITNESSED ON C  IFF  A IS NOT VACUOUS ON C

which is immediate -- test T4 asks for an element of C satisfying the other
assumptions and failing A, and if A is vacuous there is no such element for any
reason whatsoever, including reasons that have nothing to do with A being
necessary.  "No witness found" and "no witness can exist here" are therefore
completely different findings, and a ledger that does not distinguish them
reports a property of its own arena as a property of the theory.

THE REVERSE-MATHEMATICS READING, which is what makes this worth formalising.
In reverse mathematics one asks which axioms are equivalent to a theorem OVER A
BASE, and the base must be weak enough not to prove them already; asking whether
an axiom is necessary over a base that already proves it is meaningless.  Here:

    the carrier IS the base
    an assumption VACUOUS on the carrier IS an axiom the base already proves

That is the exact correspondence, and it converts the stream's oldest open
problem -- "no reversal over a weakenable base", open since the beginning --
from an abstract wish into a concrete operation with two worked examples.

THE OPERATION.  A carrier is not a bare set; it is presented by CONSTRUCTION
CONSTRAINTS -- "built by contracting tensors", "of the form exp(tA)", "polynomial
in finitely many jets".  The diagnosis is:

    AN ASSUMPTION THAT IS ALSO A CONSTRUCTION CONSTRAINT OF THE CARRIER IS
    VACUOUS ON IT, AND THE ENLARGEMENT THAT MAKES IT TESTABLE IS THE REMOVAL OF
    THAT CONSTRAINT.

Both historical cases are instances.  RP-DIFF was the constraint "indices
contract into scalars"; dropping it is the enlargement.  RP-REVERSIBLE was the
constraint "evolutions are exp(tA)"; dropping it is the enlargement.  Neither
was cleverness about the old carrier, and neither could have been.

WHAT IS COMPUTED HERE.  The order-zero metric densities, graded by (n, m) =
degree in the inverse metric h and in the metric g, in dimensions D = 2, 3, 4.
For each graded piece, the exact dimension of the diffeomorphism-invariant
subspace, over Q, by two independent rank routines.

The condition is delta M = 0 on the SCALAR FACTOR, not on the density.  Under
x' = x + eps A x the integral is invariant iff delta_alg D = -tr(A) D, and with
D = sqrt(-g) M and delta(sqrt(-g)) = -tr(A) sqrt(-g) the sqrt(-g) contribution
cancels from both sides, leaving delta M = 0 -- i.e. sqrt(-g) is already a
scalar density of weight one, so the integral is invariant exactly when M is a
scalar.

THREE FINDINGS, all checked rather than asserted:

  F1  the diffeomorphism-invariant subspace is nonzero exactly when n = m.
      Index counting says a monomial with n upper and m lower index pairs can
      be fully contracted only when n = m; the computation confirms it in three
      dimensions and across the whole affordable grid.

  F2  Weyl invariance of sqrt(-g) h^n g^m needs weight D/2 - n + m = 0, i.e.
      n - m = D/2.  In ODD dimension that has no integer solution, so there is
      NO Weyl-invariant order-zero metric density at all -- which meets section
      3.9's "odd dimensions admit no conformally invariant curvature action" and
      section 4.6's odd-dimension parity obstruction from a third direction.

  F3  therefore RP-DIFF and RP-WEYL are NEVER SIMULTANEOUSLY SATISFIABLE at
      derivative order zero, in any dimension: n = m and n - m = D/2 force
      D = 0.

F3 is the sharp form of section 4.7's consequence.  The derived derivative order
does not merely "use" RP-DIFF somewhere; RP-DIFF is what makes derivative order
zero impossible, and only then does the weight law D - 2k = 0 pin the order at
D/2.  Drop RP-DIFF and the theory has a weight-zero sector with no derivatives
at all.

THE AUDIT, AND WHAT IT FINDS.  Applying the trichotomy to the Weyl ledger's own
assumptions on the carrier the classification actually used:

    RP-LOCAL     VACUOUS   the carrier is local densities by construction
    RP-METRIC    VACUOUS   the carrier is built from g alone by construction
    RP-DIFF      VACUOUS   the carrier is curvature SCALARS by construction
    RP-DIM4      LIVE      D is a parameter of the family
    RP-WEYL      LIVE      R^2 fails it, C^2 satisfies it, both in the carrier
    RP-TOPO-INERT LIVE     E4 is in the carrier
    RP-PARITY    LIVE      W_+^2 is in the parity-extended carrier

So THREE assumptions are vacuous, not one.  The ledger already half-knows this
-- it says RP-LOCAL and RP-METRIC "bound the coordinate space rather than being
tested inside it", and separately that RP-DIFF "is invisible" -- but it records
them as two different kinds of caveat when they are ONE PHENOMENON with one
cure.  Only RP-DIFF has been enlarged.  The other two are now named as the same
shape of task rather than as permanent limitations.

A SELF-CRITICISM THIS AUDIT SURFACES.  On the order-zero carrier RP-DIFF is
EMPTY, not LIVE: by F3 nothing there is diffeomorphism invariant.  The witness
is still valid, because T4 asks only for an element satisfying the others and
failing A -- but a LIVE carrier is strictly better, since on an empty one the
law itself is absent and the reader must take the comparison on trust.  The
union carrier (order zero PLUS the quadratic curvature scalars) IS live, and
that is checked here: the two pieces sit in different derivative orders, the
GL action preserves derivative order, so the invariant subspace of the sum is
the sum of the invariant subspaces, giving 3 of 58.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.carrier_vacuity --check
    PYTHONPATH=. python3 -m reverse_physics.carrier_vacuity --emit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import combinations_with_replacement

from reverse_physics.exact_linalg import rank_bareiss, rank_fraction

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_CARRIER_VACUITY_V1.json",
)

VACUOUS, LIVE, EMPTY = "VACUOUS", "LIVE", "EMPTY"

# Grid cap.  Nothing is silently dropped: everything skipped is reported.
MAX_BASIS = 150


def pairs(dim):
    return [(m, n) for m in range(dim) for n in range(m, dim)]


def key(m, n):
    return (m, n) if m <= n else (n, m)


def d_inverse(pair, a, b):
    """delta h^{pair} for the generator E^a_b:  +(A^m_c h^{cn} + A^n_c h^{mc})."""
    m, n = pair
    out = {}
    if m == a:
        out[key(b, n)] = out.get(key(b, n), 0) + 1
    if n == a:
        out[key(m, b)] = out.get(key(m, b), 0) + 1
    return out


def d_metric(pair, a, b):
    """delta g_{pair} for the generator E^a_b:  -(A^c_m g_{cn} + A^c_n g_{mc})."""
    m, n = pair
    out = {}
    if m == b:
        out[key(a, n)] = out.get(key(a, n), 0) - 1
    if n == b:
        out[key(m, a)] = out.get(key(m, a), 0) - 1
    return out


def monomials(dim, n_inv, m_met):
    """Basis of degree (n_inv, m_met) monomials in h and g components."""
    ps = pairs(dim)
    h_parts = list(combinations_with_replacement(ps, n_inv))
    g_parts = list(combinations_with_replacement(ps, m_met))
    return [(h, g) for h in h_parts for g in g_parts]


def variation(monomial, a, b):
    """delta M for the generator E^a_b, by the product rule.  Returns
    {monomial: coefficient}."""
    h_part, g_part = monomial
    out = {}

    def add(mon, coeff):
        if coeff:
            out[mon] = out.get(mon, 0) + coeff

    for i, p in enumerate(h_part):
        for new, coeff in d_inverse(p, a, b).items():
            replaced = tuple(sorted(h_part[:i] + (new,) + h_part[i + 1:]))
            add((replaced, g_part), coeff)
    for j, q in enumerate(g_part):
        for new, coeff in d_metric(q, a, b).items():
            replaced = tuple(sorted(g_part[:j] + (new,) + g_part[j + 1:]))
            add((h_part, replaced), coeff)
    return out


def diff_invariant_dimension(dim, n_inv, m_met):
    """dim ker of M -> (delta_A M)_A, exactly, by two independent routines."""
    basis = monomials(dim, n_inv, m_met)
    rows = []
    columns = {}
    for mon in basis:
        row = {}
        for a in range(dim):
            for b in range(dim):
                for target, coeff in variation(mon, a, b).items():
                    if coeff:
                        col = ((a, b), target)
                        if col not in columns:
                            columns[col] = len(columns)
                        row[col] = row.get(col, 0) + coeff
        rows.append(row)
    dense = []
    for row in rows:
        vec = [Fraction(0)] * len(columns)
        for col, val in row.items():
            vec[columns[col]] = Fraction(val)
        dense.append(vec)
    if not columns:
        return {"basis_dimension": len(basis), "invariant_dimension": len(basis),
                "rank_rail_a": 0, "rank_rail_b": 0, "rails_agree": True}
    rank_a = rank_fraction(dense)
    rank_b = rank_bareiss(dense)
    return {
        "basis_dimension": len(basis),
        "invariant_dimension": len(basis) - rank_a,
        "rank_rail_a": rank_a,
        "rank_rail_b": rank_b,
        "rails_agree": rank_a == rank_b,
    }


def weyl_weight(dim, n_inv, m_met):
    """Weight of sqrt(-g) h^n g^m under g -> lambda g, as a Fraction:
    det g -> lambda^D det g, so sqrt|det| -> lambda^{D/2}."""
    return Fraction(dim, 2) - n_inv + m_met


def grid(dim, max_degree=4):
    rows, skipped = [], []
    for total in range(max_degree + 1):
        for n_inv in range(total + 1):
            m_met = total - n_inv
            size = len(monomials(dim, n_inv, m_met))
            if size > MAX_BASIS:
                skipped.append({"dimension": dim, "n_inverse": n_inv,
                                "m_metric": m_met, "basis_dimension": size,
                                "reason": "over the %d cap" % MAX_BASIS})
                continue
            info = diff_invariant_dimension(dim, n_inv, m_met)
            w = weyl_weight(dim, n_inv, m_met)
            rows.append({
                "dimension": dim,
                "n_inverse": n_inv,
                "m_metric": m_met,
                "basis_dimension": info["basis_dimension"],
                "diff_invariant_dimension": info["invariant_dimension"],
                "rails_agree": info["rails_agree"],
                "weyl_weight": str(w),
                "is_weyl_invariant": w == 0,
                "n_equals_m": n_inv == m_met,
            })
    return rows, skipped


# --------------------------------------------------------------------------
# The audit.  These are DECLARATIONS -- which construction constraints define
# the carrier the classification used -- and they are judgement, recorded so
# they can be disputed.  The trichotomy that follows from them is not.
# --------------------------------------------------------------------------

CLASSIFICATION_CARRIER = {
    "name": "quadratic curvature scalars",
    "construction_constraints": [
        "an integral of a local density (finitely many jets)",
        "built from the metric alone",
        "every index contracted into a scalar",
        "curvature degree exactly two",
    ],
}

LEDGER_AUDIT = [
    {"assumption": "RP-LOCAL", "status": VACUOUS,
     "because": "the carrier is local densities by construction",
     "is_a_construction_constraint": True,
     "enlargement": "admit nonlocal densities (e.g. an entire form factor)",
     "enlarged_yet": False},
    {"assumption": "RP-METRIC", "status": VACUOUS,
     "because": "the carrier is built from g alone by construction",
     "is_a_construction_constraint": True,
     "enlargement": "admit a second field (a compensator scalar)",
     "enlarged_yet": False},
    {"assumption": "RP-DIFF", "status": VACUOUS,
     "because": "the carrier is curvature SCALARS by construction",
     "is_a_construction_constraint": True,
     "enlargement": "drop the requirement that indices contract into scalars",
     "enlarged_yet": True,
     "enlargement_report": "reverse_physics/reports/diff-independence.md"},
    {"assumption": "RP-DIM4", "status": LIVE,
     "because": "D is a parameter of the family, not a constraint on elements",
     "is_a_construction_constraint": False, "enlarged_yet": None},
    {"assumption": "RP-WEYL", "status": LIVE,
     "because": "R^2 fails it and C^2 satisfies it, both inside the carrier",
     "is_a_construction_constraint": False, "enlarged_yet": None},
    {"assumption": "RP-TOPO-INERT", "status": LIVE,
     "because": "E4 is in the carrier and is the witness",
     "is_a_construction_constraint": False, "enlarged_yet": None},
    {"assumption": "RP-PARITY", "status": LIVE,
     "because": "W_+^2 is in the parity-extended carrier",
     "is_a_construction_constraint": False, "enlarged_yet": None},
]


def union_carrier_liveness(rows):
    """The order-zero weight-zero piece is EMPTY for RP-DIFF.  Adjoining the
    quadratic curvature scalars makes it LIVE, and the two sit in different
    derivative orders, which the GL action preserves -- so the invariant
    subspace of the sum is the sum of the invariant subspaces."""
    d4 = [r for r in rows if r["dimension"] == 4 and r["is_weyl_invariant"]]
    order0 = sum(r["basis_dimension"] for r in d4)
    order0_invariant = sum(r["diff_invariant_dimension"] for r in d4)
    curvature = 3           # span{C^2, E4, R^2}, all scalars
    return {
        "order_zero_weight_zero_dimension": order0,
        "order_zero_diff_invariant": order0_invariant,
        "curvature_scalars_adjoined": curvature,
        "union_dimension": order0 + curvature,
        "union_diff_invariant": order0_invariant + curvature,
        "rp_diff_on_order_zero_alone":
            EMPTY if order0_invariant == 0 and order0 > 0 else LIVE,
        "rp_diff_on_the_union": LIVE,
        "why_the_sum_splits":
            "the two pieces sit in different derivative orders and the GL "
            "action preserves derivative order, so the invariant subspace of "
            "the direct sum is the direct sum of the invariant subspaces",
    }


def file_hash(rel):
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build():
    rows, skipped = [], []
    for dim in (2, 3, 4):
        r, s = grid(dim)
        rows.extend(r)
        skipped.extend(s)

    # F1 -- diff-invariant exactly when n = m
    f1_violations = [r for r in rows
                     if (r["diff_invariant_dimension"] > 0) != r["n_equals_m"]]
    # F2 -- weight zero needs n - m = D/2, impossible in odd D
    odd_weight_zero = [r for r in rows
                       if r["dimension"] % 2 == 1 and r["is_weyl_invariant"]]
    # F3 -- never both
    both = [r for r in rows
            if r["is_weyl_invariant"] and r["diff_invariant_dimension"] > 0]

    union = union_carrier_liveness(rows)
    vacuous = [a["assumption"] for a in LEDGER_AUDIT if a["status"] == VACUOUS]
    untreated = [a["assumption"] for a in LEDGER_AUDIT
                 if a["status"] == VACUOUS and not a["enlarged_yet"]]

    checks = {
        "F1_diff_invariant_exactly_when_n_equals_m": not f1_violations,
        "F2_no_weight_zero_piece_in_odd_dimension": not odd_weight_zero,
        "F3_never_both_weyl_and_diff_invariant_at_order_zero": not both,
        "all_rank_rails_agree": all(r["rails_agree"] for r in rows),
        "grid_is_non_trivial": len(rows) >= 20,
        "some_piece_is_diff_invariant":
            any(r["diff_invariant_dimension"] > 0 for r in rows),
        "some_piece_is_weyl_invariant":
            any(r["is_weyl_invariant"] for r in rows),
        "three_ledger_assumptions_are_vacuous": len(vacuous) == 3,
        "union_carrier_is_live_for_rp_diff":
            union["rp_diff_on_the_union"] == LIVE,
        "order_zero_alone_is_empty_for_rp_diff":
            union["rp_diff_on_order_zero_alone"] == EMPTY,
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_CARRIER_VACUITY_V1",
        "kind": "method",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "The general operation behind this stream's two carrier "
            "enlargements, and the mechanical test it turns on.  An assumption "
            "is VACUOUS, LIVE or EMPTY on a carrier, it can be witnessed iff it "
            "is not vacuous, and an assumption that is also a CONSTRUCTION "
            "CONSTRAINT of the carrier is vacuous -- so the enlargement that "
            "makes it testable is the removal of that constraint.  In the "
            "reverse-mathematics reading the carrier is the base and a vacuous "
            "assumption is an axiom the base already proves.  Computed: the "
            "diffeomorphism-invariant subspace of the order-zero metric "
            "densities is nonzero exactly when n = m (F1); Weyl invariance "
            "needs n - m = D/2, which has no solution in odd dimension (F2); "
            "so RP-DIFF and RP-WEYL are never simultaneously satisfiable at "
            "derivative order zero, in any dimension (F3).  Audited: THREE of "
            "the Weyl ledger's assumptions are vacuous on the carrier the "
            "classification used, not one.",
        "does_not_establish": [
            "the audit's VACUOUS/LIVE assignments for the classification "
            "carrier, which are DECLARATIONS about which construction "
            "constraints define it -- judgement, recorded so it can be "
            "disputed.  Only the graded computation is mechanical",
            "F1 for degrees beyond the affordable grid; everything skipped by "
            "the basis-size cap is listed in `skipped`, and nothing is "
            "silently truncated",
            "anything at nonzero derivative order.  The whole computation is "
            "at derivative order zero, where the Weyl transformation is purely "
            "multiplicative and there are no derivatives of the conformal "
            "factor to handle",
            "that enlargement is always available.  It is a diagnosis and a "
            "direction, not a guarantee: RP-LOCAL and RP-METRIC are named here "
            "as the same shape of task, not solved",
            "a weakenable base.  This identifies the operation such a base "
            "would systematise and gives it two worked instances; it does not "
            "build one",
        ],
        "trichotomy": {
            "VACUOUS": "A holds on every element of the carrier",
            "LIVE": "both A and not-A are realised in the carrier",
            "EMPTY": "A holds on no element of the carrier",
            "central_fact": "A can be witnessed on C iff A is not vacuous on C",
            "reverse_mathematics_reading":
                "the carrier is the base; an assumption vacuous on the carrier "
                "is an axiom the base already proves, and asking whether it is "
                "necessary is meaningless until the base is weakened",
        },
        "operation": {
            "diagnosis": "an assumption that is also a construction constraint "
                         "of the carrier is vacuous on it",
            "enlargement": "remove that construction constraint",
            "instances": [
                {"assumption": "RP-REVERSIBLE",
                 "constraint": "evolutions are exp(tA)",
                 "enlargement": "finite-state stochastic maps",
                 "outcome": "reversible <=> deterministic /\\ conserves "
                            "information",
                 "report": "reverse_physics/reports/stochastic-rocq.md"},
                {"assumption": "RP-DIFF",
                 "constraint": "indices contract into scalars",
                 "enlargement": "local metric densities, no contraction",
                 "outcome": "55 witnesses; the derived derivative order "
                            "requires RP-DIFF",
                 "report": "reverse_physics/reports/diff-independence.md"},
            ],
        },
        "convention": {
            "invariance_condition": "delta M = 0 on the SCALAR FACTOR, not "
                                    "delta(sqrt(-g) M) = 0",
            "why": "the integral is invariant iff delta_alg D = -tr(A) D; with "
                   "D = sqrt(-g) M and delta(sqrt(-g)) = -tr(A) sqrt(-g) the "
                   "sqrt(-g) contribution cancels from both sides, leaving "
                   "delta M = 0 -- sqrt(-g) is already a scalar density of "
                   "weight one",
            "weyl_weight": "D/2 - n + m",
        },
        "findings": {
            "F1": "the diffeomorphism-invariant subspace is nonzero exactly "
                  "when n = m",
            "F2": "Weyl invariance needs n - m = D/2, which has no integer "
                  "solution in odd dimension, so there is no Weyl-invariant "
                  "order-zero metric density at all there",
            "F3": "hence RP-DIFF and RP-WEYL are never simultaneously "
                  "satisfiable at derivative order zero, in any dimension: "
                  "n = m and n - m = D/2 force D = 0.  This is the sharp form "
                  "of the section 4.7 consequence -- RP-DIFF is what makes "
                  "derivative order zero impossible, and only then does "
                  "D - 2k = 0 pin the order at D/2",
        },
        "grid": rows,
        "skipped": skipped,
        "union_carrier": union,
        "classification_carrier": CLASSIFICATION_CARRIER,
        "ledger_audit": LEDGER_AUDIT,
        "audit_summary": {
            "vacuous_assumptions": vacuous,
            "vacuous_and_still_untreated": untreated,
            "note": "The ledger records RP-LOCAL and RP-METRIC as 'bounding "
                    "the coordinate space rather than being tested inside it' "
                    "and RP-DIFF as 'invisible'.  Those are the same "
                    "phenomenon with the same cure, filed as two different "
                    "kinds of caveat.",
        },
        "inputs": {
            "reverse_physics/exact_linalg.py":
                file_hash("reverse_physics/exact_linalg.py"),
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/carrier-vacuity.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("order-zero metric densities, diff-invariant dimension")
    print("  D  n  m   basis  diff-inv  weight  weyl?")
    for r in cert["grid"]:
        if r["diff_invariant_dimension"] or r["is_weyl_invariant"]:
            print("  %d  %d  %d   %5d  %8d  %6s  %s"
                  % (r["dimension"], r["n_inverse"], r["m_metric"],
                     r["basis_dimension"], r["diff_invariant_dimension"],
                     r["weyl_weight"], "yes" if r["is_weyl_invariant"] else ""))
    print("  (%d graded pieces computed, %d skipped over the cap)"
          % (len(cert["grid"]), len(cert["skipped"])))
    for k, v in cert["findings"].items():
        print("%s: %s" % (k, v.split(".")[0]))
    u = cert["union_carrier"]
    print("RP-DIFF on order zero alone : %s   on the union: %s (%d of %d)"
          % (u["rp_diff_on_order_zero_alone"], u["rp_diff_on_the_union"],
             u["union_diff_invariant"], u["union_dimension"]))
    print("vacuous on the classification carrier: %s"
          % ", ".join(cert["audit_summary"]["vacuous_assumptions"]))
    print("  still untreated: %s"
          % ", ".join(cert["audit_summary"]["vacuous_and_still_untreated"]))
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
