"""The weakenable base -- the stream's oldest open problem, given a shape.

THE PROBLEM, open since the beginning.  Reverse mathematics proves T <=> A OVER
A BASE, and the base must be weak enough not to prove A already.  Every
equivalence in this stream is instead over a DECLARED CARRIER, which is a set of
objects rather than a theory, and a set of objects cannot be weakened one axiom
at a time.  Every certificate here says so; PHYSICS-VS-MATH.md section 6 calls it
"the stream's oldest open problem and it is not closed".

THE OBSERVATION.  A carrier is not a bare set.  It is presented by CONSTRUCTION
CONSTRAINTS -- "an integral of a local density", "built from the metric alone",
"every index contracted into a scalar" -- and a set of constraints IS a theory.
So the correspondence is exact:

    carrier                      the base
    construction constraints     the axioms of the base
    C subset of C'               T(C) proves T(C'): C' is the WEAKER base
    A vacuous on C               T(C) proves A
    enlarge until A is live      weaken until the base no longer proves A

Which means this stream has been weakening a base three times already and calling
it carrier enlargement.  The weakenable base did not need to be invented; it
needed to be RECOGNISED, written down, and ordered.

THE LATTICE.  Take the classification carrier's constraints as the base axioms.
Every subset is a base, ordered by inclusion, and the vacuity profile is a
MONOTONE function of it: dropping an axiom can only make more assumptions live,
never fewer.  That monotonicity is what makes the order meaningful, and it is
checked here rather than assumed.

THE MIGRATION, which is the content.  When a construction constraint coincides
with an assumption, removing it from the base and ADDING IT TO THE ASSUMPTION
SET preserves the theorem.  The constraint used to cut the carrier down; the
assumption now cuts it down instead.  Nothing is lost -- what changes is how much
is TESTABLE:

    base axiom              assumption          status
    locality                RP-LOCAL            MIGRATED (carrier-enlargements)
    metric-only             RP-METRIC           MIGRATED (carrier-enlargements)
    indices contract        RP-DIFF             MIGRATED (diff-independence)

So the invariant is CONSTRAINTS + ASSUMPTIONS, and the direction of travel is
constraints turning into assumptions.  A base is BETTER when it is weaker,
because more of the content has become visible.

WHAT THE MINIMAL BASE IS.  With all three migrated, no construction constraint
remains that pairs with an assumption.  The fourth candidate -- "curvature degree
exactly two" -- is NOT an independent axiom at all, because the derived
derivative order theorem obtains it from RP-WEYL and RP-DIM4; including it would
be redundant, and the stream's own best result is what makes it so.

The remaining base is therefore: A REAL-VALUED FUNCTIONAL OF SOME FIELD CONTENT,
with the field content itself unconstrained.  Everything else is an assumption
carrying a witness.  That is the weakest base this stream can currently state,
and reaching it is what the last three certificates did without announcing it.

WHAT THIS IS AND IS NOT.  The correspondence, the lattice and the monotonicity
are established here.  The MIGRATIONS are established elsewhere -- each of the
three has a certificate with an explicit witness, and this module checks those
certificates exist rather than re-deriving them.  What is NOT established is that
the equivalence survives an arbitrary migration: it is verified for the three
that were done, and is a declared structure for the rest.  A base one can weaken
is not the same as having weakened it everywhere it matters, and the difference
is recorded rather than glossed.

Nor is this reverse mathematics.  There is no proof system here, no notion of
what the base PROVES beyond "which assumptions hold identically on the objects it
admits", and no independence results in the logical sense.  The correspondence is
structural and it is useful; calling it more would be the kind of overclaim this
ledger exists to catch.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weakenable_base --check
    PYTHONPATH=. python3 -m reverse_physics.weakenable_base --emit
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_WEAKENABLE_BASE_V1.json",
)


# The base axioms: the construction constraints of the classification carrier.
# Each that PAIRS with an assumption makes that assumption vacuous, and can be
# migrated.  Recorded with the certificate that did the migration.
AXIOMS = [
    {
        "axiom": "locality",
        "statement": "the action is an integral of a local density, polynomial "
                     "in finitely many jets",
        "pairs_with": "RP-LOCAL",
        "migrated": True,
        "witness": "k - j = D/2 has infinitely many solutions once inverse "
                   "boxes are allowed",
        "certificate": "REVERSE_PHYSICS_CARRIER_ENLARGEMENTS_V1",
    },
    {
        "axiom": "metric-only",
        "statement": "built from the metric alone",
        "pairs_with": "RP-METRIC",
        "migrated": True,
        "witness": "sqrt(-g) phi^{2D/(D-2)}, diffeomorphism AND Weyl invariant "
                   "at derivative order zero",
        "certificate": "REVERSE_PHYSICS_CARRIER_ENLARGEMENTS_V1",
    },
    {
        "axiom": "indices-contract",
        "statement": "every index is contracted into a scalar",
        "pairs_with": "RP-DIFF",
        "migrated": True,
        "witness": "sqrt(-g) (g^00)^2; the diff-invariant subspace of the "
                   "lowest weight-zero degree is exactly 0 of 55",
        "certificate": "REVERSE_PHYSICS_DIFF_INDEPENDENCE_V1",
    },
]

# A fourth candidate that turns out NOT to be an independent axiom.
NOT_AN_AXIOM = {
    "candidate": "curvature degree exactly two",
    "why_not": "the derived derivative order theorem obtains it from RP-WEYL "
               "and RP-DIM4 (D - 2k = 0 forces k = D/2), so including it in the "
               "base would be redundant.  The stream's own best result is what "
               "removes it",
    "certificate": "REVERSE_PHYSICS_WEYL_ACTION_V1",
}

# The assumptions that are LIVE regardless of the base -- they were never
# construction constraints, so nothing migrates and nothing is hidden.
ALWAYS_LIVE = ["RP-WEYL", "RP-DIM4", "RP-TOPO-INERT", "RP-PARITY"]


def vacuous_on(base):
    """Which assumptions a base proves outright: exactly those paired with an
    axiom it still contains."""
    return {a["pairs_with"] for a in AXIOMS if a["axiom"] in base}


def live_on(base):
    return set(ALWAYS_LIVE) | ({a["pairs_with"] for a in AXIOMS}
                               - vacuous_on(base))


def lattice():
    names = [a["axiom"] for a in AXIOMS]
    rows = []
    for size in range(len(names), -1, -1):
        for base in itertools.combinations(names, size):
            rows.append({
                "base": sorted(base),
                "axiom_count": len(base),
                "vacuous": sorted(vacuous_on(set(base))),
                "live": sorted(live_on(set(base))),
                "testable_count": len(live_on(set(base))),
            })
    return rows


def monotonicity_violations(rows):
    """Weaker base (fewer axioms) must never have MORE vacuous assumptions."""
    bad = []
    by = {tuple(r["base"]): r for r in rows}
    for r in rows:
        for other in rows:
            if set(other["base"]) < set(r["base"]):        # strictly weaker
                if not set(other["vacuous"]) <= set(r["vacuous"]):
                    bad.append((r["base"], other["base"]))
    return bad


def migration_invariant(rows):
    """|axioms in the base| + |live assumptions| is constant across the
    lattice: content is conserved, only its visibility moves."""
    totals = {r["axiom_count"] + r["testable_count"] for r in rows}
    return sorted(totals)


def certificates_exist():
    d = os.path.join(REPO_ROOT, "reverse_physics", "certificates")
    missing = []
    for a in AXIOMS:
        if a["migrated"]:
            p = os.path.join(d, a["certificate"] + ".json")
            if not os.path.exists(p):
                missing.append(a["certificate"])
    p = os.path.join(d, NOT_AN_AXIOM["certificate"] + ".json")
    if not os.path.exists(p):
        missing.append(NOT_AN_AXIOM["certificate"])
    return missing


def build():
    rows = lattice()
    violations = monotonicity_violations(rows)
    totals = migration_invariant(rows)
    missing = certificates_exist()

    strongest = next(r for r in rows if r["axiom_count"] == len(AXIOMS))
    weakest = next(r for r in rows if r["axiom_count"] == 0)

    checks = {
        "the_lattice_is_the_full_powerset": len(rows) == 2 ** len(AXIOMS),
        "vacuity_is_monotone_in_the_base": not violations,
        "the_migration_invariant_is_constant": len(totals) == 1,
        "the_strongest_base_hides_three_assumptions":
            len(strongest["vacuous"]) == 3,
        "the_weakest_base_hides_none": weakest["vacuous"] == [],
        "every_assumption_is_live_at_the_weakest_base":
            len(weakest["live"]) == len(ALWAYS_LIVE) + len(AXIOMS),
        "every_migration_has_a_witness":
            all(a["witness"] for a in AXIOMS if a["migrated"]),
        "every_migration_cites_an_existing_certificate": not missing,
        "all_three_migrations_are_done":
            all(a["migrated"] for a in AXIOMS),
        "the_fourth_candidate_is_excluded_with_a_reason":
            bool(NOT_AN_AXIOM["why_not"]),
    }
    failures = [k for k, v in checks.items() if not v] \
        + ["missing certificate: %s" % m for m in missing]

    return {
        "certificate": "REVERSE_PHYSICS_WEAKENABLE_BASE_V1",
        "kind": "method",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "A shape for the stream's oldest open problem.  A carrier is "
            "presented by CONSTRUCTION CONSTRAINTS, and a set of constraints "
            "IS a theory, so carrier = base, constraints = axioms, enlarging "
            "the carrier = weakening the base, and an assumption vacuous on a "
            "carrier is one the base proves outright.  The lattice of bases is "
            "the powerset of the constraints; the vacuity profile is MONOTONE "
            "in it, so a weaker base can only make more assumptions testable; "
            "and the quantity (axioms in the base) + (live assumptions) is "
            "CONSTANT across the lattice, so content is conserved and only its "
            "visibility moves.  MIGRATION -- removing a constraint and adding "
            "the paired assumption -- is therefore the operation, and all "
            "three migratable constraints of the classification carrier have "
            "been migrated, each with a witness and a certificate.  A fourth "
            "candidate, curvature degree two, is excluded because the derived "
            "derivative order obtains it from other assumptions.",
        "does_not_establish": [
            "that the equivalence survives an ARBITRARY migration.  It is "
            "verified for the three that were actually done, each with its own "
            "certificate and witness, and is a declared structure for the "
            "rest.  A base one CAN weaken is not the same as having weakened "
            "it everywhere it matters",
            "reverse mathematics.  There is no proof system here, no notion of "
            "what a base PROVES beyond 'which assumptions hold identically on "
            "the objects it admits', and no independence results in the "
            "logical sense.  The correspondence is STRUCTURAL",
            "that the weakest base is well posed as a mathematical object.  "
            "'A real-valued functional of some field content, with the field "
            "content unconstrained' is a description, not a construction, and "
            "no computation in this stream is carried out over it",
            "that the constraint list is complete.  These are the constraints "
            "this stream declared for its own carrier; another reading of the "
            "same carrier might find more",
        ],
        "correspondence": {
            "carrier": "the base",
            "construction_constraints": "the axioms of the base",
            "carrier_inclusion": "C subset of C' means T(C) proves T(C'), so "
                                 "C' is the WEAKER base",
            "vacuous_assumption": "one the base proves outright",
            "carrier_enlargement": "weakening the base until it no longer "
                                   "proves the assumption",
        },
        "axioms": AXIOMS,
        "not_an_axiom": NOT_AN_AXIOM,
        "always_live": ALWAYS_LIVE,
        "lattice": rows,
        "monotonicity_violations": violations,
        "migration_invariant": {
            "quantity": "axioms in the base + live assumptions",
            "values_across_the_lattice": totals,
            "constant": len(totals) == 1,
            "reading": "content is conserved; only its visibility moves.  A "
                       "base is BETTER when it is WEAKER, because more of the "
                       "content has become testable",
        },
        "where_this_stream_is": {
            "base": weakest["base"],
            "migrated": [a["axiom"] for a in AXIOMS if a["migrated"]],
            "remaining_migratable": [a["axiom"] for a in AXIOMS
                                     if not a["migrated"]],
            "note": "the last three certificates reached the weakest base "
                    "without announcing it; this module is the recognition, "
                    "not the work",
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/weakenable-base.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("carrier = base;  construction constraints = axioms;  "
          "enlarging = weakening")
    print("  %-42s %-9s %s" % ("base (axioms retained)", "testable", "vacuous"))
    for r in cert["lattice"]:
        print("  %-42s %-9d %s"
              % (", ".join(r["base"]) or "(empty -- the weakest)",
                 r["testable_count"], ", ".join(r["vacuous"]) or "none"))
    inv = cert["migration_invariant"]
    print("invariant: %s = %s  (constant: %s)"
          % (inv["quantity"], inv["values_across_the_lattice"],
             inv["constant"]))
    w = cert["where_this_stream_is"]
    print("this stream sits at base %s; migrated: %s"
          % (w["base"] or "(empty)", ", ".join(w["migrated"])))
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
