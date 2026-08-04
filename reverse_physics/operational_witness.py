"""One witness with operational content -- states, evolution, and a measurement.

WHY THIS EXISTS.  The sharpest criticism the Assumptions of Physics programme
would make of this stream is that OUR CARRIERS HAVE NO OPERATIONAL CONTENT.
Their framework is rooted in EXPERIMENTAL VERIFIABILITY -- a statement is
physical only if a finite procedure can confirm it in finite time -- and the
topology and sigma-algebras are built from that.  Our witnesses are Lagrangian
densities.  `sqrt(-g) (g^00)^2` is a perfectly good local functional and a
perfectly bad physical system: it has no states, no evolution, and nothing to
measure.  Their version of our T4 would ask WHAT EXPERIMENT DISTINGUISHES THE
WITNESS, and we had no answer.

This does it once, for one witness, to find out whether the bridge is buildable
at all.  Doing it once is worth more than arguing about it, either way.

THE WITNESS TO PICK.  Not a Lagrangian density -- those are the ones with no
operational content, and dressing them up would be pretending.  The right one is
the Krein family from REVERSE_PHYSICS_GHOST_HARMLESS_V1, because it already HAS
what is needed:

    STATES      rays in a two-dimensional complex space carrying the indefinite
                form eta = diag(1,-1) -- one positive-norm and one
                negative-norm direction, the minimal ghost
    EVOLUTION   U(t) = exp(-i H t) with H(a,d,b) = [[a,b],[-b,d]], the general
                eta-pseudo-Hermitian generator
    OBSERVABLE  the squared amplitude of an evolved state, |U(t) e_1|^2

THE MEASUREMENT.  Computed exactly, the three regimes of the harmlessness
criterion are three OPERATIONALLY DISTINCT behaviours:

    Delta > 0   |U e_1|^2 = 25/9 - (16/9) cos 3t     BOUNDED, oscillatory
    Delta = 0   |U e_1|^2 = 2 t^2 + 1                 SECULAR, polynomial
    Delta < 0   |U e_1|^2 = (4/3) cosh(sqrt3 t) - 1/3 EXPONENTIAL

Note that the two FAILURE modes differ from each other.  Diagonalizability and
real spectrum are independent conditions in the algebra, and the independence is
visible in the laboratory: losing diagonalizability gives polynomial growth,
losing reality gives exponential growth.  The exponential RATE does not separate
bounded from secular -- both are zero -- so boundedness has to be asked
separately, which is the operational shadow of the same independence.

THE FINDING, AND IT IS IN THEIR CURRENCY.  In their framework a verifiable
statement is one a finite procedure confirms in finite time, and verifiable
statements are the OPEN sets.  Ask which regimes are verifiable, by each of the
two modalities available:

  BY WATCHING THE TRAJECTORY.  "The amplitude exceeds X by time T" is finitely
  verifiable.  So Delta < 0 and Delta = 0 are verifiable -- both grow without
  bound, so any threshold is crossed in finite time.  Delta > 0 is NOT: "stays
  bounded forever" cannot be confirmed by any finite observation.  It is
  refutable, not verifiable.

  BY MEASURING THE PARAMETERS.  Delta > 0 and Delta < 0 are OPEN conditions on
  (a,d,b), so finite-precision measurement suffices to confirm either.  Delta = 0
  is CLOSED WITH EMPTY INTERIOR -- a measure-zero set -- so no finite-precision
  measurement can ever confirm it.

Putting the two together:

                        by parameters      by trajectory
    Delta > 0 harmless      YES (open)         NO (needs forever)
    Delta = 0 exceptional   NO (measure zero)  YES (grows)
    Delta < 0 unstable      YES (open)         YES (grows)

EVERY REGIME IS VERIFIABLE BY AT LEAST ONE MODALITY, NO MODALITY VERIFIES ALL
THREE, AND THE TWO THAT MATTER MOST NEED DIFFERENT ONES.  Harmlessness is
confirmable only from the parameters; the exceptional point only from the
trajectory.

That last row is worth stating on its own.  The exceptional point is exactly the
JORDAN FAILURE MODE that this repository's own `scattering_c_factorisation`
recorded as having been MISSED -- the case where the spectrum sits in the right
place but the operator is not diagonalizable.  Operationally it is the one
configuration that cannot be confirmed by measuring the theory's parameters, only
by watching it misbehave.  A criterion checked by parameter measurement will miss
it by construction, which is a reason it gets missed rather than an accident.

WHAT THIS DOES NOT ESTABLISH.  The bridge is built once, at the smallest possible
scale, and that is the whole claim.  It does NOT show the construction
generalises to the Lagrangian witnesses, which remain without operational
content; it does not use their formal machinery (topologies of verifiable
statements, sigma-algebras) but only the informal criterion; and it says nothing
about Weyl gravity, being two-dimensional linear algebra.  C-GHOST-DYNAMICS
stays OPEN.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.operational_witness --check
    PYTHONPATH=. python3 -m reverse_physics.operational_witness --emit
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import sympy as sp

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_OPERATIONAL_WITNESS_V1.json",
)

T = sp.Symbol("t", positive=True)
ETA = sp.Matrix([[1, 0], [0, -1]])

BOUNDED, SECULAR, EXPONENTIAL = "BOUNDED", "SECULAR", "EXPONENTIAL"


def hamiltonian(a, d, b):
    return sp.Matrix([[a, b], [-b, d]])


def discriminant(a, d, b):
    return (a - d) ** 2 - 4 * b ** 2


def amplitude(a, d, b):
    """|U(t) e_1|^2 for U(t) = exp(-i H t): the observable."""
    U = sp.simplify(sp.exp(-sp.I * hamiltonian(a, d, b) * T))
    return sp.simplify(sp.Abs(U[0, 0]) ** 2 + sp.Abs(U[1, 0]) ** 2)


def classify(amp):
    """BOUNDED / SECULAR / EXPONENTIAL, from the amplitude itself."""
    rate = sp.simplify(sp.limit(sp.log(amp) / T, T, sp.oo))
    if rate != 0:
        return EXPONENTIAL, rate
    # rate zero: bounded or polynomial.  Bounded iff the limsup is finite,
    # which for these closed forms is decided by whether the expression is
    # bounded above -- tested by the limit of amp itself.
    lim = sp.limit(amp, T, sp.oo)
    if lim == sp.oo:
        return SECULAR, rate
    return BOUNDED, rate


CASES = [
    ("harmless", 5, 0, 2, BOUNDED),
    ("exceptional", 2, 0, 1, SECULAR),
    ("unstable", 1, 0, 1, EXPONENTIAL),
]


# Verifiability in the Assumptions-of-Physics sense: a statement is verifiable
# if a finite procedure confirms it in finite time.  These are JUDGEMENTS about
# their criterion applied to our regimes, recorded so they can be disputed; the
# amplitudes and the openness are computed.
VERIFIABILITY = {
    "harmless": {
        "by_parameters": True,
        "why_parameters": "Delta > 0 is an OPEN condition on (a,d,b), so "
                          "finite-precision measurement confirms it",
        "by_trajectory": False,
        "why_trajectory": "'stays bounded forever' cannot be confirmed by any "
                          "finite observation.  Refutable, not verifiable",
    },
    "exceptional": {
        "by_parameters": False,
        "why_parameters": "Delta = 0 is CLOSED WITH EMPTY INTERIOR -- a "
                          "measure-zero set -- so no finite-precision "
                          "measurement can ever confirm it",
        "by_trajectory": True,
        "why_trajectory": "the amplitude grows without bound, so any threshold "
                          "is crossed in finite time",
    },
    "unstable": {
        "by_parameters": True,
        "why_parameters": "Delta < 0 is an OPEN condition",
        "by_trajectory": True,
        "why_trajectory": "the amplitude grows exponentially",
    },
}


def openness(name, a, d, b):
    """Is the defining condition open in parameter space?"""
    delta = discriminant(a, d, b)
    if delta == 0:
        return {"condition": "Delta = 0", "open": False,
                "empty_interior": True,
                "why": "a codimension-one zero set of a polynomial"}
    return {"condition": "Delta %s 0" % (">" if delta > 0 else "<"),
            "open": True, "empty_interior": False,
            "why": "a strict polynomial inequality"}


def build():
    rows = []
    for name, a, d, b, expected in CASES:
        amp = amplitude(a, d, b)
        kind, rate = classify(amp)
        rows.append({
            "case": name,
            "H": [[a, b], [-b, d]],
            "discriminant": int(discriminant(a, d, b)),
            "amplitude": str(amp),
            "behaviour": kind,
            "expected_behaviour": expected,
            "matches": kind == expected,
            "exponential_rate": str(rate),
            "openness": openness(name, a, d, b),
            "verifiable_by_parameters":
                VERIFIABILITY[name]["by_parameters"],
            "verifiable_by_trajectory":
                VERIFIABILITY[name]["by_trajectory"],
        })

    by = {r["case"]: r for r in rows}

    checks = {
        # the observable really does separate the three regimes
        "the_three_regimes_are_operationally_distinct":
            len({r["behaviour"] for r in rows}) == 3,
        "each_behaviour_is_the_predicted_one":
            all(r["matches"] for r in rows),
        # the two failure modes differ from each other -- the operational
        # shadow of diagonalizability and reality being independent
        "the_two_failure_modes_are_distinguishable":
            by["exceptional"]["behaviour"] != by["unstable"]["behaviour"],
        "the_exponential_rate_alone_does_not_separate_them":
            by["harmless"]["exponential_rate"]
            == by["exceptional"]["exponential_rate"],
        # verifiability
        "every_regime_is_verifiable_by_at_least_one_modality":
            all(r["verifiable_by_parameters"] or r["verifiable_by_trajectory"]
                for r in rows),
        "no_modality_verifies_all_three":
            not all(r["verifiable_by_parameters"] for r in rows)
            and not all(r["verifiable_by_trajectory"] for r in rows),
        "harmlessness_needs_the_parameters":
            by["harmless"]["verifiable_by_parameters"]
            and not by["harmless"]["verifiable_by_trajectory"],
        "the_exceptional_point_needs_the_trajectory":
            by["exceptional"]["verifiable_by_trajectory"]
            and not by["exceptional"]["verifiable_by_parameters"],
        # the openness that underwrites the parameter column
        "open_conditions_are_exactly_the_nonzero_discriminants":
            all(r["openness"]["open"] == (r["discriminant"] != 0)
                for r in rows),
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_OPERATIONAL_WITNESS_V1",
        "kind": "bridge",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "One witness of this stream given operational content -- states, "
            "evolution and a measurement -- to test whether the bridge to an "
            "experimental-verifiability framework is buildable at all.  The "
            "Krein family is a system: states are rays carrying eta = "
            "diag(1,-1), evolution is U(t) = exp(-i H t), the observable is "
            "|U(t) e_1|^2.  The three regimes of the harmlessness criterion "
            "are three operationally DISTINCT behaviours -- bounded, secular, "
            "exponential -- so the two failure modes are distinguishable from "
            "each other, which is the laboratory shadow of diagonalizability "
            "and real spectrum being independent conditions.  In "
            "verifiability terms: every regime is confirmable by at least one "
            "of the two modalities, NO modality confirms all three, "
            "harmlessness is confirmable only from the parameters, and the "
            "EXCEPTIONAL POINT is confirmable only from the trajectory -- "
            "being a measure-zero condition no finite-precision parameter "
            "measurement can ever establish.",
        "does_not_establish": [
            "that the construction generalises.  The bridge is built ONCE, at "
            "the smallest possible scale.  The Lagrangian-density witnesses -- "
            "sqrt(-g)(g^00)^2, sqrt(-g) phi^4, R^2 -- remain WITHOUT "
            "operational content, and dressing them up would be pretending",
            "any use of the Assumptions of Physics formal machinery.  Only the "
            "informal criterion (a finite procedure confirming in finite time) "
            "is used; the topologies of verifiable statements and the "
            "sigma-algebras are not",
            "anything about Weyl gravity.  This is two-dimensional linear "
            "algebra.  C-GHOST-DYNAMICS stays OPEN",
            "the verifiability verdicts as computations.  The amplitudes and "
            "the openness are computed; which statements count as verifiable "
            "is a JUDGEMENT about their criterion applied to our regimes, "
            "recorded so it can be disputed",
        ],
        "the_system": {
            "states": "rays in a two-dimensional complex space carrying the "
                      "indefinite form eta = diag(1,-1): one positive-norm and "
                      "one negative-norm direction, the minimal ghost",
            "evolution": "U(t) = exp(-i H t), H(a,d,b) = [[a,b],[-b,d]] the "
                         "general eta-pseudo-Hermitian generator",
            "observable": "|U(t) e_1|^2, the squared amplitude of an evolved "
                          "state",
        },
        "regimes": rows,
        "verifiability": VERIFIABILITY,
        "the_missed_mode": {
            "what": "the exceptional point Delta = 0 is exactly the JORDAN "
                    "FAILURE MODE that this repository's own "
                    "scattering_c_factorisation recorded as having been MISSED "
                    "-- spectrum in the right place, operator not "
                    "diagonalizable",
            "operational_reading": "it is the one configuration that cannot be "
                                   "confirmed by measuring the theory's "
                                   "parameters, only by watching it misbehave.  "
                                   "A criterion checked by parameter "
                                   "measurement misses it BY CONSTRUCTION, "
                                   "which is a reason it gets missed rather "
                                   "than an accident",
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/operational-witness.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("the system: %s" % cert["the_system"]["evolution"])
    print("  %-12s %6s  %-12s %-34s %s"
          % ("regime", "Delta", "behaviour", "|U e1|^2", "verifiable by"))
    for r in cert["regimes"]:
        mods = []
        if r["verifiable_by_parameters"]:
            mods.append("parameters")
        if r["verifiable_by_trajectory"]:
            mods.append("trajectory")
        print("  %-12s %6d  %-12s %-34s %s"
              % (r["case"], r["discriminant"], r["behaviour"],
                 r["amplitude"], ", ".join(mods)))
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
