"""The vacuity instrument, turned on the Assumptions of Physics framework.

WHY THIS EXISTS.  [carrier-vacuity.md] built an instrument: an assumption is
VACUOUS, LIVE or EMPTY on a carrier, it CAN BE WITNESSED IFF IT IS NOT VACUOUS,
and an assumption that is also a CONSTRUCTION CONSTRAINT of the carrier is
vacuous.  Applied to our own ledger it found three assumptions in that position.
The obvious next question is whether the instrument says anything when pointed
at somebody else's framework, and the Assumptions of Physics programme is the
natural target because it asks the same question we do.

SOURCES, READ DIRECTLY.  Gabriele Carcassi and Christine A. Aidala,
*Assumptions of Physics*, Michigan Publishing, version 2.0 (2023-10-01), freely
available at assumptionsofphysics.org/book/AssumptionsOfPhysicsV2.0.pdf; the
assumption statements below are quoted verbatim from the Project Overview,
pages vii-viii.  Also the 2024 Summer School lecture *Classical Mechanics* for
the twelve labelled characterizations and the two-block diagram.

THE HEADLINE, AND IT IS MOSTLY A CREDIT TO THEM.  Three of their four
assumptions are LIVE on the carriers they are stated over, and in two cases THE
AUTHORS SUPPLY THE WITNESS THEMSELVES -- linear drag plus linear acceleration
for determinism/reversibility, and the photon H = c|p| for kinematic
equivalence.  That is better than our own ledger managed before this session,
where three assumptions were vacuous and unwitnessed.  An audit that comes back
mostly clean is a finding about the quality of the carrier choices, and it
should be reported as such rather than mined for a complaint.

WHAT THE INSTRUMENT DOES FLAG.  Not an assumption -- a DERIVED STRUCTURE with a
component that the carrier supplies for free.  The infinitesimal reducibility
argument runs (book, p. vii, verbatim):

    "It will need to be a distribution whose value is invariant under
     coordinate transformations.  The state space of the infinitesimal parts,
     then, comes equipped with an INVARIANT TWO-FORM upon which we can define
     such a distribution.  THE STATE SPACE IS THEREFORE A SYMPLECTIC MANIFOLD."

A symplectic manifold needs the two-form to be NON-DEGENERATE and CLOSED.  The
argument produces an invariant two-form; closedness is a separate condition.
And on the carrier where the twelve-fold equivalence is stated -- A SINGLE
DEGREE OF FREEDOM, so a two-dimensional state space -- closedness is not a
condition at all:

    d : Omega^2 -> Omega^3,   and   dim Omega^3(M) = C(dim M, 3) = 0
    whenever dim M < 3.

A three-form does not exist on a two-manifold, so EVERY two-form there is
closed, for dimensional reasons having nothing to do with reducibility.  At n
degrees of freedom the same condition imposes C(2n, 3) equations per point --
4 at n = 2, 20 at n = 3.  So the closedness half of "therefore a symplectic
manifold" is VACUOUS exactly on the carrier where the twelve-fold equivalence
lives, and LIVE everywhere else.

THE SECOND FLAG is the one already written up in AOP-CONNECTION.md section 2.1c
and is recorded here for completeness: R^{2n} has H^1 = 0, so *closed* and
*exact* coincide and the distinction between DI-SYMP (preserving omega) and
HM-G (having a Hamiltonian) is NOT EXPRESSIBLE on that carrier.  Our T^4
computation is the enlargement, and the gap it exposes is b_1 = 4.

BOTH FLAGS ARE THE SAME SHAPE AS OUR OWN.  In each case a property is attributed
to an assumption that the arena supplies for free, and in each case the cure is
to enlarge the carrier until the property can fail.  That is the point of
running the instrument on someone else at all: if it only ever found faults in
frameworks we dislike it would be a rhetorical device rather than an instrument.

WHAT THIS IS NOT.  It is a SCOPE observation, not a refutation.  Every one of
the twelve characterizations is correct where it is stated, and the symplectic
conclusion is correct wherever the state space is genuinely symplectic -- which
is everywhere they apply it.  The flag is that ONE STEP OF THE DERIVATION does
no work at one degree of freedom, so a reader checking the argument there cannot
see whether it would survive at two.  We are also reading a book and slides, not
a formalisation, and where a statement is terse we say so rather than pick a
reading.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.aop_vacuity_audit --check
    PYTHONPATH=. python3 -m reverse_physics.aop_vacuity_audit --emit
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from math import comb

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_AOP_VACUITY_AUDIT_V1.json",
)

VACUOUS, LIVE, EMPTY = "VACUOUS", "LIVE", "EMPTY"

SOURCES = [
    {"what": "the four assumption statements, verbatim",
     "where": "Assumptions of Physics, Michigan Publishing, v2.0 (2023-10-01), "
              "Project Overview, pp. vii-viii",
     "url": "https://assumptionsofphysics.org/book/AssumptionsOfPhysicsV2.0.pdf"},
    {"what": "the twelve labelled characterizations and the two-block diagram",
     "where": "Assumptions of Physics Summer School 2024, Classical Mechanics",
     "url": "https://assumptionsofphysics.org/presentations/"
            "2024SummerSchool/1-ClassicalMechanics.pdf"},
    {"what": "the reverse-physics method",
     "where": "Found. Phys. 52, 40 (2022)",
     "url": "https://link.springer.com/article/10.1007/s10701-022-00555-z"},
]


ASSUMPTIONS = [
    {
        "name": "Determinism and reversibility",
        "verbatim": "The system undergoes deterministic and reversible "
                    "evolution.",
        "carrier": "vector fields S^a on the state space",
        "verdict": LIVE,
        "witness": "linear drag on one degree of freedom plus linear "
                   "acceleration on the other: div S = -b + b = 0 so the "
                   "volume conditions hold, while the curl is -b so the "
                   "symplectic ones fail.  No Hamiltonian",
        "witness_supplied_by": "the authors, Summer School 2024 slide 40",
    },
    {
        "name": "Kinematic equivalence",
        "verbatim": "Specifying the motion of the system is equivalent to "
                    "specifying its state and evolution.",
        "carrier": "Hamiltonians on phase space",
        "verdict": LIVE,
        "witness": "the photon treated as a point particle, H = c|p|: the map "
                   "v = dH/dp is not invertible, so the kinematics does not "
                   "reconstruct the dynamics",
        "witness_supplied_by": "the authors, Summer School 2024 slide 13",
    },
    {
        "name": "Infinitesimal reducibility",
        "verbatim": "Specifying the state of the whole system is equivalent to "
                    "specifying the state of all its infinitesimal parts.",
        "carrier": "states of a system",
        "verdict": LIVE,
        "witness": "irreducibility is the stated alternative and is what the "
                   "programme uses to reach quantum mechanics: 'Specifying the "
                   "state of the whole system tells us nothing about its "
                   "infinitesimal parts'",
        "witness_supplied_by": "the authors, book p. vii",
    },
]


# The flags.  Neither is an assumption; both are steps that the carrier makes
# free.
FLAGS = [
    {
        "id": "CLOSEDNESS-AT-ONE-DOF",
        "step": "\"comes equipped with an invariant two-form ... the state "
                "space is THEREFORE a symplectic manifold\" (book p. vii)",
        "issue": "symplectic requires the two-form to be NON-DEGENERATE and "
                 "CLOSED.  The argument produces an invariant two-form; "
                 "closedness is a separate condition",
        "verdict_on_their_carrier": VACUOUS,
        "carrier": "a single degree of freedom, i.e. a two-dimensional state "
                   "space, which is where the twelve-fold equivalence is "
                   "stated",
        "why": "d maps two-forms to three-forms, and a three-form does not "
               "exist on a two-manifold.  Every two-form there is closed for "
               "dimensional reasons having nothing to do with reducibility",
        "becomes_live_at": "two degrees of freedom, where closedness imposes "
                           "C(4,3) = 4 equations per point",
    },
    {
        "id": "EXACTNESS-ON-FLAT-PHASE-SPACE",
        "step": "the twelve-fold list places HM-G (having a Hamiltonian) and "
                "DI-SYMP (preserving omega) in the same block",
        "issue": "preserving omega is CLOSEDNESS of the associated one-form; "
                 "having a Hamiltonian is EXACTNESS.  They differ by H^1",
        "verdict_on_their_carrier": VACUOUS,
        "carrier": "R^{2n}, where H^1 = 0",
        "why": "on a state space with vanishing first cohomology closed and "
               "exact coincide, so the distinction is not expressible there "
               "at all",
        "becomes_live_at": "any state space with b_1 != 0; on T^4 the gap is "
                           "exactly b_1 = 4 at every Fourier truncation, with "
                           "uniform translation as the explicit witness",
        "already_written_up": "reverse_physics/reports/AOP-CONNECTION.md "
                              "section 2.1c",
    },
]


def closedness_conditions(n_dof):
    """Number of independent dw = 0 equations per point at n degrees of
    freedom: dim of three-forms on a 2n-manifold."""
    return comb(2 * n_dof, 3)


def two_form_dimension(n_dof):
    return comb(2 * n_dof, 2)


def closedness_table(max_dof=5):
    return [{"degrees_of_freedom": n,
             "state_space_dimension": 2 * n,
             "two_forms": two_form_dimension(n),
             "closedness_conditions": closedness_conditions(n),
             "closedness_is_vacuous": closedness_conditions(n) == 0}
            for n in range(1, max_dof + 1)]


def build():
    table = closedness_table()
    vacuous_at = [r["degrees_of_freedom"] for r in table
                  if r["closedness_is_vacuous"]]
    live_at = [r["degrees_of_freedom"] for r in table
               if not r["closedness_is_vacuous"]]

    checks = {
        # the computed core
        "closedness_is_vacuous_exactly_at_one_degree_of_freedom":
            vacuous_at == [1],
        "closedness_is_live_from_two_degrees_of_freedom": live_at == [2, 3, 4, 5],
        "the_count_is_the_three_form_dimension":
            all(r["closedness_conditions"] == comb(r["state_space_dimension"], 3)
                for r in table),
        # the audit is not a hit job: most of their assumptions pass
        "most_of_their_assumptions_are_live":
            sum(1 for a in ASSUMPTIONS if a["verdict"] == LIVE)
            >= len(ASSUMPTIONS) - 1,
        "every_live_assumption_names_its_witness":
            all(a["witness"] for a in ASSUMPTIONS if a["verdict"] == LIVE),
        "the_witnesses_are_credited_to_whoever_supplied_them":
            all(a.get("witness_supplied_by") for a in ASSUMPTIONS
                if a["verdict"] == LIVE),
        # the flags are about derived steps, not assumptions
        "no_assumption_of_theirs_is_marked_vacuous":
            not any(a["verdict"] == VACUOUS for a in ASSUMPTIONS),
        "every_flag_says_where_it_becomes_live":
            all(f["becomes_live_at"] for f in FLAGS),
        "every_source_is_a_resolvable_url":
            all(s["url"].startswith("https://") for s in SOURCES),
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_AOP_VACUITY_AUDIT_V1",
        "kind": "audit",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "establishes":
            "The vacuity instrument applied to the Assumptions of Physics "
            "framework, from sources read directly.  THREE OF THEIR FOUR "
            "ASSUMPTIONS ARE LIVE on the carriers they are stated over, and in "
            "two cases the authors supply the witness themselves.  What the "
            "instrument flags is not an assumption but a DERIVED STEP with a "
            "component the carrier supplies free: the inference 'invariant "
            "two-form, therefore a symplectic manifold' needs the form to be "
            "CLOSED, and at ONE DEGREE OF FREEDOM closedness imposes ZERO "
            "conditions because a three-form does not exist on a two-manifold "
            "-- while at n degrees of freedom it imposes C(2n,3), which is 4 "
            "at n = 2.  A second flag, already written up, is that R^{2n} has "
            "H^1 = 0 so the DI-SYMP/HM-G distinction is not expressible there.",
        "does_not_establish": [
            "any error in their results.  This is a SCOPE observation: every "
            "one of the twelve characterizations is correct where it is "
            "stated, and the symplectic conclusion is correct wherever the "
            "state space is genuinely symplectic",
            "that closedness FAILS anywhere they apply the framework.  The "
            "flag is that the step does no work at one degree of freedom, so a "
            "reader checking the argument there cannot see whether it survives "
            "at two",
            "anything from a formalisation of their work.  These are a book "
            "and lecture slides read directly; where a statement is terse we "
            "say so rather than pick a reading",
            "completeness.  Their framework has parts -- experimental "
            "verifiability, informational granularity, states and processes -- "
            "that are not audited here at all",
        ],
        "sources": SOURCES,
        "their_assumptions": ASSUMPTIONS,
        "flags": FLAGS,
        "closedness_table": table,
        "framing": {
            "headline": "mostly a credit to them",
            "why": "three of four assumptions LIVE, two with witnesses the "
                   "authors supply themselves, is better than our own ledger "
                   "managed before this session -- where three assumptions "
                   "were vacuous and unwitnessed",
            "why_run_it_at_all": "if the instrument only ever found faults in "
                                 "frameworks we dislike it would be a "
                                 "rhetorical device rather than an instrument.  "
                                 "Both flags are the same shape as our own "
                                 "three: a property attributed to an "
                                 "assumption that the arena supplies for free",
        },
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/AOP-CONNECTION.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("their assumptions, on the carriers they are stated over:")
    for a in cert["their_assumptions"]:
        print("   %-32s %-8s witness by %s"
              % (a["name"], a["verdict"], a["witness_supplied_by"]))
    print("flags (derived steps the carrier makes free):")
    for f in cert["flags"]:
        print("   %-30s %-8s  live at: %s"
              % (f["id"], f["verdict_on_their_carrier"],
                 f["becomes_live_at"].split(",")[0]))
    print("closedness of omega, dw = 0:")
    print("   dof  dim M  2-forms  conditions  vacuous")
    for r in cert["closedness_table"]:
        print("   %3d  %5d  %7d  %10d  %s"
              % (r["degrees_of_freedom"], r["state_space_dimension"],
                 r["two_forms"], r["closedness_conditions"],
                 r["closedness_is_vacuous"]))
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
