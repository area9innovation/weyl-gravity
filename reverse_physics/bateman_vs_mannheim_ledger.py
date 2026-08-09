"""Bateman-Turok vs Mannheim: one premise slot, two fillings, five levels.

WHY THIS EXISTS.  The two programmes that claim to make fourth-order gravity
sensible are usually discussed as rival answers to one question.  They are not.
Asking whether they are complementary, overlapping, or alternative
reverse-physics options has no single answer -- AND THAT IS THE RESULT, not
vagueness.  As with `weyl_vs_einstein_ledger`, the comparison needs a LEVEL
axis, because the same sentence flips truth value between levels:

    "the two completions agree"     TRUE at the free level (L2)
                                    FALSE in the interacting theory (L4)

A comparison stated without the level column does not merely lose precision, it
contradicts itself.  Both truth values are already proved in this repository,
which is what forces the axis:

    L2   Paper 04, thm:bridge4.  The positive pseudo-Hermitian and Krein
         completions "induce the same complex quasifree functional on the
         gauge-invariant observable algebra A_inv; they differ in involution
         and completion only."
    L4   Paper 05, cprop:krein.  Krein pseudo-unitarity is exact ON THE SAME
         MATRIX ELEMENTS where every positive pointed metric is obstructed.
         The two real forms SEPARATE.

THE CRUX, AND IT IS A SINGLE SLOT.  Both programmes accept the same action, the
same complex spectral covariance, and the same requirement of non-negative
energies.  They differ in exactly one premise:

    WHICH INVOLUTION IS PHYSICAL?

  * Mannheim fills it with POSITIVE-DEFINITE.  Price: the dynamics must be
    diagonalizable with real spectrum (established in `ghost_harmless`), and
    the field is rotated into the complex plane -- Paper 06's "quarter-turn",
    and his own "we had to continue z into the complex plane and replace it by
    y = -iz".
  * Bateman-Turok fill it with INDEFINITE.  Price: the Born rule is generalized
    to tr(A^dag A), and positivity is carried by a charge grading whose
    one-sidedness Paper 05 shows is exact iff eps = 0.  The field stays real --
    Paper 06's "retains standard gravitational reality".

So they are not two theories.  They are TWO REAL FORMS OF ONE COMPLEX
STRUCTURE, and the choice between them is a choice of involution, i.e. of which
operators are required to be self-adjoint.

WHY THEY ARE COMPLEMENTARY RATHER THAN REDUNDANT.  Each has a regime where the
OTHER's premise is unsatisfiable, and both witnesses are already computed here:

  * Drop DIAGONALIZABLE and you are at the coincident-pole/Jordan point -- which
    is exactly where pure Weyl gravity's 1/k^4 sits.  Mannheim's similarity
    transformation is singular there (Paper 04) and his own Sec. VI withdraws
    the cutting rules.  Only the Krein real form continues nondegenerately.
  * Drop ONE-SIDED CHARGE and Bateman-Turok's null component is not null.
    Paper 05's cprop:embedding: one-sidedness holds iff eps = 0; at split mass
    both charge signs appear.

Neither premise is generic.  Each is a boundary condition, and they are
boundary conditions on DIFFERENT boundaries.

THE ROW PEOPLE GET WRONG is L5.  At loop level, at the coincident point, NEITHER
programme has a result: Mannheim's cutting rules are withdrawn there by his own
Sec. VI, and Bateman-Turok prove positivity at TREE level only, naming collinear
infrared divergence as their obstacle.  The literature reads each as having
settled the question; at the level that matters for Weyl gravity, both are open,
and they are open for unrelated reasons.

CROSS-FERTILIZATION, and the first one is concrete rather than programmatic.

  (1) BT -> MANNHEIM, and it is a candidate cure for exactly his disease.
      Mannheim's failure at coincident poles is that the cut weight becomes
      -delta'(s - m), which is no measure of any sign.  That pathology is a
      property of the FOURTH-ORDER VARIABLE, not of the theory: the O(1,1)
      embedding replaces one fourth-order field by two second-order fields with
      an off-diagonal propagator, so the poles are simple and the cuts are
      ordinary delta functions.  The double pole is dissolved by a change of
      variables.  What survives is bookkeeping -- which is why BT reach tree
      level at the point where Mannheim stops.
  (2) MANNHEIM -> BT, weaker and flagged as speculative.  BT's stated obstacle
      is collinear infrared divergence "affecting asymptotic states"; PT/C
      machinery is about constructing inner products on sectors where the naive
      one fails.  Whether it applies to an infrared rather than a signature
      problem is not established and is not claimed here.
  (3) THIS REPOSITORY -> BT, now an exact obstruction rather than a proposed
      regulator.  The neutral mass mu^2 Omega Upsilon retains charge and a
      formal double root only at a held nonstationary background.  At the true
      stationary branch one root remains massless and the poles are simple.
      The loop extension therefore needs a non-mass infrared architecture.
  (4) PAPER 04 -> BOTH, as discipline.  Because the two completions induce the
      same functional on the gauge-invariant algebra, ANY free-field-level
      dispute between the camps is about the involution and not about
      predictions.  That retires a large class of arguments without settling
      the physical question.

WHAT THIS LEDGER IS NOT.  It adjudicates nothing.  Every row is a pointer to a
result proved elsewhere in this tree or quoted from the sources; the
contribution is the axis, the slot identification, and the two independence
witnesses being placed on the same page.  No new physics is computed here.

Dependency tag: LOCAL-ALGEBRAIC.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BATEMAN_VS_MANNHEIM_LEDGER_V1.json")

# direction: SHARED | BT-OPENS | M-OPENS | BOTH-STOP
LEVELS = [
    {
        "level": "L1",
        "name": "action and classical field equations",
        "direction": "SHARED",
        "claim": "same fourth-order action, same classical content; neither "
                 "programme modifies the Lagrangian",
        "source": "both, by construction",
    },
    {
        "level": "L2",
        "name": "free state space and observables",
        "direction": "SHARED",
        "claim": "the two completions induce the SAME complex quasifree "
                 "functional on the gauge-invariant observable algebra; they "
                 "differ in involution and completion only",
        "source": "paper/04-fourth-order-gravity.tex, thm:bridge4",
        "agree": True,
    },
    {
        "level": "L3",
        "name": "the coincident-pole (Jordan) point",
        "direction": "BT-OPENS",
        "claim": "the positive metric has no nondegenerate continuation "
                 "through c1 = 0 and the similarity transformation is singular "
                 "in the equal-frequency limit; only the Krein real form "
                 "continues as a nondegenerate completion. Mannheim's own "
                 "Sec. VI withdraws the cutting rules there",
        "source": "paper/04-fourth-order-gravity.tex, thm:term and "
                  "rem:mannheimloop; Mannheim PRD 98 045014 Sec. VI",
    },
    {
        "level": "L4",
        "name": "interacting theory, second order",
        "direction": "BT-OPENS",
        "claim": "Krein pseudo-unitarity is exact on the same matrix elements "
                 "on which every positive pointed metric is obstructed: the "
                 "two real forms SEPARATE",
        "source": "paper/05-interaction-obstructions.tex, cprop:krein",
        "agree": False,
    },
    {
        "level": "L5",
        "name": "loops at the coincident point",
        "direction": "BOTH-STOP",
        "claim": "neither programme has a result. Mannheim's cutting rules are "
                 "withdrawn at the Jordan block by his own Sec. VI; "
                 "Bateman-Turok prove positivity at TREE level only and name "
                 "collinear infrared divergence as the obstacle. The two "
                 "failures are unrelated",
        "source": "REVERSE_PHYSICS_MANNHEIM_CUTTING_RULES_V1; "
                  "arXiv:2607.00096 conclusions",
        "commonly_misread": True,
    },
]

# The single contested premise slot, and what each filling costs.
SLOT = {
    "premise": "which involution is physical",
    "mannheim": {
        "filling": "positive definite",
        "requires": "diagonalizable AND real spectrum",
        "requires_source": "reverse_physics/ghost_harmless.py",
        "price": "the field is rotated into the complex plane (Paper 06's "
                 "quarter-turn; his own 'replace z by y = -iz')",
        "keeps_field_real": False,
    },
    "bateman_turok": {
        "filling": "indefinite (Krein)",
        "requires": "a charge grading with one-sided charge",
        "requires_source": "paper/05-interaction-obstructions.tex, "
                           "lem:chargenull and cprop:embedding",
        "price": "the Born rule is generalized to tr(A^dag A)",
        "keeps_field_real": True,
    },
}

# Reverse-physics independence: drop the premise, and the OTHER programme
# still has a model.  Both witnesses are computed elsewhere in this tree.
WITNESSES = [
    {
        "drop": "diagonalizable (Mannheim)",
        "witness": "the coincident-pole point -- exactly where pure Weyl "
                   "gravity's 1/k^4 sits",
        "survivor": "bateman_turok",
        "source": "paper/04-fourth-order-gravity.tex, thm:term",
    },
    {
        "drop": "one-sided charge (Bateman-Turok)",
        "witness": "split mass, eps != 0, where both charge signs appear",
        "survivor": "mannheim",
        "source": "paper/05-interaction-obstructions.tex, cprop:embedding",
    },
]

CROSS = [
    {
        "direction": "BT -> Mannheim",
        "strength": "concrete",
        "content": "the O(1,1) embedding replaces one fourth-order field by "
                   "two second-order fields with an off-diagonal propagator, "
                   "so poles are simple and cuts are ordinary delta functions. "
                   "Mannheim's -delta'(s-m) pathology is a property of the "
                   "fourth-order VARIABLE and is dissolved by the change of "
                   "variables",
    },
    {
        "direction": "Mannheim -> BT",
        "strength": "speculative, flagged",
        "content": "PT/C machinery constructs inner products where the naive "
                   "one fails; whether that bears on an INFRARED rather than a "
                   "signature problem is not established and is not claimed",
    },
    {
        "direction": "this repository -> BT",
        "strength": "exact obstruction",
        "content": "mu^2 Omega Upsilon preserves charge and a formal double "
                   "root only at the held nonstationary BT background, where "
                   "d_Upsilon V=v*mu^2. On the true stationary branch the "
                   "roots are 0 and -2*mu^2, so a non-mass infrared "
                   "architecture is required",
        "source": "REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1",
    },
    {
        "direction": "Paper 04 -> both",
        "strength": "discipline",
        "content": "since the completions induce the same functional on the "
                   "gauge-invariant algebra, any FREE-LEVEL dispute between "
                   "the camps is about the involution, not about predictions",
    },
]


def build():
    levels_by_id = {r["level"]: r for r in LEVELS}
    directions = {r["direction"] for r in LEVELS}

    # The axis is FORCED only if some sentence actually flips truth value.
    agree_l2 = levels_by_id["L2"].get("agree")
    agree_l4 = levels_by_id["L4"].get("agree")
    flip = agree_l2 is True and agree_l4 is False

    # Complementarity is real only if EACH programme is the survivor of some
    # witness.  If one survived both, it would dominate rather than complement.
    survivors = {w["survivor"] for w in WITNESSES}
    genuinely_complementary = survivors == {"mannheim", "bateman_turok"}

    checks = {
        "level_axis_is_forced_by_a_truth_value_flip": flip,
        "every_level_cites_a_source": all(r.get("source") for r in LEVELS),
        "ledger_is_not_uniformly_one_direction": len(directions) >= 3,
        "both_programmes_survive_some_witness": genuinely_complementary,
        "each_witness_cites_a_source": all(w.get("source") for w in WITNESSES),
        "the_contested_slot_is_single": isinstance(SLOT["premise"], str),
        "the_two_fillings_are_opposite": (
            SLOT["mannheim"]["keeps_field_real"]
            != SLOT["bateman_turok"]["keeps_field_real"]),
        "a_both_stop_row_exists": "BOTH-STOP" in directions,
        "cross_fertilization_is_graded_by_strength": (
            {c["strength"] for c in CROSS} >= {
                "concrete", "exact obstruction", "speculative, flagged"
            }),
    }
    failures = [k for k, v in checks.items() if not v]

    return {
        "certificate": "REVERSE_PHYSICS_BATEMAN_VS_MANNHEIM_LEDGER_V1",
        "dependency_tag": "LOCAL-ALGEBRAIC",
        "lifecycle_state": "CLASSIFIED",
        "question": "Are Bateman-Turok and Mannheim complementary, "
                    "overlapping, or alternative reverse-physics options?",
        "answer": "All three, at different levels, and the level axis is what "
                  "makes that a result rather than an evasion. They are two "
                  "REAL FORMS of one complex structure, differing in a single "
                  "premise -- which involution is physical. OVERLAPPING at the "
                  "free level, where they induce the same functional on the "
                  "gauge-invariant algebra. ALTERNATIVE in the interacting "
                  "theory, where they separate. COMPLEMENTARY in the sense "
                  "that each has a regime where the other's premise is "
                  "unsatisfiable. And at loop level at the coincident point -- "
                  "the level that matters for Weyl gravity -- NEITHER has a "
                  "result.",
        "contested_slot": SLOT,
        "levels": LEVELS,
        "independence_witnesses": WITNESSES,
        "cross_fertilization": CROSS,
        "does_not_establish": [
            "any adjudication between the programmes; every row points at a "
            "result proved elsewhere or quoted from the sources",
            "any new physics -- the contribution is the axis, the slot "
            "identification, and placing the two witnesses on one page",
            "that the speculative Mannheim -> BT transfer works; it is flagged "
            "as unestablished",
            "anything LORENTZIAN-CAUSAL",
        ],
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failures": failures,
            "ok": not failures,
        },
        "report": "reverse_physics/reports/bateman-vs-mannheim.md",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bateman-Turok vs Mannheim ledger")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    if not (args.check or args.emit):
        args.check = True

    cert = build()
    print("Bateman-Turok vs Mannheim -- one slot, two fillings, five levels")
    print()
    print("  contested premise: %s" % cert["contested_slot"]["premise"])
    print("    Mannheim       : %-22s requires %s"
          % (SLOT["mannheim"]["filling"], SLOT["mannheim"]["requires"]))
    print("    Bateman-Turok  : %-22s requires %s"
          % (SLOT["bateman_turok"]["filling"],
             SLOT["bateman_turok"]["requires"]))
    print()
    print("  %-4s %-34s %s" % ("", "level", "direction"))
    for r in LEVELS:
        print("  %-4s %-34s %s%s"
              % (r["level"], r["name"], r["direction"],
                 "   <-- commonly misread" if r.get("commonly_misread") else ""))
    print()
    print("  independence witnesses:")
    for w in WITNESSES:
        print("    drop %-32s -> %s survives" % (w["drop"], w["survivor"]))
    print()
    print("  cross-fertilization:")
    for c in CROSS:
        print("    %-24s (%s)" % (c["direction"], c["strength"]))
    print()
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
