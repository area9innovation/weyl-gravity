"""D = 6, the cubic sector: the method scales, the UNIQUENESS does not.

WHY THIS EXISTS.  OVERVIEW.md section 8 declares this gate:

    "Six derivatives in six dimensions.  The weight argument says the
     conformally invariant curvature degree is k = D/2, so odd dimensions have
     no such sector at all and D = 6 selects the CUBIC one.  Running the same
     exact linear algebra there tests whether the method scales and whether the
     parity result has an analogue.  Declared as WEYL_ACTION_SIX_DERIVATIVE_D6."

It is the last item on the list of things this stream said it would do and had
not.  The answer is more interesting than "it scales", and it is partly a
negative.

WHAT THE WEIGHT LAW DETERMINES, AND IT IS DIMENSION-GENERAL.  D - 2k = 0 selects
the curvature degree k = D/2: exactly ONE degree in each even dimension, and NONE
in odd dimension, where D/2 is not an integer.  Scanned to D = 12 here.  The same
line excludes the cosmological term (k = 0) unless D = 0 and Einstein-Hilbert
(k = 1) unless D = 2, in every dimension.  All of that scales, and all of it is
computed.

D = 2 IS A DEGENERATE HIT.  There k = 1 and the selected Lagrangian is
sqrt(-g) R -- which in two dimensions is the Euler density, hence topological.
So the invariant sector is nonempty but DYNAMICALLY EMPTY.  The weight law finds
a degree there and there is no theory at it.  Recorded because "the law selects a
degree" and "there is an action" are different statements, and D = 2 is where
they first come apart.

WHAT THE WEIGHT LAW DOES NOT DETERMINE, AND THIS IS THE FINDING.  It fixes the
DEGREE.  It says nothing about HOW MANY INDEPENDENT INVARIANTS SIT AT THAT
DEGREE, and that number is not 1 in general:

    D = 4, k = 2   the parity-even space {Riem^2, Ric^2, R^2} is 3-dimensional,
                   Weyl invariance is the single equation a + b + 3c = 0, the
                   solution space is span{C^2, E4}, and modulo the topological
                   E4 the quotient is ONE-DIMENSIONAL.  Computed, in this
                   stream (REVERSE_PHYSICS_WEYL_ACTION_V1).

    D = 6, k = 3   the conformally invariant cubic Lagrangians modulo
                   topological terms are THREE-DIMENSIONAL -- the three type-B
                   invariants I_1, I_2, I_3, alongside the type-A Euler density
                   E_6.  CITED, not computed here.

So "exactly one DEGREE" does NOT mean "exactly one ACTION".  The uniqueness that
this entire ledger rests on -- the thing that makes the Weyl action canonical,
that makes the ghost untunable because there is no other conformal action -- IS
SPECIAL TO FOUR DIMENSIONS.  The method scales; the conclusion does not.

WHY THAT MATTERS HERE RATHER THAN BEING A CURIOSITY.  weyl-ghost-forced.md argues
that the ghost cannot be tuned away BECAUSE THE ACTION IS UNIQUE: "there is no
other conformal action", so every proposal of the form 'take conformal gravity
but modify the curvature terms' is dead on arrival.  That argument is a
D = 4 argument.  In D = 6 there ARE other conformal actions -- a three-parameter
family -- so the ghost-forcing argument's SECOND step fails there even though its
first step (the pole count from D - 2k = 0) does not.  The existing table already
records that D = 6 is "worse" for the pole count; what is added is that it is
also different in kind, because uniqueness is gone.

WHAT BLOCKS COMPUTING THE D = 6 COUNT HERE, NAMED RATHER THAN GLOSSED.  The D = 4
classification is a rank computation over a THREE-DIMENSIONAL coordinate space
whose basis this stream wrote down.  The cubic analogue needs a basis of cubic
curvature invariants modulo total derivatives and dimension-dependent identities,
which this stream does not have and which is a substantial separate build -- the
Bianchi reductions alone are the bulk of the work.  Until that exists the D = 6
count is a citation, and it is marked CITED throughout.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.weyl_action_d6 --check
    PYTHONPATH=. python3 -m reverse_physics.weyl_action_d6 --emit
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_WEYL_ACTION_D6_V1.json",
)


def selected_degree(dim):
    """D - 2k = 0.  Returns the Fraction k = D/2."""
    return Fraction(dim, 2)


def scan(max_dim=12):
    rows = []
    for dim in range(2, max_dim + 1):
        k = selected_degree(dim)
        integral = k.denominator == 1
        rows.append({
            "dimension": dim,
            "selected_degree": str(k),
            "degree_is_an_integer": integral,
            "derivative_order": str(2 * k) if integral else None,
            "has_a_conformal_curvature_sector": integral,
            "excludes_cosmological_term": k != 0,
            "excludes_einstein_hilbert": k != 1,
        })
    return rows


# What sits AT the selected degree.  D = 4 is computed in this stream; D = 6 is
# cited.  The distinction is the point of the middle column.
AT_THE_DEGREE = [
    {
        "dimension": 4,
        "degree": 2,
        "parity_even_coordinate_space": 3,
        "coordinate_basis": "{Riem^2, Ric^2, R^2}",
        "invariance_condition": "a + b + 3c = 0, a single linear equation",
        "invariant_subspace": 2,
        "invariant_basis": "span{C^2, E4}",
        "topological_subspace": 1,
        "quotient": 1,
        "status": "COMPUTED",
        "source": "REVERSE_PHYSICS_WEYL_ACTION_V1",
    },
    {
        "dimension": 6,
        "degree": 3,
        "parity_even_coordinate_space": None,
        "coordinate_basis": "a basis of cubic curvature invariants modulo "
                            "total derivatives and dimension-dependent "
                            "identities -- NOT held by this stream",
        "invariance_condition": None,
        "invariant_subspace": None,
        "invariant_basis": "the three type-B invariants I_1, I_2, I_3",
        "topological_subspace": 1,
        "topological_basis": "the type-A Euler density E_6",
        "quotient": 3,
        "status": "CITED",
        "literature": [
            "Bonora, Pasti & Bregola, Class. Quantum Grav. 3 (1986) 635",
            "Deser & Schwimmer, Phys. Lett. B309 (1993) 279",
        ],
    },
]

BLOCKER = {
    "what": "a basis of cubic curvature invariants modulo total derivatives and "
            "dimension-dependent identities",
    "why_it_is_needed": "the D = 4 classification is a rank computation over a "
                        "three-dimensional coordinate space whose basis this "
                        "stream wrote down; the cubic analogue needs the same "
                        "thing one degree up",
    "why_it_is_not_cheap": "the Bianchi reductions are the bulk of the work, "
                           "and dimension-dependent identities enter at cubic "
                           "order in a way they do not at quadratic",
    "consequence": "until it exists the D = 6 count is a CITATION and is marked "
                   "so throughout",
}


def build():
    rows = scan()
    even = [r for r in rows if r["degree_is_an_integer"]]
    odd = [r for r in rows if not r["degree_is_an_integer"]]
    by_dim = {a["dimension"]: a for a in AT_THE_DEGREE}

    d2 = next(r for r in rows if r["dimension"] == 2)

    checks = {
        # the weight law, dimension-general and computed
        "a_degree_exists_exactly_in_even_dimension":
            all(r["dimension"] % 2 == 0 for r in even)
            and all(r["dimension"] % 2 == 1 for r in odd),
        "the_degree_is_D_over_2":
            all(Fraction(r["selected_degree"]) == Fraction(r["dimension"], 2)
                for r in rows),
        "the_derivative_order_equals_the_dimension":
            all(Fraction(r["derivative_order"]) == r["dimension"]
                for r in even),
        "the_cosmological_term_is_excluded_everywhere_scanned":
            all(r["excludes_cosmological_term"] for r in rows),
        "einstein_hilbert_is_excluded_except_in_D2":
            all(r["excludes_einstein_hilbert"] for r in rows
                if r["dimension"] != 2)
            and not d2["excludes_einstein_hilbert"],
        "the_scan_is_non_trivial": len(rows) >= 10,
        # what sits at the degree
        "D4_is_computed_in_this_stream":
            by_dim[4]["status"] == "COMPUTED",
        "D4_quotient_is_one": by_dim[4]["quotient"] == 1,
        "D6_is_cited_not_computed": by_dim[6]["status"] == "CITED",
        "D6_carries_literature": bool(by_dim[6].get("literature")),
        # the finding
        "uniqueness_does_not_scale":
            by_dim[6]["quotient"] != by_dim[4]["quotient"],
        "the_blocker_is_named": bool(BLOCKER["what"]),
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_WEYL_ACTION_D6_V1",
        "kind": "scaling-test",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "The declared D = 6 gate, answered partly and honestly.  COMPUTED "
            "and dimension-general: D - 2k = 0 selects exactly one curvature "
            "degree k = D/2 in each EVEN dimension and none in odd, the "
            "derivative order there equals the dimension, and the same line "
            "excludes the cosmological term everywhere and Einstein-Hilbert "
            "everywhere but D = 2.  D = 2 is a DEGENERATE HIT: the selected "
            "Lagrangian sqrt(-g) R is the two-dimensional Euler density, so the "
            "sector is nonempty but dynamically empty.  THE FINDING: the weight "
            "law fixes the DEGREE and says nothing about how many independent "
            "invariants sit at it.  At D = 4 the quotient is ONE-dimensional "
            "(computed in this stream); at D = 6 it is THREE-dimensional (the "
            "type-B invariants I_1, I_2, I_3 alongside the type-A Euler "
            "density, CITED).  So 'exactly one DEGREE' does not mean 'exactly "
            "one ACTION', and THE UNIQUENESS THIS LEDGER RESTS ON IS SPECIAL TO "
            "FOUR DIMENSIONS.  The method scales; the conclusion does not.",
        "does_not_establish": [
            "the D = 6 count.  It is CITED to the literature, not computed "
            "here, and is marked CITED throughout.  What blocks it is named: "
            "this stream has no basis of cubic curvature invariants modulo "
            "total derivatives and dimension-dependent identities",
            "anything about the D = 6 PARITY sector.  The gate asked whether "
            "the parity result has an analogue and that is not answered -- it "
            "needs the same missing basis",
            "that the ghost-forcing argument fails in D = 6.  What is "
            "established is that its SECOND step -- 'there is no other "
            "conformal action' -- is a D = 4 statement.  The first step, the "
            "pole count from D - 2k = 0, is dimension-general and the existing "
            "table already records D = 6 as worse for it",
            "any classification in D > 6, where the same blocker applies a "
            "fortiori",
        ],
        "the_gate": {
            "declared_in": "reverse_physics/reports/OVERVIEW.md section 8",
            "name": "WEYL_ACTION_SIX_DERIVATIVE_D6",
            "asked": "whether the method scales, and whether the parity result "
                     "has an analogue",
            "answered": "the method scales and the UNIQUENESS does not; the "
                        "parity question is not answered and needs the same "
                        "missing basis",
        },
        "weight_law_scan": rows,
        "at_the_selected_degree": AT_THE_DEGREE,
        "degenerate_hit": {
            "dimension": 2,
            "what": "k = 1, so the selected Lagrangian is sqrt(-g) R, which in "
                    "two dimensions is the Euler density and hence "
                    "topological",
            "reading": "the invariant sector is nonempty but DYNAMICALLY "
                       "EMPTY.  'The law selects a degree' and 'there is an "
                       "action' are different statements, and D = 2 is where "
                       "they first come apart",
        },
        "consequence_for_the_ghost_argument": {
            "what_weyl_ghost_forced_says": "the ghost cannot be tuned away "
                                           "BECAUSE the action is unique -- "
                                           "'there is no other conformal "
                                           "action' -- so every proposal to "
                                           "modify the curvature terms is dead "
                                           "on arrival",
            "what_changes_at_D6": "there ARE other conformal actions, a "
                                  "three-parameter family, so that second step "
                                  "fails.  The first step, the pole count, is "
                                  "dimension-general and unaffected",
            "not_a_correction": "the existing argument is stated at D = 4 and "
                                "is correct there.  What is added is that its "
                                "uniqueness step does not travel",
        },
        "blocker": BLOCKER,
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/weyl-action-d6.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("weight law D - 2k = 0, scanned:")
    print("   D    k     order   sector?")
    for r in cert["weight_law_scan"]:
        print("  %2d  %5s  %6s   %s"
              % (r["dimension"], r["selected_degree"],
                 r["derivative_order"] or "--",
                 "yes" if r["has_a_conformal_curvature_sector"] else "no"))
    print("at the selected degree:")
    for a in cert["at_the_selected_degree"]:
        print("   D=%d k=%d  quotient %s  [%s]"
              % (a["dimension"], a["degree"], a["quotient"], a["status"]))
    print("FINDING: one DEGREE does not mean one ACTION -- uniqueness is "
          "special to D = 4")
    print("blocker: %s" % cert["blocker"]["what"])
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
